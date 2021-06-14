# For the links to the edited Wikidata pages, please visit: 
# https://www.wikidata.org/wiki/User:Nizz009/ATP_edit_links
# For some pictures of the output (generated in CLI) while executing the script, please visit:
# https://drive.google.com/drive/folders/1HV7CyyMT09eaUcbyb6JkO4qbbyk9VQwL?usp=sharing

import pywikibot
from pywikibot import pagegenerators

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

enwiki = pywikibot.Site('en', 'wikipedia')
enwd = pywikibot.Site('wikidata', 'wikidata')
repo = enwd.data_repository()

def getURL(url='', retry=True, timeout=30):
	raw = ''
	req = urllib.request.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0' })
	try:
		raw = urllib.request.urlopen(req, timeout=timeout).read().strip().decode('utf-8')
	except:
		sleep = 10 # seconds
		maxsleep = 900
		while retry and sleep <= maxsleep:
			print('Error while retrieving: %s' % (url))
			print('Retry in %s seconds...' % (sleep))
			time.sleep(sleep)
			try:
				raw = urllib.request.urlopen(req, timeout=timeout).read().strip().decode('utf-8')
			except:
				pass
			sleep = sleep * 2
	return raw

# modified version of https://bitbucket.org/mikepeel/wikicode/src/master/wir_newpages.py
def addImportedFrom(repo='', claim='', lang=''):
	langs = { 'en': 'Q328', 'fr': 'Q8447', 'de': 'Q48183', }
	if repo and claim and lang and lang in langs.keys():
		importedfrom = pywikibot.Claim(repo, 'P143') #imported from
		importedwp = pywikibot.ItemPage(repo, langs[lang])
		importedfrom.setTarget(importedwp)
		claim.addSource(importedfrom, summary='Adding 1 reference: [[Property:P143]]: [[en]]')
		print('ATP ID added successfully\n')
	return 0

def addAtpIdIdentifier(repo='', item='', claim='', atp_id='', lang=''):
	if repo and item and claim and atp_id and lang:
		claim = pywikibot.Claim(repo, claim)
		claim.setTarget(atp_id)

		item.addClaim(claim)

		addImportedFrom(repo=repo, claim=claim, lang=lang)
	return 0

def find_id(page=''):
	if page:
		m = re.findall(r'{{ATP\|id=(\w+)', page.text)
		if m:
			return m[0]
		m = re.findall(r'{{ATP\|(\w+)', page.text)
		if m:
			return m[0]
		m = re.findall(r'{{ATP\|.+(\w{4})\|', page.text)
		if m:
			return m[0]
	else:
		print('Error in retrieving information from article.\n')
	return ''

def addAtpId(repo='', wikisite='', item='', page='', lang=''):
	if repo and wikisite and item and page and lang:
		atp_id = find_id(page=page)
		try:
			item.get()
		except:
			print('Error while retrieving item, skiping...')
			return ''

		if atp_id and len(atp_id) == 4:
			# remove any existing value and add the new value to it
			if 'P536' in item.claims:
				item.removeClaims(item.claims['P536'])

			addAtpIdIdentifier(repo=repo, item=item, claim='P536', atp_id=atp_id, lang=lang)
	return 0

# Checks if the assigned ATP ID belongs to the correct player
def check_authenticity(page=''):
	if page:
		atp_id = find_id(page=page)
		if atp_id and len(atp_id) == 4:
			searchitemurl = 'https://www.atptour.com/en/players/-/%s/overview' % (urllib.parse.quote(atp_id))
			raw = getURL(searchitemurl)

			m = re.findall(r'(.+)\| Overview', raw)
			if m:
				checker = m[0].strip()
				checker = checker.lower()
				checker = checker.split()

				pg = (page.title())
				pg = unidecode(pg)
				pg = pg.lower()
				pg = pg.split()

				i = 0
				for word in checker:
					if word == pg[i]:
						i += 1
					else:
						break
				if i == len(checker):
					return True
				else:
					return False
	return False

def main():
	category = 'ATP template with ID not in Wikidata'
	lang = 'en'

	cat = pywikibot.Category(pywikibot.Link(category, source=enwiki, default_namespace=14))
	gen = pagegenerators.CategorizedPageGenerator(cat)
	pre = pagegenerators.PreloadingGenerator(gen)

	# looping through pages of articles
	for page in pre:
		print(page.title())

		item = ''
		try:
			item = pywikibot.ItemPage.fromPage(page)
		except:
			pass

		if item:
			if (datetime.datetime.now()-item.editTime()).seconds < 120:
				print('... but is being edited')
			else:
				if check_authenticity(page=page):
					addAtpId(repo=repo, wikisite=enwiki, item=item, page=page, lang=lang)
				else:
					print('Incorrect ATP ID provided.\n')
					continue
		else:
			# if no item exists, search for a valid item
			page_title = page.title()
			page_title_ = page_title.split('(')[0].strip()
			searchitemurl = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=en&format=xml' % (urllib.parse.quote(page_title_))
			raw = getURL(searchitemurl)
			
			# check for valid search result
			if not '<search />' in raw:
				m = re.findall(r'id="(Q\d+)"', raw)

				for itemfoundq in m:
					itemfound = pywikibot.ItemPage(repo, itemfoundq)
					item_dict = itemfound.get()

					if page.title() == item_dict['labels']['en']:
						if check_authenticity(page=page):
							addAtpId(repo=repo, wikisite=enwiki, item=item, page=page, lang=lang)
						else:
							print('Incorrect ATP ID provided.\n')
							continue

						# Touch the page to force an update
						try:
							page.touch()
						except:
							null = 0
						break
	return 0

if __name__ == "__main__":
	main()