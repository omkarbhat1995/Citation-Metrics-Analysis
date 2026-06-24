import os
import re
import csv
import requests
from requests.auth import HTTPBasicAuth

# Best Practice: Load your API key from environment variables, never hardcode it.
API_KEY = os.environ.get('SEMANTIC_SCHOLAR_API_KEY', 'YOUR_API_KEY_HERE')
AUTH = HTTPBasicAuth('apikey', API_KEY)


def process_request(paper_doi: str):
    """
    Uses a paper's DOI to get citing papers' titles and authors.
    Returns a list of papers citing the target DOI.
    """
    whole_data = []
    flag = 0
    next_offset = 0

    while flag != 1:
        try:
            url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_doi}/citations?fields=title,authors&offset={next_offset}&limit=1000'
            rsp = requests.get(url, auth=AUTH)
            rsp.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                print(f"Error 404: Resource not found for DOI {paper_doi}.")
            else:
                print(f"HTTPError: {err}")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break

        data = rsp.json().get('data', [])
        if 'next' in rsp.json():
            next_offset = rsp.json()['next']
        else:
            flag = 1
            
        whole_data.extend(data)

    papers = []
    papers_titles = set()

    for paper in whole_data:
        citing_paper = paper.get("citingPaper", {})
        authors = citing_paper.get("authors", [])
        title = citing_paper.get("title")
        
        auth_list = [[author.get("authorId"), author.get("name")] for author in authors]
        
        if title and title not in papers_titles:
            papers_titles.add(title)
            papers.append([title, auth_list])

    return papers


def get_author_from_paper_doi(paper_doi: str):
    """
    Retrieves the title, unique author names, and author IDs for a given paper DOI.
    """
    url = f'https://api.semanticscholar.org/graph/v1/paper/{paper_doi}/?fields=title,authors&limit=1000'
    rsp = requests.get(url, auth=AUTH)
    rsp.raise_for_status()
    data = rsp.json()
    
    title = data.get('title')
    authors_data = data.get('authors', [])
    
    author_ids = list({entry['authorId'] for entry in authors_data if entry.get('authorId')})
    author_names = list({entry['name'] for entry in authors_data if entry.get('name')})

    return title, author_names, author_ids


def check_membership(list1: list, list2: list):
    """Checks if any member of list1 is present in list2."""
    return any(item in list2 for item in list1)


def generate_co_author_list(papers: list, original_paper_author_list: list):
    """
    Generates an extended co-author list by checking the authors 
    of citing papers against the original author list.
    """
    author_group = list(original_paper_author_list)
    
    for paper in papers:
        auth_ids = [author[0] for author in paper[1]]
        if check_membership(auth_ids, author_group):
            author_group.extend(auth_ids)
            author_group = list(set(author_group))
            
    return author_group


def refine_list(papers: list, author_group: list):
    """
    Refines the list of papers by removing any paper that has at least 
    one author present in the co-author group.
    """
    refined_papers = []
    for paper in papers:
        auth_ids = [author[0] for author in paper[1]]
        if not check_membership(auth_ids, author_group):
            refined_papers.append(paper)
    return refined_papers


def author_group_citation_count(papers: list, author_group: list):
    """Counts how many papers have at least one author in the co-author group."""
    count = 0
    for paper in papers:
        auth_ids = [author[0] for author in paper[1]]
        if check_membership(auth_ids, author_group):
            count += 1
    return count


def sanitize_file_name(name: str):
    """Removes characters that might cause issues in a file name."""
    if not name:
        return "unknown_title"
    return re.sub(r'[\\/:*?"<>|\n]', '_', name)


def store_refined_list(papers: list, refined_papers: list, title: str, output_dir: str = "data"):
    """Stores the original citing papers and the refined list into CSV files."""
    os.makedirs(output_dir, exist_ok=True)
    safe_title = sanitize_file_name(title)
    
    real_papers_path = os.path.join(output_dir, f"{safe_title}_real_papers.csv")
    refined_papers_path = os.path.join(output_dir, f"{safe_title}_refined_real_papers.csv")

    with open(real_papers_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for sublist in papers:
            auths = [author[1] for author in sublist[1]]
            writer.writerow([f"{sublist[0]}:{auths}"])

    with open(refined_papers_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for sublist in refined_papers:
            auths = [author[1] for author in sublist[1]]
            writer.writerow([f"{sublist[0]}:{auths}"])


def get_dois(keywords: list):
    """Fetches DOIs in bulk from Semantic Scholar based on search keywords."""
    doi_list = set()
    for keyword in keywords:
        print(f"Fetching DOIs for keyword: {keyword}")
        next_offset = 0
        token_str = ""
        flag = 0
        
        while flag != 1:
            url = f'https://api.semanticscholar.org/graph/v1/paper/search/bulk?query={keyword}&{token_str}fields=paperId,title&offset={next_offset}&limit=100'
            rsp = requests.get(url, auth=AUTH)
            rsp.raise_for_status()
            
            data = rsp.json().get('data', [])
            for entry in data:
                if entry.get('paperId'):
                    doi_list.add(entry.get('paperId'))
            
            token = rsp.json().get('token')
            if token:
                token_str = f"token={token}&"
            else:
                flag = 1

    return list(doi_list)