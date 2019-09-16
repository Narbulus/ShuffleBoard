import sys, os, db
import pickle
import glob
import zipfile
import subprocess

PROJECT_PATH = "/Users/spenhand/Projects/Shuffle"
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
                csv_start = index + len(SCAN_STRING_MATCH)
                scan_csv = line[csv_start:-4].strip()
                i = 0
                for entry in scan_csv.split('\\n'):
                    values = list(entry.split(','))
                    item_data = {}
                    item_data['id'] = values[0][2:]
                    item_data['min_buyout'] = values[1]
                    item_data['market_value'] = values[2]
                    item_data['num_auctions'] = values[3]
                    item_data['quantity'] = values[4]
                    item_data['timestamp'] = values[5]
                    db.insert_scan(item_data)
        print("Could not find scan CSV line")

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
        full_temp_dir = TSM_BACKUP_PATH + "/" + TEMP_DIR
        backup_path = TSM_BACKUP_PATH + "/" + backup_zip
        subprocess.call(["/usr/local/bin/7z", "x", "-y", "-o" + full_temp_dir, backup_path], stdout=open(os.devnull, 'wb'))
        extract_scan_data(full_temp_dir + "/" + "TradeSkillMaster.lua")
        scanned.append(backup_zip)

    os.chdir(cwd)
    with open(INDEX_FILE, 'a+') as index:
        for scanned_zip in scanned:
            index.write(scanned_zip + '\n')

    print("Scanned " + str(len(scanned)) + " new backups")
    
os.chdir(PROJECT_PATH)
find_new_backups(TSM_BACKUP_PATH)
