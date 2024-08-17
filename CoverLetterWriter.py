import os
import sys
import asyncio
from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.team import Team
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

'''
To enable a large language model (LLM) to perform a multi-agent task such as writing a cover letter, several specialized agents or components can be utilized
'''

class Write(Action):
    """
    This class represents the action of writing for any agent."""   
    def __init__(self, name, prompt_template):
        super().__init__()
        self.name = name
        self.prompt_template = prompt_template
    async def run(self, context):
        prompt = self.prompt_template.format(context=context)
        response = await self.ask(prompt)  
        return response
    
class Writer(Role):
    """
    This class represents the writer role in writing process."""
    def __init__(self, name, action, watches, action_prompt):
        super().__init__(name=name, desc=action)
        self.set_actions([Write(name, action_prompt)])
        self._watch(watches)

class Input(Action):
    """
    This class represents the action of collecting input from the user."""
    def __init__(self, name, input_dir, input_files):
        super().__init__(name=name)
        self.input_dir = input_dir
        self.input_files = input_files

    async def run(self):
        user_info = await self.read_input(self.input_dir, self.input_files[0])        
        job_advertisement = await self.read_input(self.input_dir, self.input_files[1])


        # Merge the user info and job advertisement
        context = f"""
        # User Info:
        {user_info}
        # Job Advertisement:
        {job_advertisement}
        """
        return await context
    
    def read_input(self, input_dir, input_file):
        with open(os.path.join(input_dir, input_file), 'r') as file:
            return file.read()
        
class InputAgent(Role):
    """
    This class represents the input agent role in the writing process."""
    def __init__(self, name, action, input_dir, input_files):
        super().__init__(name=name, desc=action)
        self.set_actions([Input(name, input_dir, input_files)])


