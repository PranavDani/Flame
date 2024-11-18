#!/usr/bin/python3

import os
import argparse
import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser(description='Process flame graph data')
parser.add_argument('input_file', help='Input CSV file path')
args = parser.parse_args()

# print(f"Input file: {args.input_file}")
script_dir = os.path.dirname(os.path.realpath(__file__))
full_path = os.path.join(script_dir, args.input_file)
print(f"File path: {full_path}")

# Read the CSV file using pandas
df = pd.read_csv(full_path)

# Access timestamp and power as series if needed
timestamps = df['timestamp']


timestamp_plot = pd.to_datetime(df['timestamp'], format='%Y/%m/%d %H:%M:%S.%f')
# Convert to nanoseconds
timestamp_plot = (timestamp_plot - timestamp_plot.iloc[0])
# Add the new values to the dataframe
df['timestamp_nanoseconds'] = timestamp_plot.dt.total_seconds() * 1e9


power = df.iloc[:, 1]
# Remove the 'W' and convert to float
power = df.iloc[:, 1].apply(lambda x: float(x.split()[0]))

target = os.path.basename(args.input_file).split('.')[0]
print(f"Target: {target}")

# Plot the line graph
plt.figure(figsize=(12, 6))
plt.plot(timestamp_plot.dt.total_seconds(), power, label='Power Consumption', color='b')
plt.xlabel('Time (seconds)')
plt.ylabel('Power')
plt.title('Power Consumption Over Time')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

directory = os.path.dirname(full_path)

# Save the plot as an image file
output_file = os.path.join(directory, f"{target}_power_consumption.png")
plt.savefig(output_file)
print(f"Plot saved as {output_file}")

output_csv = os.path.join(directory, f"{target}_power_consumption.csv")
df.to_csv(output_csv, index=False)
print(f"Data saved as {output_csv}")

