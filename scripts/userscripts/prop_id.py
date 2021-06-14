import re

import pywikibot
from pywikibot import pagegenerators


enwd = pywikibot.Site('wikidata', 'wikidata')
page_name = 'Wikidata:Database reports/List of properties/all'
page = pywikibot.Page(enwd, page_name)
# print(page.text)

page_rows = page.text.split('\n|')
prop_list = set()
for row in page_rows:
	if '[[Property:' in row:
		prop_list.add(row)

print(prop_list)

# def prop_id(prop_name=''):