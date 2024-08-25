from workflow import Message, MultiAgents
import os

from utils import read_file, save_file, run_agent, get_llm_model, AgentState




def test_message():
    message = Message.get_empty_message()
    assert message == {"name": [], "messages": []}

def test_workflow():
    input_output_dirs = read_file("input_output.yaml")

    user_info          = read_file(os.path.join(input_output_dirs["main_dir"],input_output_dirs["user_info"]))
    job_advertisement  = read_file(os.path.join(input_output_dirs["main_dir"],input_output_dirs["job_advertisement"]))
    output_dir         = os.path.join(input_output_dirs["main_dir"],input_output_dirs["output"])
    agents_and_actions = read_file("Writer/CoverLetter.yaml")
    input = {"user_info": user_info, "job_advertisement": job_advertisement}

    MAs = MultiAgents(agents_and_actions, input, output_dir)
    MAs.run()


if __name__ == "__main__":
    test_message()    
    test_workflow()