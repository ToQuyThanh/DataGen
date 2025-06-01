# Data Generator

## Overview

**Data Generator** is a Python package designed to generate synthetic data with customizable schemas and support for generating "dirty" (noisy or imperfect) data. The project provides a modular architecture for easy extension, data exporting, and integration with Streamlit for interactive UI.

---

## Project Structure
```
src/
└── data_generator/
    ├── main.py                 # Application entrypoint (Streamlit app runner)
    ├── core/                   # Core logic: data generation, schema definitions, dirty data simulation, export functions
    │   ├── __init__.py
    │   ├── generator.py
    │   ├── schema.py
    │   ├── dirty.py
    │   └── export.py
    ├── ui/                     # Streamlit UI components and layout
    │   ├── __init__.py
    │   └── streamlit_ui.py
    └── utils/                  # Utility helper functions
        ├── __init__.py
        └── helpers.py

.streamlit/
└── config.toml                 # Streamlit configuration

data/
└── generated_sample.xlsx       # Example generated data file

tests/
└── __init__.py
└── test_generator.py
└── test_schema.py
└── test_export.py
```


---

## Features

- Generate synthetic data based on user-defined schemas
- Support for generating dirty or imperfect data for realistic testing
- Export generated data to common formats such as Excel, CSV, and JSON
- Interactive Streamlit-based UI for configuring and running data generation
- Modular and extensible package structure for easy maintenance and enhancement

---

## Installation

```bash
git clone <repository_url>
cd data-generator
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -e .
