#!/bin/bash
set -e

# Install system dependencies
apt-get update
apt-get install -y libsndfile1 ffmpeg

# Install Python packages
pip install -r requirements.txt
