import os
import sys

md_file = '/Users/ayman/Documents/gpt-researcher/daily_paper_arxiv/Book/Contents/temp.md'

# Read the file
with open(md_file, 'r') as file:
    data = file.readlines()

# Find chapter numbers and titles and contents
chapter_numbers = list(range(5,21)) # This part of the book has 16 chapters from 5 to 20
chapter_titles = []
chapter_contents = []
end = -1
for i in range(len(data)):
    if end > i:
        continue
    # Find the chapter number and title
    # The chapter number is in the format new line followed by chapter number followed by new line    
    if  int(data[i]) in chapter_numbers :
        chapter_titles.append(data[i+1].strip())
        start = i+2
        # Find the chapter contents
        # The chapter contents are in the format of lines until the next chapter number
        for j in range(i+2, len(data)):
            if data[j].strip().isdigit():
                if int(data[j]) in chapter_numbers:
                    end = j
                    break
            elif j == len(data)-1:
                end = j+1


        chapter_contents.append(data[start:end-1]) # end-1 to exclude the page number of the next chapter


 # Delete header of the page 
 # The page header consists of the chapter title and the page number followed by a new line
for chapter_num, chapter in enumerate(chapter_contents):
    for i,line in enumerate(chapter):
        if  chapter_titles[chapter_num] in line and line[-3:-1].strip().isdigit():
            # delete the header
            del chapter[i]

# Add the chapter title to the beginning of the chapter
for chapter_num, chapter in enumerate(chapter_contents):
    chapter.insert(0, f'# {chapter_titles[chapter_num]}\n\n')



# Save the chapters to separate files
for chapter_num, chapter in enumerate(chapter_contents):
    chapter_file = os.path.join('/Users/ayman/Documents/gpt-researcher/daily_paper_arxiv/Book/Contents', f'{chapter_numbers[chapter_num]}.md')
    with open(chapter_file, 'w') as file:
        for line in chapter:
            file.write(line)
    print(f'Chapter {chapter_numbers[chapter_num]} saved to {chapter_file}')
        



