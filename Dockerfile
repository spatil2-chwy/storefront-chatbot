FROM python:3.11-slim

# Node for frontend
RUN apt-get update && apt-get install -y nodejs npm unzip git

WORKDIR /app

COPY . .

RUN python3 -m venv venv
RUN . venv/bin/activate && pip install -r server/requirements.txt

# Install and build frontend
RUN cd client && npm install && npm run build

# Unzip data
RUN unzip data/backend/articles/all_wp_posts.json.zip -d data/backend/articles/ \
 && unzip data/backend/products/item_df.csv.zip -d data/backend/products \
 && unzip data/backend/reviews/all_chewy_products_with_qanda.csv.zip -d data/backend/reviews \
 && unzip data/backend/reviews/results.jsonl.zip -d data/backend/reviews

# Pre-load data
RUN . venv/bin/activate && \
    cd server && python src/load_data.py && \
    cd ../scripts && python run_all_data_loading.py && python generate_landing_products.py

CMD [ "bash" ]
