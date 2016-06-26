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
    subs = r"wallpapers+wallpaper+WQHD_Wallpaper+topwalls+multiwall+" \
           r"gmbwallpapers+gmbwallpapers+MinimalWallpaper+WidescreenWallpaper+EarthPorn"
    parser.add_argument("-s", "--subreddit", type=str, default=subs)
    parser.add_argument("-t", "--time", type=str, default="day")
    args = parser.parse_args()

    # Python Reddit Api Wrapper
    print('Get top wallpaper - by /u/admin-mod (original by /u/ssimunic)')
    print('Sub(s) - {0}'.format(args.subreddit))

    # Get home directory and location where image will be saved (default location for Ubuntu is used)
    homedir = os.path.expanduser('~')
    wallpaprDir = homedir + "\\Pictures\\Wallpapers\\"

    # Create folder if it doesn't exist
    if not os.path.exists(wallpaprDir):
        os.makedirs(wallpaprDir)

    # Get top image from Reddit or local
    try:
        imageLocation = get_image_from_reddit(args.subreddit, args.time, wallpaprDir)
    except:
        print('Unable to fetch the file. Re-using local files...')
        imageLocation = get_image_from_local(wallpaprDir)

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


# Get image links of top 20 most upvoted wallpaper of the day
def get_top_images(subreddit, time):
    urls = []
    # Get top 20 posts
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
    print('Found top {0} posts.'.format(len(urls)))
    return urls


# Get image from reddit and save in local folder
def get_image_from_reddit(subreddit, time, wallpaprDir):
    # Get Praw object
    r = praw.Reddit(user_agent="Get top wallpaper - by /u/admin-mod (original by /u/ssimunic)")

    # Get top image paths in a list
    try:
        imageUrls = get_top_images(r.get_subreddit(subreddit), time)
    except:
        raise ConnectionError('Unable to connect to internet. Re-using local files...')

    # If no images returned, then raise an error.
    if len(imageUrls) == 0:
        raise ValueError('No images returned by get_top_images()')

    for i in range(0, len(imageUrls)):
        # Pick a random URL from list
        random.seed()
        imageUrl = imageUrls[random.randint(0, len(imageUrls) - 1)]

        # Get home directory and location where image will be saved
        imageName = imageUrl.rsplit("/", 1)[1]
        imageLocation = wallpaprDir + imageName

        # See if image is available locally. If yes, re-use
        if get_image_from_local(wallpaprDir, existingFile=imageName) == imageName:
            print('Image found in the local dir. Will be reused!')
            return imageLocation

        # Request image
        print('Requesting image - ', imageUrl)
        try:
            response = requests.get(imageUrl)
        except:
            raise ConnectionError('Unable to connect to internet. Re-using local files...')

        # If image is available online, proceed to save
        if response.status_code == 200:
            print('Image found!')
            
            # Write to disk
            with open(imageLocation, 'wb') as fo:
                for chunk in response.iter_content(4096):
                    fo.write(chunk)
            print('Image saved at - ', imageLocation)

            # Check if HD image width>=1920
            with Image.open(imageLocation, 'r') as im:
                width, height = im.size
            if width < 1920:
                print('Image ({0}x{1}) is not HD(width>=1920). Skipping...'.format(width, height))
                os.remove(imageLocation)
                continue
            else:
                print('Image size: {0}x{1}'.format(width, height))
                return imageLocation
        else:
            raise ValueError('Image not found!')


# Get image from local folder
def get_image_from_local(wallpaprDir, existingFile='default.jpg'):
    # Get list of existing files
    files = [f for f in os.listdir(wallpaprDir)
             if os.path.isfile(os.path.join(wallpaprDir, f)) and
             f.endswith(tuple([".jpg", ".png", ".jpeg"]))]

    # Check if there is an existing file of the name given in argument
    if existingFile in files:
        return existingFile

    # Return a random file
    return os.path.join(wallpaprDir, files[random.randint(0, len(files) - 1)])

if __name__ == '__main__':
    main()
