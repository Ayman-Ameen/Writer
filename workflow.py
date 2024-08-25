import os
import sys
import yaml
import functools
import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
from utils import read_file, save_file, run_agent, get_llm_model, AgentState
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import BaseMessage, AIMessage
from typing import TypedDict, Annotated, Sequence, List


class Message():
    @staticmethod
    def get_empty_message():
        return {"name": [], "messages": []}
    
    @staticmethod
    def combine_messages(messages: list):
        messages = [message.content if isinstance(message, AIMessage) else message for message in messages]
        return "\n # " + "\n # ".join(messages)

    @staticmethod
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
    


class MultiAgents():
    def __init__(self, agents_and_actions, input, output):
        self.workflow = StateGraph(AgentState)
        self.agents_and_actions = agents_and_actions
        self.input_agent_intialize(input)
        for agent in self.agents_and_actions[1:]:
            self.workflow.add_node(agent["name"], functools.partial(self.action_llm_response, name=agent['name'], watch=agent['watches'], llm_prompt=agent['llm_prompt']))
            self.workflow.add_edge(agent['watches'], agent['name'])
        self.workflow.set_finish_point(agent['name'])
        self.intialize_output(output)
        self.app = self.workflow.compile()



    def intialize_output(self, output_dir,outputs=["steps", "letter"],time_stamp=True):
        self.output = {}

        if time_stamp:
            time_stamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            output_dir = os.path.join(output_dir, time_stamp)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for output in outputs:
            self.output[output] = os.path.join(output_dir, f"{output}.md")
        self.output["graph"] = os.path.join(output_dir, "graph.png")

    def input_agent_intialize(self, input):
        agent = self.agents_and_actions[0]
        self.workflow.add_node(agent["name"], functools.partial(self.action_combine_messages, name=agent['name'], input=input, prompt=agent['llm_prompt']))
        self.workflow.set_entry_point(agent['name'])


    def action_combine_messages(self, state="", name="", input={},prompt=""):
        return { "name": [name],
                "messages":  [prompt.format(**input)]}
    
    def action_llm_response(self, state="", name="", watch=[], llm_prompt=""):
        llm = get_llm_model()
        watched_messages = Message.get_watched_messages(state, watch)
        prompt = llm_prompt.format(**watched_messages)
        print("current agent: ", name)
        return {
            "name": [name],
            "messages": [llm.invoke(prompt)]
        }
    
    def save_graph(self):
        with open(self.output["graph"], "wb") as file:
            file.write(self.app.get_graph(xray=True).draw_mermaid_png())

    def save_last_output(self, output, file):
        for key, value in output.items():
            value_keys = list(value.keys())
            save_file(Message.combine_messages([value[v][-1] for v in value_keys]),
                      file, continue_on_exists=True)

    def run(self, state=Message.get_empty_message()):
        self.save_graph()
        for output in self.app.stream(state):
            self.save_last_output(output, self.output["steps"])
        self.save_last_output(output, self.output["letter"])

    





