import os
import sys
import yaml
import functools
import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
from utils import read_file, save_file, run_agent, get_llm_model, AgentState
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import BaseMessage, AIMessage


'''
To enable a large language model (LLM) to perform a multi-agent task such as writing a cover letter, several specialized agents or components can be utilized
'''
def save_graph(graph, output_dir):
    output_file = os.path.join(output_dir, "graph.png")
    with open(output_file,'wb') as file:
        file.write(graph.get_graph(xray=True).draw_mermaid_png())
    return output_file

def combine_messages(messages: list):
    messages = [message.content if isinstance(message, AIMessage) else message for message in messages]
    return "\n # " + "\n # ".join(messages)

def get_watched_messages(state, watches):
    watched_messages = []
    for watch in watches:
        message = state["messages"][state["name"].index(watch)]
        if isinstance(message, AIMessage):
            message = message.content
        watched_messages.extend(
           [ "# " +  watch + ":\n" + message]
        )
    return {"context": "\n".join(watched_messages)}
        


def action_llm_response(state="", name="", watch=[], llm_prompt=""):
    llm = get_llm_model()
    watched_messages = get_watched_messages(state, watch)
    prompt = llm_prompt.format(**watched_messages)
    print("current agent: ", name)
    return {
        "name": [name],
        "messages": [llm.invoke(prompt)]
    }

def action_combine_messages(state="", name="", input={},llm_prompt=""):
    return { "name": [name],
             "messages":  [llm_prompt.format(**input)]}




# The main function that orchestrates the writing of the cover letter
def main(agents_and_actions, user_info, job_advertisement, output_dir):

    # Input 
    input = {"user_info": user_info, "job_advertisement": job_advertisement}
    # Create the output directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Output file names
    steps_output, output_final = "steps_output.md", "output.md"

    workflow = StateGraph(AgentState)
    state= {"name": [],
            "messages": [],}  
    # Iterate over the agents and actions

    for i, agent in enumerate(agents_and_actions):
        if i==0:
            workflow.add_node(agent['name'], functools.partial(action_combine_messages, name=agent['name'], input=input, llm_prompt=agent['llm_prompt']))
            workflow.set_entry_point(agent['name'])

        else:
            workflow.add_node(agent['name'], functools.partial(action_llm_response, name=agent['name'], watch=agent['watches'], llm_prompt=agent['llm_prompt']))
            workflow.add_edge(agent['watches'], agent['name'])
            # for watch in agent['watches']:
            #     workflow.add_edge(watch, agent['name'])
            if i == len(agents_and_actions) - 1:
                workflow.set_finish_point(agent['name'])
        # Run the workflow
    app = workflow.compile()
    output_graph = save_graph(app, output_dir)
    # create the steps output file
    time_stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    output_steps_file = os.path.join(output_dir, time_stamp + steps_output)
    save_file("# Date: " + time_stamp + "\n", output_steps_file)
    # Stream the output
    for output in app.stream(state):
        for key, value in output.items():
            output_text = combine_messages([value["name"][-1],value["messages"][-1],])
            save_file(output_text, output_steps_file, continue_on_exists=True)
            # print(f"{key}: {value}")
        print("================================")

    # Save the final output
    save_file(output_text, os.path.join(output_dir, time_stamp + output_final), continue_on_exists=True)
    
    return 0

if __name__ == "__main__":

    input_output_dirs = read_file("input_output.yaml")

    user_info          = read_file(os.path.join(input_output_dirs["main_dir"],input_output_dirs["user_info"]))
    job_advertisement  = read_file(os.path.join(input_output_dirs["main_dir"],input_output_dirs["job_advertisement"]))
    output_dir         = os.path.join(input_output_dirs["main_dir"],input_output_dirs["output"])
    agents_and_actions = read_file("Writer/CoverLetter.yaml")

    main(agents_and_actions, user_info, job_advertisement, output_dir)







        