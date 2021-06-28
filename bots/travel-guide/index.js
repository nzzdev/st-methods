const {originCountries, destinationCountriesToExclude, destinationCountries} = require("./helpers/countries")
const {fetchCountriesInformation, fetchTripsInformation} = require("./helpers/fetchInformation")
const {setCountriesInformation, setTripsInformations} = require("./helpers/setInformation")
const {writeFile} = require("./helpers/exportJSON")
const {updateLastUpdatedAt} = require("./helpers/updateConfig")

async function main() {
  const language = "de-DE";
  const travelDate = (new Date()).toISOString().substring(0, 10);

  let countriesInformation = [];
  let tripsInformation = [];

  console.log("------------------------------$");
  
  //------------------------------$
  // 01 Countries Information
  //------------------------------$
  try {
    countriesInformation = await fetchCountriesInformation(language, originCountries);
    countriesInformation = setCountriesInformation(countriesInformation, originCountries);
    updateLastUpdatedAt();
  } catch (error) {
    console.error(error);
  } finally {
    console.log(`${countriesInformation.length}/${originCountries.length} countriesInformation downloaded.`)
    writeFile("countriesInformation", countriesInformation);
    console.log("------------------------------$");
  }

  //------------------------------$
  // 02 Trips Information
  //------------------------------$
  try {
    tripsInformation = await fetchTripsInformation(language, originCountries, destinationCountries, destinationCountriesToExclude, travelDate);
    tripsInformation = setTripsInformations(tripsInformation);
    updateLastUpdatedAt();
  } catch (error) {
    console.error(error);
  } finally {
    console.log(`${tripsInformation.length}/${originCountries.length * destinationCountries.length - destinationCountriesToExclude.length - 2} tripsInformation downloaded.`)
    writeFile("tripsInformation", tripsInformation);
    console.log("------------------------------$");
  }
}

main();
