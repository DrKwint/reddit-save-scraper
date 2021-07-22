import json
import re
import unicodedata
from logging import root
from pathlib import Path
from re import sub

import fire
import praw
import requests
from PIL import Image
from praw.reddit import Comment, Submission
from tqdm import tqdm
import datetime


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD',
                                      value).encode('ascii',
                                                    'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def extract(item):
    summary = {}

    def add(x):
        summary[x] = str(item.__dict__[x])

    # universal
    add('id')
    add('subreddit')
    add('permalink')
    if type(item) == Submission:
        summary['type'] = 'submission'
        add('title')
        add('url')
    elif type(item) == Comment:
        summary['type'] = 'comment'
        add('link_id')
        add('parent_id')
    else:
        print(type(item))
        exit()
    return summary


def main(root_directory="./saved/"):
    reddit = praw.Reddit("educated_gynoid")
    me = reddit.redditor("educated_gynoid")
    saved_items = []

    for item in tqdm(me.saved(limit=None)):
        saved_items.append(extract(item))
    del item
    del me

    dt = str(datetime.datetime.now().date()).replace(':', '.')
    with open('saved_items_{}.json'.format(dt), 'w') as json_file:
        json.dump(list(saved_items), json_file)

    if not Path(root_directory).exists:
        Path(root_directory).mkdir()
    for item in tqdm(saved_items):
        if item['type'] == 'submission':
            if '.png' in item['url']:
                extension = '.png'
            if '.jpg' in item['url']:
                extension = '.jpg'
            else:
                continue
            subreddit_path = Path(root_directory, item['subreddit'])
            if not subreddit_path.exists():
                subreddit_path.mkdir()
            r = requests.get(item['url'])
            title = item['title'] if len(
                item['title']) < 64 else item['title'][:64]
            path = subreddit_path / (slugify(title) + extension)
            with open(path, "wb") as f:
                f.write(r.content)


if __name__ == "__main__":
    fire.Fire(main)
