#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
from pyzotero import zotero
from common import *

zot = zotero.Zotero(group_id, 'group', api_key)

all_collections = zot.everything(zot.collections())
collection_map = dict([(coll['data']['key'], coll['data']['name']) for coll in all_collections])

subcategory_mapping = {
    'rcp26':  'rcp26/ssp126',
    'ssp126': 'rcp26/ssp126',
    'rcp45':  'rcp45/ssp245',
    'ssp245': 'rcp45/ssp245',
    'rcp85':  'rcp85/ssp585',
    'ssp585': 'rcp85/ssp585',
    '2011-2040': 'near future',
    '2015-2040': 'near future',
    '2006-2040': 'near future',
    '2021-2040': 'near future',
    '2021-2050': 'near future',
    '2023-2037': 'near future',
    '2030-2059': 'mid future',
    '2031-2060': 'mid future',
    '2031-2065': 'mid future',
    '2041-2060': 'mid future',
    '2041-2060': 'mid future',
    '2041-2070': 'mid future',
    '2041-2080': 'mid future',
    '2043-2057': 'mid future',
    '2043-2057': 'mid future',
    '2046-2065': 'mid future',
    '2063-2077': 'mid future',
    '2066-2100': 'far future',
    '2070-2099': 'far future',
    '2071-2100': 'far future',
    '2080-2099': 'far future',
    '2081-2100': 'far future',
    '2083-2097': 'far future',
}

def get_subcollection_keys(zot, collection_key):
    subcollection_keys = [collection_key]
    subcollections = [collection for collection in all_collections if collection['data']['parentCollection'] == collection_key]
    subcollection_keys.extend([subcollection['key'] for subcollection in subcollections])
    return subcollection_keys

def taglist(item):
    tags = item['data']['tags']
    first_author = get_first_author(item)
    year = item['data']['date']
    rval = []
    # Categorize the item by its tags
    for tag in tags:
        if tag['tag'].startswith("#"):
            tag_parts = tag['tag'][1:].split('/')
            category = tag_parts[0].strip()
            subcategory = tag_parts[1].strip() if len(tag_parts) > 1 else ''
            auth = first_author if first_author else ''
            yr = year[0:4] if year else ''
            rval.append({
                'Category': category,
                'Subcategory': subcategory,
                'Key': f'{auth} ({yr})'
            })
    return(rval)

for collection in collection_filenames.keys():
    subcollection_keys = get_subcollection_keys(zot, collection_keys[collection])
    outfile = f'./{html_dir}/tag-table-{collection_filenames[collection]}.html'
    if os.path.exists(outfile):
      print(f'Skipping existing {collection} ...')
      continue
    print(f'Processing {collection} ...')
    banner = (
        '<p>' + '<a href="index.html">All reports</a> | ' +
        ' · '.join([f'<a href=#{plain_chars(collection_map[x])}>{collection_map[x]}</a>' for x in subcollection_keys])
    )
    html_file = open(outfile, 'w')
    html_file.write(html_header(title = 'CLIVAR 2024. Chapter 5 reference tag table'))
    html_file.write(banner)
    html_file2 = open(outfile.replace('.html', '-by-scenario.html'), 'w')
    html_file2.write(html_header(title = 'CLIVAR 2024. Chapter 5 reference tag table by scenario'))
    html_file2.write(banner)
    for key in subcollection_keys:
        items = zot.collection_items(key)
        name = collection_map[key]
        data = []
        for item in items:
            # Check if the entry has a parent item (i.e., it's not a note or attachment)
            if 'parentItem' in item['data']:
                continue
            data.extend(taglist(item))
        df = pd.DataFrame(data)
        html_file.write(f'<h2 id={plain_chars(name)}>{name} <a href="#top">^</a></h2>')
        if not 'Subcategory' in df:
            continue # No tags in this (sub) collection
        df['Subcategory'] = df['Subcategory'].map(subcategory_mapping).fillna(df['Subcategory'])
        df_grouped = df.groupby(['Category', 'Subcategory']).agg(lambda x: '<br>'.join(list(set(x))))
        html_file.write(df_grouped.to_html(escape=False))

        subcats = sorted(list(set(list(df[df['Category'] == 'SCEN']['Subcategory']))))
        data2 = []
        for subcat in subcats:
            subcatkeys = df[df['Subcategory'] == subcat]['Key']
            data2.append(df[df['Key'].isin(subcatkeys)].groupby(['Category', 'Subcategory']).agg(lambda x: '<br>'.join(sorted(list(set(x))))))
        html_file2.write(f'<h2 id={plain_chars(name)}>{name} <a href="#top">^</a></h2>')
        if not data2:
            continue
        df2 = pd.concat(data2, axis = 1).fillna('')
        df2.columns = subcats
        html_file2.write(df2.to_html(escape=False))

    html_file.write(html_footer())
    html_file.close()
    html_file2.write(html_footer())
    html_file2.close()
