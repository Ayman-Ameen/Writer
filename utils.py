import os 
def remove_underscore_numbers(folder):
    for foldername, subfolders, filenames in os.walk(folder):
        for filename in filenames:
            if '_' in filename:
                # check if the first character is a number before the underscore
                if filename[0].isnumeric():
                    new_name = filename.split('_', 1)[1]
                    print(f"Renaming {filename} to {new_name}")
                    os.rename(os.path.join(foldername, filename), os.path.join(foldername, new_name))

folder =  "/Users/ayman/Documents/gpt-researcher/daily_paper_arxiv/_(nanophotonics_AND_AI_AND_design)__20240531"           
remove_underscore_numbers(folder)