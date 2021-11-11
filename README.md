# Youtube Video Scraper
Scrape a channel's videos for the purpose of mining statistical data. 

## Background 
I've been playing Activision-Blizzard's Hearthstone Tradinfg Card Game for a few years and recently I have been aware that there is quite a sizeable online community formed around the online game sensation. Nowadays, every game has a fan base which gathers along popular streamers who activate on social media channels such as Twitch or Youtube. For Hearthstone, I've come to know some of the bigger names in the industry such as Regiskillbin or Rarran. Since I like the game but I am also into programming and data science, I decided to build a Youtube scraper which would allow me to analyze statistics about how certain channels are performing, according to certain metrics. 


## How to use 
- You can scrape the links to all of a Youtube channel's videos, by running the `channel_scraper.py` (manually accept the pop-up from Google when the driver starts). 
- This will save you a list of URLs to go through with the `video_scraper.py` which scrapes information on each video such as views, likes, dislikes, etc. 
- In order to run the scripts, you need to give them some inputs as JSON files, stored in the `config` folder. They are named after their respective scripts. 
- The data can then be analyzed by using the codes in `explore.py`.

## Future work
- Improve the data exploration part. 
- Include more info to be scraped on each video. 
- Make the web driver automate more tasks.