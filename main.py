import requests
import urllib3
import csv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://indiawris.gov.in/gwlbusinessdata"

start_year = str(1993)
stop_year = str(2023)
district = 'Bankura'
station = 'B.d.p.anchal'

query = "select TRIM(to_char(businessdata.date, 'yyyy-Mon')) as month, ROUND(AVG(businessdata.level)::numeric,2) as level, to_char(businessdata.date, 'yyyy') as yy, to_char(date, 'mm') as mm FROM public.gwl_timeseries_data as businessdata INNER JOIN public.groundwater_station as metadata on metadata.station_code = businessdata.station_code where 1=1  and metadata.agency_name = 'CGWB' and metadata.state_name = 'West Bengal' and lower(metadata.district_name) = lower('{0}') and lower(metadata.station_name) = lower('{1}') and to_char(businessdata.date, 'yyyy') between '{2}' and '{3}' group by month, yy, mm order by yy, mm".format(district,station,start_year,stop_year)
payload = {"stnVal": {"qry": query}}
headers = {"Content-Type": "application/json"}

response = requests.request("POST", url, json=payload, headers=headers, verify=False)

data = response.json()

def transform_data(input_data):
    transformed_data = [['year', 's1', 's2', 's3', 's4']]
    year_dict = {}
    
    for item in input_data:
        year = item[2]
        value = item[1]
        if item[3] in ['01', '02', '03']:
            quarter = "1"
        elif item[3] in ['04', '05', '06']:
            quarter = "2"
        elif item[3] in ['07', '08', '09']:
            quarter = "3"
        else:
            quarter = "4"
        
        if year not in year_dict:
            year_dict[year] = {'s1': None, 's2': None, 's3': None, 's4': None}
        
        year_dict[year][f's{quarter}'] = value
    
    for year, values in year_dict.items():
        transformed_data.append([int(year), values['s1'], values['s2'], values['s3'], values['s4']])
    
    
    with open('datanew.csv', 'w', newline='') as output_csv:
        csv_writer = csv.writer(output_csv)
        csv_writer.writerows(transformed_data)
    
    return 0

transform_data(data)
