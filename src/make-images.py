from xml.etree.ElementTree import XML
import yaml
import string
import os
from unidecode import unidecode
import csv
import time
import requests
import urllib.request

################################################################################
#                                                                              #
#                               Global variables                               #
#                                                                              #
################################################################################

SONG_COL = 2
LYRICS_COL = 3
NEW_LINE = "\n"

################################################################################
#                                                                              #
#                                    Functions                                 #
#                                                                              #
################################################################################

def read_yaml(config_fp):
    with open(config_fp, "r") as f:
        return yaml.safe_load(f)

def make_headers(access_token):
    headers = {
        'Authorization': 'Bearer {token}'.format(token=access_token),
        'Content-Type': 'application/json'
    }
    return headers

def make_song_style_tuples(songs_list, styles_list):
    song_style_tuples = []
    for i in range(len(songs_list)):
        for j in range(len(styles_list)):
            song_style_tuples.append((songs_list[i], styles_list[j]))
    return song_style_tuples

def clean_string_for_path(s):
    cleaned_string = s.translate(str.maketrans('', '', string.punctuation)) \
        .replace(" ", "-")
    return cleaned_string

def clean_song(song):
    # Remove weird whitespace encoding found in genius data (\u200, \xa0)
    cleaned_song = unidecode(song).strip()
    return cleaned_song

def make_path(song):
    song_for_path = clean_string_for_path(song)
    song_path = f"images/{song_for_path}"
    if not os.path.exists(song_path):
        os.makedirs(song_path)
    return song_for_path

def get_lyrics(lyrics_fp, song_from_user):
    with open(lyrics_fp, "r") as f:
        for line in csv.reader(f):
            song_from_file = line[SONG_COL]
            cleaned_song_from_file = clean_song(song_from_file)
            # Compare lower case
            if cleaned_song_from_file.lower() == song_from_user.lower():
                lyrics = line[LYRICS_COL]
                return lyrics

def make_prompt(style, lyrics):
    prompt = " ".join((
        "A", 
        style,
        "with no text, words, or numbers",
        "that represents the following lyrics.",
        "I NEED it to not have any text.",
        lyrics
    ))
    return prompt

def write_text(text, song_clean, style, type, run):
    write_fp = f"images/{song_clean}/{song_clean}_{style}_{type}_{run}.txt"
    with open(write_fp, "w") as f:
        f.write(text)
    return write_fp

def request_image(base_url, headers, prompt):
    r = requests.post(
        f"{base_url}images/generations",
        json = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
        },
        headers = headers
    )
    return r

def get_revised_prompt(image_response):
    revised_prompt = image_response.get("data")[0].get("revised_prompt")
    return revised_prompt

def write_image(image_response, song_clean, style, run):
    write_fp = f"images/{song_clean}/{song_clean}_{style}_image_{run}.jpg"
    image_url = image_response.get("data")[0].get("url")
    urllib.request.urlretrieve(image_url, write_fp)
    return write_fp

def make_image(song, style, lyrics_fp, base_url, headers, run):
    lyrics = get_lyrics(lyrics_fp, song)
    if lyrics is None:
        raise TypeError("Lyrics is NoneType")
    prompt = make_prompt(style, lyrics)
    song_for_path = make_path(song)
    style_for_path = clean_string_for_path(style)
    prompt_fp = write_text(prompt, song_for_path, style_for_path, "prompt", run)
    image_response = request_image(base_url, headers, prompt)
    if image_response.status_code != 200:
        image_response.raise_for_status()
    image_data = image_response.json()
    revised_prompt = get_revised_prompt(image_data)
    revised_prompt_fp = write_text(revised_prompt, song_for_path, style_for_path, "revised-prompt", run)
    image_fp = write_image(image_data, song_for_path, style_for_path, run)
    rv = {
        "prompt_fp": prompt_fp,
        "revised_prompt_fp": revised_prompt_fp,
        "image_fp": image_fp
    }
    return rv

def main(config_fp, lyrics_fp, verbose):
    config = read_yaml(config_fp)
    try:
        songs = config["SONGS"]
        styles = config["STYLES"]
        base_url = config["OPENAI"]["BASE_URL"]
        access_token = config["OPENAI"]["OPEN_AI_KEY"]
    except Exception as error:
        if verbose: print(f"An error occured: {error}{NEW_LINE}")
        return
    headers = make_headers(access_token)
    run = time.strftime("%Y%m%d%H%M", time.localtime())
    song_style_tuples = make_song_style_tuples(songs, styles)
    for t in song_style_tuples:
        song = t[0]
        style = t[1]
        if verbose: print(f"RUN: {run} SONG: {song} STYLE: {style}{NEW_LINE}")
        try:
            rv = make_image(song, style, lyrics_fp, base_url, headers, run)
            if verbose: print(f"Successfully saved to {rv}{NEW_LINE}")
        except Exception as error:
            if verbose: print(f"An error occurred: {error}{NEW_LINE}")

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

"""
def main(config_fp, lyrics_fp, verbose = True):
    config = read_yaml(config_fp)
    base_url = config['OPENAI']['BASE_URL']
    access_token = config['OPENAI']['OPEN_AI_KEY']
    headers = make_headers(access_token)
    run = time.strftime("%Y%m%d%H%M", time.localtime())
    for song in SONGS:
        if verbose: print(f"SONG: {song}{NEW_LINE}")
        lyrics = get_lyrics(lyrics_fp, song)
        if lyrics is None:
            if verbose: print(f"Lyrics not found{NEW_LINE}")
            continue
        song_for_path = make_path(song)
        for style in STYLES:
            if verbose: print(f"STYLE: {style}{NEW_LINE}")
            style_for_path = clean_string_for_path(style)
            prompt = make_prompt(style, lyrics)
            prompt_fp = write_text(prompt, song_for_path, style_for_path, "prompt", run)
            try:
                image_response = request_image(base_url, headers, prompt)
            except Exception as error:
                if verbose: print(f"An error occurred: {error}{NEW_LINE}")
                continue
            revised_prompt = get_revised_prompt(image_response)
            revised_prompt_fp = write_text(revised_prompt, song_for_path, style, "revised-prompt", run)
            image_fp = write_image(image_response, song_for_path, style, run)
            if verbose: print(f"PROMPT: {prompt_fp}. REVISED PROMPT: {revised_prompt_fp}. IMAGE: {image_fp}.")

main("src/config-mine.yaml", "/Users/scarlettswerdlow/tswift-golden/data/lyrics.csv")
"""