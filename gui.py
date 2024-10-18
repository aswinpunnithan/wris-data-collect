import sqlite3
import tkinter as tk
from tkinter import ttk
import requests
import csv
import urllib3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function to fetch states from the database
def fetch_states():
    conn = sqlite3.connect('location_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT state_name FROM states")
    states = [row[0] for row in cursor.fetchall()]
    conn.close()
    return states

# Function to fetch districts based on the selected state
def fetch_districts(state_name):
    conn = sqlite3.connect('location_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT d.district_name
        FROM districts d
        JOIN states s ON d.state_code = s.state_code
        WHERE s.state_name = ?
    ''', (state_name,))
    districts = [row[0] for row in cursor.fetchall()]
    conn.close()
    return districts

# Function to update district dropdown
def update_districts(event):
    selected_state = state_combobox.get() # Get selected state
    districts = fetch_districts(selected_state) # Get corresponding district
    district_combobox['values'] = districts # Set values of district combobox
    district_combobox.set('') # Clear previous values

# Function to get stations
def fetch_stations(selected_state, selected_district):
    url = "https://indiawris.gov.in/gwlbusinessdata"
    query = f"SELECT DISTINCT metadata.station_name FROM public.groundwater_station as metadata INNER JOIN public.gwl_timeseries_data as businessdata ON metadata.station_code = businessdata.station_code WHERE metadata.agency_name = 'CGWB' AND metadata.state_name = \'{selected_state}\' AND lower(metadata.district_name) = lower(\'{selected_district}\') AND businessdata.date BETWEEN '2023-05-01' AND '2024-06-01'"
    payload = {"stnVal": {"qry": query}}
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers, verify=False)
    data = response.json()
    station_list = [row[0] for row in data]
    return station_list

# Function to update station drop down
def update_stations(event):
    selected_state = state_combobox.get()
    selected_district = district_combobox.get()
    stations = fetch_stations(selected_state, selected_district)
    station_combobox['values'] = stations
    station_combobox.set('')

# Function to fetch groundwater data
def fetch_gwl(selected_state, selected_district, selected_station):
    url = "https://indiawris.gov.in/gwltimeseriesdata"
    query = f"select TRIM(to_char(businessdata.date, 'yyyy-Mon')) as month, \n\t\t\t\t\t\t   ROUND(AVG(businessdata.level)::numeric, 2) as level, \n\t\t\t\t\t\t   to_char(businessdata.date, 'yyyy') as yy, \n\t\t\t\t\t\t   to_char(businessdata.date, 'mm') as mm \n\t\t\t\t\tFROM public.gwl_timeseries_data as businessdata \n\t\t\t\t\tINNER JOIN public.groundwater_station as metadata \n\t\t\t\t\tON metadata.station_code = businessdata.station_code \n\t\t\t\t\tWHERE 1=1  and metadata.agency_name = 'CGWB' and metadata.state_name = \'{selected_state}\' and lower(metadata.district_name) = lower(\'{selected_district}\') and lower(metadata.station_name) = lower(\'{selected_station}\')  \n\t\t\t\t\tAND to_char(businessdata.date, 'yyyy-mm') between '2008-01' and '2024-05' \n\t\t\t\t\tGROUP BY month, yy, mm \n\t\t\t\t\tORDER BY yy, mm"
    payload = {"stnVal": {"qry": query}}
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, json=payload, headers=headers, verify=False)
    data = response.json()
    return data

# Function to save the data
def save_gwl():
    selected_state = state_combobox.get()
    selected_district = district_combobox.get()
    selected_station = station_combobox.get()
    global gwl_data
    gwl_data = fetch_gwl(selected_state, selected_district, selected_station)

    # CSV file
    csv_file = f"{selected_station}_groundwater_levels.csv"

    # Opening file for writing
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Year-Month", "Level", "Year", "Month"])
        writer.writerows(gwl_data)

def display_graph():
    # Create a new window for the graph
    graph_window = tk.Toplevel(root)
    graph_window.title("Groundwater Level Graph")

    # Create a new figure for the plot
    fig, ax = plt.subplots(figsize=(6, 6))

    months = [item[0] for item in gwl_data]
    levels = [item[1] for item in gwl_data]

    # Plotting the data
    ax.plot(months, levels, marker='o', linestyle='-', color='b')
    
    # Rotate the x-axis labels for better readability
    ax.set_xticklabels(months, rotation=45, ha='right')
    
    # Setting titles and labels
    ax.set_title("Groundwater Levels Over Time")
    ax.set_xlabel("Month")
    ax.set_ylabel("Water Level (m)")
    
    # Embedding the figure in the Tkinter canvas
    canvas = FigureCanvasTkAgg(fig, master=graph_window)  # A tk.DrawingArea.
    canvas.draw()
    
    # Display the plot
    canvas.get_tk_widget().pack()

# Main window
root = tk.Tk()
root.title("WRIS Data")

# Combobox for states
state_label = tk.Label(root, text="Select state:")
state_label.pack(pady=10)

state_combobox = ttk.Combobox(root, state="readonly")
state_combobox.pack(pady=10)

# Populate state combobox
states = fetch_states()
state_combobox['values'] = states

# Binding state dropdown to update district dropdown
state_combobox.bind("<<ComboboxSelected>>", update_districts)

# Combobox for districts
district_label = tk.Label(root, text="Select district:")
district_label.pack(pady=10)

district_combobox = ttk.Combobox(root, state="readonly")
district_combobox.pack(pady=10)

# Binding district dropdown to update station dropdown
district_combobox.bind("<<ComboboxSelected>>", update_stations)

# Combobox for stations
station_label = tk.Label(root, text="Select station:")
station_label.pack(pady=10)

station_combobox = ttk.Combobox(root, state='readonly')
station_combobox.pack(pady=10)

# Button to save data
save_button = tk.Button(root, text="Save Data as CSV", command=save_gwl)
save_button.pack(pady=30)

# Button to display graph
graph_button = ttk.Button(root, text="Show Graph", command=display_graph)
graph_button.pack(pady=20)

# Run the application
root.geometry("300x350")
root.mainloop()