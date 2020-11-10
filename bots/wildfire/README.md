# Wildfire Automation

This automation downloads data from [FIRMS, the Fire Information for Resource Management System](https://firms.modaps.eosdis.nasa.gov) by Nasa.

Based on the [Q map](https://medium.com/nzz-open/lets-build-together-nzz-s-storytelling-toolbox-q-is-now-open-source-39decb92aeca) that should be updated, the data will be cropped, prepared and uploaded back to the map.

## Tools needed

This tool uses [Yarn 2](https://yarnpkg.com) for package management. It's set up to use Plug'n'Play for fast script execution.

## Development
With PnP enabled, you should be good to go, there is no need to install NPM packages, they are already here.

During development, use the command `yarn run dev` to start the bot locally. It will then use environment variables set in `./lib/dev.js`.


## Deployment

The workflow definitions go into the `.github/workflows` directory.

A documented examples has been provided in `./workflow_examples`.
A documented examples has been provided in `./workflow_examples`.