async def main(input_dir, input_files, output_dir):
    agents_and_actions = [

    {
        "name": "User Input Agent",
        "actions": [
            "Collects initial information from the user, such as their name, job title, company name, job description, skills, and experiences."
        ],
        "watches": [],
        "input": ["user_info", "job_advertisement"],
        "llm_prompt": None, # No prompt needed for user input
    },

    {
        "name": "Context Understanding Agent",
        "actions": [
            "Analyzes the job description and other relevant documents to understand key requirements, responsibilities, and skills needed for the position."
        ],
        "watches": ["User Input Agent"],
        "llm_prompt": 
        """
            Based on the following information provided by the user:
            {context}
            Analyze the job description to identify key requirements, responsibilities, and necessary skills for this position. Provide a summary of these elements.
        """
    },

    {
        "name": "Profile Analysis Agent",
        "actions": [
            "Reviews the user's resume and other provided information to identify strengths, experiences, and skills that align with the job requirements."
        ],
        "watches": ["User Input Agent"],
        "llm_prompt": 
        """
            Based on the user's information:
            {context}
            Review their resume and other provided details. Identify their strengths, experiences, and skills that align with the key requirements of the job they are applying for.
        """
    },

    {
        "name": "Drafting Agent",
        "actions": [
            "Generates a draft of the cover letter using insights from both the Context Understanding Agent and Profile Analysis Agent. Ensures relevant experiences and skills are highlighted effectively."
        ],
        "watches": ["Context Understanding Agent", "Profile Analysis Agent"],
        "llm_prompt": 
        """
            You are the Drafting Agent. Your task is to generate a draft of a cover letter using insights provided by both the Context Understanding Agent and Profile Analysis Agent.
            Context: {context}

            1. Ensure that relevant experiences and skills are highlighted effectively.
            2. Structure the cover letter in a professional format.
            3. Make sure to address key points that would be important for the job role.

            Begin with an engaging introduction, followed by detailed paragraphs on experience and skills, and conclude with a strong closing statement.
        """
    },

    {
        "name": "Language Refinement Agent",
        "actions": [
            "Refines the draft for clarity, coherence, grammar, and style to ensure it meets professional standards."
        ],
        "watches": ["Drafting Agent"],
        "llm_prompt": 
        """
            You are the Language Refinement Agent. Your task is to refine the draft of a cover letter created by the Drafting Agent.
            Context: {context}

            1. Improve clarity and coherence.
            2. Correct any grammatical errors.
            3. Enhance overall style to meet professional standards.

            Make sure that each section flows well into the next, maintaining a formal tone throughout.
        """
    },

    {
        "name": "Customization Agent",
        "actions": [
            "Tailors sections of the cover letter to match specific aspects of the job description or company culture based on additional user input or contextual clues."
        ],
        "watches": ["Language Refinement Agent",  "User Input Agent"],
        "llm_prompt": 
        """
            You are the Customization Agent. Your task is to tailor sections of the refined cover letter to match specific aspects of the job description or company culture based on additional user input or contextual clues.
            Context: {context}

            1. Customize sections to align with specific job requirements or company values mentioned in user inputs or contextual clues.
            2. Ensure that each tailored section remains coherent within the overall document.

            Pay special attention to how your customizations enhance alignment with what is sought after in this particular job role or company environment.
        """
    },

    {
    "name": "Feedback Loop/Revision Control",
    "actions": [
        "After generating a draft, gathers feedback on parts of cover letter that need adjustments/enhancements.",
        "Manages multiple iterations based on user feedback until final approval is achieved."
    ],
    "watches": ["Drafting Agent", "Customization Agent"],
    "llm_prompt":
        """
        You are an expert in receiving and implementing feedback to improve drafts. 
        Based on the initial draft generated by the Drafting Agent and modified by the Customization Agent, 
        gather specific feedback that highlights areas needing adjustments or enhancements. 
        Coordinate multiple iterations until final approval is achieved.
        
        Context: {context}
        """
    
   },

    {
    "name": "Formatting/Polishing",
    "actions": [
        "Ensures final document adheres to standard formatting guidelines for professional cover letters.",
        "Reviews & refines generated content for grammar, tone coherence, & overall quality assurance."
    ],
    "watches": ["Feedback Loop/Revision Control"],
    "llm_prompt":
        """
        You are skilled in formatting and polishing professional documents. 
        After receiving the revised draft from the Feedback Loop/Revision Control Agent, 
        ensure the cover letter adheres to standard formatting guidelines. 
        Review and refine the content for grammar, tone coherence, and overall quality.
        
        Context: {context}
        """
    },

    {
        "name": "Validation",
        "actions":[
            "Performs a final review for any errors or omissions before completion."
         ],
         "watches":["Formatting/Polishing"],
         "llm_prompt":
             """
             You are responsible for performing a final review of documents. 
             After receiving the polished version from the Formatting/Polishing Agent, check thoroughly 
             for any errors or omissions to ensure it meets all quality standards before completion.
             
             Context: {context}
             """,
         "output":[]
     }

    ]
 
    Writers_team = Team()
    roles = {} 
    for agent in agents_and_actions:

        if "input" in agent:
            name = agent["name"]
            # convert list of actions to string
            action = "\n".join(agent["actions"])
            input_dir = input_dir
            input_files = input_files
            roles[name] = InputAgent(name, action, input_dir, input_files)
        else:
            name = agent["name"]
            action = "\n".join(agent["actions"])
            watches = [roles[watch] for watch in agent["watches"]]
            llm_prompt = agent["llm_prompt"]
            roles[name] = Writer(name, action, watches, llm_prompt)
        
        Writers_team.hire([roles[name]])
    Writers_team.invest(100)
    Writers_team.run_project("Write a cover letter", send_to=roles["User Input Agent"])
    await Writers_team.run(n_round=3)

if __name__ == "__main__":
    input_dir = "/Users/ayman/Library/CloudStorage/OneDrive-Personal/Notes/Notes/Skills/Soft Skills/CV/Application"
    input_files = ["General/Who am I.md", "PosDoc/7.ComputationalHealth/Adv.md"]
    output_dir = "output"
    asyncio.run(main(input_dir, input_files, output_dir))
    logger.info("Writers Team is ready to write a cover letter!")

        