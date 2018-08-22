# NZZ Storytelling, script for the NZZ hurricane maps and the following article: 
# https://www.nzz.ch/international/warum-die-gaengigste-hurrikan-visualisierung-problematisch-ist-und-was-die-nzz-an-ihrer-stelle-macht-ld.1394033
# questions and comments: marie-jose.kolly@nzz.ch

# This script leads, step by step, to a hurricane-map based on geojson files to be used with the NZZ Storytelling Toolbox Q as well as to .svg- and .pdf-versions that can be adapted for graphics to be printed on paper. 



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### MISE EN PLACE ###

# this checks if the required packages are installed and - if not - installs them 
packages<-c("rgdal",
            "geojsonio",
            "rmapshaper", # to simplify geojson
            "geojson",
            "ggmap",
            "ggplot2",
            "svglite",
            "dplyr",
            "extrafont")
new <-packages[!(packages %in% installed.packages()[, "Package"])]
if (length(new)) 
  install.packages(new, dependencies = TRUE)
sapply(packages, require, character.only = TRUE)

# font_import() # import fonts for the print-infographic, have Univers installed before, only do once

# define projection
wgs84CRS<-CRS("+init=epsg:4326")

# define colors (sequential scale)
seqOpaque<-c("#d64b47","#db5e55","#e06f63","#e47f72","#e78f81","#ea9f90","#ecaea0","#eebeb0","#eecdc0","#eeddd0","#edece1")
seq<-paste0(seqOpaque, 99) #add some transparency
trackCol<-"#05032D"

# set the path to your data folder in an additional line
myDataFolder<-"yourpath/data"

# here's where you will find the latest data. https://www.nhc.noaa.gov/gis/ (or here: https://www.nhc.noaa.gov/gis/archive_wsp.php?year=2018).
# choose "Wind Speed Probabilities", pick the current year from the drop-down list 
# and get the most recent .kmz-file called *_wsp34knt120hr_5km.kmz (34knots = tropical storm force winds, this is what we decided for with Helga Rietz)

# unzip the file (e.g. by using commandline: $ unzip *_wsp34knt120hr_5km.kmz, or by changing the extension to .zip)

# read the unzipped .kml-file into R (adapt filename)
windspeed<-readOGR(paste0(myDataFolder,"2018082206_wsp34knt120hr_5km.kml"))

# go back to https://www.nhc.noaa.gov/gis/ (or here: https://www.nhc.noaa.gov/gis/archive_forecast_results.php?id=ep03&year=2018&name=Hurricane%20BUD) 
# choose "Advisory Forecast Track, Cone of Uncertainty,and Watches/Warnings", pick the current year from the drop-down list, then pick the hurricane you'd like to show
# and get the most recent (highest number) kmz-file containing the predicted track, called EP*2018_<number>adv_TRACK.kmz or al*2018_<number>adv_TRACK.kmz

# unzip the file (see above)

# read the unzipped .kml-file into R (adapt filename)
track<-readOGR(paste0(myDataFolder,"ep142018_016adv_TRACK.kml"), require_geomType="wkbLineString")
points<-readOGR(paste0(myDataFolder,"ep142018_016adv_TRACK.kml"), require_geomType="wkbPoint")

# once more, go back to https://www.nhc.noaa.gov/gis/ (or here: https://www.nhc.noaa.gov/gis/archive_besttrack.php?year=2018)
# choose "Preliminary best track", pick the current year from the drop-down list, then pick the hurricane you'd like to show
# and get the most recent (highest number) zip-file (NOT kmz-file) containing the past track, called al*.zip or ep*.zip (CAREFUL: we'd prefer .kmz, 
# here, for the sake of consistency; however, the .kmz-file contains only points, no line, which is difficult to read in Q)

# unzip the file

# read the unzipped shapefiles containing the line and the points into R (adapt name of the shapefile-folder and filenames)
pasttrack_pts<-readOGR(paste0(myDataFolder,"ep142018_best_track/EP142018_pts.shp"))
pasttrack_lin<-readOGR(paste0(myDataFolder,"ep142018_best_track/EP142018_lin.shp"))

# get overview (the spatial objects are not yet projected)
summary(windspeed)
summary(track)
summary(points)
summary(pasttrack_pts)
summary(pasttrack_lin)



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### PROCESS DATA ###

## windspeed: simplify shape so the file doesn't take too long to load in Q:
windspeed<-ms_simplify(windspeed, keep=.05) # this function from the library rmapshaper uses the Visvalingam simplification method

