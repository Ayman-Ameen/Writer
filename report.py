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
        self.text += "# " + f"Paper {self.counter} \n"
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


def get_all_pdf_in_folder(folder):

    pdf_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))


    # sort them by number before _ then by the rest of the name
    pdf_files.sort(key=lambda x: int(x.split("/")[-1].split("_")[0]))

    return pdf_files


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

def summarize_text(llm, text):
    max_words = 96e3
    # GPT-4-o has a limit of 128k tokens 
    # 1.33 tokens = 1 word
    # 128k tokens = 96k words

    prompt = f"Summarize the scientific article below:\n \n {text}"
    return asyncio.run(prompt_llm(llm, prompt[0:int(max_words)]))
# Load the API key from the environment
api_key = os
openai.api_key = api_key

# PDF folder 
pdf_folder = "/Users/ayman/Documents/gpt-researcher/Photonic___AI_models_20240527"
pdf_json = os.path.join(pdf_folder, "results.json")
llm = get_llm_model()
report_md = report()
# Load the pdf files
pdf_files = get_all_pdf_in_folder(pdf_folder)
for counter, pdf_file in enumerate(pdf_files):
    try:
        text, reference = pdf_to_text(pdf_file)
        summary = summarize_text(llm, text)
        report_md.append_paper(summary, reference)
        print(f"Paper {counter} processed")

    except Exception as e:
        print(f"Error in processing {pdf_file}: {e}")
        continue

report_md.export_report(pdf_folder)



    
    