const fetch = require("node-fetch");

const include = "procedure,restriction";

async function fetchCountriesInformation(language, originCountries) {
  const retVal = [];

  console.log("Fetching countriesInformation...");

  for (const originCountry of originCountries) {
    let countryInformation = await fetchCountryInformation(language, originCountry);
    if (retVal.length === 0) checkCountryInformationAttributes(countryInformation);
    retVal.push(countryInformation);
  }

  return retVal;
}

function checkCountryInformationAttributes(countryInformation) {
  if (!countryInformation.hasOwnProperty("data")) throw new Error("Missing property 'data'.");
  if (!countryInformation.hasOwnProperty("included")) throw new Error("Missing property 'included'.");

  if (countryInformation.data && countryInformation.data.length < 1) return;

  if (!countryInformation.data[0].hasOwnProperty("type")) throw new Error("Missing property 'data.type'.");
  if (!countryInformation.data[0].hasOwnProperty("attributes")) throw new Error("Missing property 'data.attributes'.");
  if (!countryInformation.data[0].attributes.hasOwnProperty("type")) throw new Error("Missing property 'data.attributes.type'.");
  if (!countryInformation.data[0].attributes.hasOwnProperty("isoAlpha3")) throw new Error("Missing property 'data.attributes.isoAlpha3'.");
  if (!countryInformation.data[0].attributes.hasOwnProperty("lastUpdatedAt")) throw new Error("Missing property 'data.attributes.lastUpdatedAt'.");
}

async function fetchCountryInformation(language, originCountry) {
  const params = `language=${language}&include=${include}&key=${process.env["SHERPA_API_KEY"]}&filter[country]=${originCountry}`;
  const url = `https://${process.env["SHERPA_API_URL"]}/v2/countries?${params}`;
  const options = {
    method: "GET",
    headers: {Accept: "*/*"}
  };

  let response = await fetch(url, options);

  if (response.status === 200) {
    return response.json();
  } else {
    console.log(`${originCountry} | Fetch response: ${response.status} - ${response.statusText}`);
  }

  return [];
}

async function fetchTripsInformation(language, originCountries, destinationCountries, destinationCountriesToExclude, travelDate) {
  const retVal = [];

  console.log("Fetching tripsInformation...");

  destinationCountries = destinationCountries.filter(item => destinationCountriesToExclude.indexOf(item) < 0);
  
  for (const originCountry of originCountries) {
    for (const destinationCountry of destinationCountries) {
      if (originCountry === destinationCountry) continue;
      let tripInformation = await fetchTripInformation(language, originCountry, destinationCountry, travelDate);
      if (retVal.length === 0) checkTripInformationAttributes(tripInformation);
      retVal.push(tripInformation);
    }
  }
  
  return retVal;
}

function checkTripInformationAttributes(tripInformation) {
  if (!tripInformation.hasOwnProperty("data")) throw new Error("Missing property 'data'.");
  if (!tripInformation.hasOwnProperty("included")) throw new Error("Missing property 'included'.");

  if (tripInformation.data && tripInformation.data.length < 1) return;

  if (!tripInformation.data.hasOwnProperty("type")) throw new Error("Missing property 'data.type'.");
  if (!tripInformation.data.hasOwnProperty("attributes")) throw new Error("Missing property 'data.attributes'.");
  if (!tripInformation.data.attributes.hasOwnProperty("category")) throw new Error("Missing property 'data.attributes.category'.");
  if (!tripInformation.data.attributes.hasOwnProperty("segments")) throw new Error("Missing property 'data.attributes.segments'.");

  if (tripInformation.data.attributes.segments && tripInformation.data.attributes.segments.length < 1) return;

  if (!tripInformation.data.attributes.segments[0].hasOwnProperty("segmentType")) throw new Error("Missing property 'data.attributes.segments.segmentType'.");
  if (!tripInformation.data.attributes.segments[0].hasOwnProperty("origin")) throw new Error("Missing property 'data.attributes.segments.origin'.");
  if (!tripInformation.data.attributes.segments[0].origin.hasOwnProperty("countryCode")) throw new Error("Missing property 'data.attributes.segments.origin.countryCode'.");
  if (!tripInformation.data.attributes.segments[0].hasOwnProperty("destination")) throw new Error("Missing property 'data.attributes.segments.destination'.");
  if (!tripInformation.data.attributes.segments[0].destination.hasOwnProperty("countryCode")) throw new Error("Missing property 'data.attributes.segments.destination.countryCode'.");
  if (!tripInformation.data.attributes.segments[0].hasOwnProperty("entryRestrictions")) throw new Error("Missing property 'data.attributes.segments.entryRestrictions'.");
  if (!tripInformation.data.attributes.segments[0].hasOwnProperty("travelRestrictions")) throw new Error("Missing property 'data.attributes.segments.travelRestrictions'.");
  if (!tripInformation.data.attributes.segments[0].hasOwnProperty("documents")) throw new Error("Missing property 'data.attributes.segments.documents'.");
  if (!tripInformation.data.attributes.segments[0].hasOwnProperty("exitRestrictions")) throw new Error("Missing property 'data.attributes.segments.exitRestrictions'.");
}

async function fetchTripInformation(language, originCountry, destinationCountry, travelDate) {
  const params = `language=${language}&include=${include}&key=${process.env["SHERPA_API_KEY"]}`;
  const url = `https://${process.env["SHERPA_API_URL"]}/v2/trips?${params}`;
  const options = {
    method: "POST",
    headers: {Accept: "*/*", "Content-Type": "application/json"},
    body: JSON.stringify({
      data: {
        attributes: {
          travellers: [
            {
              nationality: originCountry
            }
          ],
          segments: [
            {
              origin: {countryCode: originCountry},
              destination: {countryCode: destinationCountry},
              segmentType: "OUTBOUND",
              departureDate: travelDate,
              departureTime: "00:00",
              arrivalDate: travelDate,
              arrivalTime: "00:00"
            }
          ],
          category: "ONE_WAY_TRIP"
        },
        type: "TRIP"
      }
    })
  };

  let response = await fetch(url, options);

  if (response.status === 200) {
    return response.json();
  } else {
    console.log(`${originCountry}-${destinationCountry} | Fetch response: ${response.status} - ${response.statusText}`);
  }

  return [];
}

exports.fetchCountriesInformation = fetchCountriesInformation
exports.fetchTripsInformation = fetchTripsInformation
