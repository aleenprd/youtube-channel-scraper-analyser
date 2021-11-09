"""
This is a YouTube Scraper based on:
https://github.com/hridaydutta123/the-youtube-scraper/tree/master/scraper
The script will parse a list of videos and retrieve specific information
from each video and store it as a JSON file for later processing.
"""
# IMPORTING PYTHON PACKAGES
# ============================ #
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
import random
import os
import sys
from tqdm import tqdm
from typing import Dict, List


# Define the format of the response
RESPONSE = {
    'id': str,
    'title': str,
    'upload_date': str,
    'duration': str,
    'description': str,
    'genre': str,
    'is_paid': bool,
    'is_unlisted': bool,
    'is_family_friendly': bool,
    'uploader': {
        'channel_id': str,
    },
    'statistics': {
        'views': int,
        'likes': int,
        'dislikes': int
    }
}


# DEFINE HELPER FUNCTIONS
# ============================ #

def read_json_local(path: str):
    """Read JSON from local path."""
    with open(path, 'r') as f:
        file = json.load(f)
    return file


def load_configuration_file(optionsPath: str):
    """
    Checks if the file that's searched (specifically options in JSON)
    and reads the file to memory if found and content is correct.
    """
    if os.path.isfile(optionsPath):
        optionsFile = read_json_local(optionsPath)
        if len(optionsFile) == 0:
            print("*\nEmpty options file.")
            return False
        else:
            return optionsFile
    else:
        print("*\nMissing or wrongly named options file.")
        return False


def make_soup(url: str) -> BeautifulSoup:
    """
    Read the contents at the given URL and returns a
    Python object based on the structure of the content.
    """
    html = urlopen(url).read()
    return BeautifulSoup(html, 'lxml')


def is_true(string: str) -> bool:
    """Convert string of type 'false/true' or '0/1' to boolean."""
    return string.lower() not in ['false', '0']


def remove_comma(string: str) -> str:
    """Removes comma from a string."""
    return ''.join(string.split(','))


def scrape_video_data(youtube_video_url: str) -> Dict:
    """
    Scrape data from YouTube video page and returns a dict.
    """
    # Extract text from URL
    soup = make_soup(youtube_video_url)

    soup_itemprop = soup.find(id='watch7-content')

    if len(soup_itemprop.contents) > 1:
        video = RESPONSE
        uploader = video['uploader']
        statistics = video['statistics']
        video['regionsAllowed'] = []

        video['id'] = id
        # get data from tags having `itemprop` attribute
        for tag in soup_itemprop.find_all(itemprop=True, recursive=False):
            key = tag['itemprop']
            if key == 'name':
                # get video's title
                video['title'] = tag['content']
            elif key == 'duration':
                # get video's duration
                video['duration'] = tag['content']
            elif key == 'datePublished':
                # get video's upload date
                video['upload_date'] = tag['content']
            elif key == 'genre':
                # get video's genre (category)
                video['genre'] = tag['content']
            elif key == 'paid':
                # is the video paid?
                video['is_paid'] = is_true(tag['content'])
            elif key == 'unlisted':
                # is the video unlisted?
                video['is_unlisted'] = is_true(tag['content'])
            elif key == 'isFamilyFriendly':
                # is the video family friendly?
                video['is_family_friendly'] = is_true(tag['content'])
            elif key == 'thumbnailUrl':
                # get video thumbnail URL
                video['thumbnail_url'] = tag['href']
            elif key == 'interactionCount':
                # get video's views
                statistics['views'] = int(tag['content'])
            elif key == 'channelId':
                # get uploader's channel ID
                uploader['channel_id'] = tag['content']
            elif key == 'description':
                video['description'] = tag['content']
            elif key == 'playerType':
                video['playerType'] = tag['content']
            elif key == 'regionsAllowed':
                video['regionsAllowed'].extend(tag['content'].split(','))

        all_scripts = soup.find_all('script')
        for i in range(len(all_scripts)):
            try:
                if 'ytInitialData' in all_scripts[i].string:
                    match = re.findall("label(.*)", re.findall(
                        "LIKE(.*?)like", all_scripts[i].string)[0])[0]
                    hasil = (''.join(match.split(',')).split("\"")[-1]).strip()
                    try:
                        video['statistics']['likes'] = eval(hasil)
                    except:
                        video['statistics']['likes'] = 0

                    match = re.findall("label(.*)", re.findall(
                        "DISLIKE(.*?)dislike", all_scripts[i].string)[0])[0]
                    hasil = (''.join(match.split(',')).split("\"")[-1]).strip()
                    try:
                        video['statistics']['dislikes'] = eval(hasil)
                    except:
                        video['statistics']['dislikes'] = 0

            except:
                pass

        # return RESPONSE
        return video

    return ({
        'error': 'Video with the ID {} does not exist'.format(id)
    })


