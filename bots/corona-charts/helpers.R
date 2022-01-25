library(jsonlite)

# Q helper function
update_chart <- function(id, title = "", subtitle = "", notes = "", data = list(), asset.groups = list(), files = list()) {
  # read qConfig file
  qConfig <- fromJSON("./q.config.json", simplifyDataFrame = FALSE)

  # update chart properties
  index = 0
  for (item in qConfig$items) {
    index <- index + 1
    for (environment in item$environments) {
      if (environment$id == id) {
  
        if (title != "") {
          qConfig$items[[index]]$item$title <- title
        }
        if (subtitle != "") {
          qConfig$items[[index]]$item$subtitle <- subtitle
        }
        if (notes != "") {
          qConfig$items[[index]]$item$notes <- notes
        }
        
        if (length(data) > 0) {
          print(names(item$item))
          if("table" %in% names(item$item$data))
          {
            qConfig$items[[index]]$item$data$table <- I(rbind(names(data), as.matrix(sapply(data, as.character))))
          }
          else
          {
            # as.matrix adds extra spaces when converting numbers to strings sapply(data, as.character)
            # trims extra characters. See also https://stackoverflow.com/questions/15618527/why-does-as-matrix-add-extra-spaces-when-converting-numeric-to-character
            qConfig$items[[index]]$item$data <- I(rbind(names(data), as.matrix(sapply(data, as.character))))
          }
        }
        
        if(length(asset.groups) > 0) {
          gr <- list()
          for(g in asset.groups)
          {
            gr <- append(gr, list(
              name = g$name,
              assets=list()
            ))
            for(file in g$files)
            {
              print(file)
              gr$assets = append(gr$assets, list(list(path=file)))
            }
          }
          qConfig$items[[index]]$item$assetGroups <- list(gr)
        }

        if(length(files) > 0) {
          qConfig$items[[index]]$item$files <- files
        }

        print(paste0("Successfully updated item with id ", id))
      }
    }
  }

  # write qConfig file
  qConfig <- toJSON(qConfig, pretty = TRUE, auto_unbox=TRUE)
  write(qConfig, "./q.config.json")
}