# round coordinates: 5 decimal places = 1 meter (4 places = 10 meters)
for (i in 1:length(windspeed@polygons)){ # 11 polygons = 11 probability buckets
  windspeed@polygons[[i]]@Polygons[[1]]@coords<-round(windspeed@polygons[[i]]@Polygons[[1]]@coords,5)
}
for(i in 1:(length(windspeed@polygons)-1)){ # one (90% = no hole) or two lines (hole in polygon)
  windspeed@polygons[[i]]@Polygons[[2]]@coords<-round(windspeed@polygons[[i]]@Polygons[[2]]@coords,5)
}
# ignore warning, if there is one

# add properties to geojson
windspeed$fill<-rev(seqOpaque)
windspeed$`fill-opacity`<-rep(.5, nrow(windspeed))
windspeed$stroke<-rev(seqOpaque)
windspeed$`stroke-opacity`<-rep(1, nrow(windspeed))
windspeed$`stroke-width`<-rep(.5, nrow(windspeed))
windspeed$Name<-gsub("%", "", windspeed$Name)
windspeed$label<-paste0(" ")

windspeed@data[which(windspeed@data[,1]==">90"),]$`fill-opacity`<-.75 # stronger opacity for >90%
windspeed@data[which(windspeed@data[,1]=="<5"),]$`label`<-paste0(windspeed$Name[1], "%") #  only keep label for >90% and <5%
windspeed@data[which(windspeed@data[,1]==">90"),]$`label`<-paste0(windspeed$Name[11], "%")

# reverse order, as we want 90% to appear first in the legend
windspeed<-windspeed[rev(order(as.numeric(row.names(windspeed)))),]

# get overview
windspeed@data


## predicted track:

# keep the 120-hour forecast track and get rid of the others
track<-track[which(grepl("120 Hour", track@data[,2])==T),]

# add label for legend
track$label<-"Verlauf (Prognose: gepunktet)" # for the day we get dashed legends in Q: track$label<-"Prognose des Verlaufs"

# add color and line type
track$stroke<-rep(trackCol, nrow(track))
track$`stroke-width`<-rep(1, nrow(track))
track$dashArray<-rep(2, nrow(track))

# get rid of columns Name and Description
track <- track[,-c(1:2)]

# get overview
track@data


## points:

# get rid of the 3rd dimension of coordinates
points@coords<-points@coords[, 1:2]

# extract label information
day<-strsplit(as.character(points$Description),"Valid at: ") %>%
  sapply(.,`[`,2) %>%
  strsplit(., ", 2018") %>%
  sapply(.,`[`,1) %>%
  strsplit(., "MDT | PDT | EDT ") %>%
  sapply(., `[`, 2) %>%
  strsplit(., " ") %>%
  sapply(., `[`, 2)

month<-strsplit(as.character(points$Description),"Valid at: ") %>%
  sapply(.,`[`,2) %>%
  strsplit(., ", 2018") %>%
  sapply(.,`[`,1) %>%
  strsplit(., "MDT | PDT | EDT ") %>%
  sapply(., `[`, 2) %>%
  strsplit(., " ") %>%
  sapply(., `[`, 1)

monthTranslator <- function(x) gsub("January", "Januar", x) %>%
  gsub("February", "Februar", .) %>%
  gsub("March", "März", .) %>%
  gsub("May", "Mai", .) %>%
  gsub("June", "Juni", .) %>%
  gsub("July", "Juli", .) %>%
  gsub("October", "Oktober", .) %>%
  gsub("December", "Dezember", .)

month <- monthTranslator(month)

points$label<-paste(day, month, sep=". ")

# add label type and label position
points$type<-rep("pointLightLabel", nrow(points)) #pointLightLabel (small) or pointHeavyLabel (larger) or pointOnly (no label, which is not what we want, here)
points$labelPosition<-c("bottom", rep("top",floor(nrow(points)-1)))

# if day starts with 0, delete that 0
for (i in 1:nrow(points)) ifelse(substr(points$label[i], 1,1)==0, points$label[i]<-substr(points$label[i], 2,nchar(points$label[i])), points$label[i]<-points$label[i])

# get rid of columns Name and Description
points <- points[,-c(1:2)]

# keep first and last point of forecast, toss the rest (additional points - out of this data - can be added by code or by hand, on a case-by-case base, by looking at points@data)
points<-points[c(1, nrow(points)),]

# get overview
points@data


## past track

# add label for legend
pasttrack_lin$label<-rep("Verlauf (Prognose: gepunktet)", nrow(pasttrack_lin)) #for the day we get dashed legends in Q: pasttrack_lin$label[1]<-"Bisheriger Verlauf"

# add color and line type
pasttrack_lin$stroke<-rep(trackCol, nrow(track))
pasttrack_lin$`stroke-width`<-rep(1, nrow(track))
pasttrack_lin$dashArray<-rep(0, nrow(pasttrack_lin))

# get rid of all columns but label, stroke, stroke-width, dashArray
pasttrack_lin <- pasttrack_lin[,c((ncol(pasttrack_lin)-3):(ncol(pasttrack_lin)))]

