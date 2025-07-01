# 📁 Scripts Directory Organization

This directory contains all data processing scripts and utilities for the Storefront Chatbot project, organized by specific function and purpose.

## 🏗️ Directory Structure

### 🔧 `chromadb-builders/`
ChromaDB vector database building and content processing scripts:
- **`productdbbuilder.py`** - Builds the product vector database from CSV data with embeddings
- **`articledbbuilder.py`** - Processes and builds article content vector database  
- **`review_synthesis_dbbuilder.py`** - Synthesizes and builds review vector database
- **`fetch_article_content.py`** - Fetches article content from external sources
- **`README.md`** - Detailed instructions for ChromaDB building

### 🔄 `data-loaders/`
Data loading and system setup scripts:
- **`load_data.py`** - Loads user and pet data into the SQL application database
- **`generate_credentials.py`** - Generates realistic user credentials and authentication data
- **`assign_pets.py`** - Randomly assigns pet profiles to customer accounts

### 📊 `data/`
Large datasets and data files organized by source:
- **`all_chewy_products_with_qanda.csv`** - Complete product catalog with Q&A data (465MB)
- **`results.jsonl`** - Review synthesis results for vector embedding (24MB)
- **`server-data/`** - Server-specific data files:
  - `customers_full.tsv` - Customer data without credentials
  - `customers_full_with_creds.tsv` - Customer data with generated login credentials
  - `pet_profiles.tsv` - Pet profile data without assignments
  - `pet_profiles_assigned.tsv` - Pet profiles assigned to customers

### 🗄️ `databases/`
Vector databases and related cache files:
- **`chroma_db/`** - ChromaDB vector database with product and review embeddings (3.6GB)
- **`metadata_filters_cache.json`** - Cached metadata filters for search performance optimization

## 🚀 Usage Workflow

### 1️⃣ **Building Vector Databases**
Navigate to `chromadb-builders/` and run the database builders:
```bash
cd chromadb-builders/
python productdbbuilder.py       # Build product vectors
python review_synthesis_dbbuilder.py  # Build review vectors
python articledbbuilder.py       # Build article vectors (optional)
```

### 2️⃣ **Loading Application Data**
Navigate to `data-loaders/` and run the data loading scripts:
```bash
cd data-loaders/
python generate_credentials.py   # Generate user credentials (if needed)
python assign_pets.py           # Assign pets to customers (if needed)
python load_data.py             # Load data into SQL database
```

### 3️⃣ **Managing Large Files**
- Large datasets are centralized in `data/` for easy access and organization
- Database files are managed in `databases/` with proper version control exclusions

## ⚙️ Setup Requirements

### Prerequisites
- **Python 3.10+** with required packages (see `server/requirements.txt`)
- **OpenAI API Key** for embedding generation
- **ChromaDB** for vector database operations
- **Pandas** for data processing

### Environment Setup
1. Ensure you have the complete product CSV file in `data/`
2. Set up your OpenAI API key in the server environment
3. Run ChromaDB builders first, then data loaders
4. The `databases/` directory will be populated with vector databases and cache files

## 📋 Notes

- **Order Matters**: Always run ChromaDB builders before data loaders
- **Large Files**: CSV and JSONL files are kept separate from scripts for better Git management
- **Path References**: All scripts use relative paths from their respective directories
- **Performance**: Metadata cache is automatically generated and stored for faster search operations
- **Development Mode**: Review synthesis file is kept light for faster development iterations

## 🔍 Troubleshooting

- **Missing Dependencies**: Install requirements from `server/requirements.txt`
- **Path Errors**: Ensure you're running scripts from their respective directories
- **Large File Issues**: Large data files may need to be downloaded separately
- **ChromaDB Errors**: Ensure ChromaDB database is built before running the application 