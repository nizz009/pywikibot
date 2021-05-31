import pywikibot
from pywikibot import pagegenerators

import json
import os
import re
import string
import sys
import _thread
import time
import unicodedata
import urllib
import urllib.request
import urllib.parse
import dateparser
import datetime
import unicodedata

enwiki = pywikibot.Site('en', 'wikipedia')
enwd = pywikibot.Site('wikidata', 'wikidata')
repo = enwd.data_repository()
encommons = pywikibot.Site('commons', 'commons')

langs = { 
	'en': 'Q328', 
	'fr': 'Q8447', 
	'it': 'Q11920', 
	}

# helper functions

# from https://bitbucket.org/mikepeel/wikicode/src/master/wir_newpages.py
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

# deals with Wikipedia articles
class WpPage:

	def __init__(self, page_name=''):
		if page_name:
			self.page_name = page_name
			self.page = pywikibot.Page(enwiki, page_name)

	def printWpContents(self):
		""" Prints contents of a Wikipedia page """

		content = self.page.get()
		print(content)

		return 0

	def searchWpPage(self, prop_id='', prop_values=''):
		""" 
		Searches for a Wp in Wd

		@param prop_id: ID of the property used to match Wd item with Wp article
		@param prop_values: Property values associated with the prop_id 

		"""

		if not prop_values:
			print('No property values for matching provided. Skipping the search.\n')
			return 1 

		page_title = self.page.title()
		page_title_ = page_title.split('(')[0].strip()
		searchitemurl = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&language=en&format=xml' % (urllib.parse.quote(page_title_))
		raw = getURL(searchitemurl)

		# searches and matches the authors for the searched item
		if not '<search />' in raw:
			q_values = re.findall(r'id="(Q\d+)"', raw)
			for q_value in q_values:
				itemfound = pywikibot.ItemPage(repo, q_value)
				item_dict = itemfound.get()
				
				if prop_id in itemfound.claims:
					itemfound_values = []
					for claim in item_dict['claims'][prop_id]:
						prop_id_value = claim.getTarget()
						prop_id_item_dict = prop_id_value.get()
						itemfound_values.append(prop_id_item_dict['labels']['en'])

					itemfound_values = [itemfound_value.replace('\xa0',' ') for itemfound_value in itemfound_values]

					if itemfound_values in prop_values:
						return (itemfound.title())
					else:
						continue
				else:
					continue
		else:
			print('Item doesn\'t exist.')
			return 0

		print('No match was found.')

		return 0



