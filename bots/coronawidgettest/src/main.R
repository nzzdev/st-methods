#### TEST #### 

#prep
rm(list=ls(all=TRUE)) # Alles bisherige im Arbeitssprecher loeschen
source("./helpers.R")


# Struktur:
#[{
#  "name": "jsonFiles",
#  "files": ["./export/dashboard.json"]
#}]

assets <- list(
  list(
    name = "jsonFiles",
    files = list("./data/dashboard.json")
  )
)


#q-cli update
update_chart(id = "e9046b127bd99afc9cd208b94d74a18f",
             asset.groups = assets)

