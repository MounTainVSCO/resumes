import openai, re
from bs4 import BeautifulSoup

openai_api_key='sk-QpmUuThjj9X3HJDBbTrteSEH9AaJ9Tuqe4yYwNZLAZT3BlbkFJPaUaqhqJBEZ7Je93fV4_9j7Eb7io7uoc2e6CzF838A'
openai.api_key = openai_api_key

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

def get_body_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    body_content = soup.body

    if body_content:
        return body_content.decode_contents()
    else:
        return "No body content found."

def filter_first_last_images(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all image tags
    images = soup.find_all('img')

    # Check if there are at least two images
    if len(images) >= 2:
        # Remove the first image
        images[0].decompose()
        # Remove the last image
        images[-1].decompose()

    # Return the modified HTML content
    return str(soup)

file_path = 'output.html'  # Replace with the correct path
body_html = get_body_content(file_path)
filtered_html = filter_first_last_images(body_html)
print(filtered_html)