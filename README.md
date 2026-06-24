# Citation Metric Analysis

An automated tool designed to analyze academic citation networks and measure the percentage of a paper's citations that originate from its own extended co-author network (AAG - Author Affinity Group). 

This project was developed as part of research for an M.S. in Systems Engineering. It leverages the Semantic Scholar API to build dependency graphs of authors, helping to identify "organic" vs. "network-driven" citation metrics.

## Features
* **Bulk DOI Processing:** Fetch citation data, titles, and authors for an array of DOIs.
* **Network Mapping:** Automatically generates a comprehensive co-author group based on the root paper's authors and citing papers.
* **Citation Refinement:** Filters out citations that come from the extended co-author network to isolate independent citations.
* **Metrics Export:** Outputs clear `.csv` files tracking author group size, total citations, and the percentage of citations stemming from within the AAG.

## Prerequisites

You will need Python 3.x and the `requests` library.

`pip install requests`

## Setup & Authentication
This script requires a Semantic Scholar API key to increase rate limits.

##Obtain an API key from Semantic Scholar.

Set your API key as an environment variable to ensure it is not hardcoded into your scripts:

### On Mac/Linux:
`export SEMANTIC_SCHOLAR_API_KEY="your_api_key_here"`
### On Windows (Command Prompt):

`set SEMANTIC_SCHOLAR_API_KEY="your_api_key_here"`

## Usage
1. Open main.py.
2. Populate the papers_doi list with the DOIs of the academic papers you wish to analyze.
3. Run the script:

`python main.py`

Output
The scripts will generate a data/ directory containing:
-`metrics.csv`: A high-level overview of all processed DOIs, including the calculated AAG citation percentages.
-`{paper_doi}_real_papers.csv`: A full list of all papers citing the target DOI.
-`{paper_doi}_refined_real_papers.csv`: The refined list of citing papers, with AAG-associated papers removed.
