#!/usr/bin/env python3
import json

with open('flatpak-db.json') as fp:
	db = json.load(fp)
	print(db.keys())

