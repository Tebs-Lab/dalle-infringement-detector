'''
A set of supporting functions for making the interim prompts we use to 
generate a final engineered image prompt.
'''

from anthropic import Anthropic
from openai import OpenAI

CHARACTER_PROMPT = 'Give a detailed physical description of the character {character} in 50 words without using the character\'s name.'

SUBJECT_PROMPT = '''Create a detailed physical description of the following subject and setting in 100 words. In your description, do not use the character's name.

Subject: {subject}

Setting: {setting}
'''

STYLE_PROMPT = 'Create a 50 word summary of the visual aspects of the following artistic style: {style}'

IMG_PROMPT_REQUEST = '''Write a prompt for an image generator using the following content and style in 150 words. In your prompt, do not use the character's name.

Image content: {content}

Image Style: {style}
'''

def fetch_scene_details_openai(client, model, subject, setting):
    '''
    Use the supplied args and OpenAI client to fetch a more
    detailed description from OpenAI.

    client (OpenAI client) -- client makes the request
    model (str) -- a valid OpenAI API model string, e.g. 'gpt-4'
    subject (str) -- a string describing a subject in plain english, for LLM use.
    setting (str) -- a string describing a setting in plain english, for LLM use.
    '''
    prompt_content = SUBJECT_PROMPT.format(subject=subject, setting=setting)

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


def fetch_scene_details_anthropic(client, model, subject, setting):
    '''
    Use the supplied args and Anthropic client to fetch a more
    detailed description from Anthropic.

    client (Anthropic client) -- client makes the request
    model (str) -- a valid Anthropic API model string, e.g. 'claude-3-haiku-latest'
    subject (str) -- a string describing a subject in plain english, for LLM use.
    setting (str) -- a string describing a setting in plain english, for LLM use.
    '''
    prompt_content = SUBJECT_PROMPT.format(subject=subject, setting=setting)

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


def fetch_style_detail_openai(client, model, style):
    '''
    Use the supplied args and OpenAI client to fetch a more
    detailed description of the art style from OpenAI.

    client (OpenAI client) -- client makes the request
    model (str) -- a valid OpenAI API model string, e.g. 'gpt-4'
    style (str) -- a string describing a subject in plain english, for LLM use.
    '''
    prompt_content = STYLE_PROMPT.format(style=style)
    
    style_response = client.responses.create(
        model=model,
        input=[
        {
            "role": "user",
            "content": prompt_content
        }],
        max_output_tokens=150,
    )

    return style_response.output_text


def fetch_style_detail_anthropic(client, model, style):
    '''
    Use the supplied args and Anthropic client to fetch a more
    detailed description of the art style from Anthropic.

    client (Antrhopic client) -- client makes the request
    model (str) -- a valid Anthropic API model string, e.g. 'claude-3-haiku-latest'
    style (str) -- a string describing a subject in plain english, for LLM use.
    '''
    prompt_content = STYLE_PROMPT.format(style=style)
    
    style_response = client.messages.create(
        model=model,
        messages=[
        {
            "role": "user",
            "content": prompt_content
        }],
        max_tokens=150,
    )

    return style_response.content[0].text


def fetch_dalle_prompt_openai(client, model, image_content_description, image_style_details):
    '''
    Use the supplied args and OpenAI client to fetch a more
    detailed description of the art style from OpenAI.

    client (OpenAI client) -- client makes the request
    model (str) -- a valid OpenAI API model string, e.g. 'gpt-4'
    image_content_description (str) -- a string describing a subject in plain english, for LLM use.
    image_style_details (str) -- a string describing an art style in plain english, for LLM use.
    '''
    prompt_content = IMG_PROMPT_REQUEST.format(content=image_content_description, style=image_style_details)

    image_prompt_response =  client.responses.create(
        model=model,
        input=[
        {
            "role": "user",
            "content": prompt_content
        }],
        max_output_tokens=700
    )
    
    return image_prompt_response.output_text


def fetch_dalle_prompt_anthropic(client, model, image_content_description, image_style_details):
    '''
    Use the supplied args and Anthropic client to fetch a more
    detailed description of the art style from Anthropic.

    client (Anthropic client) -- client makes the request
    model (str) -- a valid Anthropic API model string, e.g. 'claude-3-haiku-latest'
    image_content_description (str) -- a string describing a subject in plain english, for LLM use.
    image_style_details (str) -- a string describing an art style in plain english, for LLM use.
    '''
    prompt_content = IMG_PROMPT_REQUEST.format(content=image_content_description, style=image_style_details)

    image_prompt_response = client.messages.create(
        model=model,
        messages=[
        {
            "role": "user",
            "content": prompt_content
        }],
        max_tokens=700
    )
    
    return image_prompt_response.content[0].text


def fetch_character_description_openai(client, model, character):
    '''
    Use the supplied args and OpenAI client to fetch a more
    detailed description of the art style from OpenAI.

    client (OpenAI client) -- client makes the request
    model (str) -- a valid OpenAI API model string, e.g. 'gpt-4'
    character (str) -- the name of a well-known character, for LLM use.
    '''
    prompt_content = CHARACTER_PROMPT.format(character=character)

    character_description_response = client.responses.create(
        model=model,
        input=[
        {
            "role": "user",
            "content": prompt_content
        }],
        max_output_tokens=250
    )

    return character_description_response.output_text


def fetch_character_description_anthropic(client, model, character):
    '''
    Use the supplied args and Anthropic client to fetch a more
    detailed description of the art style from Anthropic.

    client (OpenAI client) -- client makes the request
    model (str) -- a valid Anthropic API model string, e.g. 'claude-3-haiku-latest'
    character (str) -- the name of a well-known character, for LLM use.
    '''
    prompt_content = CHARACTER_PROMPT.format(character=character)

    character_description_response = client.messages.create(
        model=model,
        messages=[
        {
            "role": "user",
            "content": prompt_content
        }],
        max_tokens=250
    )
    
    return character_description_response.content[0].text


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

