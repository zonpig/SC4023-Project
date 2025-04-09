# SC4023-Project: Resale Price Data Analysis

This project implements a columnar data store for analyzing resale price data in Singapore. The system supports various query operations, including minimum price, standard deviation of price, average price, and minimum price per square meter. The project also explores optimizations such as zone mapping, categorical encoding, and multiprocessing to improve query performance.

## Features

- **Columnar Data Store**: Implements a columnar data structure for efficient data storage and retrieval.
- **Query Operations**:
  - Minimum price
  - Standard deviation of price
  - Average price
  - Minimum price per square meter
- **Optimizations**:
  - **Zone Mapping**: Divides data into zones for faster filtering.
  - **Categorical Encoding**: Encodes categorical data for efficient processing.
  - **Multiprocessing**: Parallelizes query operations to leverage multiple CPU cores.
  - **Shared Scan**: Combines multiple queries into a single scan to reduce redundant computations.

## File Structure

### Core Components

- **`columns.py`**: Defines the base column structure and specific column types (e.g., `Month`, `Town`, `ResalePrice`).
- **`column_store.py`**: Implements the main columnar data store and query operations.

### Optimizations

- **`column_store_encoded.py`**: Adds categorical encoding for columns to `Town`.
- **`column_store_zone_map_num.py`**: Implements zone mapping for area column.
- **`column_store_zone_map_cat.py`**: Implements zone mapping for FlatModel columns based on area column.
- **`column_store_mp.py`**: Implements multiprocessing for query operations.

### Utilities

- **`column_preprocess.py`**: Contains helper classes for preprocessing, such as `CategoricalEncoder` and `ZoneMappingNum`.

### Query Execution

- **`query.py`**: Provides Query class to handle query function for the columns.

## How to Run

1. **Prepare the Dataset**:
     - Place the dataset file (`ResalePricesSingapore.csv`) in the project directory.

2. **Run the Main Scripts**:
     - To run all comparisons, execute the `project.py` script. This script will run all the implementations and print the results for each.
     - Example:

         ```bash
         python project.py
         ```

3. **Choose an Optimization**:
     - To test specific type of column store, run the corresponding script:
        - Original: `column_store.py`
        - Categorical Encoding: `column_store_encoded.py`
        - Zone Mapping (Numerical): `column_store_zone_map_num.py`
        - Zone Mapping (Categorical): `column_store_zone_map_cat.py`
        - Multiprocessing: `column_store_mp.py`

## Example Output

Each script outputs the results of the queries along with the time taken for execution. For example:

```txt
Minimum price: 350000
Time taken for min_price: 0.12 seconds

StdDev price: 15000.45
Time taken for sd_price: 0.15 seconds

Average price: 400000.75
Time taken for avg_price: 0.10 seconds

Minimum price per sqm: 4500.25
Time taken for min_price_per_sqm: 0.13 seconds
```

## Customization

- **Matric Number**: Update the `matric_number` variable in the `main()` function of each script to customize the year, month, and town used for queries.
- **Zone Mapping**: Adjust the number of zones in zone mapping scripts to experiment with performance.

## Dependencies

Install dependencies using venv:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

## Contributors

- Bryan
- Darren
- Jin Yang
