#!python

import argparse
import base64
import pathlib
import sys
from urllib.request import urlretrieve
import webbrowser

import prompts

from openai import OpenAI
from anthropic import Anthropic

def main():
    ## Arg Parse Section ##
    parser = argparse.ArgumentParser()

    # Model type options
    parser.add_argument("-g", "--gpt", 
        help="GPT model version string, default 'gpt-4'", 
        type=str,
        default="gpt-4", 
        choices=['gpt-4o', 'gpt-4', 'gpt-4.1-mini', 'gpt-4.1', 'gpt-4-turbo-preview', 'gpt-3.5-turbo', 'gpt-3.5-turbo-instruct', 'babbage-002', 'davinci-002']
    )

    parser.add_argument("-d", "--dalle",
        help="DALL-E model version string, default 'dall-e-3'",
        type=str, 
        default="dall-e-3", 
        choices=['dall-e-3', 'dall-e-2']
    )

    parser.add_argument('-c', '--claude',
        help="Anthropic model version string, default 'claude-3-7-sonnet-latest'",
        type=str,
        default="claude-3-7-sonnet-latest",
        choices=['claude-3-7-sonnet-latest', 'claude-3-5-haiku-latest', 'claude-3-opus-latest', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307']                
    )

    parser.add_argument('-p', '--prompt-generator', 
        help="Which model to use for generating intermediate prompts, default: 'gpt'",
        choices=['gpt', 'claude'],
        default='gpt'
    )

    # Output options
    parser.add_argument("-t", "--text", 
        help="Only print the final image prompt, do not send it to DALL-E", 
        action='store_true'
    )
    parser.add_argument("-o", "--open", 
        help="Automatically open all URL's returned by DALL-E", 
        action='store_true'
    )
    parser.add_argument("-i", "--interim",
        help="Print all the interim text results from various models. These always appear in the saved prompts.txt, but will only print to the screen if you use this option", 
        action='store_true'
    )
    parser.add_argument("-s", "--save", 
        help="Save all the prompts and the generated image in a folder with the path provided. The folder must not already exist, path is relative to the CWD", 
        type=str, 
        default=None
    )

    args = parser.parse_args()

    if args.save:
        save_directory = pathlib.Path(args.save)
        save_directory.mkdir(parents=True, exist_ok=False)

    # Your API key must be saved in an env variable for this to work.
    openai_client = OpenAI()
    anthropic_client = Anthropic()

    ## Collect Input Section ## 
    character_name = input("Character: ")
    image_setting = input("Setting: ")
    image_style = input("Style: ")

    text_to_save = f'Character: {character_name}\nSetting:{image_setting}\nStyle: {image_style}\n\n'

    ### Begin Prompting Section ###
    ## Character Details ##
    if args.prompt_generator == 'gpt':
        image_subject = prompts.fetch_character_description_openai(openai_client, args.gpt, character_name)
    else: 
        image_subject = prompts.fetch_character_description_anthropic(anthropic_client, args.claude, character_name)

    text_to_save += f'Expanded Character Details:\n{image_subject}\n\n'
    if args.interim:
        print(f'Expanded Character Details:\n{image_subject}\n\n')

    ## Fetch Style Details ##
    if args.prompt_generator == 'gpt':
        style_details = prompts.fetch_style_detail_openai(openai_client, args.gpt, image_style)
    else:
        style_details = prompts.fetch_style_detail_anthropic(anthropic_client, args.claude, image_style)
    
    text_to_save += f'Style details:\n{style_details}\n\n'
    if args.interim:
        print(f'Style details:\n{style_details}\n\n')

    ## Fetch Scene Details ##
    if args.prompt_generator == 'gpt':
        content_details = prompts.fetch_scene_details_openai(openai_client, args.gpt, image_subject, image_setting)
    else:
        content_details = prompts.fetch_scene_details_anthropic(anthropic_client, args.claude, image_subject, image_setting)
    
    text_to_save += f'Content Detail:\n{content_details}\n\n'
    if args.interim:
        print(f'Content details:\n{content_details}\n\n')

    ## Final Image Prompt ##
    if args.prompt_generator == 'gpt':
        image_prompt = prompts.fetch_dalle_prompt_openai(openai_client, args.gpt, content_details, style_details)
    else:
        image_prompt = prompts.fetch_dalle_prompt_anthropic(anthropic_client, args.claude, content_details, style_details)

    text_to_save += f'Final prompt:\n{image_prompt}\n\n'

    # TODO: handle this more gracefully.
    # dall-e-2 has a 1000 character max for prompt, dall-e-3 is 4000 characters
    # The below magic numbers are because of the length of the "I NEED ..." text that OpenAI suggests to use.
    # See the comment below. Yes, this is jankey.
    if args.dalle == 'dall-e-2' and len(image_prompt) >= 893:
        image_prompt = image_prompt[:893]
    elif args.dalle == 'dall-e-3' and len(image_prompt) > 3893:
        image_prompt = image_prompt[:3893]
    
    print(f'Final prompt: \n{image_prompt}\n')

    ## Image Generation ##
    if not args.text:
        # The "I NEED ..."" text below is suggested by OpenAI's docs to reduce prompt rewriting.
        # See: https://platform.openai.com/docs/guides/image-generation?image-generation-model=dall-e-3#prompting-tips
        img_response = openai_client.images.generate(
            model=args.dalle,
            prompt=f'I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS: {image_prompt}'
        )

        # We never request multiple images.
        img_response = img_response.data[0]

        if img_response.revised_prompt:
            rewritten_output = f'Prompt rewritten by OpenAI: \n\n {img_response.revised_prompt}\n\n'
            print(rewritten_output)
            text_to_save += rewritten_output

        print(f'Image URL: {img_response.url}\n\n')
        text_to_save += f'{img_response.url} \n\n'

        if args.open:
            webbrowser.open_new_tab(img_response.url)
        
        img_save_path = None
        if args.save:
            img_save_path = save_directory / f'produced_image.png'
        
        # if args.save is None a temp file will be made, otherwise f will be at the user specified path
        f, image_data = urlretrieve(img_response.url, img_save_path)

        with open(f, "rb") as image_file:
            binary_data = image_file.read()
            base_64_encoded_data = base64.b64encode(binary_data)
            base64_string = base_64_encoded_data.decode('utf-8')

        infringement_response = prompts.fetch_infrigement_detection(anthropic_client, args.claude, base64_string)
        print(f'Infringement detection:\n\n {infringement_response}\n\n')
        text_to_save += f'Infringement detection: {infringement_response}\n\n'

    ## Persist Results ##
    if args.save:
        save_text_path = save_directory / "prompts.txt"
        with save_text_path.open("w", encoding ="utf-8") as f:
            f.write(text_to_save)

if __name__ == '__main__':
    main()