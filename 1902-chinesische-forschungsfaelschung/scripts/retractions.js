const puppeteer = require("puppeteer");
const moment = require("moment");
const Papa = require("papaparse");
var fs = require("fs");
var table = "#grdRetraction";

dataarray = [];

async function run() {
  const browser = await puppeteer.launch({
    headless: true
  });

  const page = await browser.newPage();
  rowindex = 0;
  columnindex = 0;
  csv_row = 0;

  for (let a = 0; a < 121; a++) {
    await page.goto(
      "http://retractiondatabase.org/RetractionSearch.aspx?AspxAutoDetectCookieSupport=1"
    );

    await page.waitFor(1 * 1000);
    let dateback_a = moment().subtract(a + 1, "months");
    let dateback_b = moment().subtract(a, "months");
    let datestring_a = dateback_a.format("MM/DD/YYYY");
    let datestring_b = dateback_b.format("MM/DD/YYYY");
    console.log(datestring_a);
    //clicking and entering
    page.evaluate(function () {
      document.querySelector('input[name="txtOriginalDateFrom"]').value = "";
    });
    await page.click('input[name="txtOriginalDateFrom"]');

    await page.keyboard.type(datestring_a);
    await page.waitFor(1 * 1000);

    page.evaluate(function () {
      document.querySelector('input[name="txtOriginalDateTo"]').value = "";
    });
    await page.click('input[name="txtOriginalDateTo"]');

    await page.keyboard.type(datestring_b);

    await page.click('input[name="btnSearch"]');

    await page.waitFor(2 * 1000);

    // let tableHTML = await page.evaluate((sel) => {
    //   element = document.querySelector(sel);
    //   return element ? element.innerHTML : null;

    // }, table);
    try {
      let tablelength = await page.evaluate(
        sel => {
          element = document.querySelector(sel[0]).getElementsByTagName(sel[1])
            .length;
          return element;
        },
        [table, "tr"]
      );
      console.log(tablelength);

      //iterating through each row of the table
      for (let i = 1; i <= tablelength - 1; i++) {
        let rowindex = i;
        let papertitle = "";
        let scientist = "";
        let subject = "";
        let university = "";
        let publisher = "";
        let journal = "";
        let reason = "";
        let retractiondate = "";
        let retractiondoi = "";
        let publishdate = "";
        let publishdoi = "";

        //retrieving for each row the number of cells
        let numberofcells = await page.evaluate(
          sel => {
            element = document
              .querySelector(sel[0])
              .getElementsByTagName(sel[1])[sel[2]].getElementsByTagName(sel[3]).length;
            return element;
          },
          [table, "tr", rowindex, "td"]
        );

        //iterating through each cell of a row
        for (let j = 0; j <= numberofcells - 1; j++) {
          let cellindex = j;

          if (cellindex === 4) {
            let cellHTML = await page.evaluate(
              sel => {
                element = document
                  .querySelector(sel[0])
                  .getElementsByTagName(sel[1])[sel[2]].getElementsByTagName(sel[3])[sel[4]];
                return element ? element.innerHTML : null;
              },
              [table, "tr", rowindex, "td", cellindex]
            );
            if (cellHTML !== null) {
              let publishspecs = cellHTML.split("<br>");
              publishdate = publishspecs[0];
              publishdoi = String(publishspecs[2].match(">(.*?)<")[0]).slice(
                1,
                -1
              );
            }
          }
          if (cellindex === 5) {
            let cellHTML = await page.evaluate(
              sel => {
                element = document
                  .querySelector(sel[0])
                  .getElementsByTagName(sel[1])[sel[2]].getElementsByTagName(sel[3])[sel[4]];
                return element ? element.innerHTML : null;
              },
              [table, "tr", rowindex, "td", cellindex]
            );
            if (cellHTML !== null) {
              let retractionspecs = cellHTML.split("<br>");
              retractiondate = retractionspecs[0];
              retractiondoi = String(
                retractionspecs[2].match(">(.*?)<")[0]
              ).slice(1, -1);
            }
          }

          let numberofspans = await page.evaluate(
            sel => {
              element = document
                .querySelector(sel[0])
                .getElementsByTagName(sel[1])[sel[2]].getElementsByTagName(sel[3])[sel[4]].getElementsByTagName(sel[5]).length;
              return element;
            },
            [table, "tr", rowindex, "td", cellindex, "span"]
          );
          let numberofdivs = await page.evaluate(
            sel => {
              element = document
                .querySelector(sel[0])
                .getElementsByTagName(sel[1])[sel[2]].getElementsByTagName(sel[3])[sel[4]].getElementsByTagName(sel[5]).length;
              return element;
            },
            [table, "tr", rowindex, "td", cellindex, "div"]
          );

          let numberofas = await page.evaluate(
            sel => {
              element = document
                .querySelector(sel[0])
                .getElementsByTagName(sel[1])[sel[2]].getElementsByTagName(sel[3])[sel[4]].getElementsByTagName(sel[5]).length;
              return element;
            },
            [table, "tr", rowindex, "td", cellindex, "a"]
          );

          if (numberofspans !== 0) {
            for (let k = 0; k <= numberofspans - 1; k++) {
              let spanindex = k;
              let spanclass = await page.evaluate(
                sel => {
                  element = document
                    .querySelector(sel[0])
                    .getElementsByTagName(sel[1])[sel[2]].getElementsByTagName(sel[3])[sel[4]].getElementsByTagName(sel[5])[sel[6]];
                  return element ? element.className : null;
                },
                [table, "tr", rowindex, "td", cellindex, "span", spanindex]
              );

              let spanHTML = await page.evaluate(
                sel => {
                  element = document
                    .querySelector(sel[0])
                    .getElementsByTagName(sel[1])[sel[2]].getElementsByTagName(sel[3])[sel[4]].getElementsByTagName(sel[5])[sel[6]];
                  return element ? element.innerHTML : null;
                },
                [table, "tr", rowindex, "td", cellindex, "span", spanindex]
              );

              //console.log(spanclass);

              //console.log(spanHTML);
              if (spanclass === "rTitleNotIE") {
                papertitle += spanHTML + ",";
              }
              if (spanclass === "rSubject") {
                subject += spanHTML + ",";
                console.log(subject);
              }
              if (spanclass === "rJournal") {
                journal += spanHTML + ",";
              }
              if (spanclass === "rPublisher") {
                publisher += spanHTML + ",";
              }
              if (spanclass === "rInstitution") {
                spanHTML = spanHTML.replace(/^\s+/g, "");
                university += spanHTML + "; ";
              }
            }
          }
          if (numberofdivs !== 0) {
            for (let k = 0; k <= numberofdivs - 1; k++) {
              let divindex = k;
              let divclass = await page.evaluate(
                sel => {
                  element = document
                    .querySelector(sel[0])
                    .getElementsByTagName(sel[1])[sel[2]].getElementsByTagName(sel[3])[sel[4]].getElementsByTagName(sel[5])[sel[6]];
                  return element ? element.className : null;
                },
                [table, "tr", rowindex, "td", cellindex, "div", divindex]
              );

              let divHTML = await page.evaluate(
                sel => {
                  element = document
                    .querySelector(sel[0])
                    .getElementsByTagName(sel[1])[sel[2]].getElementsByTagName(sel[3])[sel[4]].getElementsByTagName(sel[5])[sel[6]];
                  return element ? element.innerHTML : null;
                },
                [table, "tr", rowindex, "td", cellindex, "div", divindex]
              );

              if (divclass == "rReason") {
                reason += divHTML.substr(1) + ",";
              }
            }
          }
          //console.log(numberofas)

          if (numberofas !== 0 && cellindex == 3) {
            for (let k = 0; k <= numberofas - 1; k++) {
              let aindex = k;
              let aHTML = await page.evaluate(
                sel => {
                  element = document
                    .querySelector(sel[0])
                    .getElementsByTagName(sel[1])[sel[2]].getElementsByTagName(sel[3])[sel[4]].getElementsByTagName(sel[5])[sel[6]];
                  return element ? element.innerHTML : null;
                },
                [table, "tr", rowindex, "td", cellindex, "a", aindex]
              );
              //console.log(aHTML)

              scientist += aHTML + ", ";
            }
          }
        }
        rowentry = {
          scientist: scientist,
          university: university,
          paper: papertitle,
          journal: journal,
          publisher: publisher,
          subject: subject,

          reason: reason,
          retractiondate: retractiondate,
          retractiondoi: retractiondoi,
          publishdate: publishdate,
          publishdoi: publishdoi
        };
        //console.log(rowentry);

        // console.log("-----")
        // console.log(scientist)
        // console.log("++++")

        // console.log(university)
        // console.log("++++")

        // console.log(papertitle)
        // console.log("++++")

        dataarray.push(rowentry);
      }
    } catch (error) {
      console.log(error);
    }
  }
  browser.close();
  var testcsv = await Papa.unparse(dataarray);
  fs.writeFile(
    "/Users/halukamaier-borst/Documents/retractions_raw.csv",
    testcsv,
    function (err) {}
  );
}
run();