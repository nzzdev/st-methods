function setCountriesInformation(countriesInformation) {
  const retVal = [];

  for (const countryInformation of countriesInformation) {
    let newCountryInformation = {};

    if (!countryInformation.data) continue;
    if (countryInformation.data.length < 1) continue;
    if (countryInformation.data[0].type.toUpperCase() !== "COUNTRY") throw new Error("Invalid data type.");
    if (countryInformation.data[0].attributes.type.toUpperCase() !== "COUNTRY") throw new Error("Invalid attributes type.");  

    newCountryInformation.country = countryInformation.data[0].attributes.isoAlpha3;
    newCountryInformation.lastUpdatedAt = countryInformation.data[0].attributes.lastUpdatedAt;

    let travelRestrictions = [];

    travelRestrictions = setIncludedInformations(countryInformation.included, true);

    newCountryInformation.ppe = filterItemsByTypeAndCategory(travelRestrictions, "PROCEDURE", "PPE");
    newCountryInformation.quarantine = filterItemsByTypeAndCategory(travelRestrictions, "PROCEDURE", "QUARANTINE");
    newCountryInformation.covidTest = filterItemsByTypeAndCategory(travelRestrictions, "PROCEDURE", "COVID_19_TEST");
    newCountryInformation.healthMeasures = filterItemsByTypeAndCategory(travelRestrictions, "PROCEDURE", "HEALTH_MEASURES");
    newCountryInformation.documents = filterItemsByTypeAndCategory(travelRestrictions, "PROCEDURE", "DOC_REQUIRED");
    // newCountryInformation.entryRestrictions = filterItemsByTypeAndCategory(travelRestrictions, "RESTRICTION", "NO_ENTRY");

    retVal.push(newCountryInformation);
  }

  return retVal;
}

function setTripsInformations(tripsInformation) {
  const retVal = [];

  for (const tripInformation of tripsInformation) {
    let newTripInformation = {};

    if (!tripInformation.data) continue;
    if (tripInformation.data.type.toUpperCase() !== "TRIP") throw new Error("Invalid data type.");
    if (tripInformation.data.attributes.category.toUpperCase() !== "ONE_WAY_TRIP") throw new Error("Invalid attributes category.");

    const outbound = tripInformation.data.attributes.segments.find(segment => segment.segmentType.toUpperCase() === "OUTBOUND");

    if (!outbound) throw new Error("No outbound data.");

    newTripInformation.category = tripInformation.data.attributes.category;
    newTripInformation.origin = outbound.origin.countryCode;
    newTripInformation.destination = outbound.destination.countryCode;

    let included = setIncludedInformations(tripInformation.included, false);
    let travelRestrictions = [];

    travelRestrictions.push(...getIncludedInformations(outbound.entryRestrictions, included));
    travelRestrictions.push(...getIncludedInformations(outbound.travelRestrictions, included));
    travelRestrictions.push(...getIncludedInformations(outbound.documents, included));
    travelRestrictions.push(...getIncludedInformations(outbound.exitRestrictions, included));

    newTripInformation.ppe = filterItemsByTypeAndCategory(travelRestrictions, "PROCEDURE", "PPE");
    newTripInformation.quarantine = filterItemsByTypeAndCategory(travelRestrictions, "PROCEDURE", "QUARANTINE");
    newTripInformation.covidTest = filterItemsByTypeAndCategory(travelRestrictions, "PROCEDURE", "COVID_19_TEST");
    newTripInformation.healthMeasures = filterItemsByTypeAndCategory(travelRestrictions, "PROCEDURE", "HEALTH_MEASURES");
    newTripInformation.documents = filterItemsByTypeAndCategory(travelRestrictions, "PROCEDURE", "DOC_REQUIRED");
    newTripInformation.entryRestrictions = filterItemsByTypeAndCategory(travelRestrictions, "RESTRICTION", "NO_ENTRY");

    newTripInformation.categoriesStatus = {
      ppe: {
        fullyVaccinated: getCategoryStatus(newTripInformation.ppe, true),
        notVaccinated: getCategoryStatus(newTripInformation.ppe, false)
      },
      quarantine: {
        fullyVaccinated: getCategoryStatus(newTripInformation.quarantine, true),
        notVaccinated: getCategoryStatus(newTripInformation.quarantine, false)
      },
      covidTest: {
        fullyVaccinated: getCategoryStatus(newTripInformation.covidTest, true),
        notVaccinated: getCategoryStatus(newTripInformation.covidTest, false)
      },
      healthMeasures: {
        fullyVaccinated: getCategoryStatus(newTripInformation.healthMeasures, true),
        notVaccinated: getCategoryStatus(newTripInformation.healthMeasures, false)
      },
      documents: {
        fullyVaccinated: getCategoryStatus(newTripInformation.documents, true),
        notVaccinated: getCategoryStatus(newTripInformation.documents, false)
      }
    };

    retVal.push(newTripInformation);
  }

  return retVal;
}

