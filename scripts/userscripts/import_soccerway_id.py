import json
import re
import urllib
import urllib.request
import urllib.parse
from unidecode import unidecode

import pywikibot
from pywikibot import pagegenerators
# link to base_ops: https://github.com/nizz009/pywikibot/blob/master/scripts/userscripts/base_ops.py
import base_ops as base

enwiki = pywikibot.Site('en', 'wikipedia')
enwd = pywikibot.Site('wikidata', 'wikidata')
repo = enwd.data_repository()

prop_id = 'P2369'

def searchPlayer(player_name=''):
	""" Searches for the player in the official site """

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
			name = unidecode(name)
			name = re.split(r'\s|\-', name)
			# print(name)
			name_parts = re.split(r'\s|\-', player_name)
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
	""" 
	Checks the correctness of the ID in Wp article 
	Compares the ID in Wp article with that in the official site 

	@param page: Wikipedia page
	@param soccerway_id: ID retrieved from Wp article

	"""
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

def addSoccerwayId(repo='', item='', lang='', soccerway_id=''):
	""" Adds the ID in Wikidata """

	# item_1 = base.WdPage(wd_value='Q4115189')
	# item_1.printWdContents()
	item.addIdentifiers(prop_id=prop_id, prop_value=soccerway_id)

def findId(page=''):
	""" Finds the ID in Wp page """
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

	# looping through pages of articles
	# i = 0
	for page in pre:

		print(page.title())

		item = ''
		try:
			item = base.WdPage(page_name=page.title())
		except:
			pass

		# print(findId(page))
		# print('\n')

		soccerway_id = findId(page=page)
		soccerway_id = unidecode(soccerway_id)
		if item:
			if soccerway_id:
				if not checkAuthenticity(page=page, soccerway_id=soccerway_id):
					print('Incorrect Soccerway ID provided in the article. Getting ID from site...\n')
					soccerway_id = getId(unidecode(page.title()))
			else:
				soccerway_id = getId(unidecode(page.title()))

			print(soccerway_id)
			# addSoccerwayId(repo=repo, item=item, lang=lang, soccerway_id=soccerway_id)

		else:
			# if no item exists, search for a valid item
			page_title = page.title()
			page_title_ = page_title.split('(')[0].strip()
			searchitemurl = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=en&format=xml' % (urllib.parse.quote(page_title_))
			raw = base.getURL(searchitemurl)
			
			# check for valid search result
			if not '<search />' in raw:
				m = re.findall(r'id="(Q\d+)"', raw)

				for itemfoundq in m:
					itemfound = pywikibot.ItemPage(repo, itemfoundq)
					item_dict = itemfound.get()

					if page.title() == item_dict['labels']['en']:
						if soccerway_id:
							if not checkAuthenticity(page=page, soccerway_id=soccerway_id):
								print('Incorrect Soccerway ID provided in the article. Getting ID from site...\n')
								soccerway_id = getId(unidecode(page.title()))
						else:
							soccerway_id = getId(unidecode(page.title()))

						print(soccerway_id)
						# addSoccerwayId(repo=repo, item=item, lang=lang, soccerway_id=soccerway_id)

						# Touch the page to force an update
						try:
							page.touch()
						except:
							print('Error in updating the page.\n')
						break

				else:
					print('No item page exists.\n')

		# if i >= 100:
		# 	break
		# else:
		# 	i += 1

	return 0

if __name__ == "__main__":
	main()