# deals with Wikidata articles
class WdPage:

	def __init__(self, wd_value='', wdpage=''):
		if wd_value:
			self.page = pywikibot.ItemPage(enwd, wd_value)
		elif wdpage:
			self.page = pywikibot.ItemPage.fromPage(wdpage)

		self.wd_value = self.page.title()

	def printWdContents(self):
		""" Prints contents of a Wikidata page """

		print(self.page.title())

		categories = self.page.get()

		for items in categories:
			try:
				print("Category: " + items)
				for item in categories[items]:
					try:
						print(categories[items][item])
					except:
						print("Error in browsing through items.")
				print("\n")
			except:
				print("Error in browsing through categories.")

		return 0

	def addWdProp(self, prop_id='', prop_value='', lang='', qualifier_id='', qualval_id=''):
		"""
		Adds a new property in Wikidata

		@param prop_id: ID of the property
		@param prop_value: ID of property's value
		@param lang: language of Wikipedia artcile: for references
		@param qualifier_id: ID of the qualifier
		@param qualval_id: ID of the qualifier's value

		@type all: string

		"""
		print(self.page.title())

		if prop_value:
			try:
				new_prop_val = pywikibot.ItemPage(enwd, prop_value)
			except:
				print('Incorrect property value provided.\n')
				return 1

		self.page.get()
		if prop_id in self.page.claims:
			choice = input('Property already exists. Select:\n\
				1 to skip\n\
				2 to over-write the existing property\n\
				3 to add another value to the property\n')

			if choice == '1':
				return

			elif choice == '2':
				self.page.removeClaims(self.page.claims[prop_id])
			
			elif choice > '3':
				print("Invalid choice.\n")
				return 1
			
		try:
			new_prop = pywikibot.Claim(enwd, prop_id)	
			new_prop.setTarget(new_prop_val)

			# confirmation
			print(new_prop)
			text = input("Do you want to save this property? (y/n) ")
			if text == 'y':
				self.page.addClaim(new_prop, summary = u'Adding new property')
				# retrieving the updated page
				self.page = pywikibot.ItemPage(enwd, self.wd_value)
				
				if lang:
					self.addImportedFrom(repo=repo, claim=new_prop, lang=lang, status=1)
					# print("Reference added.")
				if qualifier_id and qualval_id:
					self.addQualifiers(repo=repo, claim=new_prop, qualifier_id=qualifier_id, qualval_id=qualval_id, status=1)
					# print("Qualifier added.")

		except:
			print('Error in adding new property.')

		return 0

	def addFiles(self, prop_id='', prop_value='', lang='', qualifier_id='', qualval_id=''):
		""" Adds files from Commons to Wikidata """

		print(self.page.title())

		if prop_value:
			try:
				new_prop_val = pywikibot.FilePage(encommons, prop_value)
			except:
				print('Incorrect property value provided.\n')
				return 1

		self.page.get()
		if prop_id in self.page.claims:
			choice = input('Property already exists. Select:\n\
				1 to skip\n\
				2 to over-write the existing property\n\
				3 to add another value to the property\n')

			if choice == '1':
				return

			elif choice == '2':
				self.page.removeClaims(self.page.claims[prop_id])
			
			elif choice > '3':
				print("Invalid choice.\n")
				return 1
		
		try:
			new_prop = pywikibot.Claim(repo, prop_id)	
			new_prop.setTarget(new_prop_val)

			# confirmation
			print(new_prop)
			text = input("Do you want to save this property? (y/n) ")
			if text == 'y':
				self.page.addClaim(new_prop, summary = u'Adding new file')
				self.page = pywikibot.ItemPage(enwd, self.wd_value)

				if lang:
					self.addImportedFrom(repo=repo, claim=new_prop, lang=lang, status=1)
					# print("Reference added.")
				if qualifier_id and qualval_id:
					self.addQualifiers(repo=repo, claim=new_prop, qualifier_id=qualifier_id, qualval_id=qualval_id, status=1)
					# print("Qualifier added.")

		except:
			print('Error in adding new file.')

		return 0

	def addNumeric(self, prop_id='', prop_value='', lang='', qualifier_id='', qualval_id=''):
		""" Adds numeric values to Wikidata """

		print(self.page.title())

		if prop_value:
			try:
				val = pywikibot.WbQuantity(amount=prop_value, site=enwiki)
			except:
				print('Incorrect property value provided.\n')
				return 1

		self.page.get()
		if prop_id in self.page.claims:
			choice = input('Property already exists. Select:\n\
				1 to skip\n\
				2 to over-write the existing property\n\
				3 to add another value to the property\n')

			if choice == '1':
				return

			elif choice == '2':
				self.page.removeClaims(self.page.claims[prop_id])
			
			elif choice > '3':
				print("Invalid choice.\n")
				return 1
		
		try:
			new_prop = pywikibot.Claim(repo, prop_id)
			print('hello')
			new_prop.setTarget(val)
			print(val)

			# confirmation
			print(new_prop)
			text = input("Do you want to save this property? (y/n) ")
			if text == 'y':
				self.page.addClaim(new_prop, summary = u'Adding new numeric value')
				self.page = pywikibot.ItemPage(enwd, self.wd_value)

				if lang:
					self.addImportedFrom(repo=repo, claim=new_prop, lang=lang, status=1)
					# print("Reference added.")
				if qualifier_id and qualval_id:
					self.addQualifiers(repo=repo, claim=new_prop, qualifier_id=qualifier_id, qualval_id=qualval_id, status=1)
					# print("Qualifier added.")

		except:
			print('Error in adding numeric value.')

		return 0

	def addDate(self, prop_id='', date='', lang='', qualifier_id='', qualval_id=''):
		""" Adds numeric values to Wikidata """

		print(self.page.title())

		if date and date != '0-0-0':
			self.page.get()

			if prop_id in self.page.claims:
				choice = input('Property already exists. Select:\n\
					1 to skip\n\
					2 to over-write the existing property\n\
					3 to add another value to the property\n')

				if choice == '1':
					return

				elif choice == '2':
					self.page.removeClaims(self.page.claims[prop_id])
				
				elif choice > '3':
					print("Invalid choice.\n")
					return 1

			now = datetime.datetime.now()

			check_ok = True
			if int(date.split('-')[0]) > now.year:
				check_ok = False
			try:
				if int(date.split('-')[0]) == now.year and int(date.split('-')[1]) > now.month:
					check_ok = False
			except:
				null = 0

			if check_ok:
				try:
					new_prop = pywikibot.Claim(repo, prop_id)

					if len(date.split('-')) == 3:
						new_prop.setTarget(pywikibot.WbTime(year=int(date.split('-')[0]), month=int(date.split('-')[1]), day=int(date.split('-')[2])))
					elif len(date.split('-')) == 2:
						new_prop.setTarget(pywikibot.WbTime(year=int(date.split('-')[0]), month=int(date.split('-')[1])))
					elif len(date.split('-')) == 1:
						new_prop.setTarget(pywikibot.WbTime(year=int(date.split('-')[0])))

					# confirmation
					print(new_prop)
					text = input("Do you want to save this property? (y/n) ")
					if text == 'y':
						self.page.addClaim(new_prop, summary = u'Adding new numeric value')
						self.page = pywikibot.ItemPage(enwd, self.wd_value)

						if lang:
							self.addImportedFrom(repo=repo, claim=new_prop, lang=lang, status=1)
							# print("Reference added.")
						if qualifier_id and qualval_id:
							self.addQualifiers(repo=repo, claim=new_prop, qualifier_id=qualifier_id, qualval_id=qualval_id, status=1)
							# print("Qualifier added.")

				except:
					print('Error in adding numeric value.')
		return 0
		
	def checkClaimExistence(self, claim=''):
		"""
		Checks if a claim exists in Wikidata already
	
		@param claim: property and it's value to which this associated with

		"""
		claim_prop = claim.getID()
		claim_target = claim.getTarget()

		wd_items = self.page.get()

		for props in wd_items['claims']:
			if props == claim_prop:
				try:
					item = wd_items['claims'][props]
					for value in item:
						try:
							value_qid = value.getTarget()
							if claim_target.title() == value_qid.title():
								return value
						except:
							pass
				except:
					print('Error in browsing through items.')

		choice = input('Property and value do not exist. Select:\n\
			1 to add it Wikidata\n\
			2 to skip\n')

		if choice == '1':
			self.page.addClaim(claim, summary = u'Adding new property')
			self.page = pywikibot.ItemPage(enwd, self.wd_value)
			return claim
		elif choice == '2':
			print('Skipping the addition of property and source.\n')
			return 0
		else:
			print('Invalid choice.\n')
			return 0

		return 0


	def addImportedFrom(self, repo=repo, prop_id='', prop_value='', claim='', lang='', status=0):
		"""
		Adds a reference/source
	
		@param repo:
		@param prop_id: ID of the property
		@param prop_val: ID of value associated with property
		@param claim: property and it's value to which this associates with
		@param lang: language of the wiki - must be a value from 'langs' dict
		@param status: decide whether to test for claim's existence or not
						(0 - method is called directly by user
						 1 - method is called indirectly by other methods which add a property to Wd)

		"""
		if prop_id and prop_value:
			try:
				new_prop_val = pywikibot.ItemPage(enwd, prop_value)
				claim = pywikibot.Claim(enwd, prop_id)	
				claim.setTarget(new_prop_val)
			except:
				print('Incorrect property id or value provided.\n')
				return 1

		if status == 0:
			claim = self.checkClaimExistence(claim)

		if repo and claim and lang and lang in langs.keys():
			importedfrom = pywikibot.Claim(repo, 'P143') #imported from
			importedwp = pywikibot.ItemPage(repo, langs[lang])
			importedfrom.setTarget(importedwp)
			claim.addSource(importedfrom, summary='Adding 1 reference: [[Property:P143]]')
			self.page = pywikibot.ItemPage(enwd, self.wd_value)
			print('Reference/Source added successfully.\n')

		return 0

	def addQualifiers(self, repo=repo, prop_id='', prop_value='', claim='', qualifier_id='', qualval_id='', status=0):
		"""
		Adds a qualifier
	
		@param qualifier_id: ID of the qualifier
		@param qualval_id: ID of the qualifier's value

		@type of all (except repo and claim): string

		"""
		if prop_id and prop_value:
			try:
				new_prop_val = pywikibot.ItemPage(enwd, prop_value)
				claim = pywikibot.Claim(enwd, prop_id)	
				claim.setTarget(new_prop_val)
			except:
				print('Incorrect property id or value provided.\n')
				return 1

		if status == 0:
			claim = self.checkClaimExistence(claim)

		if repo and claim and qualifier_id and qualval_id:
			qualifier = pywikibot.Claim(repo, qualifier_id)
			qualifier_val = pywikibot.ItemPage(repo, qualval_id)
			qualifier.setTarget(qualifier_val)
			claim.addQualifier(qualifier, summary='Adding 1 qualifier')
			self.page = pywikibot.ItemPage(enwd, self.wd_value)
			print('Qualifier added successfully.\n')

		return 0


