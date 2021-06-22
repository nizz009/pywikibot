# File name: nobel_laureates_phy.py
# https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Physics

import re
import base_ops as base

prop_ids = {
	'birth_name': 'P1477',
	'birth_date': 'P569',
	'birth_place': 'P19',
	'death_date': 'P570',
	'death_place': 'P20',
	'nationality': 'P27',
	'field': 'P101',
	'alma_mater': 'P69',
	'workplaces': 'P937',
	'doctoral_advisor': 'P184',
	'doctoral_students': 'P185',
	'notable_students': 'P802',
	'known_for': 'P166',
	'prizes': 'P18',
	'signature': 'P569',
	'image': 'P18',
	'caption': 'P2096',
}

def main():
	page_name = 'List of Nobel laureates in Physics'

	wp_list = base.WpPage(page_name)

	contents = wp_list.getWpContents()
	list_items = re.split(r'==[\w\s]*==', contents)[2]
	# print(list_items)
	rows = list_items.split('|-')

	article_names = list()
	for row in rows:
		if '[[File:' in row:
			# print(row)
			laureats = re.findall(r'scope.* \[\[(.*)\]\]', row)
			laureat = laureats[0].split('|')
			# print(laureat)
			article_names.append(laureat[0])

	i = 1
	for article_name in article_names:
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
				try:
					if 'date' in str(prop):
						wd_page.addDate(prop_id=prop_ids[str(prop)], date=info[prop])
					elif 'image' in str(prop):
						wd_page.addFiles(prop_id=prop_ids[str(prop)], prop_value=str(info[prop]))
					else:
						wd_page.addWdProp(prop_id=prop_ids[str(prop)], prop_value=str(info[prop]))
				except:
					pass

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
