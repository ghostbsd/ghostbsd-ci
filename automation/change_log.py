#!/usr/bin/env python
"""Generate HTML and Markdown changelogs from GitHub project data."""

import sys
import os
import requests

# GitHub GraphQL endpoint
API_URL = "https://api.github.com/graphql"

# Get token from environment
token = os.getenv("GITHUB_TOKEN")
if not token:
    print("Set GITHUB_TOKEN environment variable")
    sys.exit(1)

# Headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "GraphQL-Features": "issue_types"
}

# Simple GraphQL query without nested nodes
QUERY = """
query($cursor: String) {
  organization(login: "ghostbsd") {
    projectV2(number: 4) {
      items(first: 100, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          content {
            ... on Issue {
              number
              title
              url
              author {
                login
              }
              issueType {
                id
                name
              }
              assignees(first: 10) {
                nodes {
                  login
                  name
                }
              }
              labels(first: 10) {
                nodes {
                  name
                }
              }
              repository {
                nameWithOwner
              }
            }
            ... on PullRequest {
              number
              title
              url
              author {
                login
              }
              assignees(first: 10) {
                nodes {
                  login
                  name
                }
              }
              labels(first: 10) {
                nodes {
                  name
                }
              }
              repository {
                nameWithOwner
              }
            }
          }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
              ... on ProjectV2ItemFieldIterationValue {
                title
                field {
                  ... on ProjectV2FieldCommon {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

# Fetch all pages
all_items = []
CURSOR = None

while True:
    variables = {"cursor": CURSOR}
    response = requests.post(API_URL, json={"query": QUERY, "variables": variables}, headers=headers, timeout=30)
    data = response.json()

    if "errors" in data:
        print("Errors:", data["errors"])
        break

    items_data = data["data"]["organization"]["projectV2"]["items"]
    items = items_data["nodes"]
    all_items.extend(items)

    # Check if there are more pages
    if not items_data["pageInfo"]["hasNextPage"]:
        break

    CURSOR = items_data["pageInfo"]["endCursor"]

print(f"Found {len(all_items)} total items")


def get_field_value(project_item, field_name):
    """Get project field value by name"""
    for node in project_item["fieldValues"]["nodes"]:
        if node.get("field", {}).get("name") == field_name:
            return node.get("name") or node.get("title") or node.get("text")
    return None


def get_issue_type(project_item):
    """Get issue type from either issueType or project fields"""
    if project_item.get("content", {}).get("issueType"):
        return project_item["content"]["issueType"]["name"]
    return get_field_value(project_item, "Issue Type")


def build_item_line(project_item):
    """Build HTML line for changelog item"""
    content = project_item["content"]
    url = content["url"]
    repository = content["repository"]["nameWithOwner"]
    number = content["number"]
    title = content["title"]
    return f'<a href="{url}">{repository}#{number}</a> {title}'


def build_item_line_md(project_item):
    """Build Markdown line for changelog item"""
    content = project_item["content"]
    url = content["url"]
    repository = content["repository"]["nameWithOwner"]
    number = content["number"]
    title = content["title"]
    return f'[{repository}#{number}]({url}) {title}'


def categorize_item(type_name):
    """Determine which changelog section an item belongs to"""
    if type_name in ['Bug']:
        return 'Bug'
    if type_name in ['Security']:
        return 'Security'
    if type_name in ['Epic']:
        return 'Epic'
    return 'Feature'


RELEASE = '26.01-R15.0p2'

EPIC = '<h3>Epics</h3>\n<ul>\n'
FEATURE = '<h3>Enhancement, Improvements and New Features</h3>\n<ul>\n'
BUG = '<h3>Bug Fixes</h3>\n<ul>\n'
SECURITY = '<h3>Security Fixes</h3>\n<ul>\n'

EPIC_MD = '### Epics\n\n'
FEATURE_MD = '### Enhancement, Improvements and New Features\n\n'
BUG_MD = '### Bug Fixes\n\n'
SECURITY_MD = '### Security Fixes\n\n'

DO_NOT_LIST = {'ericbsd'}

ISSUE_AUTHORS = set()
PR_AUTHORS = set()

# Process all items
for item in all_items:
    # Skip items without content
    if not item.get("content"):
        continue

    # Check if item is for target release
    release_field = get_field_value(item, "Release")
    if release_field != RELEASE:
        continue

    # Collect author by type
    AUTHOR = item["content"].get("author", {})
    if AUTHOR and AUTHOR.get("login") and AUTHOR["login"] not in DO_NOT_LIST:
        if "issueType" in item["content"]:
            ISSUE_AUTHORS.add(AUTHOR["login"])
        else:
            PR_AUTHORS.add(AUTHOR["login"])

    # Build the changelog lines
    LINE = build_item_line(item)
    LINE_MD = build_item_line_md(item)

    # Get issue type and determine item type (Issue/PR)
    ISSUE_TYPE = get_issue_type(item)
    ITEM_TYPE = "Issue" if "issueType" in item["content"] else "PR"

    # Categorize and add to appropriate section
    CATEGORY = categorize_item(ISSUE_TYPE)

    if CATEGORY == 'Bug':
        BUG += f'<li>\n{ITEM_TYPE}: {LINE}\n</li>\n'
        BUG_MD += f'- {ITEM_TYPE}: {LINE_MD}\n'
    elif CATEGORY == 'Security':
        SECURITY += f'<li>\n{ITEM_TYPE}: {LINE}\n</li>\n'
        SECURITY_MD += f'- {ITEM_TYPE}: {LINE_MD}\n'
    elif CATEGORY == 'Epic':
        EPIC += f'<li>\n{ITEM_TYPE}: {LINE}\n</li>\n'
        EPIC_MD += f'- {ITEM_TYPE}: {LINE_MD}\n'
    else:  # Feature
        FEATURE += f'<li>\n{ITEM_TYPE}: {LINE}\n</li>\n'
        FEATURE_MD += f'- {ITEM_TYPE}: {LINE_MD}\n'

EPIC += '</ul>\n'
FEATURE += '</ul>\n'
BUG += '</ul>\n'
SECURITY += '</ul>\n'

with open('change-log.html', 'w', encoding='utf-8') as file:
    file.writelines(f'<h2>{RELEASE} Changelog</h2>\n')
    file.writelines(EPIC)
    file.writelines(FEATURE)
    file.writelines(BUG)
    file.writelines(SECURITY)

with open('change-log.md', 'w', encoding='utf-8') as file:
    file.write(f'## {RELEASE} Changelog\n\n')
    file.write(EPIC_MD + '\n')
    file.write(FEATURE_MD + '\n')
    file.write(BUG_MD + '\n')
    file.write(SECURITY_MD + '\n')

ISSUE_LIST = ", ".join(sorted(ISSUE_AUTHORS))
PR_LIST = ", ".join(sorted(PR_AUTHORS))

with open('contributors.html', 'w', encoding='utf-8') as file:
    file.write(f'<p>Thanks to (Github users): {ISSUE_LIST} for reporting issues.</p>\n')
    file.write(f'<p>Thanks to (Github users): {PR_LIST} for contributing.</p>\n')
