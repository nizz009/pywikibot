# File name: historicplaces_riverhead_ny.py

import re
import base_ops as base

prop_ids = {
	
}

def main():
	page_name = 'National Register of Historic Places listings in Riverhead (town), New York'

	wp_list = base.WpPage(page_name)

	# Narrowing down the area of interest:
	contents = wp_list.getWpContents()
	item_list = re.split(r'==[\w\s]*==', contents)[1]
	# print(item_list)

	article_names = re.findall(r'\|article\=(.+)', item_list)
	# print(article_names)

	i = 1
	for article_name in article_names:
		print(article_name)

		wp_page = base.WpPage(article_name)
		print(wp_page.page.text)
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
