import re

import pywikibot
from pywikibot import pagegenerators


enwd = pywikibot.Site('wikidata', 'wikidata')
page_name = 'Wikidata:Database reports/List of properties/all'
page = pywikibot.Page(enwd, page_name)
# print(page.text)


""" 
Class Property:
Elements:
- prop id
- data type : wikibase item, commons item, etc.

"""

class Property:

	def __init__(self, row=''):
		if row:
			element = row.split('||')
			self.prop_id = re.findall(r'\[\[Property:(P\d+)\|', row[0])
			self.data_type = re.findall(r'(.+)', row[4])

def searchProp(prop=''):
	page_rows = page.text.split('\n|')
	prop_list = set()
	for row in page_rows:
		if '[[Property:' in row and prop in row:
			prop_list.add(row)

	print(prop_list)

searchProp('birth date')

# def prop_id(prop_name=''):