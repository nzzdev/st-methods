library(jsonlite)

# Q helper function
update_chart <- function(id, title = "", subtitle = "", notes = "", data = list()) {
  # read qConfig file
  qConfig <- fromJSON("./q.config.json", simplifyDataFrame = TRUE)

  # update chart properties
  for (item in qConfig$items) {
    index <- 0
    for (environment in qConfig$items$environments) {
      index <- index + 1
      if (environment$id == id) {
        if (title != "") {
          qConfig$items$item$title[[index]] <- title
        }
        if (subtitle != "") {
          qConfig$items$item$subtitle[[index]] <- subtitle
        }
        if (notes != "") {
          qConfig$items$item$notes[[index]] <- notes
        }
        if (length(data) > 0) {
          # as.matrix adds extra spaces when converting numbers to strings sapply(data, as.character)
          # trims extra characters. See also https://stackoverflow.com/questions/15618527/why-does-as-matrix-add-extra-spaces-when-converting-numeric-to-character
          qConfig$items$item$data[[index]] <- rbind(names(data), as.matrix(sapply(data, as.character)))
        }
        print(paste0("Successfully updated item with id ", id))
      }
    }
  }

  # write qConfig file
  qConfig <- toJSON(qConfig, pretty = TRUE)
  write(qConfig, "./q.config.json")
}