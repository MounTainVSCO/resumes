import openai, cloudconvert, requests
from bs4 import BeautifulSoup
import pdfkit, time
import openai
import re
from bs4 import BeautifulSoup, NavigableString

# openai_api_key=''
# openai.api_key = openai_api_key

# api_key = ''

# cloudconvert.configure(api_key=api_key)
# job = cloudconvert.Job.create(payload={
#     "tasks": {
#         'import-my-file': {
#             'operation': 'import/upload'
#         },
#         'convert-my-file': {
#             'operation': 'convert',
#             'input': 'import-my-file',
#             'output_format': 'html'
#         },
#         'export-my-file': {
#             'operation': 'export/url',
#             'input': 'convert-my-file'
#         }
#     }
# })

# # Upload the PDF file
# upload_task_id = job['tasks'][0]['id']
# upload_task = cloudconvert.Task.find(id=upload_task_id)
# cloudconvert.Task.upload(file_name='William_Zhao_Technical_Resume.pdf', task=upload_task)

# # Wait for the job to complete and retrieve the output URL
# job = cloudconvert.Job.wait(id=job['id'])
# export_task_id = [task['id'] for task in job['tasks'] if task['operation'] == 'export/url'][0]
# export_task = cloudconvert.Task.find(id=export_task_id)
# file = export_task['result']['files'][0]
# cloudconvert.download(filename='output.html', url=file['url'])
def clean_text(text):
    # Remove unwanted single and double quotes from the text
    text = re.sub(r"[‘’“”\"']", "", text)
    return text.strip()

def translate_text_batch(texts, context=""):
    # Clean the text to remove unnecessary quotes before translation
    cleaned_texts = [clean_text(text) for text in texts]
    
    # Create a prompt that includes the context and the text segments for translation
    prompt = "Translate the following text to Chinese. Each segment is separated by triple asterisks. Ignore the HTML structure but keep the translation accurate:\n\n"
    prompt += f"Context: {context}\n\n"
    prompt += "***\n".join(cleaned_texts)
    
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Use "gpt-3.5-turbo" or "gpt-4"
        messages=[
            {"role": "system", "content": "You are a translator."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000
    )
    
    translated_texts = response.choices[0].message['content'].split("***")
    return [text.strip() for text in translated_texts]

def process_html_body_in_place(body_tag):
    max_tokens = 3000  # Maximum tokens to fit within the API limit
    text_elements = []
    context_elements = []
    current_token_count = 0

    def calculate_tokens(text):
        return len(text.split())

    for element in body_tag.descendants:
        if element and isinstance(element, NavigableString) and element.strip():
            element_text = element.strip()

            # Exclude text containing '' or other unnecessary quotes
            if "''" in element_text or "\"" in element_text:
                continue
            
            tokens = calculate_tokens(element_text)
            
            if current_token_count + tokens > max_tokens:
                # Translate the current batch if adding another element exceeds the max token count
                context = " ".join([e.strip() for e in context_elements])
                translated_texts = translate_text_batch([e.strip() for e in text_elements], context=context)
                for original, translated in zip(text_elements, translated_texts):
                    original.replace_with(translated)
                text_elements = []
                context_elements = []
                current_token_count = 0

            text_elements.append(element)
            context_elements.append(element)
            current_token_count += tokens

    # Process any remaining elements not handled in the last batch
    if text_elements:
        context = " ".join([e.strip() for e in context_elements])
        translated_texts = translate_text_batch([e.strip() for e in text_elements], context=context)
        for original, translated in zip(text_elements, translated_texts):
            original.replace_with(translated)

# Load the HTML content
with open('output.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Locate the body tag and process it
body_tag = soup.body
if body_tag:
    process_html_body_in_place(body_tag)

# Save the translated HTML content back to the same file
with open('translated_output.html', 'w', encoding='utf-8') as file:
    file.write(str(soup))

print("Translation completed and saved in-place to output.html")