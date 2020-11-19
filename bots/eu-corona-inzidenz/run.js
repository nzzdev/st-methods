const vega = require('vega');
const fs = require('fs')
const geo = require("d3-geo-projection")
const request = require('superagent');
const csvtojson = require('csvtojson');
const arquero = require('arquero')
const jenks = require('./jenks');
const svgexport = require("svgexport")
const assert = require('assert')

const COLORS = ["#edece1", "#dfcca9", "#daa878", "#d97e55", "#d64b47"]
const BREAKS = 5

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

function getEURegionsTopoJSON(file) {
    // Only accepts existing files
    assert(fs.existsSync(file), `TopoJSON file ${file} doesn't exist`)

    let json = JSON.parse(fs.readFileSync(file, "utf-8"))

    // Guarantees a TopoJSON
    assert(json["type"] == "Topology", "Not a TopoJSON file")

    // Guarantees a "regions"-layer
    assert(json['objects']['regions'])

    return json
}

function getSpec(filename) {
    // Only accepts existing files
    assert(fs.existsSync(filename), `Vega file ${filename} doesn't exist`)

    let spec = JSON.parse(fs.readFileSync(filename, 'utf8'));

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
// TODO: Plausibility check and error if bad
function joinCSVToTopoJSON(csv, topojson) {
    data = arquero.from(csv)

    // Plausibility checks
    assert(data.rollup({"min": d => arquero.op.min(d['Incidence7day'])}).objects()[0].min >= 0)
    assert(data.rollup({"max": d => arquero.op.max(d["Incidence7day"])}).objects()[0].max <= 100000)
    assert(data.groupby("UID").count().objects().length <= 673, "Region(s) added")
    assert(data.groupby("UID").count().objects().length >= 673, "Region(s) removed")

    topojson.objects.regions.geometries.forEach(geom => {
        geom.properties["Incidence7day"] = Number(
          data
            .params({ id: geom.properties.UID })
            .filter((d, $) => d.UID == $.id)
            .objects()[0]["Incidence7day"]
        );
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


function getLegend(breaks, colors) {
    let _help = []
    for(let i=1; i<breaks.length; i++) {
        _help.push({
            "from": breaks[i-1],
            "to": breaks[i],
            "color": colors[i-1]
        })
    }
    return addLabels(_help)
}

function addLabels(legendData) {
    legendData[0] = {...legendData[0],
        "label": {
            "name": `${legendData[0].from}`,
            "position": legendData[0].from,
            "align": "left"
        }
    }

    let last = legendData.length-1

    legendData[last] = {...legendData[last],
        "label": {
            "name": `${legendData[last].to}`,
            "position": legendData[last].to,
            "align": "right"
        }
    }

    return legendData
}

function addLegendToSpec(legend, spec) {
    spec["data"][1]['values'] = legend
    spec['scales'][1]['domain'] = [Math.min.apply(this, legend.map(d => d.from)), Math.max.apply(this, legend.map(d => d.to))]
    return spec
}

// generate SVG from Vega-Spec
function generateSVGfromSpec(filepath, spec) {
    let view = new vega.View(vega.parse(spec), {renderer: 'none'});

    //fs.writeFileSync("out.vg.json", JSON.stringify(spec, null, 2))

    view.toSVG()
      .then(function(svg) {
        fs.writeFile(filepath, svg, function (err) {
            if (err) return console.log(err);
          });
      })
      .catch(function(err) { console.error(err); });    
}

async function main() {
    let csv = await downloadCSV("https://www.arcgis.com/sharing/rest/content/items/54d73d4fd4d94a0c8a9651bc4cd59be0/data")
    let euRegions = await getEURegionsTopoJSON("eu-regions.json")
    let mapData = joinCSVToTopoJSON(csv, euRegions)

    createDirectory('svgs');
    createDirectory('pngs')

    ///////

    let mw = addMapDataToSpec(
        mapData,
        getSpec('mw.vg.json')
    )
    mw = addBreaksToSpec(
            getBreaks(csv, BREAKS), 
        mw)
    
    mw = addLegendToSpec(
                getLegend(
                    getBreaks(csv, BREAKS),
                    COLORS
                ), 
            mw)

    ////////
    let cw = addMapDataToSpec(
        mapData,
        getSpec('cw.vg.json')
    )
    cw = addBreaksToSpec(
        getBreaks(csv, BREAKS), 
    cw)

    cw = addLegendToSpec(
        getLegend(
            getBreaks(csv, BREAKS),
            COLORS
        ), 
    cw)


  /////////
  let fw = addMapDataToSpec(
        mapData,
        getSpec('fw.vg.json')
    )
    fw = addBreaksToSpec(
        getBreaks(csv, BREAKS), 
    fw)

    fw = addLegendToSpec(
        getLegend(
            getBreaks(csv, BREAKS),
            COLORS
        ), 
    fw)
/*
   generateSVGfromSpec('svgs/mw.svg', mw)
   generateSVGfromSpec('svgs/cw.svg', cw)
   generateSVGfromSpec('svgs/fw.svg', fw)

   svgexport.render([ {
    "input" : ["svgs/mw.svg"],
    "output": [ ["pngs/mw.png", "2x"] ]
},
{
    "input" : ["svgs/cw.svg"],
    "output": [ ["pngs/cw.png", "2x"] ]
},
{
    "input" : ["svgs/fw.svg"],
    "output": [ ["pngs/fw.png", "2x"] ]
}])

*/
    
}

main()


function validURL(str) {
    var pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
      '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
      '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
      '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
      '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
      '(\\#[-a-z\\d_]*)?$','i'); // fragment locator
    return !!pattern.test(str);
  }
