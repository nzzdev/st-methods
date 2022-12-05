import json
import pandas as pd


def update_chart(id, title="", subtitle="", notes="", data=pd.DataFrame(), asset_groups=[], files=[]):  # Q helper function
    # read qConfig file
    json_file = open('./q.config.json')
    qConfig = json.load(json_file)

    # update chart properties
    for item in qConfig.get('items'):
        for environment in item.get('environments'):
            if environment.get('id') == id:
                if title != '':
                    item.get('item').update({'title': title})
                if subtitle != '':
                    item.get('item').update({'subtitle': subtitle})
                if notes != '':
                    item.get('item').update({'notes': notes})
                if data.size > 0:
                    # reset_index() and T (for transpose) are used to bring column names into the first row
                    transformed_data = data.applymap(str).reset_index(
                        drop=True).T.reset_index().T.apply(list, axis=1).to_list()
                    if 'table' in item.get('item').get('data'):
                        item.get('item').get('data').update(
                            {'table': transformed_data})
                    else:
                        item.get('item').update({'data': transformed_data})
                if len(asset_groups) > 0:
                    groups = []
                    for g in asset_groups:
                        groups.append({
                            'assets': [{"path": f} for f in g['files']],
                            'name': g['name']
                        })
                    item['item']['assetGroups'] = groups

                if len(files) > 0:
                    item['item']['files'] = files

                print('Successfully updated item with id', id,
                      'on', environment.get('name'), 'environment')

    # write qConfig file
    with open('./q.config.json', 'w', encoding='utf-8') as json_file:
        json.dump(qConfig, json_file, ensure_ascii=False,
                  indent=1, default=str)
    json_file.close()
