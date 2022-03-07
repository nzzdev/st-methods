#!/usr/bin/env node

const https = require('https');
const url = require('url');

const dataunwrapper = module.exports = function(id, fn){
	if (!id) return fn("usage: dataunwrapper <id>");
	if (!/^[a-z0-9]+$/i.test(id)) fn("invalid id");

	// resolve metatag-redirect
	https.get('https://datawrapper.dwcdn.net/'+id+'/', function(res){
		if (res.statusCode !== 200) fn("response: http status "+res.statusCode);

		let content = [];

		res.on('error', function(err){

			fn(err);

		}).on('data', function(chunk){

			content.push(chunk);

		}).on('end', function(){

			content = content.join("");
			
			if (!/<meta http-equiv="REFRESH" content="0; url=(.*?)\/([a-z0-9]+)\/([0-9]+)\/">/i.test(content)) return console.log(RegExp.$0),fn(new Error("No version redirect found"));
			
			const ver = RegExp.$3;

			// fetch content
			https.get('https://datawrapper.dwcdn.net/'+id+'/'+ver+'/', function(res){

				if (res.statusCode !== 200) fn("response: http status "+res.statusCode);

				let content = [];

				res.on('error', function(err){

					fn(err);

				}).on('data', function(chunk){

					content.push(chunk);

				}).on('end', function(){

					extract(content.join(""), fn);

				});

			});
			
		});
	});
};

// extract inline data from over-webpacked code
const extract = module.exports.extract = function(content, fn){

	// new svelte version, extract __DW_SVELTE_PROPS__ blob
	if (/window\.__DW_SVELTE_PROPS__/.test(content) && /window\.__DW_SVELTE_PROPS__ = JSON\.parse\("([^\n]+)"\);\n/.test(content)) {

		let data;
		try {
			data = JSON.parse(JSON.parse("\""+RegExp.$1+"\""));
		} catch (err) {
			return fn(err);
		}

		// check for version override (datawrapper publishes the wrong version in their inline data)
		let versionOverride = false;
		if (/<link rel="alternate" type="application\/json\+oembed"(\s+)href="https:\/\/api\.datawrapper\.de\/v3\/oembed\?url=https:\/\/datawrapper\.dwcdn\.net\/([^\/]+)\/([0-9]+)\/&format=json"(\s+)title="oEmbed" \/>/.test(content)) {
			versionOverride = RegExp.$3;
		}
		
		let dataurl;
		if (!!data.chart.externalData) {
			dataurl = data.chart.externalData;
		} else {
			// find csv endpoint in __DW_SVELTE_PROPS__ blob
			if (!data.hasOwnProperty("assets") || typeof data.assets !== "object") return fn(new Error("data.assets not present"));
			const endpoint = Object.keys(data.assets).find(function(k){
				return /\.csv$/.test(k);
			});
			if (!endpoint) return fn(new Error("csv url not found in data.assets"));
			
			// override version
			if (versionOverride) data.chart.publicUrl = data.chart.publicUrl.replace(/\/[0-9]+\/?$/,'/'+versionOverride+'/');
			
			dataurl = url.resolve(data.chart.publicUrl, data.assets[endpoint].url);
		}
		
		// get csv from url
		https.get(dataurl, function(res){
			if (res.statusCode !== 200) fn("response: http status "+res.statusCode);

			let content = [];
			res.on('error', function(err){
				fn(err);
			}).on('data', function(chunk){
				content.push(chunk);
			}).on('end', function(){
				return fn(null, content.join(""))
			});

		});

		return;
		
	}

	// most common
	if (/\\"(?:data|chartData)/.test(content) && /\\"(?:data|chartData)\\":\\"(.*?[^\\])\\",/.test(content)) {
		try {
			let data = JSON.parse("\""+JSON.parse("\""+RegExp.$1+"\"")+"\"");
		} catch (err) {
			return fn(err);
		}
		return fn(null, data);
	}

	// less common
	if (/render\(\{/.test(content) && /render\(\{(.*?)\schartData: "(.*?)",?\n(.*?)\}\);/s.test(content)) {
		try {
			let data = JSON.parse('"'+RegExp.$2+'"');
		} catch (err) {
			return fn(err);
		}
		return fn(null, data);
	}

	// way less common
	if (/__dw\.init\(\{/.test(content) && /__dw\.init\(\{(.*?)\sdata: "(.*?)",?\n(.*?)\}\);/s.test(content)) {
		try {
			let data = JSON.parse('"'+RegExp.$2+'"');
		} catch (err) {
			return fn(err);
		}
		return fn(null, data);
	}
	
	// only found once
	if (/__dw\.init\(\$\.extend\(\{/.test(content) && /__dw\.init\(\$\.extend\(\{(.*?)\sdata: "(.*?)",?\n(.*?)\}, window\.__dwParams\)\);/s.test(content)) {
		try {
			let data = JSON.parse('"'+RegExp.$2+'"');
		} catch (err) {
			return fn(err);
		}
		return fn(null, data);
	}

	// report a bug if you find a non-functioning version
	return fn(new Error("could not find data"));
};

if (require.main === module) dataunwrapper(process.argv[2], function(err, data){
	if (err) console.error(err.toString()), process.exit(1);
	console.log(data);
});
