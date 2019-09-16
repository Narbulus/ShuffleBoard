import sqlite3

DB = "/Users/spenhand/Projects/Shuffle/shuffle.db"
conn = sqlite3.connect(DB)

def insert_item(item):
	c = conn.cursor()
	values = (item['id'], item['name'], item['level'], item['vendor_sell'], item['vendor_buy_min'], item['vendor_buy_max'], item['max_stack'])
	c.execute('INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?)', values)
	conn.commit()

def get_item(item_id):
	c = conn.cursor()
	c.execute('SELECT * FROM items WHERE id=?', (item_id,))
	return c.fetchone()

def insert_scan(scan):
	c = conn.cursor()
	values = (scan['id'], scan['timestamp'], scan['min_buyout'], scan['market_value'], scan['num_auctions'], scan['quantity'])
	c.execute('INSERT INTO tsm VALUES (?, ?, ?, ?, ?, ?)', values)
	conn.commit()