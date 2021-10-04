####################
# SECO indicator
####################

pg <- read_html("https://www.seco.admin.ch/seco/de/home/wirtschaftslage---wirtschaftspolitik/Wirtschaftslage/indikatoren/wwa.html")

# get all the Excel (xls) links on that page:

html_nodes(pg, xpath=".//a[contains(@href, '.xls')]") %>% 
  html_attr("href") %>% 
  sprintf("https://www.seco.admin.ch%s", .) -> excel_links

excel_links[1]

url <- excel_links[1]
GET(url, write_disk(tf <- tempfile(fileext = ".xls")))

seco <- readWorksheetFromFile (tf, 3, startRow = 4, header = T)

seco$Col3 <- ifelse(seco$Col2 < 10, paste0('0', as.character(seco$Col2)), as.character(seco$Col2))
seco$KW <- paste0(as.character(seco$Col1), '-W', seco$Col3)

q <- seco %>% dplyr::select(KW, WEA) %>% drop_na()

#q-cli update
update_chart(id = "c366afc02f262094669128cd054faf78", 
             data = q)




#######################################################################
# Monitoring Consumption Switzerland -- ALL DATA 
#######################################################################


download <- getURL("https://drive.switch.ch/index.php/s/4JmvjqxKnlmrSVn/download?path=%2F&files=MCS_Overview_Data.csv")
transactions <- read.csv (text = download)


transactions <- subset(transactions, TRANSACTIONS != 'ATM_DEPOSIT')

transactions$Date <- as.Date(transactions$DATE, "%Y-%m-%d")

transactions$week <- strftime(transactions$Date, format = "%V")
transactions$year <- strftime(transactions$Date, format = "%Y")
transactions$year[transactions$week == '53'] <- '2020'

transactions$week_year <- paste0(transactions$year, '-', transactions$week)


transactions <- transactions %>% 
  group_by(week_year) %>% 
  summarise(Total = sum(AMOUNTCHF, na.rm = TRUE))

transactions$week <- substr(transactions$week_year, 6, 7)
transactions$year <- substr(transactions$week_year, 1, 4)

transactions$Datum <- as.Date(paste0(transactions$week_year,'-1'), '%Y-%W-%u') - 7

start = '01'
end = max(subset(transactions,year == 2021)$week)

transactions_2019 = subset(transactions, year == 2019 & week>=start)
transactions_2020 = subset(transactions, year == 2020 & week>=start)
transactions_2021 = subset(transactions, year == 2021 & week>=start)

transactions_2019 <- transactions_2019[order(transactions_2020$Datum),]
transactions_2020 <- transactions_2020[order(transactions_2020$Datum),]
transactions_2021 <- transactions_2021[order(transactions_2021$Datum),]

transactions <- merge(transactions_2020, transactions_2021, by = 'week', all.x = TRUE) %>%
  dplyr::select(week, Total.x, Total.y) %>%
  dplyr::rename(`2021` = Total.y,
                `2020` = Total.x) #%>%
#merge(transactions_2019, by = 'week', all.x = TRUE) %>%
#select(week,`2021`, `2020`, Total) %>%
#rename(`2019` = Total)

transactions <- transactions %>% filter(week != "53")

transactions$week <- paste0('2021-W', transactions$week) 

#q-cli update
update_chart(id = "909e73515b8785336ef65c05d0fa36c7", 
             data = transactions)



#######################################################################
# Monitoring Consumption Switzerland -- Merchant categories
#######################################################################

download <- getURL("https://drive.switch.ch/index.php/s/PSg7Y8Za5LmQ5dn/download?path=%2F2_ACQUIRING%20DATA&files=ACQ_NOGA_Channel.csv") 

merchanttype <- read.csv (text = download) 

merchanttype <- merchanttype %>% 
  group_by(Date, Merchant.category) %>% 
  summarise(All = sum(Amount.CHF))

merchanttype$Date <- as.Date(merchanttype$Date)

merchanttype$week <- strftime(merchanttype$Date, format = "%V")
merchanttype$year <- strftime(merchanttype$Date, format = "%Y")
merchanttype$year[merchanttype$week == '53'] <- '2020'

