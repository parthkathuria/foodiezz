#!/usr/bin/env bash

# Shell script to setup the environment for the App and install all the required dependencies
# You only need to run this script once.
# Requires Python3.6 or higher installed in the system

python3 -m pip install --user virtualenv
python3 -m venv venv
source venv/bin/activate && pip install -r requirements.txt
