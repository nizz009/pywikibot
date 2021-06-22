# File name: historicplaces_riverhead_ny.py

import re
import base_ops as base

prop_ids = {
	'location': 'P279',
	'coordinates': 'P625',
	# 'locmapin': '',
	'area': 'P2046',
	'built': 'P571',
	'architecture': 'P149',
	# 'added': '',
	# 'refnum': '',
	'image': 'P18',
	'caption': 'P2096',
}

def main():
	page_name = 'National Register of Historic Places listings in Riverhead (town), New York'

	wp_list = base.WpPage(page_name)
	# wp_list.printWpContents()

	contents = wp_list.getWpContents()
	item_list = re.split(r'==[\w\s]*==', contents)[1]
	# print(item_list)

	article_names = re.findall(r'\|article\=(.+)', item_list)
	# print(article_names)

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
