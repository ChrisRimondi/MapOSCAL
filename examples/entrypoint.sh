#!/bin/bash

# Entrypoint script for the application
# This script handles proper signal handling and startup

set -e

# Function to handle shutdown gracefully
shutdown() {
    echo "Received shutdown signal, stopping application..."
    # Send SIGTERM to the main process
    kill -TERM "$child" 2>/dev/null
    wait "$child"
    exit 0
}

# Set up signal handlers
trap shutdown SIGTERM SIGINT

# Start the application in the background
echo "Starting application..."
exec "$@" &

# Store the PID
child=$!

# Wait for the child process
wait "$child"
