const fs = require("fs");

function writeFile(fileName, data) {
  if (!data) throw new Error("Missing parameter.");
  
  console.log("Exporting as JSON file...");

  fs.writeFile(`${fileName}.json`, JSON.stringify(data), (error) => {
    if (error) throw new Error(
      `${error}
        ${fileName}.json`
    );
  });
}

exports.writeFile = writeFile
