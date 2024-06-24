# This code get all the pdf files in a given directory and convert them to markdown then send them one by one to open AI to summarize them and write a report about them with the references.
import os
import openai
import json
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyMuPDFLoader
import asyncio

class report():
    def __init__(self,):
        self.text = ""
        self.report_type = "Markdown"
        self.counter = 0 
        self.references = ""
        self.summary = ""
    def append_text(self, text):
        # self.text += "# " + f"Paper {self.counter} \n"
        self.text += text
        self.text += "\n\n"
    def append_reference(self, reference):
        self.references += f"Paper {self.counter}: {reference} \n"
    def append_paper(self, text, reference):
        self.append_text(text)
        self.append_reference(reference)
        self.counter += 1
    def write_report(self):
        report = self.text + "\n\n" + self.references
        return report
    def export_report(self, file_loc=None, filename="report.md"):
        if file_loc is not None:
            filename = os.path.join(file_loc, filename)
        with open(filename, "w") as f:
            f.write(self.write_report())
        return filename

def pdf_to_text(pdf_file):
    loader = PyMuPDFLoader(pdf_file)
    pdf_content = loader.load() 
    all_text = ""
    for page in pdf_content:
        all_text += page.page_content
    reference = pdf_content[0].metadata
    return all_text, reference
 
def save_markdown(text, filename):
    with open(filename, "w") as f:
        f.write(text)

def get_all_files_in_folder(folder, extension=".pdf"):
    files_extenstion = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(extension):
                files_extenstion.append(os.path.join(root, file))
    # sort them by number before _ then by the rest of the name
    try :
        # files_extenstion.sort(key=lambda x: int(x.split("/")[-1].split("_")[0]))
        files_extenstion.sort(key=lambda x: int(x.split("/")[-1].split(".")[0]))

    except:
        print("Error in sorting the files")

    return files_extenstion


def get_llm_model(model='gpt-4o', temperature=0.55, max_tokens=4000, api_key=os.environ.get("OPENAI_API_KEY")):
    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key,
        n=1,# number of predictions to generate for each prompt (default is 1)
    )
    return llm

async def prompt_llm(llm, prompt):
    output = await llm.ainvoke(prompt)
    return output.content

def get_llm_max_words(llm):
    # GPT-4-o has a limit of 128k tokens 
    # 1.33 tokens = 1 word
    # 128k tokens = 96k words
    All_models = {
        "gpt-4o": 96000,
        "gpt-3.5-turbo": 4096,
        "gpt-3.5": 4096,
    }
    model_name = llm.model_name
    if model_name in All_models:
        return All_models[model_name]
    else:
        return int(llm.max_tokens/1.33 - 100 )
 
def get_prompt(prompt_name):
    prompts = {

        "summarize": "Summarize the following text:\n \n",
        "outline": "Outline the following text:\n \n",

        "summarize_sci": "Summarize the scientific article below:\n \n ",
        "review_sci": "Write a review of the scientific article below:\n \n ",
        "write_sci": "Write a scientific article based on the followin g prompt:\n \n" ,

        "write_poem": "Write a poem based on the following prompt:\n \n " ,

        "translate_en": "Translate the following text to English:\n \n ",
        "translate_fr": "Translate the following text to French:\n \n ",
        "translate_ar": "Translate the following text to Arabic:\n \n ",
        "translate_de": "Translate the following text to German:\n \n ",
    }
    # assert prompt_name in prompts.keys(), f"Prompt {prompt_name} not found"
    if prompt_name in prompts.keys():
        return prompts[prompt_name] 
    else:
        return prompt_name + ":\n \n "

def process_text(llm, text, prompt_name):
    max_words = get_llm_max_words(llm)
    # prompt = f"Write a review of the scientific article below:\n \n {text}"
    prompt = get_prompt(prompt_name) + text
    return asyncio.run(prompt_llm(llm, prompt[0:int(max_words)]))

# Load the API key from the environment
api_key = os
openai.api_key = api_key

# PDF folder 
folder    = "/Users/ayman/Documents/gpt-researcher/daily_paper_arxiv/Book/Contents"
# prompt_name = "summarize the following chaper of \"Book name\" book: "
prompt_name = "Outline the following chaper of \"Book name\" book: "
# "summarize" # "summarize" or "outline" or "review_sci" or "write_sci" or "write_poem" or "translate_en" or "translate_fr" or "translate_ar" or "translate_de"

extension = '.md' # ".pdf" or ".md"
# file_json = os.path.join(folder, "results.json")
llm = get_llm_model()
report_md = report()
# Load the pdf files
files = get_all_files_in_folder(folder, extension=extension)
for counter, file in enumerate(files):
    try:
        if extension == ".pdf":
            text, reference = pdf_to_text(file)
            save_markdown(text, file.replace(".pdf", ".md"))
        elif extension == ".md":
            with open(file, "r") as f:
                text = f.read()
                reference = ""
        else:
            print(f"Error in loading {file}")
            continue

        processed_text = process_text(llm, text, prompt_name)

        report_md.append_paper(processed_text, reference)
        print(f"Paper {counter} processed")

    except Exception as e:
        print(f"Error in processing {file}: {e}")
        continue

report_md.export_report(folder)



    
    