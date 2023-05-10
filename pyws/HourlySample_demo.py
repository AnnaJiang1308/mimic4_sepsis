import pandas as pd
import csv

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

# Set the folder path where the CSV files are stored
folder_path = './output_state/'
columns=['chartdatetime']

# define a new dataframe
df_output = pd.DataFrame(columns=columns)


#FIXME flag only for test
i=0

# Loop through the file paths and read each file into a DataFrame
for itemid in itemid_list:
    
    feature=label[str(itemid)]
    feature_num=feature+'num'
    path = folder_path + feature+'.csv'
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(path,names=['stay_id', 'chartdatetime', feature,feature_num ])

    selected_id = 30588857
    df_filtered = df[df['stay_id'] == selected_id]
    

    # Convert the 'datetime' column to a datetime object
    df_filtered['chartdatetime'] = pd.to_datetime(df_filtered['chartdatetime'])


    # Set the 'datetime' column as the DataFrame's index
    df_filtered.set_index('chartdatetime', inplace=True)


    # # Resample the DataFrame hourly and forward fill missing values
    df_hourly= df_filtered.resample('H').ffill()
    df_hourly=df_hourly.drop(['stay_id'],axis=1)
    #print(df_hourly)
    df_output=pd.merge(df_output,df_hourly,how='outer',on='chartdatetime')
    
    i+=1
    if(i==30): break

df_output.to_csv('./output/stay_id30588857.csv',index=0)


# # Reset the index and save the resampled DataFrame to a new CSV file
# df_hourly.reset_index().to_csv('./output/your_resampled_file.csv', index=False, header=None)