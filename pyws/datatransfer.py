import pymysql
import csv
import pandas as pd

# generate the dictionary of itemid-abbr
with open('itemid_label.csv', newline='') as csvfile:
    # Create a CSV reader object
    reader = csv.reader(csvfile)
    # Skip the header row
    next(reader)
    # Initialize an empty dictionary and list
    label = {}
    itemid_list = []
    # Iterate over the rows in the CSV file
    for row in reader:
        # Add the key-value pair to the dictionary
        label[row[0]] = row[1]
        # Add the itemid to the list
        itemid_list.append(row[0])

        
conn = pymysql.connect(host='localhost', user='root', password='Jhx081399', db='mimic4')


# create table

# Execute the SQL command

with conn.cursor() as cursor:
    
    for itemid in itemid_list:
        command = "select stay_id, charttime, value, valuenum from Charteventsneeded where itemid={} order by charttime;".format(itemid)
        cursor.execute(command)
            
        result = cursor.fetchall()
        df=pd.DataFrame(result)
        df.to_csv('./output/{}.csv'.format(label[str(itemid)]),index=0)
        print("output:"+label[str(itemid)]+".csv")

conn.close()


