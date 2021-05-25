#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
options(scipen=999)
library(tidyverse)
library(clipr)
library(jsonlite)
library(readxl)
library(ggrepel)

setwd("~/Downloads")

#read-in
koeln <- read_excel("koeln_final.xlsx")
bawue <- read_excel("bawue_final.xlsx")

#regression analyis for Köln

#with migration background
fit <- lm(Coronafälle_kumulativ_pro_100000_Einwohner ~ Arbeitslosenquote + Mieten_in_Euro_pro_Quadratmeter + Abiturientenquote + Migrationshintergrund + Haushaltsdichte_pro_Hektar + AfD_2017, data=koeln)
summary(fit) # show results

koeln_r <- cor(x = koeln[3:29], y = koeln[30], use = "pairwise.complete.obs")^2 %>% 
  as.data.frame() %>%
  arrange(desc(Coronafälle_kumulativ_pro_100000_Einwohner))

ggplot(koeln, aes(x=Migrationshintergrund, y = Coronafälle_kumulativ_pro_100000_Einwohner, label = Name)) + 
  geom_point() +
  geom_smooth(method = lm) +
  geom_text_repel()

ggsave(filename = "inz-mighint-label.svg")

ggplot(koeln, aes(x=Migrationshintergrund, y = Coronafälle_kumulativ_pro_100000_Einwohner)) + 
  geom_point() +
  geom_smooth(method = lm)

ggsave(filename = "inz-mighint.svg")

#with foreigners
fit2 <- lm(Coronafälle_kumulativ_pro_100000_Einwohner ~ Arbeitslosenquote + Mieten_in_Euro_pro_Quadratmeter + Abiturientenquote + Ausländeranteil + Haushaltsdichte_pro_Hektar + AfD_2017, data=koeln)
summary(fit2) # show results

ggplot(koeln, aes(x=Ausländeranteil, y = Coronafälle_kumulativ_pro_100000_Einwohner, label = Name)) + 
  geom_point() +
  geom_smooth(method = lm) +
  geom_text_repel()

ggsave(filename = "inz-ausl-label.svg")

ggplot(koeln, aes(x=Ausländeranteil, y = Coronafälle_kumulativ_pro_100000_Einwohner)) + 
  geom_point() +
  geom_smooth(method = lm)

ggsave(filename = "inz-ausl.svg")

#just r-sqared mighint

fit_mh <- lm(Coronafälle_kumulativ_pro_100000_Einwohner ~  Migrationshintergrund, data=koeln)
summary(fit_mh) # show results


#regression analysis for Baden-Wüttemberg (vaccinations)

bawue_r2_vac <- cor(x = bawue[3:38], y = bawue[39], use = "pairwise.complete.obs")^2 %>% 
  as.data.frame() %>%
  arrange(desc(Ungeimpfte_Bevölkerung))

bawue_r2_cases <- cor(x = bawue[3:38], y = bawue[40], use = "pairwise.complete.obs")^2 %>% 
  as.data.frame() %>%
  arrange(desc(Coronafälle_kumulativ_pro_100000_Einwohner))

fit3 <- lm(Ungeimpfte_Bevölkerung ~ Haushalte_mit_niedrigem_Einkommen + Durchschnittsalter + Beschäftigte_am_Wohnort_ohne_Berufsabschluss + AfD_2017 + Ausländeranteil, data=bawue)
summary(fit3) # show results

fit4 <- lm(Coronafälle_kumulativ_pro_100000_Einwohner ~ Haushalte_mit_niedrigem_Einkommen + Durchschnittsalter + Beschäftigte_am_Wohnort_ohne_Berufsabschluss + AfD_2017 + Ausländeranteil, data=bawue)
summary(fit4) # show results

