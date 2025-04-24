#!/bin/bash

if ! source .venv/bin/activate; then
    echo "Virtual environment activation failed. Please read the readme and install a virtual env."
fi

export PATH=$(pwd)/.venv/bin:$PATH

# Check if sufficient arguments are provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <executable_path> [<executable_args>...]"
    exit 1
fi

# Get the executable path and name
executable_path="$1"
executable_name=$(basename "$1")

# Check if executable is a Python file
if [[ "$executable_name" == *.py ]]; then
    # Remove .py extension from the name
    executable_name="${executable_name%.py}"
    run_cmd=(sudo nsys profile -t cuda,nvtx,osrt,cudnn,cublas -s none -o "Results/$executable_name/$executable_name.nsys-rep" "$(pwd)/.venv/bin/python" "$executable_path" "${@:2}")
else
    run_cmd=(sudo nsys profile -t cuda,nvtx,osrt,cudnn,cublas -s none -o "Results/$executable_name/$executable_name.nsys-rep" "$executable_path" "${@:2}")
fi

results_dir="Results/$executable_name"
echo "Executable name: $executable_name"

# Make a directory to store the results
mkdir -p "$results_dir"
# Fix permissions for the results directory so it can be deleted later
sudo chown -R $(whoami):$(whoami) "$results_dir"

# Run the executable in background and pipe the output to a log file
"${run_cmd[@]}" & executable_pid=$!

echo "Executable PID: $executable_pid is running"

if [ $? -ne 0 ]; then
    echo "Error: Executable failed to run"
    exit 1
fi

# Run nvidia-smi in background and log the power draw of the GPU
sudo nvidia-smi --query-gpu=timestamp,power.draw --format=csv -lms 100 -f "$results_dir/$executable_name-smi.csv" & pid_nvidia=$!

wait $executable_pid
sudo kill $pid_nvidia

echo "Executable PID: $executable_pid has finished running"
echo "Killing nvidia-smi PID: $pid_nvidia"

echo "Running nsys stats"
nsys stats --report cuda_gpu_trace:base --format csv,column --output "$results_dir/$executable_name" "$results_dir/$executable_name.nsys-rep" 

echo "Running report.py"
./report.py "$results_dir/$executable_name.csv"

echo "Running flamegraph.pl for GPU"
./flamegraph.pl --title "GPU Energy Flame Graph" --countname "microwatts" ./Results/$executable_name/$executable_name\_gpu.collapsed > "$results_dir/$executable_name-gpu.svg"