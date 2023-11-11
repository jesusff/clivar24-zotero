#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from datetime import datetime
from pyzotero import zotero

group_id = '5149914'
api_key = 'ca9nfF3QebWRnCOu2yx39luQ'

zot = zotero.Zotero(group_id, 'group', api_key)
current_date = datetime.now().strftime('%Y-%m-%d %H:%M')

collection_keys = {
    'temperature' : 'T7N74W2T',
    'precipitation' : 'B4JY8RHB',
    'circulation' : '9342658V',
    'wind' : 'YAAWRDMV',
    'multi-variable-indices' : 'LVC9385S',
    'other-variables' : 'N5I79E23',
}

all_collections = zot.everything(zot.collections())
#collection_keys = dict([(coll['data']['name'], coll['data']['key']) for coll in all_collections])

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
    for subcollection in subcollections:
        subcollection_keys.extend(get_subcollection_keys(zot, subcollection['key']))
    return subcollection_keys

def get_first_author(item):
    if 'creatorSummary' in item['meta']:
        first_author = item['meta']['creatorSummary']
    else:
        first_author = ''
        creators = item['data'].get('creators', [])
        for creator in creators:
            if creator.get('name'):
                first_author = creator['name'].split(',')[0]
                break
            elif creator.get('lastName'):
                first_author = creator['lastName']
                break
    return(first_author)

for collection in collection_keys.keys():
    print(f'Processing {collection} ...')
    items = []
    for collection_key in get_subcollection_keys(zot, collection_keys[collection]):
        items.extend(zot.collection_items(collection_key))
    data = []
    for item in items:
        # Check if the entry has a parent item (i.e., it's not a note or attachment)
        if 'parentItem' in item['data']:
            continue
        tags = item['data']['tags']
        first_author = get_first_author(item)
        year = item['data']['date']

        # Categorize the item by its tags
        for tag in tags:
            if tag['tag'].startswith("#"):
                tag_parts = tag['tag'][1:].split('/')
                category = tag_parts[0].strip()
                subcategory = tag_parts[1].strip() if len(tag_parts) > 1 else ''
                auth = first_author if first_author else ''
                yr = year[0:4] if year else ''
                data.append({
                    'Category': category,
                    'Subcategory': subcategory,
                    'Key': f'{auth} et al. ({yr})'
                })

    df = pd.DataFrame(data)

    df['Subcategory'] = df['Subcategory'].map(subcategory_mapping).fillna(df['Subcategory'])
    df_grouped = df.groupby(['Category', 'Subcategory']).agg(lambda x: '<br>'.join(list(set(x))))
    with open(f'tag-table-{collection}.html', 'w') as html_file:
        html_file.write(f'''
<html>
<head>
<style> 
  table, th, td {{font-size:10pt; border:1px solid black; border-collapse:collapse; text-align:left;}}
  th, td {{padding: 5px; min-width: 160px}}
</style>
</head>
<body>
{
    df_grouped.to_html(escape=False)
}
</body>
</html>'''
)

    subcats = sorted(list(set(list(df[df['Category'] == 'SCEN']['Subcategory']))))
    data2 = []
    for subcat in subcats:
        subcatkeys = df[df['Subcategory'] == subcat]['Key']
        data2.append(df[df['Key'].isin(subcatkeys)].groupby(['Category', 'Subcategory']).agg(lambda x: '<br>'.join(sorted(list(set(x))))))
    df2 = pd.concat(data2, axis = 1).fillna('')
    df2.columns = subcats
    with open(f'tag-table-{collection}-by-scenario.html', 'w') as html_file:
        html_file.write(f'''
<html>
<head>
<style> 
  table, th, td {{font-size:10pt; border:1px solid black; border-collapse:collapse; text-align:left;}}
  th, td {{padding: 5px; min-width: 160px}}
</style>
</head>
<body>
<h1>CLIVAR 2024. Chapter 5 reference tag table</h1>
({current_date})
{
  df2.to_html(escape=False)
}
</body>
</html>'''
)
