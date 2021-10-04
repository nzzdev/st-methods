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


