const fetch = require("node-fetch");

const include = "procedure,restriction";

async function fetchCountriesInformation(language, originCountries) {
  const retVal = [];

  console.log("Fetching countriesInformation...");

  for (const originCountry of originCountries) {
    let countryInformation = await fetchCountryInformation(language, originCountry);
    retVal.push(countryInformation);
  }

  return retVal;
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
      retVal.push(tripInformation);
    }
  }
  
  return retVal;
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
