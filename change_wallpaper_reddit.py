#!/usr/bin/env python
import praw
import os
import subprocess
import requests
import argparse
import ctypes
import platform
import random

# Argument parser
parser = argparse.ArgumentParser()
subs = r"wallpapers+wallpaper+WQHD_Wallpaper+topwalls+multiwall+gmbwallpapers+gmbwallpapers"
parser.add_argument("-s", "--subreddit", type=str, default=subs)
parser.add_argument("-t", "--time", type=str, default="day")
args = parser.parse_args()

# Get image link of most upvoted wallpaper of the day
def get_top_image(subreddit):
    urls = []
    for submission in subreddit.get_top(params={'t': args.time}, limit=20):
        url = submission.url
        if url.endswith(".jpg"):
            urls.append(url)
            continue
        # Imgur support
        if ("imgur.com" in url) and ("/a/" not in url):
            if url.endswith("/new"):
                url = url.rsplit("/", 1)[0]
            id = url.rsplit("/", 1)[1].rsplit(".", 1)[0]
            urls.append("http://imgur.com/" + id + ".jpg")
            continue

    return urls

# Python Reddit Api Wrapper
r = praw.Reddit(user_agent="Get top wallpaper from /r/" + args.subreddit + " by /u/ssimunic")

# Get top image path
imageUrls = get_top_image(r.get_subreddit(args.subreddit))
imageUrl = imageUrls[random.randint(0, len(imageUrls)-1)]

# Request image
response = requests.get(imageUrl)

# If image is available, proceed to save
if response.status_code == 200:
    # Get home directory and location where image will be saved (default location for Ubuntu is used)
    homedir = os.path.expanduser('~')
    id = imageUrl.rsplit("/", 1)[1].rsplit(".", 1)[0]
    saveLocation = homedir + "/Pictures/Wallpapers/" + id + ".jpg"

    # Create folders if they don't exist
    dir = os.path.dirname(saveLocation)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Write to disk
    with open(saveLocation, 'wb') as fo:
        for chunk in response.iter_content(4096):
            fo.write(chunk)

    # Check if OS is Linux or Windows, then execute command to change wallpaper
    platformName = platform.system()
    if platformName.startswith("Lin"):
        os.system("gsettings set org.gnome.desktop.background picture-uri file://" + saveLocation)
    if platformName.startswith("Win"):
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, saveLocation, 3)
