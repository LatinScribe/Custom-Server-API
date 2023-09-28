#!/bin/sh

# Disable filename globbing
set -f

# Make the GET request and store the response
response=$(curl -s "https://grade-logging-api.chenpan.ca/signUp?utorid=chenpan")

# Extract the value from the JSON response
value=$(echo "$response" | awk -F'"' '/token/ {print $4}')

# Output the extracted value
echo "Value: $value"