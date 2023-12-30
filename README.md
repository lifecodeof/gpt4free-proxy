# GPT4Free Proxy

GPT4Free Proxy is a project that emulates the OpenAI API using GPT-4-free providers. It automatically cycles through providers in case of a failure with the current one.

## Requirements
- Python 3.10 (Note: The quickjs library may encounter issues with Python 3.11)

## Quickstart (PowerShell)
```powershell
# Create and activate a virtual environment
python3.10 -m virtualenv .venv
. .venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt

# Run the application
python3.10 main.py

## Usage
Set your OpenAI client's base URL to "localhost:1337" and you're done.
