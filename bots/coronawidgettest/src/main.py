#!/usr/bin/env python
# coding: utf-8

from io import StringIO
import os
from helpers import *
from pathlib import Path

# Set Working Directory
os.chdir(os.path.dirname(__file__))

# Generate the file. Pure Magic! (Open it and save it again :-) Just to test github actions
with open(Path('../data/test.json'), 'r', encoding='utf-8') as f_read:
  with open(Path('../export/dashboard.json'), 'w', encoding='utf-8') as f_write:
    f_write.write(f_read.read())

# Get Data
chartid = 'e9046b127bd99afc9cd208b94d74a18f'
my_assets = [{
  "name": "jsonFiles",
  "files": ["./export/dashboard.json"]
}]

update_chart(
    id = chartid,
    asset_groups = my_assets
)
