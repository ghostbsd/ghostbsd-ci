#!/usr/bin/env python

import json
import re
import requests

issues_completed_url = 'https://github.com/orgs/ghostbsd/projects/4/views/17'

raw_page = requests.get(issues_completed_url).text

# search = '<script type="application/json" id="memex-items-data">'
items_pattern = r'<script type="application/json" id="memex-items-data">(.*?)</script>'
columns_pattern = r'<script type="application/json" id="memex-columns-data">(.*?)</script>'

# issues_text = re.search(rf'(.*?{search}.*?)\n', raw_page).group(1)

columns_text = re.search(columns_pattern, raw_page).group(1)
columns_data = json.loads(columns_text)

items_text = re.search(items_pattern, raw_page).group(1)
items_data = json.loads(items_text)

#issues = json.loads(issues_text.replace(search, '').replace('</script>', ''))

Epic = '<h3>Epics</h3>\n<ul>\n'
Feature = '<h3>Enhancement, Improvements and New Features</h3>\n<ul>\n'
Bug = '<h3>Bug Fixes</h3>\n<ul>\n'
Security = '<h3>Security Fixes</h3>\n<ul>\n'

for column in columns_data:
    if column['name'] == 'Release':
        print(column['name'])
        print(column['id']) # 58331422
        # print(json.dumps(column, indent=4))
        # exit()
        for obj in column['settings']['configuration']['iterations']:
            print(obj['id'], ': ', obj['title'])

for items in items_data:
    print(json.dumps(items, indent=4))
    exit()
    if issue['memexProjectColumnValues'][0]['value']['state'] in ['closed', 'merged']:
        # issues_completed.append(issue)
        # print(issue['contentType'])
        url = issue['content']['url']
        repository = issue['memexProjectColumnValues'][4]['value']['nameWithOwner']
        issue_number = issue['memexProjectColumnValues'][0]['value']['number']
        title = issue['memexProjectColumnValues'][0]['value']['title']['raw']
        line = f'<a href="{url}">{repository}#{issue_number}</a> {title}'
        if 'bug' in str(issue['memexProjectColumnValues'][3]):
            Bug += '<li>\n'
            Bug += f'{line}\n'
            Bug += '</li>\n'
        elif 'security' in str(issue['memexProjectColumnValues'][3]):
            Security += '<li>\n'
            Security += f'{line}\n'
            Security += '</li>\n'
        elif 'feature' in str(issue['memexProjectColumnValues'][3]):
            Feature += '<li>\n'
            Feature += f'{line}\n'
            Feature += '</li>\n'
        elif 'enhancement' in str(issue['memexProjectColumnValues'][3]):
            Feature += '<li>\n'
            Feature += f'{line}\n'
            Feature += '</li>\n'
        elif 'task' in str(issue['memexProjectColumnValues'][3]):
            Feature += '<li>\n'
            Feature += f'{line}\n'
            Feature += '</li>\n'
        elif 'epic' in str(issue['memexProjectColumnValues'][3]):
            Epic += '<li>\n'
            Epic += f'{line}\n'
            Epic += '</li>\n'


Epic += '</ul>\n'
Feature += '</ul>\n'
Bug += '</ul>\n'
Security += '</ul>\n'

file = open('change-log.html', 'w')
file.writelines('<h2>[version] Changelog<h2>\n')
file.writelines(Epic)
file.writelines(Feature)
file.writelines(Bug)
file.writelines(Security)
file.close()
