'''
A set of supporting functions for making the interim prompts we use to 
generate a final engineered image prompt.
'''

from anthropic import Anthropic
from openai import OpenAI

SCENE_GENERATOR_PROMPT = '''Generate an output prompt for an image generator using the following subject, setting, and art style. Focus on the physical elements of the subject and setting.  Do not use the subjects name anywhere in your output. Be detailed but use 150 words or less. 

Subject: {subject}

Setting: {setting}

Art Style: {style}
'''

def fetch_scene_details_openai(client, model, subject, setting, style):
    '''
    Use the supplied args and OpenAI client to fetch a more
    detailed description from OpenAI.

    client (OpenAI client) -- client makes the request
    model (str) -- a valid OpenAI API model string, e.g. 'gpt-4'
    subject (str) -- a string describing a subject in plain english, for LLM use.
    setting (str) -- a string describing a setting in plain english, for LLM use.
    '''
    prompt_content = SCENE_GENERATOR_PROMPT.format(subject=subject, setting=setting, style=style)

    subject_response = client.responses.create(
        model=model,
        input=[
        {
            "role": "user",
            "content": prompt_content
        }],
        max_output_tokens=500,
    )

    return subject_response.output_text


def fetch_scene_details_anthropic(client, model, subject, setting, style):
    '''
    Use the supplied args and Anthropic client to fetch a more
    detailed description from Anthropic.

    client (Anthropic client) -- client makes the request
    model (str) -- a valid Anthropic API model string, e.g. 'claude-3-haiku-latest'
    subject (str) -- a string describing a subject in plain english, for LLM use.
    setting (str) -- a string describing a setting in plain english, for LLM use.
    '''
    prompt_content = SCENE_GENERATOR_PROMPT.format(subject=subject, setting=setting, style=style)

    subject_response = client.messages.create(
        model=model,
        messages=[
        {
            "role": "user",
            "content": prompt_content
        }],
        max_tokens=500,
    )

    return subject_response.content[0].text


def fetch_infrigement_detection(client, model, base_64_image):
    '''
    Use the supplied args and Anthropic client to determine if the input image
    contains any copyright or trademark protected characters.

    client (Anthropic client) -- client makes the request
    model (str) -- a valid Anthropic API model string, e.g. 'claude-3-haiku-latest'
    base_64_image (str) -- the base 64 encoded image to check for infringement
    '''
    prompt = "Check if this image contains any copyright or trademark protected characters. If so please list them. If not, please say 'No copyright or trademark infringement detected'."
    message_list = [
        {
            "role": 'user',
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base_64_image}},
                {"type": "text", "text": prompt}
            ]
        }
    ]

    response = client.messages.create(
        model=model,
        max_tokens=300,
        messages=message_list
    )
    return response.content[0].text

