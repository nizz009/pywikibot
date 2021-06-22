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

prop_id = 'P597'

def searchPlayer(player_name=''):
	""" Searches for the player in the official site """

	if player_name:
		name_parts = re.split(r'\s|\-', player_name)

		searchitemurl = 'http://www.wtatennis.com/search?term=%s' % (name_parts[0])
		raw = base.getURL(searchitemurl)
		print(raw)
		players = re.findall(r'<a class="match-table">', raw, re.IGNORECASE)
		names = re.findall(r'<a class="match-table__player match-table__player--link" title="([\s\w])" href="[\/\-\w]">', raw, re.IGNORECASE)
		print(names)
		print(players)

		i = 0
		for name in names:
			flag = 'y'
			name = unidecode(name)
			name = re.split(r'\s|\-', name)
			# print(name)
			# print(name_parts)

			for name_part in name_parts:
				name_part = unidecode(name_part)
				if name_part != 'career' or name_part != 'statistics' or '(' not in name_part or not name_part.isnumeric():
					if name_part not in name:
						flag = 'n'
						break

			if flag == 'n':
				i += 1
				continue

			text = players[i]
			return text

	return ''

def getId(player_name=''):
	""" Gets the player ID from the official site """

	if player_name:
		text = ''
		text = searchPlayer(player_name=player_name)

		if text:
			wta_id = re.findall(r'<td class="player"><a href="/players/([\/\-\w]*)" class="[\_\s\/\-\w]*">.*</a></td>', text, re.IGNORECASE)
			wta_id = wta_id[0].strip('/')
			return wta_id

		else:
			print('No player was found on the official site.\n')
			return ''

	else:
		print('No player name is given.\n')
		return ''

	return ''

def checkAuthenticity(page='', wta_id=''):
	""" 
	Checks the correctness of the ID in Wp article and official site 

	@param page: Wikipedia page
	@param wta_id: ID retrieved from Wp article

	"""
	if page and wta_id:
		first_name = ''
		last_name = ''

		searchitemurl = 'https://int.wta.com/players/%s' % (wta_id)
		raw = base.getURL(searchitemurl)
		first_name = re.findall(r'<dd data-first_name="first_name">(.*)</dd>', raw, re.IGNORECASE)
		last_name = re.findall(r'<dd data-last_name="last_name">(.*)</dd>', raw, re.IGNORECASE)
		
		if first_name and last_name:
			first_name = unidecode(first_name[0]).split()
			last_name = unidecode(last_name[0]).split()

			# print(first_name)
			# print(last_name)

			name_parts = (page.title()).split()

			count = 0
			for name_part in name_parts:
				name_part = unidecode(name_part)
				if name_part != 'career' or name_part != 'statistics' or '(' not in name_part or not name_part.isnumeric():
					if name_part in first_name or name_part in last_name:
						count += 1

			if count >= (len(name_parts)/2):
				return True
			else:
				return False

	else:
		print('Inadequate information provided.\n')
		return False

def addWtaId(repo='', item='', lang='', wta_id=''):
	""" Adds the ID in Wikidata """

	# item_1 = base.WdPage(wd_value='Q4115189')
	# item_1.printWdContents()
	item.addIdentifiers(prop_id=prop_id, prop_value=wta_id)

def findId(page=''):
	""" Finds the ID in Wp page """
	if page:
		m = re.findall(r'{{WTA\s*\|(\d+\/[A-Za-zÀ-ÖØ-öø-ÿ\-]+)', page.text, re.IGNORECASE)
		if m:
			return m[0]
		m = re.findall(r'{{WTA\s*\|id=(\d+\/[A-Za-zÀ-ÖØ-öø-ÿ\-]+)', page.text, re.IGNORECASE)
		if m:
			return m[0]
	else:
		print('Error in retrieving information from article.\n')
	return ''

def main():
	category = 'WTA template with ID not in Wikidata'
	lang = 'en'

	cat = pywikibot.Category(pywikibot.Link(category, source=enwiki, default_namespace=14))
	gen = pagegenerators.CategorizedPageGenerator(cat)
	pre = pagegenerators.PreloadingGenerator(gen)

	# searchitemurl = 'https://www.wtatennis.com/search?term=Nora%20Baj%C4%8D%C3%ADkov%C3%A1'
	# raw = base.getURL(searchitemurl)
	# print(raw)

	# looping through pages of articles
	i = 0
	for page in pre:
		# if page.title() == 'Amine Abbès':
		print(page.title())
		# print(page.text)

		item = ''
		try:
			item = base.WdPage(page_name=page.title())
		except:
			pass

		player_name = unidecode('Amélie Mauresmo')
		# print(player_name)
		print(searchPlayer(player_name=player_name))
		# print(checkAuthenticity(page=page, wta_id='-/449795/'))
		break

		# print(findId(page))
		# print('\n')

		wta_id = findId(page=page)
		wta_id = unidecode(wta_id)
		if item:
			if wta_id:
				if not checkAuthenticity(page=page, wta_id=wta_id):
					print('Incorrect WTA ID provided in the article. Getting ID from site...\n')
					wta_id = getId(unidecode(page.title()))
			else:
				wta_id = getId(unidecode(page.title()))

			print(wta_id)
			addWtaId(repo=repo, item=item, lang=lang, wta_id=wta_id)

		if i < 1:
			i += 1
		else:
			break

		# else:
		# 	# if no item exists, search for a valid item
		# 	page_title = page.title()
		# 	page_title_ = page_title.split('(')[0].strip()
		# 	searchitemurl = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=en&format=xml' % (urllib.parse.quote(page_title_))
		# 	raw = base.getURL(searchitemurl)
			
		# 	# check for valid search result
		# 	if not '<search />' in raw:
		# 		m = re.findall(r'id="(Q\d+)"', raw)

		# 		for itemfoundq in m:
		# 			itemfound = pywikibot.ItemPage(repo, itemfoundq)
		# 			item_dict = itemfound.get()

		# 			if page.title() == item_dict['labels']['en']:
		# 				if wta_id:
		# 					if not checkAuthenticity(page=page, wta_id=wta_id):
		# 						print('Incorrect WTA ID provided in the article. Getting ID from site...\n')
		# 						wta_id = getId(unidecode(page.title()))
		# 				else:
		# 					wta_id = getId(unidecode(page.title()))

		# 				print(wta_id)
		# 				addWtaId(repo=repo, item=item, lang=lang, wta_id=wta_id)

		# 				# Touch the page to force an update
		# 				try:
		# 					page.touch()
		# 				except:
		# 					null = 0
		# 				break
	return 0

if __name__ == "__main__":
	main()
