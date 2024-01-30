# Streamline Preprocessing Script

## Overview
The `streamline_preprocess.py` script is a Python utility designed to process and analyze JSON files containing windowed logs. These logs typically include user interaction data from web applications, such as clicks and page visits, along with metadata like session IDs, client times, and browser details. The primary functionality of this script is to extract and analyze the 'name' elements from these logs, generating cyclical list permutations to be fed into a segment log prediction model.

## Features
- **Data Ingestion**: The script can ingest JSON files, handling multiple file inputs and converting timestamps to a standardized format.
- **Data Processing**: Extracts 'name' elements from the logs and generates cyclical list permutations.
- **Dataframe Creation**: Outputs a pandas DataFrame with 'inputs' and 'targets' columns, suitable for being fed into our segment log prediction model.

## Requirements
- Python 3.9.13
- Pandas library
- Custom `distill` library (for date and UUID conversions)

## Input Format
The script is designed to work with JSON files of the following format:

```json
[
    {
        "target": "<element>",
        "path": ["<element>", ..., "<element>"],
        "clientTime": <timestamp>,
        "type": "<event_type>",
        "details": {
            "name": "<name>",
            ...
        },
        "sessionID": "<session_id>",
        ...
    },
    ...
]
```

## Output
The output is a pandas DataFrame displayed in the console. Each row contains:

*   inputs: A list of names leading up to the target.
*   targets: The target name for a given sequence of inputs.

Example output:
```php
inputs             targets
[<name1>, <name2>] <name3>
...
```

## Usage
1. Place your JSON files in a directory structure that the script can access.
2. Ensure Python and all required libraries are installed.
3. Run the script using the command: python streamline_preprocess.py
4. The script will process the input files and output the first few rows of the DataFrame for preview.

## Contact
For questions or potential contributions, please contact <vrife@umd.edu>.