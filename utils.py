from humanfriendly.terminal import message
import tweepy
import json
import logging
import coloredlogs
# import subprocess
# https://beta.openai.com/docs/api-reference/completions/create?lang=python

data_path = '.data/'
coloredlogs.DEFAULT_FIELD_STYLES = dict(
        asctime=dict(color='green'),
        hostname=dict(color='cyan'),
        name=dict(color='red'),
        levelname=dict(color='white', bold=True),
        message=dict(color='yellow')
    )


def set_logger():
    
    coloredlogs.install()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    return logging.getLogger("BePequenoVQGAN")

def get_tweepy_api():
    with open('.tweepy/credentials.json') as json_file:
        credentials = json.load(json_file)

    auth = tweepy.OAuthHandler(credentials["API_key"], credentials["API_key_secret"])
    auth.set_access_token(credentials["Access_token"], credentials["Access_secret"])

    return tweepy.API(auth)


def hashtagify(sentence):
    #sentence = re.sub("[^0-9a-zA-Z]+", " ", sentence)
    return ''.join([word.capitalize() for word in sentence.replace('-', ' ').split()])


def split_auth_work(r):
    s = r.split(',')
    if len(s) == 1:
        return s[0], None
    else:
        return s[0], s[1].lstrip()