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

def get_datetime(datestr, end=False):
    datelst = [int(x) for x in datestr.split('/')]
    datedef = [0, 1, 1] if not end else [0, 12, 31]
    for ii, val in enumerate(datedef):
      if len(datelst) <= ii:
        datelst.append(datedef[ii])
    return(datetime(*datelst))

def parse_period(period):
    if '-' in period:
        start, end = period.split('-')
        return get_datetime(start), get_datetime(end, end=True)
    else:
        return get_datetime(period), get_datetime(period, end=True)

def is_valid(per):
    [y1, y2] = per.split('-')
    length = int(y2)-int(y1)+1
    return(10 <= length <= 50)

if __name__ == '__main__':
    top_collection_name = '3_Variables'
    cachefile = 'periods.json'
    
    if os.path.exists(cachefile):
        with open(cachefile, "r") as file:
            data = json.load(file)
    else:
        zot = zotero.Zotero(group_id, 'group', api_key)
        all_collections = zot.everything(zot.collections())
        collection_map = dict([(coll['data']['key'], coll['data']['name']) for coll in all_collections])
        top_collection_key = collection_keys[top_collection_name]
        target_keys = set(get_all_subcollection_keys(top_collection_key))
        with open(sys.argv[1], "r") as file:
            all_items = json.load(file)
        data = {}
        for item in all_items['items']:
            if 'parentItem' in item['data']:
                continue # note or attachment
            if not set(item['data']['collections']) & target_keys:
                continue # item not in target collection set
            name = f'{get_first_author(item)}, {item["data"]["date"][0:4]}' 
            while name in data:
                name = name + 'i'
            data[name] = pertags(item)
        with open(cachefile, "w") as file:
            json.dump(data, file)
    
    # Counting the frequency of each period
    period_counts = Counter()
    for periods in data.values():
        for period in periods:
            if '-' in period:  # Only consider periods with a dash (no GWL)
                period_counts[period] += 1
    
    # Sorting the periods by start year and then by length (descending)
    sorted_periods = sorted(
        set(period_counts.keys()),
        key = lambda x: (int(x.split('-')[0]), -int(x.split('-')[1]))
    )
    
    plot_data = [(period, period_counts[period]) for period in sorted_periods if is_valid(period)]
    
    # Plotting
    fig, ax = plt.subplots()
    max_count = max(period_counts.values())
    yticklabels = []
    for idx, (period, count) in enumerate(plot_data):
        color_intensity = 1 - (0.2 + 0.8 *count / max_count)
        ax.plot(parse_period(period), [idx, idx], color=(color_intensity, color_intensity, color_intensity))
        yticklabels.append(f'{period} ({count})')
    
    ax.set_yticks(range(len(plot_data)))
    ax.set_yticklabels(yticklabels)
    ax.invert_yaxis()  # Invert y-axis to display the earliest period at the top
    
    ax.xaxis_date()
    ax.set_xlim([datetime(1950, 1, 1), datetime(2102, 1, 1)])
    ax.xaxis.set_major_locator(mdates.YearLocator(10))  # Every 10 years
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    plt.show()
    
