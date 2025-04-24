# AP-GPU Flame Project

## Overview

This project provides a script to profile GPU-powered applications by using NVIDIA Nsight Systems (nsys) along with additional tools to analyze and visualize GPU power consumption. The core functionality is enabled via the `nvidia.sh` script.

## Prerequisites

- A Python virtual environment located at `.venv` with necessary dependencies installed.
- NVIDIA Nsight Systems (nsys) installed.
- `nvidia-smi` available on your system.
- Scripts for data analysis and visualization:
  - `report.py`
  - `flamegraph.pl`

## Setup

1. Ensure you have a virtual environment set up:
   - Activate it by running: `source .venv/bin/activate`
2. Install the required dependencies as per your project guidelines.

## Usage

Run the main profiling script with:
```
./nvidia.sh <executable_path> [<executable_args>...]
```

### How It Works

- The script first activates the virtual environment and extends the PATH to include `.venv/bin`.
- It then profiles the provided executable using NVIDIA Nsight Systems.
- If the target executable is a Python file, it is run via the virtual environment's python interpreter.
- The script logs GPU power draw using `nvidia-smi` and stores results in a `Results/<executable_name>` folder.
- Once profiling is complete, it runs additional steps:
  - **Nsight Stats:** To generate GPU trace statistics.
  - **report.py:** To create a summarized report.
  - **flamegraph.pl:** To generate a GPU energy flame graph.

## Example

For a Python script call it as:
```
./nvidia.sh ./my_app.py --arg1 value1
```

For other executables, use:
```
./nvidia.sh ./my_app --option value
```

## Notes

- Ensure that paths for tools such as `report.py` and `flamegraph.pl` are correctly set up.
- Check that your system configuration meets all the prerequisites before profiling.
