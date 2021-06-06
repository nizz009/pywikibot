import re

def indiv_val(found_items):
	""" "Refines" the data to remove unwanted text """

	values = found_items[0].split('[[')
	# print(values)
	items = list()
	for value in values:
		item = re.findall(r'[&\w\s]+[^\[\],][&\w\s\|\(\)\-\,]+', value)
		if item:
			items.append(item[0])
	return items

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
		found_items = re.findall(r'\|\s{1,}%s\s+\=\s*\s*([\w\s]+[^\n\}\|]+)' % word, page_text, re.IGNORECASE)
		# print(found_items)
		if found_items:
			item_list = indiv_val(found_items)
			return item_list
	except:
			print('Error in retrieving information for author')

	return 0

def infobox(page_text='', word=''):
	print(page_text)
	if not page_text:
		print('No text is present.\n')
		return 1

	if word:
		print(search_infobox_value(page_text=page_text, word=word))
	else:
		properties = search_infobox_prop(page_text=page_text)
		print('Found ' + str(len(properties)) + ' properties.\n')
		print('Select the index of the property to check. (Leave blank for checking all properties)\n')

		index = 1
		for prop in properties:
			print(str(index) + ' ' + str(prop))
			index += 1
		print('\n')

		indices = list()
		try:
			while True:
				indices.append(int(input()))
		except:
			pass

		propval_pair = dict()
		if indices:
			for index in indices:
				prop = properties[index - 1]
				value = search_infobox_value(page_text=page_text, word=prop)
				# print(value)
				try:
					propval_pair[str(prop)] = str(value[0])
				except:
					print('No corresponding value for ' + str(prop) + ' exists. Skipping...')

		else:
			for prop in properties:
				value = search_infobox_value(page_text=page_text, word=prop)
				try:
					propval_pair[str(prop)] = str(value[0])
				except:
					print('No corresponding value for ' + str(prop) + ' exists. Skipping...')

		print('\n')
		for prop in propval_pair:
			print(str(prop) + ': ' + str(propval_pair[prop]))

	return 0