import sys, os
import pickle
import glob
import zipfile
import subprocess

TSM_BACKUP_PATH = "/Users/spenhand/Library/Application Support/TradeSkillMaster/TSMApplication/Backups"
INDEX_FILE = "tsm_backup_index"
SCAN_STRING_MATCH = "itemString,minBuyout,marketValue,numAuctions,quantity,lastScan\\n"
TEMP_DIR = "scrape_temp_dir"
BACKUP_SCAN_DIR = "tsm_backup_scans"

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

def save_scan_data(data, directory):
    timestamp = data['timestamp']
    output_file = directory + '/tsm_scan_' + timestamp + '.pickle'
    print(output_file)
    with open(output_file, 'wb') as output:
        pickle.dump(data, output, protocol=pickle.HIGHEST_PROTOCOL)
    print("Wrote scan data to '" + output_file + "'")

def find_new_backups(backup_path):
    previously_scanned = []
    scanned = []
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'rb') as index:
            for filename in index:
                previously_scanned.append(filename.strip())

    cwd = os.getcwd()
    if not os.path.exists(BACKUP_SCAN_DIR):
        os.mkdir(BACKUP_SCAN_DIR)
    os.chdir(TSM_BACKUP_PATH)
    if not os.path.exists(TEMP_DIR):
        os.mkdir(TEMP_DIR)
    for backup_zip in glob.glob("*.zip"):
        if backup_zip in previously_scanned:
            continue
        subprocess.call(["7z", "x", "-y", "-o" + TEMP_DIR, backup_zip], stdout=open(os.devnull, 'wb'))
        data = extract_scan_data(TEMP_DIR + "/" + "TradeSkillMaster.lua")
        save_scan_data(data, cwd + "/" + BACKUP_SCAN_DIR)
        scanned.append(backup_zip)

    os.chdir(cwd)
    with open(INDEX_FILE, 'a+') as index:
        for scanned_zip in scanned:
            index.write(scanned_zip + '\n')

    print("Scanned " + str(len(scanned)) + " new backups")
    
find_new_backups(TSM_BACKUP_PATH)
