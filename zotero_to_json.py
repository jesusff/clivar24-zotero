import json
from datetime import datetime
from pyzotero import zotero

group_id = '5149914'
api_key = 'ca9nfF3QebWRnCOu2yx39luQ'

zot = zotero.Zotero(group_id, 'group', api_key)
all_items = zot.everything(zot.items())
all_collections = zot.everything(zot.collections())
current_date = datetime.now().strftime('%Y%m%d_%H%M')
output_file = f'{all_items[0]["library"]["name"]}_{current_date}.json'

dump_data = {'items': all_items, 'collections': all_collections}
with open(output_file, 'w') as json_file:
    json.dump(dump_data, json_file, indent=2)

print(f"All items and collections dumped to {output_file}")
