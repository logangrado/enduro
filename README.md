# `Enduro`

Endurance race pitstop calculator

## Installation

* Install [`poetry`](https://python-poetry.org/docs/#installation)
* Create environment, install dependencies: `poetry install`


## Usage

* Activate shell: `poetry shell`
* Run: `python enduro/cli/main.py CONFIG_PATH`

## Config Files

All info is specified via config file. See the `config` directory for examples. All config values are checked via `pydantic`. Options are specified in the [config](enduro/config.py)