#!/bin/bash

for i in {1..20}; do
  echo "Running visit #$i"
  python3 simulate-engagement.py
  sleep $((RANDOM % 5 + 2))  # Random delay between 2–6 seconds
done

