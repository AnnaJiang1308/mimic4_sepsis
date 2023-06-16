import shutil
import csv
import pandas as pd
import numpy as np
import os
from datetime import timedelta
import psycopg2
from psycopg2 import sql
from sklearn.impute import KNNImputer
from sklearn.neighbors import KNeighborsRegressor

# Create a custom imputation function
def lq_distance_imputer(X):
    # Calculate the Lq distances
    distances = np.abs(X - X[:, -1].reshape(-1, 1)) ** q

    # Calculate the weights based on the inverse distances
    weights = 1 / distances

    # Normalize the weights
    weights /= np.sum(weights, axis=1).reshape(-1, 1)

    # Multiply the weights with the feature values and compute the weighted mean
    return np.sum(weights * X[:, :-1], axis=1)

def hourly_sample_state(selected_id, itemid_list_state, label_state, k = 5):
    # Set the folder path where the CSV files are stored
    folder_path = './output/data/data_raw/state/'
    columns=['chartdatetime']

    # define a new dataframe
    df_output = pd.DataFrame(columns=columns)


    #FIXME: flag only for test
    i=0

    # Loop through the file paths and read each file into a DataFrame
    for itemid in itemid_list_state:
        
        feature=label_state[str(itemid)]
        path = folder_path + feature+'.csv'
        
        # Load the CSV file into a pandas DataFrame
        dtypes={'stay_id':str,'chartdatetime':str,feature:str}
        df = pd.read_csv(path,names=['stay_id', 'chartdatetime', feature ],dtype=dtypes)
        df['stay_id'] = pd.to_numeric(df['stay_id'], errors='coerce')
        
        # Filter the DataFrame to only the rows from the selected stay_id
        df_filtered = df[df['stay_id'] == selected_id]
        
        # Convert the 'datetime' column to a datetime object
        df_filtered.loc[:,'chartdatetime'] = pd.to_datetime(df_filtered['chartdatetime'].copy())
        #df_filtered['chartdatetime'] = df_filtered['chartdatetime'].apply(pd.to_datetime)

        # Set the 'datetime' column as the DataFrame's index
        df_filtered.set_index('chartdatetime', inplace=True)
        
        # # Resample the DataFrame hourly and forward fill missing values
        df_hourly= df_filtered.resample('H').ffill()
        df_hourly=df_hourly.drop(['stay_id'],axis=1)
        
        df_output['chartdatetime'] = pd.to_datetime(df_output['chartdatetime'])
        #df_output = pd.concat([df_output, df_hourly], join="outer",sort=False)
        df_output=pd.merge(df_output,df_hourly,how='outer',on='chartdatetime')
        
        
        if feature=='PH_A':
        
            missing_rows = df_output['TemperatureF'].isnull()
            #print(missing_rows)
            df_output.loc[missing_rows,'TemperatureF'] = (df_output.loc[missing_rows,'TemperatureC'] * 9 / 5 + 32)
            df_output=df_output.drop(['TemperatureC'],axis=1)
        
        #imputer = KNNImputer(n_neighbors=k,weights='distance',missing_values=float('NaN'))
        
        if not df_output[feature].isnull().all():
        
            imputer = KNNImputer(n_neighbors=k,weights=lq_distance_imputer,missing_values=float('NaN'))
            imputed_values=imputer.fit_transform(df_output[feature].values.reshape(-1,1))
            df_output[feature] = imputed_values

    os.makedirs('./output/data/data_hourly_sample/state', exist_ok=True)
    df_output.reset_index().to_csv(f'./output/data/data_hourly_sample/state/stay_id{selected_id}.csv',index=0)

    # print(i)
    # # Reset the index and save the resampled DataFrame to a new CSV file
    # df_hourly.reset_index().to_csv('./output/your_resampled_file.csv', index=False, header=None)  

