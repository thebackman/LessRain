""" setup the sqlite tables """

# -- libs

import sqlite3
import os

# -- create the table to hold the data

# location of database file
DB_FILE = os.path.join(os.getcwd(), "weatherdata.db")

# table def
create_string = """
CREATE TABLE 'hourly' (
'key' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
'api_time' TEXT,
'script_run_time' TEXT,
'rain_now' TEXT,
'rain_1h' NUMERIC,
'rain_6h' NUMERIC,
'rain_12h' NUMERIC,
'rain_24h' NUMERIC,
'success' INTEGER,
'origin' TEXT)
"""

# create and commit the table
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
cur.execute(create_string)
conn.commit()
conn.close()
