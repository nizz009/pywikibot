import re
import datetime
import dateparser

def indiv_val(code='', found_items=''):
	""" 
	"Refines" the data to remove unwanted text 
	@param code: 1 for properties other than date
				2 for dates

	@param found_items: list of found values

	"""

	if code == 1:
		values = found_items[0].split('[[')
		# print(values)
		items = list()
		for value in values:
			item = re.findall(r'[&\w\s]+[^\[\],][&\w\s\|\(\)\-\,]+', value)
			if item:
				items.append(item[0])
		return items

	elif code == 2:
		if found_items:
			try:
				if len(found_items[0]) == 3:
					value = dateparser.parse(str(found_items[0][0])+' '+str(found_items[0][1])+' '+str(found_items[0][2]))
					return str(value.year) + '-' + str(value.month) + '-' + str(value.day)
				elif len(found_items[0]) == 2:
					value = dateparser.parse(str(found_items[0][0])+' '+str(found_items[0][1]))
					return str(value.year) + '-' + str(value.month)
				elif len(found_items[0]) == 1:
					value = dateparser.parse(str(found_items[0][0]))
					return str(value.year)
			except:
				found_items = False
			return ''

	else: 
		print('No code provided.\n')
		return ''

	return ''

def date_val(page_text='', word=''):
	if not page_text:
		print('No text is available.')
		return 1

	if not word:
		print('No date property is available.')
		return 1

	try:
		m = re.findall(r'\|\s*%s\s+\=\s*{{[\w\s]*\|\s*(\d+)\|(\d+)\|(\d+)' % word, page_text.replace('|df=yes','').replace('|df=y','').replace(',','').replace('[','').replace(']',''), re.IGNORECASE)
		return indiv_val(code=2, found_items=m)

		m = re.findall(r'\|\s*%s\s+\=\s*([A-Z0-9a-z\s]+)' % word, page_text.replace('|df=yes','').replace('|df=y','').replace(',','').replace('[','').replace(']',''), re.IGNORECASE)
		if m:
			m[0] = m[0].split()
			return indiv_val(code=2, found_items=m[0])

	except:
		print('Error in retrieving information for %s date.' % word)
		return ''
	return ''

"""
# INFOBOX #

"""
def search_infobox_prop(page_text=''):
	"""
	Searches for all the properties in the infobox

	@params page_text: text of the Wp page
	@return value: list of values 

	"""
	if not page_text:
		print('No text is available.')
		return 1

	try:
		found_items = re.findall(r'\|\s*([A-Z_]+)\s+\=\s*', page_text, re.IGNORECASE)
		return found_items
	except:
			print('Error in retrieving information for author')

	return 0

def search_infobox_value(page_text='', word=''):
	"""
	Searches for information from the infobox

	@params page_text: text of the Wp page
	@return value: list of values 

	"""
	if not page_text:
		print('No text is available.')
		return 1

	try:
		found_items = re.findall(r'\|\s{1,}%s\s+\=\s*\s*([\w\s]{1,}[^\n\}<\|]{1,})' % word, page_text, re.IGNORECASE)
		# print(found_items)
		if found_items:
			item_list = indiv_val(code=1, found_items=found_items)
			return item_list
	except:
			print('Error in retrieving information for %s' % word)

	return 0

def infobox(page_text='', word=''):
	# print(page_text)
	if not page_text:
		print('No text is present.\n')
		return None

	if word:
		print(search_infobox_value(page_text=page_text, word=word))
	else:
		properties = search_infobox_prop(page_text=page_text)
		print('Found ' + str(len(properties)) + ' properties.\n')
		print('Select the index of the property to check. (Leave blank for all properties and 0 for none.)\n')

		index = 1
		for prop in properties:
			print(str(index) + ' ' + str(prop))
			index += 1
		# print('\n')

		indices = list()
		try:
			while True:
				indices.append(int(input()))
		except:
			pass

		propval_pair = dict()
		if indices:
			if indices[0] == 0:
				print('Exiting...')
				return None
			for index in indices:
				prop = properties[index - 1]

				if 'date' in prop:
					value = date_val(page_text=page_text, word=prop)
				else:
					value = search_infobox_value(page_text=page_text, word=prop)
				# print(value)
				try:
					propval_pair[str(prop)] = str(value[0])
				except:
					print('No corresponding value for ' + str(prop) + ' exists. Skipping...')

		else:
			for prop in properties:
				if 'date' in prop:
					value = date_val(page_text=page_text, word=prop)
				else:
					value = search_infobox_value(page_text=page_text, word=prop)
				try:
					if len(value) == 1:
						propval_pair[str(prop)] = str(value[0])
					else:
						propval_pair[str(prop)] = str(value)
				except:
					print('No corresponding value for ' + str(prop) + ' exists. Skipping...')

		print('\n')

	return propval_pair
