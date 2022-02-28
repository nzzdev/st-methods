from pathlib import Path
import git
import os
import geojson_export

# Set working directory
workingdir = Path(__file__).parents[1].absolute()
os.chdir(workingdir)

# Init Git
repo = git.Repo(workingdir)
print("Repo: %s" % workingdir)

print("Pull from git")
repo.git.pull()

geojson_export.create_geojson(Path(workingdir / 'export/annotations.json'))

print("Try to comming")
repo.git.add(workingdir / 'export/')
if repo.git.diff(None, cached=True) != "":
    repo.git.commit('-m', 'auto-sync', author='Simon Huwiler <webmaster@simonhuwiler.ch>')
    repo.git.push()
else:
    print("Nothing changed")
