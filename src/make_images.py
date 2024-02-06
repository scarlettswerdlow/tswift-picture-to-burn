"""Module generating images of song lyrics with OpenAI's dall-e-3."""

import string
import csv
import time
import urllib.request
import os
import yaml
from unidecode import unidecode
import requests

################################################################################
#                                                                              #
#                               Global variables                               #
#                                                                              #
################################################################################

SONG_COL = 2
LYRICS_COL = 3
NEW_LINE = "\n"
INSTRUCTIONS_DICT = {
    "photo": "I NEED it to be a photograph.",
    "no_text": "I NEED it to NOT have any text, letters, words, or numbers."
}

################################################################################
#                                                                              #
#                                    Functions                                 #
#                                                                              #
################################################################################

def read_yaml(config_fp):
    """Function reading yaml file"""
    with open(config_fp, mode = "r", encoding = "utf-8") as f:
        return yaml.safe_load(f)

def make_headers(access_token):
    """Function making headers for REST request"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    return headers

def make_song_style_tuples(songs_list, styles_list):
    """Function making song, style tuples for prompts"""
    song_style_tuples = []
    for song in songs_list:
        for style in styles_list:
            song_style_tuples.append((song, style))
    return song_style_tuples

def clean_string_for_path(s):
    """Function for removing punctuation and spaces in strings"""
    cleaned_string = s.translate(str.maketrans("", "", string.punctuation)) \
        .replace(" ", "-")
    return cleaned_string

def clean_song(song):
    """Function for removing trailing whitespace and unusual whitespace encoding"""
    # Remove weird whitespace encoding found in genius data (\u200, \xa0)
    cleaned_song = unidecode(song).strip()
    return cleaned_song

def make_path(song):
    """Function for creating subdirectory for song if it doesn't exist"""
    song_for_path = clean_string_for_path(song)
    song_path = f"images/{song_for_path}"
    if not os.path.exists(song_path):
        os.makedirs(song_path)
    return song_for_path

def get_lyrics(lyrics_fp, song_from_user):
    """Function for reading lyrics for select song"""
    with open(lyrics_fp, mode = "r", encoding = "utf-8") as f:
        for line in csv.reader(f):
            song_from_file = line[SONG_COL]
            cleaned_song_from_file = clean_song(song_from_file)
            # Compare lower case
            if cleaned_song_from_file.lower() == song_from_user.lower():
                lyrics = line[LYRICS_COL]
                return lyrics
    return None

def make_prompt(style, lyrics, instructions):
    """Function making prompt"""
    prompt_l = ["A", style, "that represents the following lyrics."]
    if instructions is not None:
        for instruction in instructions:
            prompt_l.append(INSTRUCTIONS_DICT.get(instruction))
    prompt_l.append(lyrics)
    prompt = " ".join(prompt_l)
    return prompt

def make_filename(song_clean, style, type_, run, ext):
    """Function for making filename"""
    filename = f"{song_clean}_{style}_{type_}_{run}"
    filename_len = len(filename)
    if filename_len > 251:   # Max filename length excluding extension
        filename = f"{song_clean}_{style[:(len(style)-(filename_len-251))]}_{type_}_{run}"
    filename_path = f"images/{song_clean}/{filename}.{ext}"
    # If file with same name exists, add incrementer
    counter = 1
    while os.path.exists(filename_path):
        dec = len(str(counter)) + 1
        filename = f"{filename[:251-dec]}_{counter}"
        filename_path = f"images/{song_clean}/{filename}.{ext}"
        counter += 1
    return f"{filename}.{ext}"

def write_text(text, song_clean, style, type_, run):
    """Function writing text to file"""
    filename = make_filename(song_clean, style, type_, run, "txt")
    write_fp = f"images/{song_clean}/{filename}"
    with open(write_fp, mode = "w", encoding = "utf-8") as f:
        f.write(text)
    return write_fp

def request_image(base_url, headers, prompt):
    """Function for generating image with dall-e-3"""
    r = requests.post(
        f"{base_url}images/generations",
        json = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
        },
        headers = headers,
        timeout = 180
    )
    return r

def get_revised_prompt(image_response):
    """Function for getting revised prompt from API return"""
    revised_prompt = image_response.get("data")[0].get("revised_prompt")
    return revised_prompt

def write_image(image_response, song_clean, style, run):
    """Function writing image to file"""
    filename = make_filename(song_clean, style, "image", run, "jpg")
    write_fp = f"images/{song_clean}/{filename}"
    image_url = image_response.get("data")[0].get("url")
    urllib.request.urlretrieve(image_url, write_fp)
    return write_fp

def make_image(song, style, lyrics_fp, instructions, base_url, headers, run):
    """Function for making image for single song and style"""
    lyrics = get_lyrics(lyrics_fp, song)
    if lyrics is None:
        raise TypeError("Lyrics is NoneType")
    prompt = make_prompt(style, lyrics, instructions)
    song_for_path = make_path(song)
    style_for_path = clean_string_for_path(style)
    prompt_fp = write_text(prompt, song_for_path, style_for_path, "prompt", run)
    image_response = request_image(base_url, headers, prompt)
    if image_response.status_code != 200:
        image_response.raise_for_status()
    image_data = image_response.json()
    revised_prompt = get_revised_prompt(image_data)
    revised_prompt_fp = write_text(revised_prompt, song_for_path, style_for_path, "revised-prompt",
                                   run)
    image_fp = write_image(image_data, song_for_path, style_for_path, run)
    rv = {
        "prompt_fp": prompt_fp,
        "revised_prompt_fp": revised_prompt_fp,
        "image_fp": image_fp
    }
    return rv

def main(config_fp, lyrics_fp, verbose):
    """Main function"""
    config = read_yaml(config_fp)
    try:
        songs = config["SONGS"]
        styles = config["STYLES"]
        instructions = config["INSTRUCTIONS"]
        base_url = config["OPENAI"]["BASE_URL"]
        access_token = config["OPENAI"]["OPEN_AI_KEY"]
    except KeyError as error:
        if verbose:
            print(f"An error occured: {error}{NEW_LINE}")
        return
    headers = make_headers(access_token)
    run = time.strftime("%Y%m%d%H%M", time.localtime())
    song_style_tuples = make_song_style_tuples(songs, styles)
    for t in song_style_tuples:
        song = t[0]
        style = t[1]
        if verbose:
            print(f"RUN: {run} SONG: {song} STYLE: {style}{NEW_LINE}")
        try:
            rv = make_image(song, style, lyrics_fp, instructions, base_url, headers, run)
            if verbose:
                print(f"Successfully saved to {rv}{NEW_LINE}")
        except RuntimeError as error:
            if verbose:
                print(f"An error occurred: {error}{NEW_LINE}")

################################################################################
#                                                                              #
#                                       Main                                   #
#                                                                              #
################################################################################

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description = "Generate image for song lyrics")
    parser.add_argument("-c", "--config", required = True,
                        help = "Path to config file")
    parser.add_argument("-l", "--lyrics", required = True,
                        help = "Path to lyrics file")
    parser.add_argument("-v", "--verbose", action = "store_true",
                        help = "Print statements")
    args = parser.parse_args()

    main(config_fp = args.config, lyrics_fp = args.lyrics, verbose = args.verbose)
