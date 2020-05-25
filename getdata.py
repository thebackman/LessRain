""" calls the API and gets some data on rain """

### Cron #######################################################################

# sudo crontab -e
# 0 */3 * * * python3 /home/pi/Projects/weather/getdata.py
# run every third hour

### Setup ######################################################################

# libs
import requests
import os
import sqlite3
import datetime
import logging
import json

# logging
LOGFILE = os.path.join("/home/pi/Projects/weather", "getdata.log")
FORMAT = '%(asctime)s %(levelname)s: %(module)s: %(funcName)s(): %(message)s'
logging.basicConfig(level=logging.DEBUG, format = FORMAT, filename = LOGFILE, filemode = "a")

# globals
PROJ_FOLDER = "/home/pi/Projects/weather"
CREDSPATH = os.path.join(PROJ_FOLDER, "api_key.json")

# API key from json file
with open(CREDSPATH, 'r') as f:
    API_KEY = json.load(f)["apikey"]

# location keys (found on website)
# KEY_HANNOVER = "169824"
# KEY_GOTHENBURG = "315909"
KEYS = {"key_hannover": 169824, "key_gothenburg": 315909}

# location of database file 
DB_FILE = os.path.join(PROJ_FOLDER, "weatherdata.db")

### Functions ##################################################################

def dummy_data():
    """ returns dummy data to be written to the database in case of non 200 response """
    
    out = {'epoch_time': '2099-01-01T12:12:12',
           'HasPrecipitation': True,
           'precipitation_1h': 9999,
           'precipitation_6h': 9999,
           'precipitation_12h': 9999,
           'precipitation_24h': 9999,
           'success': 0}
    
    out["script_time"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return out
    
def extract_data(json_data):
    """ extracts the data and returns a dict in case of 400 response"""
    
    out = {}
    
    raw = json_data[0]
    
    # get the timestamp of the recorded data
    out["epoch_time"] = datetime.datetime.fromtimestamp(raw["EpochTime"])\
    .strftime("%Y-%m-%dT%H:%M:%S")

    # get current timestamp, when the script was run
    out["script_time"] = datetime.datetime.now()\
    .strftime("%Y-%m-%dT%H:%M:%S")
    
    # comes something from the sky now?
    out["HasPrecipitation"] = raw["HasPrecipitation"]
    
    # get the 24h of percipation
    out["precipitation_1h"] = raw["PrecipitationSummary"]["PastHour"]["Metric"]["Value"]
    out["precipitation_6h"] = raw["PrecipitationSummary"]["Past6Hours"]["Metric"]["Value"]
    out["precipitation_12h"] = raw["PrecipitationSummary"]["Past12Hours"]["Metric"]["Value"]
    out["precipitation_24h"] = raw["PrecipitationSummary"]["Past24Hours"]["Metric"]["Value"]
    
    # success 
    out["success"] = 1
    
    return out


def do_api_call(location_key, raw = False):
    """ calls the api and gets the lastest observations"""
    
    # adress to api
    adr = (f"http://dataservice.accuweather.com" +
           f"/currentconditions/v1/{location_key}" +
           f".json?apikey={API_KEY}&details=true")
    
    # make API call and get data
    response = requests.get(adr)
    
    # check if successful and extract data
    if response.status_code == 200:
        # get all data
        if raw == False:    
            data = extract_data(response.json())
        else:
            data = response.json()
    else:
        data = dummy_data()
    
    return(data)

def write_to_sqlite(the_dict, key):
    """ write the API response to the DB file that is definied in 'run_once' """
    
    # initiate the connection to the DB
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # write the data to the DB
    cur.execute("""
                INSERT INTO hourly (
                api_time,
                script_run_time,
                rain_now,
                rain_1h,
                rain_6h,
                rain_12h,
                rain_24h,
                success,
                origin)
                VALUES ('{a}', '{b}', {c}, {d}, {e}, {f}, {g}, {h}, {i})
                """.\
              format(a = data["epoch_time"],
                     b = data["script_time"],
                     c = data["HasPrecipitation"],
                     d = data["precipitation_1h"],
                     e = data["precipitation_6h"],
                     f = data["precipitation_12h"],
                     g = data["precipitation_24h"],
                     h = data["success"],
                     i = key))
          
    # commit changes and close
    conn.commit()
    conn.close()

### Get the data ###############################################################

logging.debug("Making an API call")
for key, value in KEYS.items():
    print("Start iterating and do API calls")
    print(key)
    print(value)    
    data = do_api_call(location_key = value, raw = False)
    write_to_sqlite(the_dict = data, key = value)
    
# release the logging
logging.shutdown()
