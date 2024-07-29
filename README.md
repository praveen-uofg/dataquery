# DataQuery [![Testing and Static Analysis](https://github.com/qudo-ai/querycraft/actions/workflows/general-pipeline.yml/badge.svg)](https://github.com/qudo-ai/querycraft/actions/workflows/general-pipeline.yml)

## About
DataQuery is a Python package designed to simplify interactions with PostgreSQL databases. It leverages SQLAlchemy and pandas to provide an intuitive interface for retrieving, updating, inserting, and deleting data within a database. This package is ideal for data scientists and developers looking for a streamlined way to handle database operations.

## Features
- Easy retrieval of data into pandas DataFrames.
- Simplified update, insert, and delete operations.
- Customizable query capabilities with filtering criteria.
- Designed with best practices in database connections and session management.

## Installation

Ensure you have Python 3.11 or higher installed. It's recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install DataQuery using pip:

```bash
pip install dataquery
```

Or, if you're installing directly from the source:

```bash
git clone https://github.com/yourusername/querycraft.git
cd dataquery
pip install .
```

## Usage

### Initialization

First, initialize the DataQuery object with your database credentials:

```python
from dataquery import DataQuery

qc = DataQuery(host='localhost', port='5432', username='your_username', password='your_password',
                database='your_database')
```

### Retrieving Data

To retrieve data from a table:

```bash
df = qc.retrieve_data('table_name', {'column_name': 'value'})
```

### Updating Data

To update data in a table:

```bash
from pandas import DataFrame

data = DataFrame({...})  # Your data to update
qc.update_data('table_name', ['column_to_match'], data)
```

Replace `'table_name'`, `['column_to_match']`, and `data` with your specific table name, columns to match, and DataFrame containing the new data.

## Contribution and Development Guidelines

Contributions to DataQuery are welcome! If you're interested in contributing, please follow these guidelines:


1. **Create a New Branch**: Create a new branch for your feature or fix.
2. **Commit Your Changes**: Make your changes and commit them to your branch.
3. **Push to Your Brach**: Push your branch on GitHub.
4. **Submit a Pull Request**: Submit a pull request from your branch to the development branch.

Please ensure your code adheres to PEP 8 standards and include tests for new features or bug fixes.

## License

DataQuery is licensed under the BSD 3-Clause License. See the LICENSE file for more details.
