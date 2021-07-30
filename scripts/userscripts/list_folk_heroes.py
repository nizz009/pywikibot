# File name: list_folk_heroes.py
# https://en.wikipedia.org/wiki/List_of_folk_heroes

import re
import pywikibot
import datetime
import dateparser
import base_ops as base

# properties to be imported
prop_ids = {
	'image': 'P18',
	'image_name': 'P18',
	'birth_place': 'P19',
	'death_place': 'P20',
	'father': 'P22',
	'mother': 'P25',
	'spouse': 'P26',
	'issue': 'P40',
	'children': 'P40',
	'dynasty': 'P53',
	'occupation': 'P101',
	'signature': 'P109',
	'placeofburial': 'P119',
	'cause': 'P509',
	'death_cause': 'P509',
	'birth_date': 'P569',
	'death_date': 'P570',
	'battles': 'P607',
	'students': 'P802',
	'allegiance': 'P945',
	'teacher': 'P1066',
	'predecessor': 'P1365',
	'successor': 'P1366',
	'conviction': 'P1399',
	'nickname': 'P1449',
	'charge': 'P1595',
	'conviction_penalty': 'P1596',
	'native_name': 'P1559',
	'caption': 'P2096',
	'image_caption': 'P2096',
	'altname': 'P4970',
	'other_name': 'P4970',
}

# segragating properties to use appropriate methods while importing
wikibase_item = ['P18', 'P19', 'P20', 'P22', 'P25', 'P26', 'P40', 'P53',
				 'P101', 'P119', 'P509', 'P607', 'P802', 'P945', 'P1066', 'P1365',
				 'P1366', 'P1399', 'P1595', 'P1596']
# files, images, etc.
commons_media = ['P18', 'P109']
# dates, etc.
time = ['P569', 'P570']
# monolingual text
string = ['P1449', 'P1559', 'P4970']
# properties which ideally contain only one value
# single_values = list()
single_values = ['P19', 'P20', 'P22', 'P25', 'P119', 'P509', 'P569', 
				'P570', 'P945', 'P1365', 'P1366', 'P1705']

lang = 'en'

def checkExistence(claim='', prop_id='', prop_value='',):
	""" 
	Checks for the existence of a claim with the given

	@param claim: the claim to be compared with
	@param prop_id: property ID of the property to be added/checked
	@param prop_value: value of property to be looked for

	"""
	try:
		item_value = claim.getTarget()
		if prop_id in time:
			flag = 0
			date = prop_value.split()
			try:
				if len(date) == 3:
					import_date = dateparser.parse(str(date[0])+' '+str(date[1])+' '+str(date[2]))
					if import_date.year == item_value.year and import_date.month == item_value.month and import_date.day == item_value.day:
						flag = 1
				elif len(date) == 2:
					import_date = dateparser.parse(str(date[0])+' '+str(date[1]))
					if import_date.year == item_value.year and import_date.month == item_value.month:
						flag = 1
				elif len(date) == 1:
					import_date = dateparser.parse(str(date[0]))
					if import_date.year == item_value.year:
						flag = 1
			except:
				print('Error in extracting date.\n')
				return True
			if flag:
				return True
		
		elif prop_id in commons_media:
			wd_propval = item_value.title()
			wd_propval = wd_propval.replace('File:', '').replace('Image:', '').replace('image:', '').lower()
			article_file = prop_value.replace('File:', '').replace('Image:', '').replace('image:', '').lower()
			if article_file == wd_propval:
				return True

		elif prop_id in string:
			prop_value = prop_value.replace('[', '').replace(']', '')
			if prop_value == item_value.text:
				return True

		elif prop_id in wikibase_item:
			wd_propval = item_value.title()
			wdpage_val = base.WdPage(wd_value=wd_propval)
			wdpage_value = wdpage_val.page.labels['en'].lower()
			prop_value_refined = prop_value.replace('[', '').replace(']', '')
			if prop_value_refined.lower() == wdpage_value:
				return True

	except:
		pass

	return False

