#!/bin/bash

# This script starts the Socket.IO proxy with a sample configuration.
# It sets the required environment variables and then runs the proxy module.

# Run the proxy with the configuration file.
# The -m flag tells Python to run the module as a script.
echo "Starting Socket.IO proxy with config.yaml..."

pip install -e .
socketio-proxy --config config.yaml