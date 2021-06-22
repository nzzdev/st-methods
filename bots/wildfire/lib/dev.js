//TODO move these configurations to individual github action configs
process.env.DATA_URL =
  'https://firms2.modaps.eosdis.nasa.gov/data/active_fire/c6/shapes/zips/MODIS_C6_South_America_24h.zip'
process.env.FILENAME = 'MODIS_C6_South_America_24h'
process.env.QID = 'e9046b127bd99afc9cd208b94d044b48'
process.env.Q_SERVER_BASE_URL = 'https://q-server.st-staging.nzz.ch/'
process.env.LD_USERNAME = 'kaspar.manz@nzz.ch'
process.env.CONFIDENCE = 80
process.env.MARKER_RADIUS = 10
process.env.USE_PROXY = true
process.env.NOTES = 'Diese Grafik wurde automatisiert aktualisiert.'

require('./index.js')
