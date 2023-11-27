#!/bin/sh

sudo apt-get update
sudo apt-get install -y python3-pip libpython3.8

# upgrade pip
python3.8 -m pip install --upgrade pip

# install dependencies
python3.8 -m pip install -r requirements.txt
