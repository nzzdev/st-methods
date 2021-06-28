const fs = require("fs");

function readJSON(file) {
  return JSON.parse(fs.readFileSync(file, "utf-8"));
}

function updateLastUpdatedAt() {
  let qConfig = readJSON("q.config.json");

  qConfig.items[0].item.data[1] = [new Date()];

  fs.writeFileSync("q.config.json", JSON.stringify(qConfig, null, 4));
}

exports.updateLastUpdatedAt = updateLastUpdatedAt
