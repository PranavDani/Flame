#!/usr/bin/python3

import os
import argparse
import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt
from collections import defaultdict

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process flame graph data')
    parser.add_argument('input_file', help='Input CSV file path')
    return parser.parse_args()

def get_file_paths(input_file):
    input_file_smi = input_file.replace('.csv', '') + "-smi.csv"
    input_file_cuda = input_file.replace('.csv', '') + "_cuda_gpu_trace_base.csv"
    script_dir = os.path.dirname(os.path.realpath(__file__))
    full_path_smi = os.path.join(script_dir, input_file_smi)
    full_path_cuda = os.path.join(script_dir, input_file_cuda)
    return full_path_smi, full_path_cuda

def read_csv_files(full_path_smi, full_path_cuda):
    df_smi = pd.read_csv(full_path_smi)
    df_cuda = pd.read_csv(full_path_cuda)
    return df_smi, df_cuda

def get_timestamps(df_cuda):
    min_timestamp_cuda = df_cuda.iloc[:, 0].min()
    max_timestamp_cuda = df_cuda.iloc[:, 0].max() + df_cuda.iloc[:, 1].iloc[-1]
    return min_timestamp_cuda, max_timestamp_cuda

def process_smi_data(df_smi):
    timestamp_plot = pd.to_datetime(df_smi['timestamp'], format='%Y/%m/%d %H:%M:%S.%f')
    timestamp_plot = (timestamp_plot - timestamp_plot.iloc[0])
    df_smi['timestamp_nanoseconds'] = timestamp_plot.dt.total_seconds() * 1e9
    power = df_smi.iloc[:, 1].apply(lambda x: float(x.split()[0]))
    return df_smi, power

def plot_power_consumption(x, y, full_path_smi, min_ts, max_ts):
    target = os.path.basename(full_path_smi).split('.')[0]
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
    output_file = os.path.join(os.path.dirname(full_path_smi), f"{target}_power_consumption.png")
    plt.savefig(output_file)
    print(f"Plot saved as {output_file}")

def combine_data(df_smi, df_cuda, power):
    rows = []
    for i in range(len(df_smi) - 1):
        start_time = df_smi['timestamp_nanoseconds'].iloc[i]
        end_time = df_smi['timestamp_nanoseconds'].iloc[i + 1]
        
        cuda_values = df_cuda[(df_cuda.iloc[:, 0] >= start_time) & (df_cuda.iloc[:, 0] + df_cuda.iloc[:, 1] < end_time)].iloc[:, -1].tolist()
        rows.append([start_time, cuda_values, power.iloc[i]])
    return pd.DataFrame(rows, columns=['timestamp_nanoseconds', 'cuda_values', 'power'])

def calculate_chain_power(df_combined):
    chain_power = defaultdict(float)
    for row in df_combined.iterrows():
        chain = row[1]['cuda_values']
        if len(chain) == 0:
            continue
        ppc = row[1]['power'] / len(chain)
        for chain_record in chain:
            if chain_record:
                chain_power[chain_record] += ppc
    return chain_power

def save_chain_power(chain_power, input_file, script_dir):
    target = input_file.replace('.csv', '')
    target_name = target[target.rfind('/') + 1:]
    output_file = os.path.join(script_dir, f"{target_name}_gpu.collapsed")
    with open(output_file, 'w') as f:
        for chain, power in chain_power.items():
            f.write(f"{target_name};{chain} {power}\n")
    print(f"Chain power saved as {output_file}")

def main():
    args = parse_arguments()
    full_path_smi, full_path_cuda = get_file_paths(args.input_file)
    df_smi, df_cuda = read_csv_files(full_path_smi, full_path_cuda)
    min_timestamp_cuda, max_timestamp_cuda = get_timestamps(df_cuda)
    df_smi, power = process_smi_data(df_smi)
    plot_power_consumption(df_smi['timestamp_nanoseconds'] / 1e9, power, full_path_smi, min_timestamp_cuda, max_timestamp_cuda)
    df_combined = combine_data(df_smi, df_cuda, power)
    chain_power = calculate_chain_power(df_combined)
    save_chain_power(chain_power, args.input_file, os.path.dirname(full_path_smi))

if __name__ == "__main__":
    main()
