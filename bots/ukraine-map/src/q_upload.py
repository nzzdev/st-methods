from pathlib import Path
import os
import geojson_export
import helpers
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', type=str, required=True, help='"staging" or "production"')
args = parser.parse_args()
print("Update %s" % args.p)

# Set working directory
workingdir = Path(__file__).parents[1].absolute()
os.chdir(workingdir)

export_path = Path(workingdir / 'annotations.json')

geojson_export.create_geojson(export_path)

if args.p.lower() == 'staging':
    chartid = 'ecf1db20c4ca6dcf6e7909906709f3f7'
elif args.p.lower() == 'production':
    chartid = 'c43940da317fdc578cf589dd9357512c'
else:
    raise Exception('Unknown platform: %s' % args.p)

files = [{
        "file": {
            'path': str(export_path)
        }
    }]

helpers.update_chart(
    id = chartid,
    files = files
)
