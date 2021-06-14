# File name: nobel_laureates_phy.py
# https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Physics

import re
import base_ops as base

prop_ids = {
	
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
			info = wp_page.findInfobox()

			wd_page = base.WdPage(page_name=article_name)
			for prop in info.keys():
				print(str(prop) + ': ' + str(info[prop]))

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
