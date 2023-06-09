import shutil
import csv
import pandas as pd
import os
import psycopg2
from psycopg2 import sql

def data_transfer_state(conn, num_stay_ids, percent = 1000):
    # generate the list of itemid
    itemid_list_state=[]
    # generate the dictionary of itemid-abbr
    with open('itemid_info/itemid_label_state.csv', newline='') as csvfile:
        # Create a CSV reader object
        reader = csv.reader(csvfile)
        # Skip the header row
        next(reader)
        # Initialize an empty dictionary and list
        label_state = {}
        itemid_list = []
        # Iterate over the rows in the CSV file
        for row in reader:
            # Add the key-value pair to the dictionary
            label_state[row[0]] = row[1]
            # Add the itemid to the list
            itemid_list.append(row[0])
    
    if os.path.exists('./output/data/data_raw/state'):shutil.rmtree('./output/data/data_raw/state')
    os.makedirs('./output/data/data_raw/state', exist_ok=True)

    # Execute the SQL command
    with conn.cursor() as cursor:
        
        for itemid in itemid_list:
            
            command_count = "select count(distinct(stay_id)) from mimiciv_derived_sepsis.sepsis_state where itemid={};".format(itemid)
            cursor.execute(command_count)
            num = cursor.fetchone()[0]
            
            command = "select stay_id, charttime, valuenum from mimiciv_derived_sepsis.sepsis_state where itemid={} order by charttime;".format(itemid)
            cursor.execute(command)   
            result = cursor.fetchall()
            df=pd.DataFrame(result)
            try:
                df.columns = ['stay_id', 'charttime', 'valuenum']
                df.astype({'stay_id': int, 'charttime': 'datetime64[ns]', 'valuenum': float})
            except (Exception, psycopg2.DatabaseError) as error:
                print("Error executing SQL statement:", error) 
            
            if (num<num_stay_ids*percent and label_state[str(itemid)]!="TemperatureC" ):
                print("drop:{0:40}".format(label_state[str(itemid)]+".csv")+"\tnumber of stay_id:"+str(num))
                
            else:
                df.to_csv('./output/data/data_raw/state/{}.csv'.format(label_state[str(itemid)]),index=0)
                itemid_list_state.append(itemid)
                print("output:{0:40}".format(label_state[str(itemid)]+".csv")+"\tpercent of stay_id:"+str(num/7404))

        cursor.close()
    # print(itemid_list_state)
    return itemid_list_state, label_state


def data_transfer_action_IV_fluid_bolus(conn):
        # generate the dictionary of action
    with open('itemid_info/itemid_label_action.csv', newline='') as csvfile:
        # Create a CSV reader object
        reader = csv.reader(csvfile)
        # Skip the header row
        next(reader)
        # Initialize an empty dictionary and list
        action_label = {}
        a_itemid_list = []
        # Iterate over the rows in the CSV file
        for row in reader:
            # Add the key-value pair to the dictionary
            action_label[row[0]] = row[1]
            # Add the itemid to the list
            a_itemid_list.append(row[0])

    if os.path.exists('./output/data/data_raw/action/IV_fluid_bolus'):shutil.rmtree('./output/data/data_raw/action/IV_fluid_bolus')
    os.makedirs('./output/data/data_raw/action/IV_fluid_bolus')

    with conn.cursor() as cursor:

        for itemid in a_itemid_list:
            if "Dextrose_5%" in action_label[str(itemid)] or "NaCl_0_9%" in action_label[str(itemid)]:
                command = "select stay_id, starttime, endtime, amount from mimiciv_derived_sepsis.sepsis_action_inputevents where itemid={} order by starttime;".format(itemid)
                cursor.execute(command)

                result = cursor.fetchall()
                df = pd.DataFrame(result)
                df.columns = ['stay_id', 'starttime', 'endtime', 'amount']
                
                df['duration'] = df['endtime'] - df['starttime']
                df['duration'] = df['duration'].dt.total_seconds()  # Convert duration to seconds
                df['duration'] = df['duration'] / 60
                df['value_per_minute'] = df['amount'] / df['duration']
                
                df.to_csv('./output/data/data_raw/action/IV_fluid_bolus/{}.csv'.format(action_label[str(itemid)]), index=0)
                print("output action (IV_fluid_bolus):\t"+action_label[str(itemid)]+".csv")
        cursor.close()

def data_transfer_action_vasopressors_equivalent_dose(conn):
    # Get the equivalent dose values of the 5 vasopressors from mimiciv_derived_sepsis.sepsis_action_vasopressors_equivalent_dose: norepinephrine_equivalent_dose

    if os.path.exists('./output/data/data_raw/action/vasopressors'):shutil.rmtree('./output/data/data_raw/action/vasopressors')
    os.makedirs('./output/data/data_raw/action/vasopressors')

    with conn.cursor() as cursor:
        command = "select stay_id, starttime, endtime, norepinephrine_equivalent_dose from mimiciv_derived_sepsis.sepsis_action_vasopressors_equivalent_dose order by starttime;"

        cursor.execute(command)

        result = cursor.fetchall()
        df = pd.DataFrame(result)
        df.columns = ['stay_id', 'starttime', 'endtime', 'norepinephrine_equivalent_dose']  # norepinephrine_equivalent_dose in mcg/kg/min
        
        df['duration'] = df['endtime'] - df['starttime']
        df['duration'] = df['duration'].dt.total_seconds()  # Convert duration to seconds
        df['duration'] = df['duration'] / 60
        df['norepinephrine_equivalent_dose'] = df['norepinephrine_equivalent_dose'].astype(float)
        
        df.to_csv('./output/data/data_raw/action/vasopressors/vasopressors_equivalent_dose.csv', index=0)
        print("output action (vasopressors): vasopressors_equivalent_dose.csv")

        cursor.close()

