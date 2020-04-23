#### Supplementary code for corona-master.R

## Vergleich der Schätzungen Geheilte

all_ctry_est <- all_ctry %>%
  group_by(Ort) %>% 
  arrange(Ort) %>%
  mutate(`Genesene (Schätzung, China fit)` = 
           ((lag(`alle Fälle`,14, default = 0)-lag(Tote, 14, default = 0)) * 0.60) + 
           ((lag(`alle Fälle`,28, default = 0)-lag(Tote, 28, default = 0)) * 0.30) + 
           ((lag(`alle Fälle`,42, default = 0)-lag(Tote, 42, default = 0)) * 0.10)) %>%
  mutate(`Genesene (Schätzung BL)` = 
           ((lag(`alle Fälle`,10, default = 0)-lag(Tote, 10, default = 0)) * 0.85) + 
           ((lag(`alle Fälle`,17, default = 0)-lag(Tote, 17, default = 0)) * 0.11) + 
           ((lag(`alle Fälle`,38, default = 0)-lag(Tote, 38, default = 0)) * 0.04)) %>% 
  mutate(`Genesene (Schätzung NZZ)` = 
           ((lag(`alle Fälle`,14, default = 0)-lag(Tote, 14, default = 0)) * 0.75) + 
           ((lag(`alle Fälle`,21, default = 0)-lag(Tote, 21, default = 0)) * 0.10) + 
           ((lag(`alle Fälle`,28, default = 0)-lag(Tote, 28, default = 0)) * 0.10) +
           ((lag(`alle Fälle`,42, default = 0)-lag(Tote, 42, default = 0)) * 0.05)) %>% 
  ungroup()

#China

jhu_cn_est <- filter(all_ctry_est, Land == "China")  %>%
  group_by(Datum) %>%
  summarise(Genesene = sum(Genesene), 
            `Genesene (Schätzung BL)` = sum(`Genesene (Schätzung BL)`),
            `Genesene (Schätzung NZZ)` = sum(`Genesene (Schätzung NZZ)`),
            `Genesene (Schätzung, China fit)` = sum(`Genesene (Schätzung, China fit)`)) %>%
  select("Datum", "Genesene", "Genesene (Schätzung BL)", "Genesene (Schätzung NZZ)", "Genesene (Schätzung, China fit)")

tail(jhu_cn_est)
write_clip(jhu_cn_est)

#Schweiz

jhu_ch_est <- filter(all_ctry_est, Ort == "Switzerland")  %>% 
  select("Datum", 
         "Genesene", 
         "Genesene (Schätzung BL)", 
         "Genesene (Schätzung NZZ)", 
         "Genesene (Schätzung, China fit)")

write_clip(jhu_ch_est)

#### FT-style relative chart ROLLING AVERAGES, WORK IN PROGRESS ####
meta <- lastgr %>%
  group_by(Land, Datum) %>%
  summarise(fallzahl = sum(fallzahl, na.rm = T)) %>% 
  arrange(Land) %>% 
  mutate(tmin7 = lag(fallzahl, 7)) %>% #letzte 7 Tage
  mutate(delta7 = fallzahl-tmin7) %>%
  mutate(ravg =delta7/7) %>%
  filter(Datum < "2020-04-07")

ftrit <- filter(meta, Land == "Italy" & fallzahl > 99) %>% select(ravg) %>% deframe()
ftrch <- filter(meta, Land == "Switzerland" & fallzahl > 99) %>% select(ravg) %>% deframe()
ftrde <- filter(meta, Land == "Germany" & fallzahl > 99) %>% select(ravg) %>% deframe()
#ftrcn <- filter(meta, Land == "China" & fallzahl > 99) %>% select(ravg) %>% deframe()
ftrjp <- filter(meta, Land == "Japan" & fallzahl > 99) %>% select(ravg) %>% deframe()
ftrsk <-  filter(meta, Land == "Korea, South" & fallzahl > 99) %>% select(ravg) %>% deframe()
ftrus <-  filter(meta, Land == "US" & fallzahl > 99) %>% select(ravg) %>% deframe()
ftres <-  filter(meta, Land == "Spain" & fallzahl > 99) %>% select(ravg) %>% deframe()

#add china/sweden/spain ????

lmax <- max(length(ftrch), 
            length(ftrit),
            length(ftrde),
            #length(ftrcn),
            length(ftrjp),
            length(ftrsk),
            length(ftrus),
            length(ftres))

ftrit <- c(ftrit, rep(NA, lmax-length(ftrit)))
ftrch <- c(ftrch, rep(NA, lmax-length(ftrch)))
ftrde <- c(ftrde, rep(NA, lmax-length(ftrde)))
#ftrcn <- c(ftrcn, rep(NA, lmax-length(ftrcn)))
ftrjp <- c(ftrjp, rep(NA, lmax-length(ftrjp)))
ftrsk <- c(ftrsk, rep(NA, lmax-length(ftrsk)))
ftrus <- c(ftrus, rep(NA, lmax-length(ftrus)))
ftres <- c(ftres, rep(NA, lmax-length(ftres)))

#this could be done more beautifully with apply/lapply/sapply (if someone is the expert here, feel free)

ftr <- cbind((1:lmax)-1 ,ftrit, ftrch, ftrde, ftrjp, ftrsk, ftrus, ftres) %>% as.data.frame()

colnames(ftr) <- c("Tag", "Italien", "Schweiz", "Deutschland", 
                  "Japan", "Südkorea", "USA", "Spanien")

write_csv(ftr, "ftr-rolling.csv")

ft_plotr <- gather(ftr, Land, Wert, 2:ncol(ftr))

ggplot(ft_plotr, aes(Tag, Wert, color = Land)) +
  geom_line() + 
  geom_point() + 
  # geom_abline(intercept = log10(100), slope = log10(1.33),linetype="dashed", color = "gray40") + #33% daily growth
  # geom_abline(intercept = log10(100), slope = log10(1.10),linetype="dashed", color = "gray40") + #10% daily growth
  # geom_abline(intercept = log10(100), slope = log10(1.05),linetype="dashed", color = "gray40") + #05% daily growth
  theme_minimal() + 
  theme(legend.position="bottom") +
  scale_color_brewer(palette="Set2") + 
  scale_y_continuous(trans = 'log10', breaks = c(10,50, 100, 500, 1000, 5000, 10000,50000), limits = c(10, 50000)) + 
  xlab("Tage seit Fall 100")

#### NON-TIME-CHART

meta2 <- filter(meta, Land %in% c("Switzerland", "Germany", "US", "China", "Korea, South", "France", "Spain", "Japan", "United Kingdom", "Netherlands", "Austria"))
meta2$fallzahl[meta2$fallzahl < 49] <- NA
meta2$delta7[meta2$fallzahl < 49] <- NA

ggplot(meta2, aes(fallzahl, delta7, color = Land)) +
  geom_path() +
  theme_minimal() +
  scale_y_continuous(trans = 'log10') +
  scale_x_continuous(trans = 'log10')
  
write_csv(meta2, "non-time.csv")


