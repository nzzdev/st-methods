const vega = require('vega');
const fs = require('fs')
const geo = require("d3-geo-projection")
const request = require('superagent');
const csvtojson = require('csvtojson');
const arquero = require('arquero')
const jenks = require('./jenks');
const svgexport = require("svgexport");
const assert = require('assert');

const COLORS = ["#edece1", "#dfcca9", "#daa878", "#d97e55", "#d64b47"]
const BREAKS = 5

// Register the Robinson projection which is not included in Vega by default
vega.projection("robinson", geo.geoRobinson)

// Download the CSV from https://experience.arcgis.com/experience/3a056fc8839d47969ef59949e9984a71
async function downloadCSV(url) {
    assert(validURL(url), "URL is not valid")


    let json = await csvtojson().fromStream(
        request.get(url)
    )

    // Check if the schema is correct
    // The faction guarantees a list of JSON-objects
    // with these properties
    assert(json[0]['UID'], "Property 'UID' is missing in data")
    assert(json[0]['Incidence7day'], "Property 'Incidence7day is missing in data")
    return json
}

function createDirectory(dir) {

    if (!fs.existsSync(dir)){
        fs.mkdirSync(dir);
    }

    // The function guarantees that the directory exists
    assert(fs.existsSync(dir), `Directory ${dir} could not be created`)
}

function readJSON(file) {
        // Only accepts existing files
        assert(fs.existsSync(file), `TopoJSON file ${file} doesn't exist`)

        return JSON.parse(fs.readFileSync(file, "utf-8"))
}

function getEURegionsTopoJSON(file) {
    json = readJSON(file)

    // Guarantees a TopoJSON
    assert(json["type"] == "Topology", "JSON file does'nt exist")

    // Guarantees a "regions"-layer
    assert(json['objects']['regions'])

    return json
}

function getSpec(filename) {
    let spec = readJSON(filename)

    // Guarantees a Vega-Spec
    assert(spec['$schema'] == 'https://vega.github.io/schema/vega/v5.json')

    // Guarantees important properties in the Vega-Spec
    assert(spec.data[0])
    assert(spec.scales[0])
    assert(spec.data[1])
    assert(spec.scales[1])

    return spec
}

// Import and join the data from a CSV to the TopoJSON.
function joinCSVToTopoJSON(csv, topojson) {
    data = arquero.from(csv)

    // Plausibility checks
    assert(data.rollup({"min": d => arquero.op.min(d['Incidence7day'])}).objects()[0].min >= 0)
    assert(data.rollup({"max": d => arquero.op.max(d["Incidence7day"])}).objects()[0].max <= 100000)

    console.log(data.groupby("UID").count().objects().length)
    assert(data.groupby("UID").count().objects().length <= 756, "Region(s) added")
    assert(data.groupby("UID").count().objects().length >= 756, "Region(s) removed")

    topojson.objects.regions.geometries.forEach(geom => {
       let incidence = data
            .params({ id: geom.properties.UID })
            .filter((d, $) => d.UID == $.id)
            .objects()


        if(incidence.length>0) {
            geom.properties["Incidence7day"] = Number(incidence[0]["Incidence7day"]);
        } else {
            //console.log(geom.properties.UID)
        }
      })
    
          return topojson
}

// Add the new TopoJSON to the imported spec
function addMapDataToSpec(data, spec) {
    delete spec.data[0].url
    spec.data[0].values = data
    return spec
}

// Adds an array with color breaks to the proper scale
function addBreaksToSpec(breaks, spec) {
    spec.scales[0].domain = breaks
    return spec
}

// Calculates color breaks from the data
function getBreaks(data, breakCount) {
    let _d = data.map(d => Number(d["Incidence7day"]))
    return jenks.jenks(_d, breakCount)
}

// Builds the JSON-fragment to populate legend-data
function getLegend(breaks, colors) {
    let _help = []
    for(let i=1; i<breaks.length; i++) {
        _help.push({
            "from": breaks[i-1],
            "to": breaks[i],
            "color": colors[i-1]
        })
    }
    return _help
}

// Generate the JSON-fragemnt to populate the legendLabels-data
function getLabels(legendData) {

    _help = [
        {"name": Math.round(legendData[0].from), "position": legendData[0].from, "align": "left"}
    ]

    legendData.forEach(segement => {
        _help.push({
            "name": Math.round(segement.to),
            "position": segement.to,
            "align": "center"
        })
    })

    _help[_help.length-1].align = "right"

    return _help
}

