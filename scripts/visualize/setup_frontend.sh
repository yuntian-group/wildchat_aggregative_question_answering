#!/bin/bash
START_DIR=$(pwd)   # remember where you started
source init.sh
cd data_visualize/frontend
npm install .
cd "$START_DIR"