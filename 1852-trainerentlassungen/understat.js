const puppeteer = require("puppeteer");
const moment = require("moment");
const Papa = require("papaparse");
var fs = require('fs');

var date_for_table = "Dec 1, 2018"

const columnheaders = ["RealRank", "Team", "Matches", "Wins", "Draws", "Losses", "GoalsScored", "GoalsConceded", "Points", "ExpectedGoals", "ExpectedGoalsConceded", "ExpectedPoints", "Date"]
dataarray = []



const tablebody = "body > div.wrapper > div.page-wrapper > div:nth-child(3)"
async function run() {
  const browser = await puppeteer.launch({
    headless: true
  });

  const page = await browser.newPage();
  rowindex = 0
  columnindex = 0
  csv_row = 0
  const datestring = "Dec 01, 2018"

  //sending to the page
  //https://understat.com/league/EPL
  //https://understat.com/league/La_liga/2018
  //https://understat.com/league/Bundesliga/2018
  //https://understat.com/league/Serie_A/2018
  //https://understat.com/league/Ligue_1/2018
  await page.goto("https://understat.com/league/Ligue_1/2018");
  for (let a = 0; a < 180; a++) {
    let dateback = (moment().subtract(a, 'days'))
    let datestring = dateback.format("MMM DD, YYYY")
    let date_for_table = dateback.format("DD-MM-YYYY")
    console.log(date_for_table)

    await page.waitFor(2 * 1000);

    //clicking and entering
    page.evaluate(function () {
      document.querySelector('input[name="date-end"]').value = ''
    })
    await page.click('input[name="date-end"]');

    await page.keyboard.type(datestring);

    await page.click(tablebody);

    let headerwidth = await page.evaluate((sel) => {
      return element = document.getElementsByTagName(sel[0])[0].getElementsByTagName(sel[1])[0].getElementsByTagName(sel[2]).length;
    }, ["table", "tr", "th"]);
    //only get the tablebody
    let listLength = await page.evaluate((sel) => {
      return document.getElementsByTagName(sel[0])[0].getElementsByTagName(sel[1])[0].getElementsByTagName(sel[2]).length;
    }, ["table", "tbody", "tr"]);
    dataarray[0] = columnheaders
    for (let i = 0; i <= listLength - 1; i++) {
      let rowindex = i;
      csv_row = csv_row + 1;


      dataarray[csv_row] = []
      for (let j = 0; j <= headerwidth; j++) {
        let columnindex = j;
        if (j == headerwidth) {
          dataarray[csv_row][columnindex] = date_for_table

        } else {
          let celltext = await page.evaluate((sel) => {
            let element = document.getElementsByTagName(sel[0])[0].getElementsByTagName(sel[1])[0].getElementsByTagName(sel[2])[(sel[3])].getElementsByTagName(sel[4])[(sel[5])];

            return element ? element.innerHTML : null;

          }, ["table", "tbody", "tr", rowindex, "td", columnindex]);
          if (columnindex === 1) {
            celltext = celltext.match(/<a [^>]+>([^<]+)<\/a>/)[1];
          }
          if (columnindex > 8) {
            celltext = celltext.split('<sup')[0];
          }
          dataarray[csv_row][columnindex] = celltext
        }
      };
      //has to be here, otherwise you start with csv_row=1 and start filling up the array from row 1 and not from row 0
    };


  }

  var testcsv = await Papa.unparse(dataarray);
  fs.writeFile("/Users/halukamaier-borst/Documents/Ligue1.csv", testcsv, function (err) {})


  //This resolves when the page navigates to a new URL or reloads.
  //This links to a new page

  // wait for 2 seconds
  await page.waitFor(5 * 1000);


  browser.close();
}



run();