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

- **`column_store_zone_map_num.py`**: Implements zone mapping for numerical columns.
- **`column_store_zone_map_cat.py`**: Implements zone mapping for categorical columns.
- **`column_store_encoded.py`**: Adds categorical encoding for columns like `Town`.
- **`column_store_combined_num.py`**: Combines zone mapping (numerical) and categorical encoding.
- **`column_store_combined_cat.py`**: Combines zone mapping (categorical) and categorical encoding.
- **`column_store_mp.py`**: Implements multiprocessing for query operations.

### Utilities

- **`column_preprocess.py`**: Contains helper classes for preprocessing, such as `CategoricalEncoder` and `ZoneMappingNum`.

### Query Execution

- **`query.py`**: (Not included in the provided files) Presumably handles query orchestration and execution.

## How to Run

1. **Prepare the Dataset**:
     - Place the dataset file (`ResalePricesSingapore.csv`) in the project directory.

2. **Run the Main Scripts**:
     - Each script contains a `main()` function that demonstrates the functionality of the respective implementation.
     - Example:

         ```bash
         python column_store.py
         ```

3. **Choose an Optimization**:
     - To test specific optimizations, run the corresponding script:
         - Zone Mapping (Numerical): `column_store_zone_map_num.py`
         - Zone Mapping (Categorical): `column_store_zone_map_cat.py`
         - Categorical Encoding: `column_store_encoded.py`
         - Combined Optimizations: `column_store_combined_num.py` or `column_store_combined_cat.py`
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

- Python 3.8+
- Required libraries:
  - `pandas`
  - `multiprocessing`

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

## Future Improvements

- Add support for more complex queries.
- Optimize memory usage for large datasets.
- Implement additional indexing techniques for faster lookups.

## Contributors

- Bryan
- Darren
- Jin Yang
