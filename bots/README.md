# Automated Scripts

This directory contains scripts that automate the update process of charts. Typically, a script fetches data from a data source, transforms it and updates a chart with the new data. These scripts are usually written in [R](https://www.r-project.org/), [Python](https://www.python.org/) or [JavaScript](https://nodejs.org/) and use the [Q cli](https://github.com/nzzdev/q-cli) to update the chart with new data in Q. Finally, [Github Actions](https://github.com/features/actions) is used to run these scripts on a schedule.

## How to add a new automated script

- Create a new directory with a descriptive name (use dashes to separate words)
- Create a file for the script and a file with name `q.config.json` used by Q cli
- Develop the script in your preferred language
- Try to run and update the chart locally using Q cli (see [wiki post](https://wiki.nzzmg.ch/confluence/pages/viewpage.action?spaceKey=RED&title=Q+Grafiken+automatisiert+aktualisieren) for more details)
- Setup the [Github Actions workflow file](https://docs.github.com/en/actions/quickstart) (use the [corona-charts workflow](../.github/workflows/corona-charts.yml) as reference)
- Run the Github Action manually using the run workflow button in the Actions Tab on Github
- The action is now set up and will run on the schedule defined in the workflow file

## What should be considered when developing a new automated script

### Use a dependency manager

A script typically uses external dependencies for things like data fetching, data analysis or manipulation json data. To make these dependencies available within Github Actions a dependency manager is required. It is recommended to use the following dependency managers:

- R: [renv](https://rstudio.github.io/renv/articles/renv.html)
  - Install renv: `install.packages("renv")`
  - Initialize new project: `renv::init()`
  - Save dependencies to lockfile: `renv::snapshot()`
  - Restore dependencies: `renv::restore()`
- Python: [Pip](https://pip.pypa.io/en/stable/installing/)
  - Install pip: `python -m pip install --upgrade pip setuptools wheel`
  - Save dependencies to requirements file: `pip freeze > requirements.txt`
  - Restore dependencies: `pip install -r requirements.txt`
- JavaScript: [npm](https://www.npmjs.com/get-npm)
  - Install npm: `npm install npm@latest -g`
  - Initialize new project: `npm init`
  - Save dependencies to lockfile: `npm install --save <dependency-name>`
  - Restore dependencies: `npm install`

### Create a separate script for each dataset

Scripts can get quickly complex and it gets hard for other collegues to further develop the script. Usually it's a good practice to create a separate script for each dataset. This ensures that charts using the same dataset are in the same script and the dataset is only fetched once for all charts using it.

The [corona-charts workflow](./corona-charts) can be used as a reference. There is one script for each dataset and all scripts share a common `q.config.json` file. The Github Action runs all the script sequentially and in the end runs the Q cli once which updates all charts defined in `q.config.json`.

### Share common helper functions between scripts

Helper functions which are used in more than one script should be extracted into a helper file. The script can access this functions by importing the helper file.

Use the [corona-charts workflow](./corona-charts/helpers.R) as reference. It uses both R and Python scripts and provides functions for fetching dataset and update charts in a helper file.

#### Import helper functions in R

```R
# import helper functions
source("./helpers.R")
```

#### Import helper functions in Python

```Python
# add parent directory to path so ../helpers.py file can be referenced
sys.path.append(os.path.dirname((os.path.dirname(__file__))))
from helpers import *
```

### Exclude temporary files and folders from version control

Some IDEs (RStudio) can create temporary files/folders while developing or sometimes it can make sense to store fetched datasets locally before transforming them. This files should be excluded from version control by adding them to the `.gitignore` file.

```bash
# Ignore temporary data folders
data/

# Ignore temporary Python files
__pycache__

# Ignore temporary R files
.RData
.Rhistory
.Rapp.history
.Renviron
.Rproj.user/
.Ruserdata
*.Rproj
```
