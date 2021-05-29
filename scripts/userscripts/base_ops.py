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

enwiki = pywikibot.Site('en', 'wikipedia')
enwd = pywikibot.Site('wikidata', 'wikidata')
repo = enwd.data_repository()
encommons = pywikibot.Site('commons', 'commons')

langs = { 
	'en': 'Q328', 
	'fr': 'Q8447', 
	'it': 'Q11920', 
	}

# deals with Wikipedia articles
class WpPage:

	def __init__(self, page_name=''):
		if page_name:
			self.page = pywikibot.Page(enwiki, page_name)

	def printWpContents(self):
		""" Prints contents of a Wikipedia page """

		content = self.page.get()
		print(content)

		return 0


# deals with Wikidata articles
class WdPage:

	def __init__(self, wd_value='', wdpage=''):
		if wd_value:
			self.page = pywikibot.ItemPage(enwd, wd_value)
		elif wdpage:
			self.page = pywikibot.ItemPage.fromPage(wdpage)

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

				if lang:
					self.addImportedFrom(repo=repo, claim=new_prop, lang=lang)
				if qualifier_id and qualval_id:
					self.addQualifiers(repo=repo, claim=new_prop, qualifier_id=qualifier_id, qualval_id=qualval_id)

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

				if lang:
					self.addImportedFrom(repo=repo, claim=new_prop, lang=lang)
				if qualifier_id and qualval_id:
					self.addQualifiers(repo=repo, claim=new_prop, qualifier_id=qualifier_id, qualval_id=qualval_id)

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
			new_prop.setTarget(val)

			# confirmation
			print(new_prop)
			text = input("Do you want to save this property? (y/n) ")
			if text == 'y':
				self.page.addClaim(new_prop, summary = u'Adding new numeric value')

				if lang:
					self.addImportedFrom(repo=repo, claim=new_prop, lang=lang)
				if qualifier_id and qualval_id:
					self.addQualifiers(repo=repo, claim=new_prop, qualifier_id=qualifier_id, qualval_id=qualval_id)

		except:
			print('Error in adding numeric value.')

		return 0
		
	def checkClaimExistence(self, claim=''):
		"""
		Checks if a claim exists in Wikidata already
	
		@param claim: property and it's value to which this associated with

		"""
		wd_items = self.page.get()

		flag = 0
		for items in wd_items['claims']:
			try:
				item = wd_items['claims'][items]
				if claim in item:
					flag = 1
					break
			except:
				print('Error in browsing through items.')

		if flag == 0:
			choice = input('Property and value do not exist. Select:\n\
				1 to add it Wikidata\n\
				2 to skip\n')

			if choice == '1':
				self.page.addClaim(claim, summary = u'Adding new property')
			elif choice == '2':
				print('Skipping the addition of property and source.\n')
				return 
			else:
				print('Invalid choice.\n')
				return

		return 0

	def addImportedFrom(self, repo='', prop_id='', prop_val='', claim='', lang=''):
		"""
		Adds a reference/source
	
		@param repo:
		@param prop_id: ID of the property
		@param prop_val: ID of value associated with property
		@param claim: property and it's value to which this associates with
		@param lang: language of the wiki - must be a value from 'langs' dict

		"""
		if prop_id and prop_val:
			try:
				new_prop_val = pywikibot.ItemPage(enwd, prop_value)
				claim = pywikibot.Claim(enwd, prop_id)	
				claim.setTarget(new_prop_val)
			except:
				print('Incorrect property id or value provided.\n')
				return 1

		self.checkClaimExistence(claim)

		if repo and claim and lang and lang in langs.keys():
			importedfrom = pywikibot.Claim(repo, 'P143') #imported from
			importedwp = pywikibot.ItemPage(repo, langs[lang])
			importedfrom.setTarget(importedwp)
			claim.addSource(importedfrom, summary='Adding 1 reference: [[Property:P143]]')
			print('Information added successfully.\n')

		return 0

	def addQualifiers(self, repo='', prop_id='', prop_val='', claim='', qualifier_id='', qualval_id=''):
		"""
		Adds a qualifier
	
		@param qualifier_id: ID of the qualifier
		@param qualval_id: ID of the qualifier's value

		@type of all (except repo and claim): string

		"""
		if prop_id and prop_val:
			try:
				new_prop_val = pywikibot.ItemPage(enwd, prop_value)
				claim = pywikibot.Claim(enwd, prop_id)	
				claim.setTarget(new_prop_val)
			except:
				print('Incorrect property id or value provided.\n')
				return 1

		self.checkClaimExistence(claim)

		if repo and claim and qualval_id:
			qualifier = pywikibot.Claim(repo, qualifier_id)
			qualifier_val = pywikibot.ItemPage(repo, qualval_id)
			qualifier.setTarget(qualifier_val)
			claim.addQualifier(qualifier, summary='Adding 1 qualifier')
		return 0


def main():
	# page_name = input('Name of article: ')
	wd_value = 'Q4115189'
	wp_page = ''
	wd_page = ''

	# Test for Wikipedia page
	# try:
	# 	wp_page = WpPage(page_name)
	# except:
	# 	("Page does not exist.\n")
	# 	return 1

	# if wp_page:
	# 	wp_page.printWpContents()

	# Test for Wikidata page
	try:
		wd_page = WdPage(wd_value)
	except:
		("Page does not exist.\n")
		return 1
		
	if wd_page:
		# wd_page.printWdContents()
		wd_page.addWdProp(prop_id='P31', prop_value='Q13406268', lang='en')

	return 0
		
if __name__ == "__main__":
	main()