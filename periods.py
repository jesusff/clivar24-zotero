#!/usr/bin/env python
# coding: utf-8

import json
import math
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys
from collections import Counter
from common import *
from datetime import datetime
from pyzotero import zotero

top_collection_name = '3_Variables'
cachefile = 'periods.json'

zot = zotero.Zotero(group_id, 'group', api_key)
all_collections = zot.everything(zot.collections())
collection_map = dict([(coll['data']['key'], coll['data']['name']) for coll in all_collections])

def get_subcollection_keys(collection_key):
    subcollection_keys = [collection_key]
    subcollection_keys.extend([x['key'] for x in all_collections if x['data']['parentCollection'] == collection_key])
    return subcollection_keys

def get_all_subcollection_keys(collection_key):
    def recurse(key, descendants):
        for item in all_collections:
            if item['data'].get('parentCollection') == key:
                descendants.append(item['key'])
                recurse(item['key'], descendants)
        return descendants
    return recurse(collection_key, [collection_key])

def pertags(item):
    tags = item['data']['tags']
    rval = []
    for tag in tags:
        if tag['tag'].startswith("#PER"):
            rval.append(tag['tag'].split('/')[1].strip())
    return(rval)

def parse_period(period):
    if '-' in period:
        start, end = period.split('-')
        return datetime(int(start), 1, 1), datetime(int(end), 12, 31)
    else:
        year = int(period)
        return datetime(year, 1, 1), datetime(year, 12, 31)

if os.path.exists(cachefile):
    with open(cachefile, "r") as file:
        data = json.load(file)
else:
    top_collection_key = collection_keys[top_collection_name]
    target_keys = get_all_subcollection_keys(top_collection_key)
    data = {}
    for key in target_keys:
        name = collection_map[key]
        items = zot.collection_items(key)
        data[name] = []
        for item in items:
            # Check if the entry has a parent item (i.e., it's not a note or attachment)
            if 'parentItem' in item['data']:
                continue
            data[name].extend(pertags(item))
    with open(cachefile, "w") as file:
        json.dump(data, file)

# Counting the frequency of each period
period_counts = Counter()
for periods in data.values():
    for period in periods:
        if '-' in period:  # Only consider periods with a dash
            period_counts[period] += 1

# Sorting the periods by start year and then by length (descending)
sorted_periods = sorted(set(period_counts.keys()), key=lambda x: (datetime.strptime(x.split('-')[0], '%Y'), 
                                                                 -(datetime.strptime(x.split('-')[1], '%Y') - datetime.strptime(x.split('-')[0], '%Y'))))

# Preparing the data for plotting
plot_data = [(parse_period(period), period_counts[period]) for period in sorted_periods]

# Plotting
fig, ax = plt.subplots()
max_count = max(period_counts.values())
yticklabels = []
for idx, ((start, end), count) in enumerate(plot_data):
    print(((start, end), count))
    color_intensity = 1 - (0.2 + 0.8 *count / max_count)
    ax.plot([start, end], [idx, idx], color=(color_intensity, color_intensity, color_intensity))
    yticklabels.append(f'{sorted_periods[idx]} ({count})')

# Setting the y-axis
ax.set_yticks(range(len(plot_data)))
ax.set_yticklabels(yticklabels)
ax.invert_yaxis()  # Invert y-axis to display the earliest period at the top

# Setting the x-axis
ax.xaxis_date()
ax.set_xlim([datetime(1940, 1, 1), datetime(2101, 1, 1)])
ax.xaxis.set_major_locator(mdates.YearLocator(10))  # Every 10 years
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

plt.show()

