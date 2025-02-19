# Setting Up a Python Virtual Environment

A virtual environment isolates your project's dependencies from other Python projects and your system's Python installation.

## Creating the Virtual Environment

Navigate to your project directory and run the command below to create a new virtual environment in a directory called `.venv`:

```bash
python3 -m venv .venv
```

## Activating the Virtual Environment

Activate your virtual environment with:

```bash
source .venv/bin/activate
```

You can verify that the virtual environment is active by checking the location of your Python interpreter:

```bash
which python
```

## Deactivating the Virtual Environment

To exit the virtual environment, simply run:

```bash
deactivate
```

For additional details, see the [Using pip and Virtual Environments guide](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