def main():
	# page_name = input('Name of article: ')
	wd_value = 'Q4115189'
	wp_page = ''
	wd_page = ''

	# # Test for Wikipedia page
	# try:
	# 	wp_page = WpPage(page_name)
	# 	print(wp_page.searchWpPage('P50', [['J. K. Rowling']]))
	# except:
	# 	("Page does not exist.\n")
	# 	return 1

	# if wp_page:
	# 	wp_page.printWpContents()

	# # Test for Wikidata page
	# try:
	# 	wd_page = WdPage(wd_value)
	# except:
	# 	("Page does not exist.\n")
	# 	return 1
		
	# if wd_page:
		# wd_page.printWdContents()
		# wd_page.addWdProp(prop_id='P31', prop_value='Q5', lang='en', qualifier_id='P1013', qualval_id='Q139')
		# wd_page.addFiles(prop_id='P18', prop_value='Harry Potter i les reliquies de la mort.jpg', lang='fr')
		# wd_page.addNumeric(prop_id='P1104', prop_value=123)
		# wd_page.addImportedFrom(prop_id='P31', prop_value='Q5', lang='en')
		# wd_page.addQualifiers(prop_id='P31', prop_value='Q5', qualifier_id='P1013', qualval_id='Q139')

		# Mention the date in yyyy-mm-dd/yyyy-mm/yyyyformat(s)
		# wd_page.addDate(prop_id='P577', date='2012-02-03', lang='fr')

	return 0
		
if __name__ == "__main__":
	main()