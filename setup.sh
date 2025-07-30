#!/bin/bash

# Navigate to project root
cd storefront-chatbot

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
venv/bin/pip install -r server/requirements.txt --no-cache-dir

# git checkout dev [REMOVE!!!]

# Unzip data files
unzip data/backend/articles/all_wp_posts.json.zip -d data/backend/articles/ 
unzip data/backend/products/item_df.csv.zip -d data/backend/products
unzip data/backend/reviews/all_chewy_products_with_qanda.csv.zip -d data/backend/reviews
unzip data/backend/reviews/results.jsonl.zip -d data/backend/reviews

# Load data
cd server
python src/load_data.py

# Run custom scripts
cd ../scripts
python run_all_data_loading.py
python generate_landing_products.py

# Build frontend
cd ../client
npm install
npm run build
