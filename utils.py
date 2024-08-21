import os 
import sys
import yaml
import asyncio
import operator
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated, Sequence, List
from langchain_core.messages import BaseMessage



def read_file(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found")
    
    if file_path.endswith(".yaml"):
        with open(file_path, 'r') as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    else:
        with open(file_path, 'r') as file:
            return file.read()
        
def save_file(text, filename, continue_on_exists=False):

    mode = "w" if not continue_on_exists else "a"

    if os.path.exists(filename):
        print(f"File {filename} already exists. The new output will be appended to the existing file" if continue_on_exists else f"File {filename} already exists. It will be overwritten")

    if filename.endswith(".yaml"):
        with open(filename, mode) as f:
            yaml.dump(text, f)
    if filename.endswith(".md"):
        with open(filename, mode) as f:
            f.write(text)
    else:
        raise ValueError("File extension not supported")
    
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

def run_agent(llm_properties, prompt):
    llm = get_llm_model(**llm_properties)
    output = asyncio.run(prompt_llm(llm, prompt))
    return output




class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    name: Annotated[Sequence[BaseMessage], operator.add]