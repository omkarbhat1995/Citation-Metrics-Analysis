import os
import csv
from helper import (
    process_request, 
    get_author_from_paper_doi, 
    generate_co_author_list, 
    refine_list, 
    store_refined_list, 
    author_group_citation_count
)

def main():
    # Example input - modify this list with the DOIs you want to analyze
    papers_doi = [] 
    
    if not papers_doi:
        print("Please add DOIs to the 'papers_doi' list in main.py to begin.")
        return

    # Ensure output directory exists
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    csv_file_path = os.path.join(output_dir, "metrics.csv")
    headers = ["DOI", "Paper_Title", "Authors", "Percentage Citations from AAG", "Citations", "Author_group size"]
    
    # Initialize the metrics CSV
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(headers)
        
    ignored_dois = []

    for paper_doi in papers_doi:
        print(f"Processing DOI: {paper_doi}")
        papers = process_request(paper_doi)
        
        # Only process if the paper has a significant amount of citations
        if len(papers) > 200:
            title, author_list, author_ids = get_author_from_paper_doi(paper_doi)
            author_group = generate_co_author_list(papers, author_ids)
            refined_paper_list = refine_list(papers, author_group)
            
            # Store the specific paper data
            store_refined_list(papers, refined_paper_list, paper_doi, output_dir=output_dir)
            
            if len(papers) > 0:
                percentage = author_group_citation_count(papers, author_group) / len(papers)
                author_listed = ';'.join(author_list)
                
                data_row = [
                    paper_doi, 
                    title, 
                    author_listed, 
                    percentage * 100, 
                    len(papers), 
                    len(author_group)
                ]
                
                # Append metrics to the main CSV
                with open(csv_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(data_row)
                    
                print(f"Metrics updated for {title}!")
            else:
                ignored_dois.append(paper_doi)
        else:
            print(f"DOI {paper_doi} ignored (Not enough citations: {len(papers)}).")

    if ignored_dois:
        print(f"\nFinished. Ignored DOIs (due to low citation count): {ignored_dois}")

if __name__ == "__main__":
    main()