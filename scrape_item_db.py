import wowhead_scrape, sys, pickle, db

tsm_data = pickle.load(open(sys.argv[1], "rb"))
for item_id in tsm_data:
	if db.get_item(item_id) is None:
		print("Scanning item " + item_id)
		item = wowhead_scrape.scrape_item(item_id)
		print(item)
		db.insert_item(item)
		print('Done')
		sys.stdout.flush()