# get overview
pasttrack_lin@data


## past points

# extract label information
day<-as.character(pasttrack_pts$DAY)
month<-as.character(pasttrack_pts$MONTH)

monthNumberTranslator <- function(x) gsub("01", "Januar", x) %>%
  gsub("02", "Februar", .) %>%
  gsub("03", "März", .) %>%
  gsub("04", "April", .) %>%
  gsub("05", "Mai", .) %>%
  gsub("06", "Juni", .) %>%
  gsub("07", "Juli", .) %>%
  gsub("08", "August", .) %>%
  gsub("09", "September", .) %>%
  gsub("10", "Oktober", .) %>%
  gsub("11", "November", .) %>%
  gsub("12", "Dezember", .)

month <- monthNumberTranslator(month)

pasttrack_pts$label<-paste(day, month, sep=". ")

# if day starts with 0, delete that 0
for (i in 1:nrow(pasttrack_pts)) ifelse(substr(pasttrack_pts$label[i], 1,1)==0, pasttrack_pts$label[i]<-substr(pasttrack_pts$label[i], 2,nchar(pasttrack_pts$label[i])), pasttrack_pts$label[i]<-pasttrack_pts$label[i])

# add label type and label position
pasttrack_pts$type<-rep("pointLightLabel", nrow(pasttrack_pts)) #pointLightLabel (small) or pointHeavyLabel (larger) or pointOnly (no label, which is not what we want, here)
pasttrack_pts$labelPosition<-rep("bottom", nrow(pasttrack_pts))

# get rid of all columns but label, type, labelPositon
pasttrack_pts <- pasttrack_pts[,c((ncol(pasttrack_pts)-2):(ncol(pasttrack_pts)))]

# keep first point of past track, toss the rest (additional points - out of this data - can be added by code or by hand, on a case-by-case base, by looking at pasttrack_pts@data)
pasttrack_pts<-pasttrack_pts[1,]

# get overview
pasttrack_pts@data



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### VISUALIZE FOR YOUR OWN OVERVIEW ###
plot(windspeed[windspeed$Name=="<5",], col=seq[11], border="transparent")
plot(windspeed[windspeed$Name=="5-10",], col=seq[10], border="transparent", add=T)
plot(windspeed[windspeed$Name=="10-20",], col=seq[9], border="transparent", add=T)
plot(windspeed[windspeed$Name=="20-30",], col=seq[8], border="transparent", add=T)
plot(windspeed[windspeed$Name=="30-40",], col=seq[7], border="transparent", add=T)
plot(windspeed[windspeed$Name=="40-50",], col=seq[6], border="transparent", add=T)
plot(windspeed[windspeed$Name=="50-60",], col=seq[5], border="transparent", add=T)
plot(windspeed[windspeed$Name=="60-70",], col=seq[4], border="transparent", add=T)
plot(windspeed[windspeed$Name=="70-80",], col=seq[3], border="transparent", add=T)
plot(windspeed[windspeed$Name=="80-90",], col=seq[2], border="transparent", add=T)
plot(windspeed[windspeed$Name==">90",], col=seq[1], border="transparent", add=T)
plot(track, col=trackCol, lty=3, add=T)
plot(pasttrack_lin, col=trackCol, add=T)
plot(points, pch=20, col=trackCol, add=T)
text(points, label=points$label, cex=.8, pos=4)
plot(pasttrack_pts, pch=20, col=trackCol,add=T)
text(pasttrack_pts, label=pasttrack_pts$label, cex=.8, pos=4)



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### BIND DATASETS TOGETHER ###


## lines

# attribute projection to pasttrack_lin
pasttrack_lin<-spTransform(pasttrack_lin, proj4string(track))

# bind
allTracks<-rbind(track, pasttrack_lin)

# get overview
allTracks@data


## points

# attribute projection to pasttrack_pts
pasttrack_pts<-spTransform(pasttrack_pts, proj4string(points))

# bind
allPoints<-rbind(pasttrack_pts, points)

# add "useForInitialView":true to points
allPoints$useForInitialView<-rep(TRUE, nrow(allPoints))

# get overview
allPoints@data



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### WRITE DATA FOR VISUALISATION IN Q ###
setwd("/Users/marie-jose/Documents/a_NZZ/projects/a_2018/hurricanes/data")

filenameWindspeed<-paste0("hurricaneProb_", Sys.Date(), ".geojson")
filenameTracks<-paste0("hurricaneTracks_", Sys.Date(), ".geojson")
filenamePoints<-paste0("hurricanePoints_", Sys.Date(), ".geojson")

# write windspeed probabilities
writeOGR(windspeed, filenameWindspeed, layer="windspeed", driver="GeoJSON")

# write track
writeOGR(allTracks, filenameTracks, layer="track", driver="GeoJSON")

