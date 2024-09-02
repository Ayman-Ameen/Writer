import arxiv
import os
from urllib.request import urlretrieve


    
def get_text_query(query_text):
    if query_text is None:
        raise ValueError("Query text is required")
    elif type(query_text) == list:
        query_text = " AND ".join(query_text)
    elif type(query_text) != str:
        raise ValueError("Query text must be a string or a list of strings")
    query_text = " (" + query_text + ") "
    return query_text

    
def download_papers(query_text, max_results=100, time_query=None, output_folder='output', max_char_pdf_name=100):
    os.makedirs(output_folder, exist_ok=True)

    # Print the query and date
    query_text = get_text_query(query_text)
    print("searching for papers related to: ", query_text)
    query = query_text + time_query


    # Search query
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending,
    )
    # Get the results
    results = list(arxiv.Client().results(search))

    if len(results) == 0:
        print("No papers found")
        return
    
    # save the results as JSON
    with open(os.path.join(output_folder,'results.json'), 'w') as f:
        f.write(str(results))
        
    # download the papers
    for counter, result in enumerate(results):
        try: 
            print(result)
            pdf_url = result.pdf_url
            title = result.title
            path_pdf = os.path.join(output_folder,str(counter)+"_"+ title.replace(" ", "_")[0:max_char_pdf_name] + ".pdf")
            urlretrieve(pdf_url, path_pdf)
            print(f"Downloaded: {path_pdf}")
        except Exception as e:
            print(f"Error downloading paper: {e}")


'''
This script search the arXiv database for papers related to a given query in the last 24 hours.
Then, download the papers and save them in a folder.
'''

# Query
# Query list 
query_text_list = [
    ["photonics", "AI", "inverse design"],
    ["photonics", "artificial intelligence", "inverse design"],
    ["photonics", "AI", "design"],
    ["photonics", "artificial intelligence", "design"],
    ["photonics", "artificial intelligence"],
    ["photonics", "AI"],
    ["nanophotonics", "AI", "inverse design"],
    ["nanophotonics", "artificial intelligence", "inverse design"],
    ["nanophotonics", "AI", "design"],
    ["nanophotonics", "artificial intelligence", "design"],
    ["nanophotonics", "artificial intelligence"],
    ["nanophotonics", "AI"],
    ["nanophotonics", "artificial intelligence"],
    # "One dimensional photonic crystal",
    # "Photonics",
    # "Image animation",
]

for query_text in query_text_list:

    query_text = get_text_query(query_text)
    output_folder = query_text.replace(' ', '_').replace('+', '_') + datetime.datetime.now().strftime("_%Y%m%d")

    download_papers(query_text, time_query=get_period(None), output_folder=output_folder)