// Inserts the legend-data and the corresponding scale into the spec
function addLegendToSpec(legend, spec) {
    spec["data"][1]['values'] = legend
    spec['scales'][1]['domain'] = [Math.min.apply(this, legend.map(d => d.from)), Math.max.apply(this, legend.map(d => d.to))]
    return spec
}

// Inserts the legendLabels-data. The scale is the same as with the Legend.
function addLegendLabelsToSpec(labels, spec) {
    spec["data"][2]['values'] = labels
    return spec
}

// generate SVG from Vega-Spec
function generateSVGfromSpec(filepath, spec) {
    let view = new vega.View(vega.parse(spec), {renderer: 'none'});

    fs.writeFileSync("out.vg.json", JSON.stringify(spec, null, 2))

    view.toSVG()
      .then(function(svg) {
        fs.writeFile(filepath, svg, function (err) {
            if (err) throw(err);
          });
      })

}

// Updates the q.config to include the timestamp of today
// Returns null because it writes to a file
function updateLastUpdated() {
    let qConfig = readJSON("q.config.json")
    let text = `Die unterschiedlich grossen Gruppen kommen durch ein statistisches Verfahren zustande, welches die Werte so in Gruppen einteilt, dass die Unterschiede zwischen den Regionen möglichst gut sichtbar werden (Jenks Natural Breaks). Letzte Aktualisierung am ${dateTodayFormatted()}`

    qConfig.items[0].item.notes = text

    fs.writeFileSync("q.config.json", JSON.stringify(qConfig, null, 4))
}

// Today's date, nicely formatted as 19. 11. 2020
function dateTodayFormatted() {
    let ts = new Date()
    return `${ts.getDate()}. ${ts.getMonth()+1}. ${ts.getFullYear()}`
}


function combineDataIntoSpec(mapData, csv, specFile) {

    let breaks = getBreaks(csv, BREAKS)

    let spec = addMapDataToSpec(
        mapData,
        getSpec(specFile)
    )
    spec = addBreaksToSpec(
        breaks, 
        spec
    )
    
    spec = addLegendToSpec(
        getLegend(
            breaks,
            COLORS
        ), 
        spec
    )

    spec = addLegendLabelsToSpec(
        getLabels(
            getLegend(
                [breaks[0], breaks[breaks.length-1]],
                COLORS
            )
        ), 
        spec
    )


    return spec
}

// This is the pipeline that combines different data files with a Vega spec, generates SVGs and PNGs from these
async function main() {
    
    // Load the necessary data
    let csv = await downloadCSV("https://arcgis.com/sharing/rest/content/items/54d73d4fd4d94a0c8a9651bc4cd59be0/data")
    let euRegions = await getEURegionsTopoJSON("eu-regions.json")
    let mapData = joinCSVToTopoJSON(csv, euRegions)

    // Create directories for output files
    createDirectory('svgs');
    createDirectory('pngs')

    // Create final specs
    let mw = combineDataIntoSpec(mapData, csv, "mw.vg.json")
    let cw = combineDataIntoSpec(mapData, csv, "cw.vg.json")
    let fw = combineDataIntoSpec(mapData, csv, "fw.vg.json")

   // Generate SVGs
   generateSVGfromSpec('svgs/mw.svg', mw)
   generateSVGfromSpec('svgs/cw.svg', cw)
   generateSVGfromSpec('svgs/fw.svg', fw)

   let styles = "";

   // Get NZZ font-face definitions
   const response = await request.get("https://context-service.st.nzz.ch/stylesheet/fonts/nzz.ch.css");
   if(response) {
    styles = response.text;
    // correct shorthand version of links (// -> https://)
    styles = styles.replace(/\/\//g, "https://");
   }

   // Generate PNGs
   svgexport.render([ {
    "input" : ["svgs/mw.svg"],
    "output": [ ["pngs/mw.png", "2x", styles] ]
    },
    {
    "input" : ["svgs/cw.svg"],
    "output": [ ["pngs/cw.png", "2x", styles] ]
    },
    {
    "input" : ["svgs/fw.svg"],
    "output": [ ["pngs/fw.png", "2x", styles] ]
    }])

    // Update Timestamp
    updateLastUpdated()
    
}

main()


// Check if an URL is valid
function validURL(str) {
    var pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
      '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
      '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
      '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
      '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
      '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
    return !!pattern.test(str);
  }
