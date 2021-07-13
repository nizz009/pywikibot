# File name: list_folk_heroes.py
# https://en.wikipedia.org/wiki/List_of_folk_heroes

import re
import base_ops as base

prop_ids = {
	'successor': 'P1366',
	'predecessor': 'P1365',
	# 'succession':,
	'father': 'P22',
	'spouse': 'P26',
	'issue': 'P40',
	'dynasty': 'P53',
	'image': 'P18',
	'caption': 'P2096',
}

def main():
	page_name = 'List of folk heroes'

	wp_list = base.WpPage(page_name)
	# wp_list.printWpContents()

	contents = wp_list.getWpContents()
	list_items = re.split(r'==[\w\s]*==', contents)[1]
	# print(list_items)
	rows = list_items.split('*')

	names = list()
	for row in rows:
		row = row.split('–')[0]
		names.append(row)

	# print(names)
	i = 0
	article_names = list()
	for name in names:
		# print(name)
		article_name = ''
		article_name = re.findall(r'\[\[([\w\s\'\-\(\)\.]*)\]\]|$', name)[0]
		if not article_name:
			article_name = re.findall(r'\[\[([\w\s\'\-\(\)\.]*)\|[\w\s]*\]\]|$', name)[0]
		# print(article_name)
		
		if article_name:
			print(article_name)
			wp_page = base.WpPage(article_name)
			# print(wp_page.page.text)
			if wp_page.getWpContents():
				info = wp_page.findInfobox(check_all='y')

				wd_page = base.WdPage(page_name=article_name)
				wd_page = base.WdPage(wd_value='Q4115189')
				# print(wd_page.wd_value)

				for prop in info.keys():
					print(str(prop) + ': ' + str(info[prop]))
					# try:
					# 	if 'date' in str(prop):
					# 		wd_page.addDate(prop_id=prop_ids[str(prop)], date=info[prop])
					# 	elif 'image' in str(prop):
					# 		wd_page.addFiles(prop_id=prop_ids[str(prop)], prop_value=str(info[prop]))
					# 	else:
					# 		wd_page.addWdProp(prop_id=prop_ids[str(prop)], prop_value=str(info[prop]))
					# except:
					# 	pass

				print('\n')
			else:
				print('No such page exists. Skipping...\n')
				continue
			if i < 2:
				i += 1
			else:
				break

if __name__ == "__main__":
	main()
