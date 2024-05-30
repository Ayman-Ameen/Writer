import arxiv
import datetime
import os
from urllib.request import urlretrieve

def get_period(period):
    
    assert period in ['daily', 'weekly', 'monthly', 'yearly']

    today = datetime.datetime.now()
    template = "%Y%m%d"

    if period == 'daily':
        start_date = today
        end_date = today
    elif period == 'weekly':
        start_date = today - datetime.timedelta(days=7)
        end_date = today
    elif period == 'monthly':
        start_date = today - datetime.timedelta(days=30)
        end_date = today
    elif period == 'yearly':
        start_date = today - datetime.timedelta(days=365)
        end_date = today
    else:
        raise ValueError("Invalid period")
    
    time_query = 'AND submittedDate:[' + start_date.strftime(template) + ' TO ' + end_date.strftime(template) + ']'
    return time_query
    


def download_papers(query_text, max_results=100, time_query=None, output_folder='output', max_char_pdf_name=100):
    os.makedirs(output_folder, exist_ok=True)

    # Print the query and date
    print("searching for papers related to: ", query_text)
    query = "(" + query_text + ") " + time_query 


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
    "Photonic AND AI models",
    # "One dimensional photonic crystal",
    # "Photonics",
    # "Image animation",
    # "Electrical impedance tomography"
]

for query_text in query_text_list:
    output_folder = query_text.replace(' ', '_').replace('+', '_') + datetime.datetime.now().strftime("_%Y%m%d")

    download_papers(query_text, time_query=get_period('yearly'), output_folder=output_folder)