const path = require("path");
const promptly = require("promptly");
const fetch = require("node-fetch");
const shapefile = require("shapefile");
const fs = require("fs-extra");
const unzipper = require("unzipper");
const ProxyAgent = require("simple-proxy-agent");
Intl = require('intl')

async function getBearerToken() {
  if (!process.env.Q_SERVER_AUTH) {
    let password;

    // take the password from the environment variables …
    if (process.env.PASSWORD && process.env.PASSWORD !== "") {
      password = process.env.PASSWORD;
    } else {
      // otherwise prompt for it
      password = await promptly.password("Enter your livingdocs password: ", {
        replace: "*",
      });
    }

    const response = await fetch(
      `${process.env.Q_SERVER_BASE_URL}/authenticate`,
      {
        method: "POST",
        body: JSON.stringify({
          username: process.env.LD_USERNAME,
          password: password.trim(),
        }),
      }
    );
    if (response.ok) {
      const body = await response.json();
      return `Bearer ${body.access_token}`;
    } else {
      throw new Error(
        `Error occured while authenticating: (${response.status}) ${response.statusText}`
      );
    }
  } else {
    return `Bearer ${process.env.Q_SERVER_AUTH}`;
  }
}

async function getItem(itemUrl, bearer) {
  const response = await fetch(`${itemUrl}/${process.env.QID}`, {
    headers: {
      Authorization: bearer,
    },
  });
  if (response.ok) {
    return await response.json();
  }
}

async function saveItem(itemUrl, bearer, item) {
  delete item.updatedDate;
  const response = await fetch(itemUrl, {
    method: "PUT",
    body: JSON.stringify(item),
    headers: {
      Authorization: bearer,
      "Content-Type": "application/json",
    },
  });
  if (response.ok) {
    return await response.json();
  }
}

/**
 * Download shapefiles from the URL configurer through environment variables,
 * extract the ZIP files and store the resulting files and specified
 * path.
 * @param {string} shapefilePath
 */
async function saveShapefile(shapefilePath) {
  const useProxy = process.env.USE_PROXY || false;
  let fetchConfig = {};

  // in case we are on NZZ premises and need a proxy …
  if (useProxy) {
    fetchConfig = {
      ...fetchConfig,
      agent: new ProxyAgent("http://165.225.94.14:9400"),
    };
  }

  const response = await fetch(process.env.DATA_URL, fetchConfig);
  if (response.ok) {
    return new Promise((resolve, reject) => {
      response.body
        .pipe(unzipper.Extract({ path: shapefilePath }))
        .on("close", () => resolve());
    });
  }
}

/**
 * Download the shapefiles and convert them to GeoJSON data
 *
 * @returns {GeoJSON.FeatureCollection}
 */
async function getGeojsons() {
  try {
    const shapefilePath = path.join(__dirname, "/data");
    await saveShapefile(shapefilePath);
    const result = await shapefile.read(
      `${shapefilePath}/${process.env.FILENAME}.shp`,
      `${shapefilePath}/${process.env.FILENAME}.dbf`,
      {
        encoding: "utf-8",
      }
    );
    if (result) {
      await fs.remove(shapefilePath);
      return result.features;
    }
  } catch (error) {
    console.error(error);
  }
}

function formatNote(
  text = "Jede Hotspot- / Aktivfeuererkennung stellt die Mitte eines ungefähr 1km langen Pixels dar, auf dem ein oder mehrere Feuer oder andere thermische Anomalien (z. B. Vulkane) angezeigt werden."
) {
  const formatDate = new Intl.DateTimeFormat("de-CH", { dateStyle: "medium" })
    .format;

  return `${text} Stand: ${formatDate(Date.now())}`.trim();
}

module.exports = {
  getBearerToken: getBearerToken,
  getItem: getItem,
  saveItem: saveItem,
  getGeojsons: getGeojsons,
  formatNote,
};
