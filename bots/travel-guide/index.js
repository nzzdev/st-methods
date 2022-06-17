const {originCountries, destinationCountriesToExclude, destinationCountries} = require("./helpers/countries")
const {fetchCountriesInformation, fetchTripsInformation} = require("./helpers/fetchInformation")
const {setCountriesInformation, setTripsInformations} = require("./helpers/setInformation")
const {writeFile} = require("./helpers/exportJSON")
const {updateFiles, updateLastUpdatedAt} = require("./helpers/updateConfig")

async function main() {
  const language = "de-DE";
  const travelDate = (new Date()).toISOString().substring(0, 10);

  let countriesInformation = [];
  let tripsInformation = [];

  console.log("------------------------------$");
  
  //------------------------------$
  // 01 Countries Information
  //------------------------------$
  if (process.exitCode === 1) return;
  try {
    countriesInformation = await fetchCountriesInformation(language, originCountries);
    countriesInformation = setCountriesInformation(countriesInformation, originCountries);

    console.log(`${countriesInformation.length}/${originCountries.length} countriesInformation downloaded.`)

    writeFile("countriesInformation", countriesInformation);
    updateLastUpdatedAt();
  } catch (error) {
    console.error(error);
    process.exitCode = 1;
  } finally {
    console.log("------------------------------$");
  }

  //------------------------------$
  // 02 Trips Information
  //------------------------------$
  if (process.exitCode === 1) return;
  try {
    tripsInformation = await fetchTripsInformation(language, originCountries, destinationCountries, destinationCountriesToExclude, travelDate);
    tripsInformation = setTripsInformations(tripsInformation);

    console.log(`${tripsInformation.length}/${originCountries.length * (destinationCountries.length - destinationCountriesToExclude.length) - 2} tripsInformation downloaded.`)

    writeFile("tripsInformation", tripsInformation);
    updateLastUpdatedAt();
  } catch (error) {
    console.error(error);
    process.exitCode = 1;
  } finally {
    console.log("------------------------------$");
  }

  if (process.exitCode === 1) return;
  try {
    updateFiles();
  } catch (error) {
    console.error(error);
    process.exitCode = 1;
  }
}

main();
