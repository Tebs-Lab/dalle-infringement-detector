#!python

import argparse
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
        default="gpt-4o", 
        choices=['gpt-4o', 'gpt-4', 'gpt-4-turbo-preview', 'gpt-3.5-turbo', 'gpt-3.5-turbo-instruct', 'babbage-002', 'davinci-002']
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
    

    # Image generation parameters
    parser.add_argument("-z", "--size", 
        help="DALL-E image size string, default '1024x1024'. dall-e-2 only supports the default size.", 
        type=str, 
        default='1024x1024', 
        choices=['1024x1024', '1024x1792', '1792x1024']
    )

    parser.add_argument("-q", "--quality", 
        help="DALL-E image quality string, default 'standard'", 
        type=str, 
        default='standard', 
        choices=['standard', 'hd']
    )

    # Output options
    parser.add_argument("-t", "--text", 
        help="Only print the final image prompt, do not send it to DALL-E", 
        action='store_true'
    )
    parser.add_argument("-p", "--open", 
        help="Automatically open all URL's returned by DALL-E", 
        action='store_true'
    )
    parser.add_argument("-i", "--interim",
        help="Print all the interim text results from various models", 
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
    client = OpenAI()

    ## Collect Input Section ## 
    character_name = input("Character: ")
    image_setting = input("Setting: ")
    image_style = input("Style: ")

    text_to_save = f'Character: {character_name}\nSetting:{image_setting}\nStyle: {image_style}\n\n'

    ## Begin Prompting Section ##
    ## Character Details ##
    image_subjects = prompts.fetch_character_description(client, args.gpt, character_name)
    image_subject = image_subjects[0].message.content

    text_to_save += f'Expanded Character Details:\n{image_subject}\n\n'
    if args.interim:
        print(f'Expanded Character Details:\n{image_subject}\n\n')

    ## Fetch Style Details ##
    style_details = prompts.fetch_style_detail(client, args.gpt, image_style)
    text_to_save += f'Style details:\n{style_details}\n\n'

    
    if args.interim:
        print(f'Style details:\n{style_details}\n\n')


    ## Image Generation Section ##
    ## Combine Setting With Character ##

    content_details = prompts.fetch_scene_details(client, args.gpt, image_subject, image_setting)
    text_to_save += f'Content Detail:\n{content_details}\n\n'
    if args.interim:
        print(f'Content details:\n{content_details}\n\n')

    image_prompt = prompts.fetch_dalle_prompt(client, args.gpt, content_details, style_details)

    text_to_save += f'Final prompt:\n{image_prompt}\n\n'

    # dall-e-2 has a 1000 character max for prompt, dall-e-3 is 4000 characters
    # TODO: handle this more gracefully?
    if args.dalle == 'dall-e-2' and len(image_prompt) > 1000:
        image_prompt = image_prompt[:1000]
    elif args.dalle == 'dall-e-3' and len(image_prompt) > 4000:
        image_prompt = image_prompt[:4000]
    
    print(f'Final prompt: \n{image_prompt}\n')

    if not args.text:
        # The I NEED text below is suggested by OpenAI's docs to reduce prompt rewriting.
        img_response = client.images.generate(
            model=args.dalle,
            prompt=f'I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS: {image_prompt}',
            size=args.size,
            quality=args.quality,
        )

        for idx, img_data in enumerate(img_response.data):
            if img_data.revised_prompt:
                rewritten_output = f'Prompt rewritten by OpenAI: \n\n {img_data.revised_prompt}\n\n'
                print(rewritten_output)
                text_to_save += rewritten_output

            print(img_data.url)
            text_to_save += f'{img_data.url} \n\n'

            if args.open:
                webbrowser.open_new_tab(img_data.url)
            
            if args.save:
                img_save_path = save_directory / f'{idx}.png' # TODO: more robust
                urlretrieve(img_data.url, img_save_path)

    if args.save:
        save_text_path = save_directory / "prompts.txt"
        with save_text_path.open("w", encoding ="utf-8") as f:
            f.write(text_to_save)



if __name__ == '__main__':
    main()