# write points
writeOGR(allPoints, filenamePoints, layer="points", driver="GeoJSON")



# make a copy -  "als Vorlage benutzen" - of the latest hurricane graphic in Q (NZZ Storytelling Toolbox). The content of the files written above should now be copy-pasted in a GeoJSON FeatureCollection each. 
# if there are several different polygon-groups of windspeed probabilities (i.e., several storms): drag the windspeed-file (hurricaneProb_*) to geojson.io and delete the ones that belong to other storm(s) than the one you want to show
# make sure to copy the tracks-file (hurricaneTracks_*) into the last FeatureCollection in Q so the lines appear as a first layer
# in the points-file (hurricanePoints_*), change 1 to true and 0 to false in the property "useForInitialView" (R encondes TRUE and FALSE as 1 and 0 when writing GeoJSON).
# possibly add a few points with geographical locations by hand
# possibly add a few points with additional dates + times by hand (or by code, see above :-))



#------------------------------------------------------------------------------------------------------------------------------------------------------------
### CREATE SVG TO BE USED FOR PRINT GRAPHICS ###
setwd("yourpath/graphics/")

# get map layer to plot "behind" the hurricane data
lat<-mean(coordinates(points)[,1])
lon<-mean(coordinates(points)[,2])
layer<-ggmap(get_googlemap(center=c(lat, lon), maptype = "terrain", scale=2, zoom=4), extent="normal", darken = c(0.2, "white"))

# plot
layer+
  geom_polygon(data=fortify(windspeed[windspeed$Name=="<5",]), aes(long, lat, group=group), fill=seq[11], colour=seqOpaque[11]) +
  geom_polygon(data=fortify(windspeed[windspeed$Name=="5-10",]), aes(long, lat, group=group), fill=seq[10], colour=seqOpaque[10]) +
  geom_polygon(data=fortify(windspeed[windspeed$Name=="10-20",]), aes(long, lat, group=group), fill=seq[9], colour=seqOpaque[9]) +
  geom_polygon(data=fortify(windspeed[windspeed$Name=="20-30",]), aes(long, lat, group=group), fill=seq[8], colour=seqOpaque[8]) +
  geom_polygon(data=fortify(windspeed[windspeed$Name=="30-40",]), aes(long, lat, group=group), fill=seq[7], colour=seqOpaque[7]) +
  geom_polygon(data=fortify(windspeed[windspeed$Name=="40-50",]), aes(long, lat, group=group), fill=seq[6], colour=seqOpaque[6]) +
  geom_polygon(data=fortify(windspeed[windspeed$Name=="50-60",]), aes(long, lat, group=group), fill=seq[5], colour=seqOpaque[5]) +
  geom_polygon(data=fortify(windspeed[windspeed$Name=="60-70",]), aes(long, lat, group=group), fill=seq[4], colour=seqOpaque[4]) +
  geom_polygon(data=fortify(windspeed[windspeed$Name=="70-80",]), aes(long, lat, group=group), fill=seq[3], colour=seqOpaque[3]) +
  geom_polygon(data=fortify(windspeed[windspeed$Name=="80-90",]), aes(long, lat, group=group), fill=seq[2], colour=seqOpaque[2]) +
  geom_polygon(data=fortify(windspeed[windspeed$Name==">90",]), aes(long, lat, group=group), fill=seq[1], colour=seqOpaque[1]) +
  geom_path(data=fortify(track), aes(long, lat, group=group), col=trackCol, lwd=.5, linetype="dotted") +
  geom_path(data=fortify(pasttrack_lin), aes(long, lat, group=group), col=trackCol, lwd=.5) +
  geom_point(data=as.data.frame(allPoints), aes(coordinates(allPoints)[,1], coordinates(allPoints)[,2]), col=trackCol) +
  geom_text(data=as.data.frame(allPoints), aes(coordinates(allPoints)[,1], coordinates(allPoints)[,2], label=allPoints$label), size=2.5, hjust=-.3, family="UniversLTStd-Light", color=trackCol) +
  coord_map(projection = "mercator") +
  theme(line = element_blank(),
        legend.title = element_blank(),
        plot.title = element_text(family="UniversLTStd-Light", color="#05032D", size=16, hjust=0.5), 
        panel.background = element_blank(),
        axis.title=element_blank(),
        axis.text=element_blank(),
        axis.ticks=element_blank(),
        legend.position="left",
        legend.text=element_text(family="UniversLTStd-Light", size=11, color="#6E6E7E"))

# save as pdf (grouping seems better than in .svg, and univers-font, too)
filename<-paste0("hurricane_", Sys.Date(), ".pdf")
ggsave(filename, width = 20, device=cairo_pdf)

# save as svg
filename<-paste0("hurricane_", Sys.Date(), ".svg")
ggsave(filename, width = 20)


