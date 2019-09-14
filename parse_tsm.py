import sys
import pickle

TSM_BACKUP_PATH = "~/Library/Application Support/TradeSkillMaster/TSMApplication/Backups"
INDEX_FILE = "tsm_backup_index.pickle"
SCAN_STRING_MATCH = "itemString,minBuyout,marketValue,numAuctions,quantity,lastScan\\n"

def extract_scan_data(backup_file):
    with open(backup_file, "rb") as f:
        for line in f.readlines():
            index = line.find(SCAN_STRING_MATCH)
            if index >= 0:
                timestamp = None
                data = {}
                csv_start = index + len(SCAN_STRING_MATCH)
                scan_csv = line[csv_start:-4].strip()
                i = 0
                for entry in scan_csv.split('\\n'):
                    values = list(entry.split(','))
                    item_id = values[0][2:]
                    item_data = {}
                    item_data['min_buyout'] = values[1]
                    item_data['market_value'] = values[2]
                    item_data['num_auctions'] = values[3]
                    item_data['quantity'] = values[4]
                    if not 'timestamp' in data:
                        data['timestamp'] = values[5]
                    data[item_id] = item_data
                return data
        print("Could not find scan CSV line")

def save_scan_data(data):
    timestamp = data['timestamp']
    output_file = 'tsm_scan_' + timestamp + '.pickle'
    with open(output_file, 'wb') as output:
        pickle.dump(data, output, protocol=pickle.HIGHEST_PROTOCOL)
    print("Wrote scan data to '" + output_file + "'")
    
data = extract_scan_data(sys.argv[1])
save_scan_data(data)
