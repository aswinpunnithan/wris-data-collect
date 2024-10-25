import requests
import urllib3
import sqlite3

# Creating a database to store state_name, state_code, district_name

# Connecting to SQLite database (it will create the file if it doesn't exist)
conn = sqlite3.connect('location_data.db')
cursor = conn.cursor()

# Creating a table for States
cursor.execute('''
CREATE TABLE IF NOT EXISTS states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state_name TEXT NOT NULL,
    state_code TEXT NOT NULL UNIQUE
)
''')

# Creating a table for districts
cursor.execute('''
CREATE TABLE IF NOT EXISTS districts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    district_name TEXT NOT NULL,
    state_code TEXT NOT NULL,
    FOREIGN KEY (state_code) REFERENCES states (state_code)
)
''')

# Calling the API to get data
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
url = "https://indiawris.gov.in/adminboundaries"

# 1. Getting the list of states and union territories
payload = {"stnVal": {"View": "State", "Parent": "All"}}
headers = {"Content-Type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers, verify=False)
states_data = response.json()

# Inserting the states_data into the 'states' table
for state in states_data:
    cursor.execute('''
            INSERT OR IGNORE INTO states (state_name, state_code)
            VALUES (?,?)''', (state['State'], state['State code']))

# 2. Getting the list of districts of each states

# 2.1 Fetching state_code from states table
cursor.execute("SELECT state_code FROM states")
state_codes = cursor.fetchall() # Returns a list of tuples [('AN',), ('AP',), ('AR',), ('AS',)]

# Converting the list of tuples to a list of strings
state_codes = [code[0] for code in state_codes]  # Now list of string ['AN', 'AP', 'AR', 'AS']

# Looping through each state_code and request district data
for state_code in state_codes:
    payload_districts = {"stnVal": {"View": "District", "Parent": f"\"'{state_code}'\""}}
    response_district = requests.request("POST", url, json=payload_districts, headers=headers, verify=False)
    
    if response_district.status_code == 200:
        district_data = response_district.json()

        # Inserting each district into districts table
        for district in district_data:
            cursor.execute('''
                INSERT OR IGNORE INTO districts (district_name, state_code)
                VALUES (?, ?)''', (district['District'], state_code))
    else:
        print("Failed to retrieve")

# Comitting the changes and closing the connection
conn.commit()
conn.close()