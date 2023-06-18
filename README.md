# Knowledge Graph Generation for Web-Based Educational Resources - Master Thesis

This repository contains the Python code developed for the Master's thesis project, which aims to generate a Knowledge Graph (KG) from web-based educational resources. 

## Overview

This project provides a framework that helps educators create KGs from their educational material. The KG makes these materials available in a standardized way, facilitating links to other materials and topics. Moreover, it serves as a stepping stone towards the development of a resource recommendation system that can provide learners with contextualized suggestions based on their individual profiles. The generated KG is especially beneficial for online learning scenarios, supporting self-directed learning and enhancing the understanding of interconnected topics.

## Methodology

The project's methodology follows an Extract-Transform-Load (ETL) schema, where data is extracted from educational resources, transformed into a suitable format, and finally loaded into a Neo4j graph database. The Python code integrates this ETL process into a single pipeline, which also supports handling CSV files for interim results, thus minimizing API requests and reducing the total runtime.

## Dependencies

The project is implemented in Python and makes use of several libraries, including:

- Beautiful Soup: For parsing HTML and XML documents
- rdflib: For working with RDF, a language for representing information
- requests: For making HTTP requests in Python

## Setup Guide

Follow these steps to set up the project on your machine:

1. Clone this repository:

```bash
git clone https://github.com/<your_github_username>/<your_repository_name>
```

2. Navigate into the cloned directory:

```bash
cd <your_repository_name>
```

3. It is recommended to use a virtual environment (optional). You can set it up using the following command:
```bash
python3 -m venv env
```

4. Activate the virtual environment (optional):
```bash
source env/bin/activate  # On Windows use `env\Scripts\activate`
```

5. Install the required dependencies:
```bash
pip install -r requirements.txt
```

6. Create a .env file with the following variables (if you want to use neo4j):
```
NEO4J_URI = "neo4j://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password_here"
```

7. Run the Python script:
```bash
python main.py
```

## Data
You can find the final_data.csv file in the final_data directory, which can be used to quickly reproduce the results.

## Structure
The main code and pipeline can be found in the main.py file. This file executes several functions which can be found in the other files. The otherfiles have a prefix for which part they define functions. The parts are divided into extract, transform, and load part. One can also find this structure in the main.py pipeline.

## Contributing
I welcome contributions!

## License
This project is licensed under the GPLv3 license. For more details, see the LICENSE file.