function setIncludedInformations(includedInformations, includeIncludedProperty) {
  const retVal = [];
  
  for (const includedItem of includedInformations) {
    let newIncludedItem = {};

    // We don't need transit information
    if (includedItem.attributes.category === "TRANSIT" || includedItem.attributes.subCategory === "TRANSIT") continue;
    if (includedItem.attributes.travelPurpose && includedItem.attributes.travelPurpose.length === 1 && includedItem.attributes.travelPurpose[0] === "TRANSIT") continue;

    newIncludedItem.id = includedItem.id;
    newIncludedItem.type = includedItem.type;
    newIncludedItem.category = includedItem.attributes.category;
    newIncludedItem.country = includedItem.attributes.country;
    newIncludedItem.description = includedItem.attributes.description;
    // newIncludedItem.directionality = includedItem.attributes.directionality;
    newIncludedItem.documentType = includedItem.attributes.documentType;
    newIncludedItem.documentLinks = includedItem.attributes.documentLinks;
    newIncludedItem.lastUpdatedAt = includedItem.attributes.lastUpdatedAt;
    newIncludedItem.more = includedItem.attributes.more;
    newIncludedItem.severity = includedItem.attributes.severity;
    newIncludedItem.sourceTitle = includedItem.attributes.source.title;
    newIncludedItem.sourceUrl = includedItem.attributes.source.url;
    // newIncludedItem.stillCurrentAt = includedItem.attributes.stillCurrentAt;
    // newIncludedItem.subCategory = includedItem.attributes.subCategory;
    newIncludedItem.tags = includedItem.attributes.tags;
    newIncludedItem.title = includedItem.attributes.title;
    newIncludedItem.enforcement = includedItem.attributes.enforcement;

    // We don't need this property when using the Trips endpoint
    if (includeIncludedProperty && includedItem.attributes.included) {
      newIncludedItem.included = includedItem.attributes.included.map(item => item.isoAlpha3);
    }
    
    retVal.push(newIncludedItem);
  }

  return retVal;
}

function getIncludedInformations(items, includedInformations) {
  if (!items) return [];
  return items.flatMap(item => {
    let included = findIncludedById(item.id, includedInformations);
    return included ? included : [];
  });
}

function filterItemsByTypeAndCategory(items, type, category) {
  if (!items) return [];
  if (type === "RESTRICTION") {
    switch (category) {
      case "NO_ENTRY":
        return items.filter(item =>
          item.type === "RESTRICTION" &&
          ["NO_ENTRY"].indexOf(item.category) > -1 &&
          item.severity >= 5
        );
      default:
        return items.filter(item =>
          item.type === "RESTRICTION"
        );
    }
  } else if (type === "PROCEDURE") {
    switch (category) {
      case "QUARANTINE":
        return items.filter(item =>
          item.type === "PROCEDURE" &&
          ["QUARANTINE", "NO_QUARANTINE"].indexOf(item.category) > -1
        );
      case "COVID_19_TEST":
        return items.filter(item =>
          item.type === "PROCEDURE" && (
            ["COVID_19_TEST", "NO_COVID_TEST"].indexOf(item.category) > -1 || (
              item.category === "DOC_REQUIRED" &&
              item.documentType &&
              item.documentType.indexOf("COVID_TEST_RESULT") > -1
            )
          )
        );
      case "HEALTH_MEASURES":
        return items.filter(item =>
          item.type === "PROCEDURE" &&
          ["HEALTH_MEASURES", "HEALTH_ASSESSMENT", "SANITIZATION"].indexOf(item.category) > -1
        );
      case "PPE":
        return items.filter(item =>
          item.type === "PROCEDURE" &&
          ["PPE"].indexOf(item.category) > -1
        );
      case "DOC_REQUIRED":
        return items.filter(item =>
          item.type === "PROCEDURE" &&
          ["DOC_REQUIRED", "RE_ENTRY_PERMIT", "DEPOSIT_REQUIRED", "HEALTH_INSURANCE", "TRAVEL_INSURANCE"].indexOf(item.category) > -1 &&
          item.documentType &&
          item.documentType.indexOf("COVID_TEST_RESULT") === -1 // already added in category COVID_19_TEST
        );
      default:
        return items.filter(item =>
          item.type === "PROCEDURE"
        );
    }
  } else {
    return [];
  }
}
// Function also used here: https://github.com/nzzdev/Q-custom-code-projects/blob/e1157859121356eaaae17985a67090605360bfaa/2112-travel-guide/src/helpers/helpers.js#L141
function getCategoryStatus(procedures, vaccinated) {
  if (procedures.length === 0) return null; // undefined not allowed in json

  if (hasProcedures(procedures, "MANDATORY", vaccinated)) {
    return "MANDATORY";
  }
  if (hasProcedures(procedures, "MAY_BE_REQUIRED", vaccinated)) {
    return "MAY_BE_REQUIRED";
  }
  if (hasProcedures(procedures, "RECOMMENDED", vaccinated)) {
    return "RECOMMENDED";
  }
  if (hasProcedures(procedures, "OPTIONAL", vaccinated)) {
    return "OPTIONAL";
  }
  if (hasProcedures(procedures, "NOT_REQUIRED", vaccinated)) {
    return "NOT_REQUIRED";
  }

  return null;
}
// Function also used here: https://github.com/nzzdev/Q-custom-code-projects/blob/e1157859121356eaaae17985a67090605360bfaa/2112-travel-guide/src/helpers/helpers.js#L163
function hasProcedures(procedures, enforcement, vaccinated) {
  let proceduresByEnforcement = procedures.filter(travelRestriction => travelRestriction.enforcement === enforcement);
  
  let countVaccinatedTags = proceduresByEnforcement.filter(travelRestriction => travelRestriction.tags && travelRestriction.tags.indexOf("fully_vaccinated") > -1).length;
  let countNotVaccinatedTags = proceduresByEnforcement.filter(travelRestriction => travelRestriction.tags && travelRestriction.tags.indexOf("not_vaccinated") > -1).length;
  let countRemainingProcedures = proceduresByEnforcement.length - countVaccinatedTags - countNotVaccinatedTags;

  if (countRemainingProcedures > 0) return true;

  if (vaccinated) {
    if (countVaccinatedTags > 0) return true;
  } else {
    if (countNotVaccinatedTags > 0) return true;
  }

  return false;
}

function findIncludedById(id, includedInformations) {
  if (!includedInformations) return undefined;
  return includedInformations.find(item => item.id === id);
}

exports.setCountriesInformation = setCountriesInformation
exports.setTripsInformations = setTripsInformations
