#!/usr/bin/python3

import os
import argparse
import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description='Process flame graph data')
parser.add_argument('input_file', help='Input CSV file path')
args = parser.parse_args()

# Remove ".csv" from the input_file and append "-smi.csv"
input_file_smi = args.input_file.replace('.csv', '') + "-smi.csv"
input_file_cuda = args.input_file.replace('.csv', '') + "_cuda_kern_exec_trace_base.csv"

script_dir = os.path.dirname(os.path.realpath(__file__))
full_path_smi = os.path.join(script_dir, input_file_smi)
print(f"Smi file path: {full_path_smi}")

full_path_cuda = os.path.join(script_dir, input_file_cuda)
print(f"Cuda file path: {full_path_cuda}")

# Read the CSV file using pandas
df_smi = pd.read_csv(full_path_smi)
df_cuda = pd.read_csv(full_path_cuda)

# Access timestamp and power as series if needed
timestamps = df_smi['timestamp']


# Convert to nanoseconds (Easier to compare with cuda timestamps)
timestamp_plot = pd.to_datetime(df_smi['timestamp'], format='%Y/%m/%d %H:%M:%S.%f')
timestamp_plot = (timestamp_plot - timestamp_plot.iloc[0])
df_smi['timestamp_nanoseconds'] = timestamp_plot.dt.total_seconds() * 1e9


# Remove the 'W' and convert to float
power = df_smi.iloc[:, 1]
power = df_smi.iloc[:, 1].apply(lambda x: float(x.split()[0]))

def plot_power_consumption(x, y, full_path_smi):
    target = os.path.basename(full_path_smi).split('.')[0]
    print(f"Target: {target}")

    # Plot the line graph
    plt.figure(figsize=(12, 6))
    plt.plot(x, y, label='Power Consumption', color='b')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Power')
    plt.title('Power Consumption Over Time')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    directory = os.path.dirname(full_path_smi)

    # Save the plot as an image file
    output_file = os.path.join(directory, f"{target}_power_consumption.png")
    plt.savefig(output_file)
    print(f"Plot saved as {output_file}")

    output_csv = os.path.join(directory, f"{target}_power_consumption.csv")
    df = pd.DataFrame({'timestamp_nanoseconds': x * 1e9, 'power': y})
    df.to_csv(output_csv, index=False)
    print(f"Data saved as {output_csv}")

# Call the function
plot_power_consumption(df_smi['timestamp_nanoseconds'] / 1e9, power, full_path_smi)

# Create a dictionary to store the mapping of timestamps to lists of CUDA values
timestamp_to_cuda_values = {}

# Loop through all values in df_smi['timestamp_nanoseconds']
for i in range(len(df_smi) - 1):
    start_time = df_smi['timestamp_nanoseconds'].iloc[i]
    end_time = df_smi['timestamp_nanoseconds'].iloc[i + 1]
    
    # Filter the CUDA dataframe for values between start_time and end_time
    cuda_values = df_cuda[(df_cuda.iloc[:, 4] >= start_time) & (df_cuda.iloc[:, 4] < end_time)].iloc[:, -1].tolist()
    
    # Append the CUDA values to the map
    timestamp_to_cuda_values[start_time] = cuda_values

# Print the resulting map
for timestamp, values in timestamp_to_cuda_values.items():
    print(f"Timestamp: {timestamp}, CUDA Values: {values}")