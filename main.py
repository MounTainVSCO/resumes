import openai, cloudconvert, requests
from bs4 import BeautifulSoup
import pdfkit, time
import openai
import re
from bs4 import BeautifulSoup, NavigableString

openai_api_key='sk-QpmUuThjj9X3HJDBbTrteSEH9AaJ9Tuqe4yYwNZLAZT3BlbkFJPaUaqhqJBEZ7Je93fV4_9j7Eb7io7uoc2e6CzF838A'
openai.api_key = openai_api_key
# api_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiMjhiNTU5YmQ2MWUzOWI4MmM1YjI5Y2Q5ZTA1NTYyZWFlMjU2ZmNmMGMzNGY5NmM4MjRjN2I2ZmU2YTgzNDMzM2RjM2I1Nzk5NjEwZGQxOWIiLCJpYXQiOjE3MjQ5ODc1MjguMDA2ODE5LCJuYmYiOjE3MjQ5ODc1MjguMDA2ODIxLCJleHAiOjQ4ODA2NjExMjguMDAyMjM0LCJzdWIiOiI2OTQ0MDY0OCIsInNjb3BlcyI6WyJ1c2VyLnJlYWQiLCJ1c2VyLndyaXRlIiwidGFzay5yZWFkIiwidGFzay53cml0ZSIsIndlYmhvb2sucmVhZCIsIndlYmhvb2sud3JpdGUiLCJwcmVzZXQucmVhZCIsInByZXNldC53cml0ZSJdfQ.J852PkmJeXRLQ1DLh77oCC0MfYchjo4ENTNRD3t7Km9ZnxUk3BDcWD9vBNrb6OUR0_ev1EcmyxBgzHnyDfiwZRp2dKmw4RELeOKkkenyp_Q1Dd-obtv8qOYk8qq6J7ihkPcLTVIpvG1l7XVNKLHfCt_jd3cGTE-nNXLKmtguG2GTPxwBedZKYGtxX_TUQDsMsoa7HY8dRMM-o7eixVgj0mCSulAWuk_PiS53kniS-9vn1GscKYhRaqz3l0ZaZCzLdR2h9bObpkWu5KTjIIKzb0jbRF-fcw31vDyITbKnC02FCiRw0qunfCJj-Za280_EWHRBa2_fR5CxdKm63NnOGkjFZ_kP3ZerxxtrnaVtWJdg-mom4UHcvvejq5595MpBJEZcqXp4oWKzwWaXI2Y1xjl63VBl2lH_luVxQ7R4CWQmKMamYnDtoKliqBQHa-UcExE6ytaxV753wfdHQ7qLHurbPgT8k6gNjW7qYOEqsU1KULIxc_sEUCeJ0CM2tGG6pc4rgM9NJ7ocP8F_S80SAk3oT3EJmOJE2RhmG9PGZ9uTOB3gM1mKfeB59ykvFxyuNpuh7BjehorKzReef_Z0wglXzrcVfy8bMG-DLH3wf8Xfbi9MRE3jWDeTCIDnzw9Njv26ZUbQg48yiwtFcv2J46a5BBtCmbV0uaKYtcoN2zI'
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