def extract_metadata(res: Dict) -> Dict:
    """Extract specific metadata from a dictionary of values."""
    title = res['title']
    uploader = res['uploader']['channel_id']
    upload_date = res['upload_date']

    duration = res['duration']
    minutes = int(re.search('PT(.*)M', duration).group(1))
    seconds = int(re.search('M(.*)S', duration).group(1))
    duration = minutes * 60 + seconds

    views = res['statistics']['views']
    likes = str(res['statistics']['likes']).replace('.', '')
    dislikes = res['statistics']['dislikes']

    out = {
        'title': title,
        'channel_id': uploader,
        'upload_date': upload_date,
        'duration': duration,
        'views': views,
        'likes': str(likes),
        'dislikes': dislikes,
        'scrape_date': current_date
    }

    return out


def scrape_list(links_list: List) -> List:
    """Scrape a list of URL links."""
    # Print current datetime
    print(datetime.now().strftime(" %H:%M:%S"))

    # Keep track of runtime
    t1 = time.time()
    with open(links_list) as f:
        channel_videos = f.readlines()

    scraped_videos_list = []
    for i in tqdm(range(0, len(channel_videos))):
        try:
            response = scrape_video_data(channel_videos[i])
            metadata = extract_metadata(response)
            scraped_videos_list.append(metadata)
            if i % 10 == 0:
                print(i)
                print(datetime.now().strftime(" %H:%M:%S"))
        except:
            pass
        time.sleep(random_generator)

    # Keep track of runtime
    print(f"URL list scraped in: {round(time.time()-t1,2):,}s")

    return scraped_videos_list


# THE MAIN METHOD
# ============================ #
if __name__ == "main":
    runtime_start = time()

    # Random generate times for sleep intervals
    random_generator = random.randint(0, 3)

    # Keep track of current position in time
    current_date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    current_time = datetime.now().strftime(" %H:%M:%S")
    current_date = datetime.today().strftime('%Y-%m-%d')

    # Unpack the configuration options
    # -------------------------------------- #
    config_path = "config/scraper_config.json"
    config_options = load_configuration_file(config_path)

    if config_options is False:
        print("\nMissing, empty or wrongly named config file. \
            Program will terminate.")
        sys.exit()
    else:
        print("\nFetching options from configuration file: ")
        print("# -------------------------------------- #")
        for option in config_options.keys():
            print(f"\t* {option}: {config_options[option]}")
        print()
        links_list = config_options["INPUT_PATH"]
        output_path = config_options["OUTPUT_PATH"]

    # Scrape list of videos on the channel
    # -------------------------------------- #
    scraped_videos_list = scrape_list(links_list)

    # Save the results in a JSON file
    # -------------------------------------- #
    with open(output_path, 'w') as f:
        json.dump(scraped_videos_list, f)

    # Keeping track of runtime.
    # -------------------------------------- #
    runtime_end = time()
    print(f"\nScript done in {round(runtime_end-runtime_start,2):,}s")
