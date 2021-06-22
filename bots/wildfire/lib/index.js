const path = require("path");
const turf = require("@turf/turf");
const helpers = require(path.join(__dirname, "helpers.js"));

const itemUrl = `${process.env.Q_SERVER_BASE_URL}item`;

/**
 * Prepare the GeoJSON data for display within Q.
 *
 * @param {GeoJSON.featureCollection} geojsons
 */
function getGeojsonsWithAttributes(geojsons, bbox) {
  // filter by confidence
  let filteredGeoJsons = geojsons.filter((geojson) => {
    return geojson.properties.CONFIDENCE >= process.env.CONFIDENCE;
  });

  // filter only visible points
  if (bbox) {
    const crop = turf.bboxPolygon(bbox);
    filteredGeoJsons = turf.pointsWithinPolygon(
      turf.featureCollection(filteredGeoJsons),
      crop
    );
  }

  // transform points to circles
  const geojsonsWithAttributes = filteredGeoJsons.features.map((geojson) => {
    const circle = turf.circle(
      geojson.geometry.coordinates,
      process.env.MARKER_RADIUS,
      {
        steps: 10,
        units: "kilometers",
        properties: {
          fill: "#d64b47",
          "fill-opacity": 0.75,
          useForInitialView: true,
        },
      }
    );
    return circle;
  });
  return turf.dissolve(turf.featureCollection(geojsonsWithAttributes));
}

/**
 * Retrieves the Q Item
 */
async function getQItem() {
  const bearer = await helpers.getBearerToken();
  const item = await helpers.getItem(itemUrl, bearer);
  return item;
}

async function updateQItem(geojsons, item) {
  // get single features (e.g. manually added points of interest)
  const otherFeatures = item.geojsonList.filter(
    (feat) => feat.type === "Feature"
  );

  // create a new item from the old data
  // add the new geojsonList using the single features and the new data
  const newItem = {
    ...item,
    geojsonList: [...otherFeatures, geojsons],
    notes: helpers.formatNote(process.env.NOTES),
  };
  const bearer = await helpers.getBearerToken();
  const response = await helpers.saveItem(itemUrl, bearer, newItem);
  if (response && response._rev) {
    console.log(`Q-Item ${process.env.QID} successfully updated.`);
  } else {
    throw new Error(
      `An error occured while updateding the Q-Item ${process.env.QID}. Make sure that you don't have the Q-Item open in your browser.`
    );
  }
}

/**
 * Main function, called when executing this file.
 */
async function main() {
  try {
    // first, get the original item
    const qItem = await getQItem();

    // get GeoJSON data
    const geojsons = await helpers.getGeojsons();

    const geojsonsWithAttributes = getGeojsonsWithAttributes(
      geojsons,
      qItem.options.dimension.bbox
    );
    await updateQItem(geojsonsWithAttributes, qItem);
  } catch (error) {
    console.error(error.message);
    process.exit(1)
  }
}

main();