merchanttype$week_year <- paste0(merchanttype$year, '-', merchanttype$week)

merchanttype <- merchanttype %>% 
  group_by(week_year, Merchant.category) %>% 
  summarise(Total = sum(All, na.rm = TRUE))

merchanttype$week <- substr(merchanttype$week_year, 6, 7)
merchanttype$year <- substr(merchanttype$week_year, 1, 4)

merchanttype$Datum <- as.Date(paste0(merchanttype$week_year,'-1'), '%Y-%W-%u') 

start = '01'
end = max(subset(merchanttype,year == 2021)$week)

merchanttype_2019 = subset(merchanttype, year == 2019 & week>=start)
merchanttype_2020 = subset(merchanttype, year == 2020 & week>=start)
merchanttype_2021 = subset(merchanttype, year == 2021 & week>=start)

merchanttype_2019 <- merchanttype_2019[order(merchanttype_2020$Datum),]
merchanttype_2020 <- merchanttype_2020[order(merchanttype_2020$Datum),]
merchanttype_2021 <- merchanttype_2021[order(merchanttype_2021$Datum),]

merchanttype <- merge(merchanttype_2020, merchanttype_2021, by = c('week', 'Merchant.category'), all.x = TRUE) %>%
  dplyr::select(week, Merchant.category, Total.y, Total.x) %>%
  dplyr::rename(`2021` = Total.y,
                `2020` = Total.x) %>%
  merge(merchanttype_2019, by = c('week', 'Merchant.category'), all.x = TRUE) %>%
  dplyr::select(week, Merchant.category, Total, `2020`, `2021`, Total) %>%
  dplyr::rename(`2019` = Total)

merchanttype <- merchanttype %>% filter(week != "53")
merchanttype$week <- paste0('2021-W', merchanttype$week)

q <- subset(merchanttype, Merchant.category == 'Retail: Food, beverage, tobacco', select = c('week','2019', '2020', '2021'))
update_chart(id = "fa0c8fc6907b186bd970f740254d4c57", 
             data = q)

q <- subset(merchanttype, Merchant.category == 'Accommodation', select = c('week','2019', '2020', '2021'))
update_chart(id = "fa0c8fc6907b186bd970f7402560f664", 
             data = q)

q <- subset(merchanttype, Merchant.category == 'Retail: Other goods', select = c('week','2019', '2020', '2021'))
update_chart(id = "fa0c8fc6907b186bd970f740255f9af7", 
             data = q)

q <- subset(merchanttype, Merchant.category == 'Food and beverage services', select = c('week','2019', '2020', '2021'))
update_chart(id = "47b8b7f460b37c786692405da9c795fd", 
             data = q)


#######################
### Auslastung SBB
#######################

pg <- read_html("https://news.sbb.ch/medien/artikel/101333/coronavirus-hintergrundinformationen-fuer-medienschaffende")

# get all the Excel (xlsx) links on that page:

html_nodes(pg, xpath=".//a[contains(@href, '.xlsx')]") %>% 
  html_attr("href") %>% 
  sprintf("https://news.sbb.ch%s", .) -> excel_links

excel_links[1]

url <- excel_links[1]
GET(url, write_disk(tf <- tempfile(fileext = ".xlsx")))
sbb <- read_excel(tf, sheet=1, skip = 2, col_names = FALSE) 
sbb[1] <- NULL

names(sbb)[1] <- "type"
names(sbb)[2:54]<- paste0("2020-W", 2:ncol(sbb)-1)
names(sbb)[55:ncol(sbb)]<- paste0("2021-W", 55:ncol(sbb)-53) 


sbb <- sbb  %>%
  filter(type == 'Regionalverkehr'| type == 'Fernverkehr') %>%
  gather(key = "KW", value = "value", 2:ncol(sbb)) %>%
  mutate(value = value*100) %>%
  ## necessary to preserve ordering of KW
  mutate(KW = factor(KW, levels=unique(KW))) %>% 
  spread("type", "value")

update_chart(id = "3819150d9ecde64169327d9dd0c610f7", 
             data = q)









