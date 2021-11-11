# %%
"""
Use Selenium to browse through a channel's videos page.
Extract the URLs to all the videos in the channel.
URLs will be parsed later for extracting other information.
Solution based on:
https://github.com/banhao/scrape-youtube-channel-videos-url/blob/master/scrape-youtube-channel-videos-url.py
"""
import sys
import os
from time import time, sleep
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
import json


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


# THE MAIN METHOD
# ============================ #
if __name__ == "__main__":
    runtime_start = time()
    random_generator = random.randint(0, 36)

    # Unpack the configuration options
    # -------------------------------------- #
    config_path = "config/channel_scraper_config.json"
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
        url = config_options["INPUT_PATH"]
        output_path = config_options["OUTPUT_PATH"]

    # Set up the driver
    # -------------------------------------- #

    # Don't foget to get the type of Chromedriver you need,
    # save it on disk somwhere and then specify the path to it
    # as per this answer on StackOverflow:
    # https://stackoverflow.com/questions/42478591/python-selenium-chrome-webdriver

    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=chrome-data")
    driver = webdriver.Chrome(executable_path=r"C:\\chromedriver.exe")

    # Start up the driver
    # -------------------------------------- #
    channel_id = url.split('/')[4]
    print(f"\nScraping channel id: {channel_id}")
    driver.get(url)
    sleep(random_generator)
    dt = datetime.datetime.now().strftime("%Y%m%d%H%M")
    height = driver.execute_script(
        "return document.documentElement.scrollHeight")
    lastheight = 0

    # Scrolling through the page
    # -------------------------------------- #
    while True:
        if lastheight == height:
            break
        lastheight = height
        driver.execute_script("window.scrollTo(0, " + str(height) + ");")
        sleep(random_generator)
        height = driver.execute_script(
            "return document.documentElement.scrollHeight")

    user_data = driver.find_elements_by_xpath('//*[@id="video-title"]')

    # SAVING THE USER DATA
    # ============================ #
    print(user_data)
    for i in user_data:
        print(i.get_attribute('href'))
        link = (i.get_attribute('href'))
        f = open(output_path + channel_id + '-' + dt + '.list', 'a+')
        f.write(link + '\n')
    f.close

    # Keeping track of runtime.
    # -------------------------------------- #
    runtime_end = time()
    print(f"\nScript done in {round(runtime_end-runtime_start,2):,}s")
