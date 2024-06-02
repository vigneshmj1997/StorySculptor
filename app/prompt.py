from jinja2 import Template

CREATE_STORY = Template(
    """Your given a story from the user enclosed in #### your task is to break the story into small chunks
such that each chunk can be imagined with a single image and output a array of dictionary which contains two keys 
CHUNK_TEXT and CHUNK_IMAGE_GENERATION_PROMPT
                        
CHUNK_TEXT Rules:
- This contains the text of chunk     
- Make sure it approx 10 words 
- Make sure the CHUNK_TEXT creates continuous story
- Make sure it doesn't contain any extremely violent text and if moderate in nature
- Make sure its grammatically correct and do not use any hard words
                        
CHUNK_IMAGE_GENERATION_PROMPT Rules:
- This contains the described prompt to create a image from CHINK_TEXT 
- Make sure it descriptive and contains all the information to generate image from the text to perfectly represent the chunk
- Make sure the images are dark in the bottom
                        

### 
{{ story }}
###                        
"""
)
