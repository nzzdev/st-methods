const fs = require("fs");

async function getItem() {
  const response = await fetch(`${process.env.Q_PRODUCTION_SERVER}/${process.env.Q_PRODUCTION_ID}`, {
    headers: {
      Authorization: `Bearer ${process.env.Q_PRODUCTION_ACCESSTOKEN}`,
    },
  })

  if (response.ok) {
    return await response.json()
  }

  throw new Error(
    `Error occured while downloading Q item. ${response.status}: ${response.statusText}`
  )
}

function readJSON(file) {
  return JSON.parse(fs.readFileSync(file, "utf-8"));
}

async function updateFiles() {
  const item = await getItem();
  let files = item.files.filter(file => file.loadSyncBeforeInit === true);

  files.push(
    { "loadSyncBeforeInit": false, "file": { "path": "./countriesInformation.json" } },
    { "loadSyncBeforeInit": false, "file": { "path": "./tripsInformation.json" } }
  )

  let qConfig = readJSON("q.config.json");

  qConfig.items[0].item.files = files;

  fs.writeFileSync("q.config.json", JSON.stringify(qConfig, null, 4));
}

function updateId() {
  let qConfig = readJSON("q.config.json");

  qConfig.items[0].environments = [
    { "name": "production", "id": `${process.env.Q_PRODUCTION_ID}` }
  ];

  fs.writeFileSync("q.config.json", JSON.stringify(qConfig, null, 4));
}

function updateLastUpdatedAt() {
  let qConfig = readJSON("q.config.json");

  qConfig.items[0].item.data[1] = [new Date()];

  fs.writeFileSync("q.config.json", JSON.stringify(qConfig, null, 4));
}

exports.updateFiles = updateFiles
exports.updateId = updateId
exports.updateLastUpdatedAt = updateLastUpdatedAt
