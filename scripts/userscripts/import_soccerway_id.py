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

def searchPlayer(player_name=''):
	if player_name:
		player_name = player_name.replace(' ', '+')
		searchitemurl = 'https://int.soccerway.com/search/players/?q=%s' % (player_name)
		raw = base.getURL(searchitemurl)
		# print(raw)
		players = re.findall(r'<td class="player"><a href="[\/\-\w]*" class="[\_\s\/\-\w]*">.*</a></td>', raw, re.IGNORECASE)
		names = re.findall(r'<td class="player"><a href="[\/\-\w]*" class="[\_\s\/\-\w]*">(.*)</a></td>', raw, re.IGNORECASE)
		# print(names)
		# print(players)

		player_name = player_name.replace('+', ' ')
		i = 0
		for name in names:
			flag = 'y'
			name = unidecode(name).split()
			# print(name)
			name_parts = player_name.split()
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
	if player_name:
		text = ''
		text = searchPlayer(player_name=player_name)

		if text:
			soccerway_id = re.findall(r'<td class="player"><a href="/players/([\/\-\w]*)" class="[\_\s\/\-\w]*">.*</a></td>', text, re.IGNORECASE)
			soccerway_id = soccerway_id[0].strip('/')
			return soccerway_id

		else:
			print('No player was found on the official site.\n')
			return ''

	else:
		print('No player name is given.\n')
		return ''

	return ''

def checkAuthenticity(page='', soccerway_id=''):
	if page and soccerway_id:
		first_name = ''
		last_name = ''

		searchitemurl = 'https://int.soccerway.com/players/%s' % (soccerway_id)
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

def addSoccerwayId(repo='', wikisite='', item='', page='', lang=''):
	print('\n')

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
			item = pywikibot.ItemPage.fromPage(page)
		except:
			pass

		# player_name = unidecode('Andrey Soto')
		# # print(player_name)
		# print(getId(player_name=player_name))
		# # print(checkAuthenticity(page=page, soccerway_id='-/449795/'))
		# break

		# print(findId(page))
		# print('\n')

		soccerway_id = ''
		if item:
			if (datetime.datetime.now()-item.editTime()).seconds < 120:
				print('... but is being edited')
			else:
				soccerway_id = findId(page=page)
				soccerway_id = unidecode(soccerway_id)
				if soccerway_id:
					if not checkAuthenticity(page=page, soccerway_id=soccerway_id):
						print('Incorrect Soccerway ID provided in the article. Getting ID from site...\n')
						soccerway_id = getId(unidecode(page.title()))
				else:
					soccerway_id = getId(unidecode(page.title()))

				print(soccerway_id)
				addSoccerwayId(repo=repo, wikisite=enwiki, item=item, page=page, lang=lang)

		if i < 100:
			i += 1
		else:
			break

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
