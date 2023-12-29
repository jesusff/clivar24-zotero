#!/usr/bin/env python
# coding: utf-8
from datetime import datetime

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

def html_header(title='CLIVAR 2024. Chapter 5'):
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    return(f'''<html>
<head>
<style> 
  table, th, td {{font-size:10pt; border:1px solid black; border-collapse:collapse; text-align:left;}}
  th, td {{padding: 5px; vertical-align: top;}}
  h2 {{ padding-top: 20px; padding-bottom: 0px; }}
  a {{ text-decoration: none; color: #3399ff;}}
</style>
</head>
<body>
<h1 id="top">{title}</h1>
({current_date})
''' )

def html_footer():
    return(f'''
</body>
</html>
''' )

def plain_chars(string):
  return(string
    .replace('/', '-')
    .replace(' ', '-')
    .replace('_', '-')
    .lower()
  )
    
group_id = '5149914'
api_key = 'ca9nfF3QebWRnCOu2yx39luQ'
collection_filenames = {
    '1_Temperature': 'temperature',
    '2_Precipitation': 'precipitation',
    '3_Wind': 'wind',
    '4_Circulation': 'circulation',
    '5_Moisture': 'moisture',
    '6_Radiation_and_clouds': 'radiation-clouds',
    '7_Multivariable_relationships_and_indices': 'multi-variable-indices',
    'Mountain': 'mountain',
    'Canary_islands': 'canaries',
}
html_dir = 'docs'

# from pyzotero import zotero
# from pprint import pprint
# zot = zotero.Zotero(group_id, 'group', api_key)
# all_collections = zot.everything(zot.collections())
# collection_keys = dict([(coll['data']['name'], coll['data']['key']) for coll in all_collections])
# pprint(collection_keys)

collection_keys = {
 '1_Introduction': 'XL7H6ZXC',
 '1_Temperature': 'T7N74W2T',
 '2_Data_and_methods': 'NDDCIJUY',
 '2_Precipitation': 'B4JY8RHB',
 '3_Variables': 'I558W5FS',
 '3_Wind': 'YAAWRDMV',
 '4_Circulation': '9342658V',
 '4_Regions': 'BULHQHCH',
 '5_Moisture': 'VEGUIVI9',
 '6_Radiation_and_clouds': 'N5I79E23',
 '7_Multivariable_relationships_and_indices': 'LVC9385S',
 'Aerosols': 'T7UIGVD2',
 'Agroclimatic indices': 'BBEYZLW9',
 'Balearic_islands': 'QNUWP2VQ',
 'Canary_islands': 'YISDMTJT',
 'Cities': 'H9US9FG2',
 'Clouds': 'D6PP8GPW',
 'Drought and aridity': '4BIIWSYU',
 'Fire risk': 'WLURSQSF',
 'Human comfort and heat stress': 'CFNNZXVV',
 'Large-scale modes': 'A5B8S5R3',
 'Mountain': 'ARYMAD6H',
 'Multivar relationships': 'IU3BA6T9',
 'Radiation': 'YQI3D6WT',
 'Renewable energies': 'WUIZHRXS',
 'Weather types': 'VGWLNMJV',
 'andres-new': 'VWA33YQV',
 'nuevos-angel': '66N93HFT'}

if __name__ == '__main__':
  fp = open(f'./{html_dir}/index.html', 'w')
  fp.write(f'''
<html>
<head>
<style> 
  table, th, td {{font-size:10pt; border:1px solid black; border-collapse:collapse; text-align:left;}}
  th, td {{padding: 5px;}}
</style>
</head>
<body>
<h1>CLIVAR 2024. Chapter 5 references</h1>
<table>
''')
  for title, fname in collection_filenames.items():
    fp.write(f'''
<tr>
<td>{title}</td>
<td><a href="report-{fname}.html">Report</a></td>
<td><a href="tag-table-{fname}.html">Tags</a></td>
<td><a href="tag-table-{fname}-by-scenario.html">Tags by scenario</a></td>
</tr>
''')

  fp.write(f'''
</table>
</body>
</html>
''')