def addToWd(wp_page='', wd_page='', prop_id='', prop_value='', prop_list=''):
	""" check for previous existence of property-value pair in page """
	for prop_claim in wd_page.page.claims:
		items = wd_page.page.claims[prop_claim]

		if prop_id == prop_claim:
			if prop_id in single_values:
				print('The property exists already. Skipping...')
				return

			for item in items:
				if checkExistence(claim=item, prop_id=prop_id, prop_value=prop_value):
					print('Same property-value exist in the page already. Skipping...')
					return 1

		# checks for prop-val pairs in qualifiers
		for item in items:
			for qualifier in item.qualifiers:
				if prop_id == qualifier:
					qual_items = item.qualifiers[qualifier]
					for qual_item in qual_items:
						if checkExistence(claim=qual_item, prop_id=prop_id, prop_value=prop_value):
							print('Same property-value exist in the page as qualifier. Skipping...')
							return 1		

	# wd_page = base.WdPage(wd_value='Q4115189')

	# addition of source
	import_url = 'https://en.wikipedia.org/w/index.php?title=%s&oldid=%s' % (wp_page.title.replace(' ', '_'), wp_page.latest_revision_id)

	""" import details into Wikidata """
	if prop_id in time:
		wd_page.addDate(prop_id=prop_id, date=prop_value, lang=lang, source_id='P4656', sourceval=import_url, confirm='y', append='y')
	
	elif prop_id in commons_media:
		# setting captions/media legend for images
		if prop_id == 'P18' and 'caption' in prop_list.keys():
			caption_string = str(prop_list['caption']).replace('[', '').replace(']', '')
			caption = pywikibot.WbMonolingualText(text=caption_string, language=lang)
			wd_page.addFiles(prop_id=prop_id, prop_value=prop_value, lang=lang, source_id='P4656', sourceval=import_url, qualifier_id='P2096', qualval=caption, confirm='y', append='y')
		else:
			wd_page.addFiles(prop_id=prop_id, prop_value=prop_value, lang=lang, source_id='P4656', sourceval=import_url, confirm='y', append='y')

	elif prop_id in string:
		if 'native_name_lang' in prop_list.keys():
			wd_page.addMonolingualText(prop_id=prop_id, prop_value=prop_value, lang=lang, source_id='P4656', sourceval=import_url, text_language=str(prop_list['native_name_lang']), confirm='y', append='y')
		else:
			print('Missing native language.')

	elif prop_id in wikibase_item:
		if '[' not in prop_value:
			print('Simple string present. Skipping...')
			return 1

		try:
			prop_value = prop_value.replace('[', '').replace(']', '')
			value_wp_page = base.WpPage(prop_value.strip())
			value_wd_page = base.WdPage(page_name=value_wp_page.title)
			wd_page.addWdProp(prop_id=prop_id, prop_value=value_wd_page.wd_value, lang=lang, source_id='P4656', sourceval=import_url, confirm='y', append='y')
		except:
			print('Error adding new wd property.')

	return 0

def main():
	page_name = 'List of folk heroes'

	wp_list = base.WpPage(page_name)
	# wp_list.printWpContents()

	""" Retrieving names of the Wp articles """
	contents = wp_list.getWpContents()
	list_items = re.split(r'==[\w\s]*==', contents)[1]
	rows = list_items.split('*')

	article_names = list()
	for row in rows:
		row = row.split('–')[0]
		article_names.append(row)

	# i = 0
	for name in article_names:
		# print(name)
		article_name = ''
		article_name = re.findall(r'\[\[([\w\s\'\-\(\)\.]*)\]\]|$', name)[0]
		if not article_name:
			article_name = re.findall(r'\[\[([\w\s\'\-\(\)\.]*)\|[\w\s]*\]\]|$', name)[0]

		if article_name:
			wp_page = base.WpPage(article_name)

			# check for existence of page
			if wp_page.getWpContents():
				print(wp_page.title)

				""" Extracting info from infobox and adding to Wikidata """
				# find info from the infobox
				info = wp_page.findInfobox(check_all='y')

				# get the Wd page
				wd_page = ''
				try:
					wd_page = base.WdPage(page_name=wp_page.title)
				except:
					pass

				# wd_page = base.WdPage(wd_value='Q4115189')

				if info and wd_page:
					# iterate through each info extracted from infobox
					for prop in info.keys():
						print(str(prop) + ': ' + str(info[prop]))
						try:
							# multiple values for a prop - add each value separately
							if type(info[prop]) is list:
								for val in info[prop]:
									try:
										addToWd(wp_page=wp_page, wd_page=wd_page, prop_id=prop_ids[str(prop)], prop_value=val, prop_list=info)
									except:
										print('Error adding property.')
										continue
							else:
								addToWd(wp_page=wp_page, wd_page=wd_page, prop_id= prop_ids[str(prop)], prop_value=info[prop], prop_list=info)

							print('\n')
						except:
							pass
					print('\n')

			else:
				print('No such page exists. Skipping...\n')
				continue
		# if i < 2:
		# 	i += 1
		# else:
		# 	break

if __name__ == "__main__":
	main()