def hourly_sample_action_IV_fluid_bolus(selected_id): # (mL/1 hour)
    # Create a list of two fluid types
    fluid_types = ['Dextrose_5%', 'NaCl_0_9%']
    
    # Initialize an empty DataFrame to store the results
    df_resampled_all = pd.DataFrame()

    # For each fluid type
    for fluid in fluid_types:
        # Read the CSV file and convert the date column to datetime objects
        df = pd.read_csv(f'./output/data/data_raw/action/IV_fluid_bolus/{fluid}.csv')
        df['starttime'] = pd.to_datetime(df['starttime'])
        df['endtime'] = pd.to_datetime(df['endtime'])

        # Filter the selected stay_id
        df_filtered = df[df['stay_id'] == selected_id].copy()

        # Create a new DataFrame for minute-wise data
        df_minutes = []

        # Generate data for each minute for each row
        for _, row in df_filtered.iterrows():
            minutes = int((row['endtime'] - row['starttime']).total_seconds() / 60)
            for minute in range(minutes):
                time = row['starttime'] + timedelta(minutes=minute)
                df_minutes.append({'stay_id': row['stay_id'], 
                                   'starttime': time, 
                                   'endtime': time + timedelta(minutes=1), 
                                   f'{fluid}_per_hour': row['value_per_minute'], 
                                   'duration': 1})

        # Convert the list to a DataFrame
        df_minutes = pd.DataFrame(df_minutes)

        # Set starttime as the index
        df_minutes.set_index('starttime', inplace=True)

        # Resample and calculate the total fluid per hour
        df_resampled = df_minutes[f'{fluid}_per_hour'].resample('H').sum()

        # Reset the index
        df_resampled = df_resampled.reset_index()

        # Add the resampled results of this fluid type to the overall result DataFrame
        if df_resampled_all.empty:
            df_resampled_all = df_resampled
        else:
            df_resampled_all = pd.merge(df_resampled_all, df_resampled, on='starttime')

    # Calculate the sum of the two fluid types per hour
    df_resampled_all['IV_fluid_bolus_per_hour'] = df_resampled_all['Dextrose_5%_per_hour'] + df_resampled_all['NaCl_0_9%_per_hour']

    # If the amount is missing, replace it with 0
    df_resampled_all.fillna(0, inplace=True)

    # Discretize norepinephrine_equivalent_dose_rate
    bins = [-np.inf, 0, 12.5, 45, 132.5, np.inf]
    labels = [1, 2, 3, 4, 5]
    df_resampled_all['Discretized_IV_fluid_bolus'] = pd.cut(df_resampled_all['IV_fluid_bolus_per_hour'], bins=bins, labels=labels)

    # Write to a CSV file
    os.makedirs('./output/data/data_hourly_sample/action/IV_fluid_bolus/', exist_ok=True)
    df_resampled_all.to_csv(f'./output/data/data_hourly_sample/action/IV_fluid_bolus/{selected_id}.csv', index=False)

def hourly_sample_action_vasopressors_equivalent_dose(selected_id): # (mcg/kg/min)
    # Read the CSV file and convert the date columns to datetime objects
    df = pd.read_csv('./output/data/data_raw/action/vasopressors_norepinephrine_equivalent_dose.csv')
    df['starttime'] = pd.to_datetime(df['starttime'])
    df['endtime'] = pd.to_datetime(df['endtime'])

    # Filter for the selected stay_id
    df_filtered = df[df['stay_id'] == selected_id].copy()

    # Create a new DataFrame to hold data by minute
    df_minutes = []

    # For each row, generate data for each minute
    for _, row in df_filtered.iterrows():
        minutes = int((row['endtime'] - row['starttime']).total_seconds() / 60)
        for minute in range(minutes):
            time = row['starttime'] + timedelta(minutes=minute)
            df_minutes.append({'stay_id': row['stay_id'], 
                               'starttime': time, 
                               'endtime': time + timedelta(minutes=1), 
                               'norepinephrine_equivalent_dose_rate': row['norepinephrine_equivalent_dose_rate'], 
                               'duration': 1})

    # Convert the list to a DataFrame
    df_minutes = pd.DataFrame(df_minutes)

    # Set starttime as the index
    df_minutes.set_index('starttime', inplace=True)

    # Resample and get the max value for each hour
    df_resampled = df_minutes['norepinephrine_equivalent_dose_rate'].resample('H').max()

    # If the norepinephrine_equivalent_dose_rate is NaN, replace it with 0
    df_resampled.fillna(0, inplace=True)

    # Reset the index
    df_resampled = df_resampled.reset_index()

    # Discretize norepinephrine_equivalent_dose_rate
    bins = [-np.inf, 0, 0.08, 0.22, 0.45, np.inf]
    labels = [1, 2, 3, 4, 5]
    df_resampled['Discretized_vasopressors'] = pd.cut(df_resampled['norepinephrine_equivalent_dose_rate'], bins=bins, labels=labels)

    # Write the discretized DataFrame to a CSV file
    os.makedirs('./output/data/data_hourly_sample/action/discrete_resampled_vasopressors_norepinephrine_equivalent_dose', exist_ok=True)
    df_resampled.to_csv(f'./output/data/data_hourly_sample/action/discrete_resampled_vasopressors_norepinephrine_equivalent_dose/{selected_id}.csv', index=False)
