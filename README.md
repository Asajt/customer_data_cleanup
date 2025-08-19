# Customer Data Cleanup Repository

## Overview

This repository contains various scripts and modules for detecting and correcting errors in customer data. The project primarily focuses on validating, identifying, and fixing inconsistencies in names, addresses, phone numbers, and email fields. It is designed to work with Slovenian customer data, but it can be adapted for other datasets.

## Features

- **Synthetic Data Generation**: Creates realistic Slovenian customer data using government datasets.
- **Error Injection**: Introduces common errors found in real-world datasets for testing purposes.
- **Error Detection**: Identifies and categorizes issues in customer data fields.
- **Error Correction**: Fixes detected issues using predefined rules.

## Installation

### Prerequisites

Ensure you have Python installed (>=3.8). You can install the required dependencies using:

```sh
pip install -r requirements.txt
```

---

## Usage

### 1. Generate Synthetic Data

```sh
python utils/customer_data_generator.py
```

This will create a dataset of synthetic Slovenian customer records.

### 2. Inject Errors

```sh
python utils/chaos_engineering.py
```

Adds random errors to the dataset for testing the detection and correction functions.

### 3. Detect Errors

```sh
python detection/detect_names.py
python detection/detect_address.py
python detection/detect_email.py
python detection/detect_phone.py
```

Identifies issues in the dataset, such as formatting mistakes, missing values, duplicates, and invalid characters.

### 4. Correct Errors

```sh
python correction/correct_names.py
python correction/correct_address.py
python correction/correct_email.py
python correction/correct_phone.py
```

Applies predefined correction rules to fix detected errors in the dataset.

---

## Error Types

The project detects and corrects multiple types of errors:

- **Name Errors** (Unnecessary spaces, invalid characters, duplicate values, formatting issues)
- **Address Errors** (House number formatting, missing data, invalid abbreviations, incorrect spacing)
- **Phone Number Errors** (Invalid country code, missing digits, incorrect separators, duplicate numbers)
- **Email Errors** (Invalid domain, missing '@', multiple emails in one field, formatting issues)

---

## License

This project is licensed under the MIT License.

---

## Contact

For any questions or support, please contact the repository maintainer.
