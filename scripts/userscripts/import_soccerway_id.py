import json
import os
import re
import sys
import _thread
import time
import unicodedata
import urllib
import urllib.request
import urllib.parse
import dateparser
import datetime
from unidecode import unidecode

import pywikibot
from pywikibot import pagegenerators
import base_ops as base

enwiki = pywikibot.Site('en', 'wikipedia')
enwd = pywikibot.Site('wikidata', 'wikidata')
repo = enwd.data_repository()

def getId(text=''):
	pass

def checkAuthenticity(page=''):
	pass

def addSoccerwayId(repo='', wikisite='', item='', page='', lang=''):
	pass

def findId(page=''):
	if page:
		m = re.findall(r'{{soccerway\s*\|([A-Za-zÀ-ÖØ-öø-ÿ\-]+\/\d+)', page.text, re.IGNORECASE)
		if m:
			return m[0]
		m = re.findall(r'{{soccerway\s*\|id=([A-Za-zÀ-ÖØ-öø-ÿ\-]+\/\d+)', page.text, re.IGNORECASE)
		if m:
			return m[0]
	else:
		print('Error in retrieving information from article.\n')
	return ''

def main():
	category = 'Soccerway template with ID not in Wikidata'
	lang = 'en'

	cat = pywikibot.Category(pywikibot.Link(category, source=enwiki, default_namespace=14))
	gen = pagegenerators.CategorizedPageGenerator(cat)
	pre = pagegenerators.PreloadingGenerator(gen)

	searchitemurl = 'https://www.wtatennis.com/players/20003/nora-bajchikova'
	raw = base.getURL(searchitemurl)
	print(raw)

	# looping through pages of articles
	# i = 0
	# for page in pre:
	# 	# if page.title() == 'Amine Abbès':
	# 	print(page.title())
	# 	# print(page.text)

	# 	item = ''
	# 	try:
	# 		item = pywikibot.ItemPage.fromPage(page)
	# 	except:
	# 		pass

	# 	# print(findId(page))
	# 	# print('\n')

	# 	soccerway_id = ''
	# 	if item:
	# 		if (datetime.datetime.now()-item.editTime()).seconds < 120:
	# 			print('... but is being edited')
	# 		else:
	# 			soccerway_id = findId(page=page)
	# 			if soccerway_id:
	# 				if checkAuthenticity(page=page):
	# 					addSoccerwayId(repo=repo, wikisite=enwiki, item=item, page=page, lang=lang)
	# 				else:
	# 					print('Incorrect Soccerway ID provided in the article. Getting ID from site...\n')
	# 					getId(unidecode(page.title()))
	# 			else:
	# 				getId(unidecode(page.title()))
		# if i < 100:
		# 	i += 1
		# else:
		# 	break

		# else:
		# 	# if no item exists, search for a valid item
		# 	page_title = page.title()
		# 	page_title_ = page_title.split('(')[0].strip()
		# 	searchitemurl = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=en&format=xml' % (urllib.parse.quote(page_title_))
		# 	raw = getURL(searchitemurl)
			
		# 	# check for valid search result
		# 	if not '<search />' in raw:
		# 		m = re.findall(r'id="(Q\d+)"', raw)

		# 		for itemfoundq in m:
		# 			itemfound = pywikibot.ItemPage(repo, itemfoundq)
		# 			item_dict = itemfound.get()

		# 			if page.title() == item_dict['labels']['en']:
		# 				if checkAuthenticity(page=page):
		# 					addSoccerwayId(repo=repo, wikisite=enwiki, item=item, page=page, lang=lang)
		# 				else:
		# 					print('Incorrect ATP ID provided.\n')
		# 					continue

		# 				# Touch the page to force an update
		# 				try:
		# 					page.touch()
		# 				except:
		# 					null = 0
		# 				break
	return 0

if __name__ == "__main__":
	main()
