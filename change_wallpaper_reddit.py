#!/usr/bin/env python
import praw
import os
import subprocess
import requests
import argparse
import ctypes
import platform
import random
from PIL import Image


def main():
    # Argument parser
    parser = argparse.ArgumentParser()
    subs = r"wallpapers+wallpaper+WQHD_Wallpaper+topwalls+multiwall+gmbwallpapers+gmbwallpapers"
    parser.add_argument("-s", "--subreddit", type=str, default=subs)
    parser.add_argument("-t", "--time", type=str, default="day")
    args = parser.parse_args()

    # Python Reddit Api Wrapper
    print('Get top wallpaper - by /u/ssimunic & /u/admin-mod')
    print('Sub(s) - {0}'.format(args.subreddit))

    imageLocation = get_image_from_reddit(args.subreddit, args.time)

    if imageLocation:
        # Check if OS is Linux or Windows, then execute command to change wallpaper
        platformName = platform.system()
        if platformName.startswith("Lin"):
            os.system("gsettings set org.gnome.desktop.background picture-uri file://" + imageLocation)
            print('Wallpaper changed...')
        if platformName.startswith("Win"):
            SPI_SETDESKWALLPAPER = 20
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, imageLocation, 3)
            print('Wallpaper changed...')
    else:
        print('Wallpaper not changed!')


# Get image link of most upvoted wallpaper of the day
def get_top_image(subreddit, time):
    urls = []
    for submission in subreddit.get_top(params={'t': time}, limit=20):
        url = submission.url
        if url.endswith(tuple([".jpg", ".png", ".jpeg"])):
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


def get_image_from_reddit(subreddit, time):

    r = praw.Reddit(user_agent="Get top wallpaper - by /u/ssimunic & /u/admin-mod")
    # Get top image paths in a list
    imageUrls = get_top_image(r.get_subreddit(subreddit), time)

    for i in range(0, len(imageUrls)):
        # Pick a random URL from list
        random.seed()
        imageUrl = imageUrls[random.randint(0, len(imageUrls) - 1)]

        # Request image
        print('Requesting image - ', imageUrl)
        response = requests.get(imageUrl)

        # If image is available, proceed to save
        if response.status_code == 200:
            print('Image found!')
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

            # Check if HD width>=1900
            hd = False
            with Image.open(saveLocation, 'r') as im:
                width, height = im.size
                if width < 1920:
                    print('Image ({0}x{1}) is not HD(width>=1920). Skipping...'.format(width, height))
                    hd = False
                else:
                    print('Image size: {0}x{1}'.format(width, height))
                    hd = True
            # If HD Image then all good, return with the location
            if hd:
                return saveLocation
            # If not, then remove the image and try another one
            else:
                os.remove(saveLocation)
                continue
        else:
            print('Image not found!')

    # If here, then no good image found.
    return ''


if __name__ == '__main__':
    main()
