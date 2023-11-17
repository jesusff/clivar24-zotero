#!/usr/bin/env python
# coding: utf-8

import os
from datetime import datetime
from pyzotero import zotero

def get_top_level_items(zot, collection_key):
    items = zot.collection_items(collection_key)
    top_level_items = [item for item in items if 'parentItem' not in item['data']]
    return top_level_items

def get_notes(zot, collection_key):
    items = zot.collection_items(collection_key)
    notes = [item for item in items if item['data']['itemType'] == 'note' and 'parentItem' in item['data']]
    return notes

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
    
def extract_tags_and_notes(zot, item, notes_data):
    item_data = item['data']
    title = item_data.get('title', 'N/A')
    first_author = get_first_author(item)
    year = item_data.get('date', 'N/A')
    year = year.split('-')[0] if '-' in year else year
    tags = [tag['tag'] for tag in item_data.get('tags', []) if tag['tag'].startswith("#")]
    collections = [coll for coll in item_data.get('collections', [])]
    collections = sorted(list(map(collection_map.get, collections)))
    notes = []
    for note_data in notes_data:
        # Check if the note corresponds to the current top-level item
        if note_data['data']['parentItem'] == item_data['key']:
            notes.append(('Literal messages', note_data['data']['note']))
    return {
        'Title': title,
        'First Author': first_author,
        'Year': year,
        'Tags': tags,
        'Collections' : collections,
        'Notes': notes}

def html_header():
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    return(f'''<html>
<head>
<style> 
  table, th, td {{font-size:10pt; border:1px solid black; border-collapse:collapse; text-align:left;}}
  th, td {{padding: 5px; vertical-align: top;}}
  h2 {{ padding-top: 20px; padding-bottom: 0px; }}
</style>
</head>
<body>
<h1>CLIVAR 2024. Chapter 5 references</h1>
({current_date})
''' )

def html_footer():
    return(f'''
</body>
</html>
''' )

def generate_html_table(report_data, collection):
    html_table = f"""
<h2>{collection}</h2>
<table>"""
    for item_data in report_data:
        # Multicolumn entry for author, year, and title
        html_table += (
            f"<tr><td colspan='2' style='border-left: 1px solid white; border-right: 1px solid white; padding-top: 15px;'><b>{item_data['First Author']} ({item_data['Year']})</b> {item_data['Title']}</td></tr>"
        )
        # Tags row
        html_table += f"<tr><td>Tags</td><td>{', '.join(item_data['Tags'])}</td></tr>"
        # Collections row
        html_table += f"<tr><td>Collections</td><td>{', '.join(item_data['Collections'])}</td></tr>"
        # Notes rows
        for note_type, note_content in item_data['Notes']:
            html_table += f"<tr><td>{note_type}</td><td>{note_content}</td></tr>"
    html_table += "</table></body></html>"
    return html_table

group_id = '5149914'
api_key = 'ca9nfF3QebWRnCOu2yx39luQ'
collections = {
    'temperature' : 'T7N74W2T',
    'precipitation' : 'B4JY8RHB',
    'circulation' : '9342658V',
    'wind' : 'YAAWRDMV',
    'moisture' : 'VEGUIVI9'
    'multi-variable-indices' : 'LVC9385S',
    'other-variables' : 'N5I79E23',
}    

zot = zotero.Zotero(group_id, 'group', api_key)
all_collections = zot.everything(zot.collections())
collection_map = dict([(coll['data']['key'], coll['data']['name']) for coll in all_collections])

for collection_name, collection_key in collections.items():
  
    report_filename = f'report-{collection_name}.html'
    if os.path.exists(report_filename):
        print(f'{report_filename} exists. Skipping ...')
        continue

    top_level_items = get_top_level_items(zot, collection_key)
    notes = get_notes(zot, collection_key)
    report_data = [extract_tags_and_notes(zot, item, notes) for item in top_level_items]
    report_data = sorted(report_data, key=lambda x: (x['First Author'].lower(), x['Year']))
    html_table = generate_html_table(report_data, collection_name)
    html_file = open(report_filename, 'w')
    html_file.write(html_header())
    html_file.write(html_table)
        
    subcollections = [collection for collection in all_collections if collection['data']['parentCollection'] == collection_key]
    for subcollection in subcollections:
        subcollection_key = subcollection['data']['key']
        subcollection_name = subcollection['data']['name']

        top_level_items = get_top_level_items(zot, subcollection_key)
        notes = get_notes(zot, subcollection_key)
        report_data = [extract_tags_and_notes(zot, item, notes) for item in top_level_items]
        report_data = sorted(report_data, key=lambda x: (x['First Author'].lower(), x['Year']))
        html_table = generate_html_table(report_data, f'{collection_name}/{subcollection_name}')
        html_file.write(html_table)
    html_file.write(html_footer())
    html_file.close()
    print(f"Report for {collection_name} saved to {report_filename}")

