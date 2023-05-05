import pandas as pd
# Load the CSV file into a pandas DataFrame
df = pd.read_csv('./output_state/ABE.csv',names=['stay_id', 'chartdatetime', 'value', 'valuenum'])

selected_id = 30588857
df_filtered = df[df['stay_id'] == selected_id]

# Convert the 'datetime' column to a datetime object
df_filtered['chartdatetime'] = pd.to_datetime(df_filtered['chartdatetime'])




# Set the 'datetime' column as the DataFrame's index
df_filtered.set_index('chartdatetime', inplace=True)

print(df_filtered)

# # Resample the DataFrame hourly and forward fill missing values
df_hourly= df_filtered.resample('H').ffill()

print(df_hourly)

# # Reset the index and save the resampled DataFrame to a new CSV file
# df_hourly.reset_index().to_csv('./output/your_resampled_file.csv', index=False, header=None)