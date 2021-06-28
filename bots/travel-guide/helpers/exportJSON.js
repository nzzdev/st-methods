const fs = require("fs");

function writeFile(fileName, data) {
  try {
    if (!data) throw new Error("Missing parameter.");
    
    console.log("Exporting as JSON file...");

    fs.writeFile(`data/${fileName}.json`, JSON.stringify(data), (error) => {
      if (error) throw new Error(
        `${error}
         data/${fileName}.json`
      );
    });
  } catch (error) {
    console.error(error);
  }
}

exports.writeFile = writeFile
