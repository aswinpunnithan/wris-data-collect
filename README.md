# WRIS-DATA-Collect

A simple Python GUI program to save the groundwater level data that can be obtained from  https://indiawris.gov.in/wris/#/.

Note: Download only the **database.py** and **gui.py** files.

## database.py

A Python script, which is used to create a Sqlite database. This database would contain a list of states, and districts in India. Run this file first before running **gui.py**, if you are using this program for the first time. Once the **location_data.db** file has been created, no need to run this file again.

## gui.py

Select the state, district, and the station name from the dropdown list. On clicking **Save Data as CSV** button, the data would be saved as a csv file. Clicking on the <b>Show graph</b> button would display the plot.

## Some screenshots of the program.

<img src="https://github.com/aswinpunnithan/wris-data-collect/blob/main/screenshots/main_window.PNG" width="250">
<img src="https://github.com/aswinpunnithan/wris-data-collect/blob/main/screenshots/data_selected.PNG" width="250">
<img src="https://github.com/aswinpunnithan/wris-data-collect/blob/main/screenshots/graph.PNG" width="250">
