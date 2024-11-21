#!/usr/bin/python3

import os
import argparse
import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt
from collections import defaultdict

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
# Get the smallest and largest value for timestamp from df_cuda (first column)
min_timestamp_cuda = df_cuda.iloc[:, 0].min()
max_timestamp_cuda = df_cuda.iloc[:, 0].max()

print(f"Smallest timestamp in df_cuda: {min_timestamp_cuda/1e9}")
print(f"Largest timestamp in df_cuda: {max_timestamp_cuda/1e9}")

# Convert to nanoseconds (Easier to compare with cuda timestamps)
timestamp_plot = pd.to_datetime(df_smi['timestamp'], format='%Y/%m/%d %H:%M:%S.%f')
timestamp_plot = (timestamp_plot - timestamp_plot.iloc[0])
df_smi['timestamp_nanoseconds'] = timestamp_plot.dt.total_seconds() * 1e9

# Remove the 'W' and convert to float
power = df_smi.iloc[:, 1]
power = df_smi.iloc[:, 1].apply(lambda x: float(x.split()[0]))

def plot_power_consumption(x, y, full_path_smi, min_ts, max_ts):
    target = os.path.basename(full_path_smi).split('.')[0]
    print(f"Target: {target}")

    # Plot the line graph
    plt.figure(figsize=(12, 6))
    plt.plot(x, y, label='Power Consumption', color='b')
    plt.fill_between(x, y, where=(x >= min_ts / 1e9) & (x <= max_ts / 1e9), color='skyblue', alpha=0.4)
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

# Call the function
plot_power_consumption(df_smi['timestamp_nanoseconds'] / 1e9, power, full_path_smi, min_timestamp_cuda, max_timestamp_cuda)

# Create a list to store the rows for the new DataFrame
rows = []

# Loop through all values in df_smi['timestamp_nanoseconds']
for i in range(len(df_smi) - 1):
    start_time = df_smi['timestamp_nanoseconds'].iloc[i]
    end_time = df_smi['timestamp_nanoseconds'].iloc[i + 1]
    
    # Filter the CUDA dataframe for values between start_time and end_time
    cuda_values = df_cuda[(df_cuda.iloc[:, 4] >= start_time) & (df_cuda.iloc[:, 4] < end_time)].iloc[:, -1].tolist()
    
    # Join the cuda_values with ";" and append the row to the list
    cuda_values_str = ";".join(map(str, cuda_values))
    rows.append([start_time, cuda_values_str, power.iloc[i]])

# Create a new DataFrame from the rows
df_combined = pd.DataFrame(rows, columns=['timestamp_nanoseconds', 'cuda_values', 'power'])

# Print the resulting DataFrame
# print(df_combined)

# Save the combined DataFrame to a CSV file
# combined_output_csv = os.path.join(os.path.dirname(full_path_smi), f"{os.path.basename(full_path_smi).split('.')[0]}_combined.csv")
# df_combined.to_csv(combined_output_csv, index=False)
# print(f"Combined data saved as {combined_output_csv}")


chain_power = defaultdict(float)

for row in df_combined.iterrows():
    chain = row[1]['cuda_values'].split(';')
    # print (f"Chain: {chain}")
    
    if len(chain) == 0:
        continue
    
    ppc = row[1]['power'] / len(chain)
    
    for chain_record in chain:
        if chain_record:  # Ignore empty chain_record
            chain_power[chain_record] += ppc

target = args.input_file.replace('.csv', '')
target_name = target[target.rfind('/') + 1:]
output_file = os.path.join(script_dir, f"{target}_gpu.collapsed")

with open(output_file, 'w') as f:
    for chain, power in chain_power.items():
        f.write(f"{target_name};{chain} {power}\n")

# print(chain_power)