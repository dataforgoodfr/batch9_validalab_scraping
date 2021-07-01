import pandas as pd
import karmahutils as kut
import warnings
import urllib
from time import sleep
from bs4 import BeautifulSoup
import numpy as np

warnings.filterwarnings('ignore')


def build_about_urls(account, silent_mode=True, radicals=None, with_validation=True):
    """
    This function is meant to find the about page of a youtube account.
    :param account: name of a youtube account
    :param silent_mode: (default True)QoL option for tracing
    :param radicals : (default None) possible youtube radicals for channels/userpages and such.
    set to ['c', 'channel', 'user'] if empty.
    :param with_validation: (default True) check the existence of the constructed url before returning
    :return: a dict with one of the working URL and its 'type' in youtube classification (channel or user page..)
    """
    urls = []
    if radicals is None:
        radicals = ['c', 'channel', 'user']
    for radical in radicals:
        url = '/'.join(['https://www.youtube.com', radical, account, 'about'])
        if with_validation:
            try:
                urllib.request.urlopen(url)
            except Exception as e:
                if not silent_mode:
                    print('url', url, e)
                continue
        urls.append({'youtubeAccount': account, 'aboutURL': url, 'type': radical})
    return urls[0] if len(urls) else {'youtubeAccount': account, 'aboutURL': None, 'type': None}


def get_youtube_about(account_series, batch_size=300, sleep_time=5):
    """
    batch version of the previous function with a cadence to avoid hurting youtube's feelings.
    :param account_series: a series containing name of youtube accounts
    :param batch_size:number of 'simultaneous calls' (default 300)
    :param sleep_time: pause between secquence of calls (in s , default 5s)
    :return: a dataframe with for each account : the account name , the about page url , the type of account.
    """
    kut.display_message('reading accounts to fetch about urls')
    accounts = pd.DataFrame(account_series)
    start = kut.yet()
    result = []
    batch_number = 0
    for g, df in accounts.groupby(np.arange(len(accounts)) // batch_size):
        series = accounts[account_series.name]
        batch_df = series.apply(lambda x: pd.Series(build_about_urls(x)))
        result.append(batch_df)
        if batch_number:
            print('batch', batch_number)
            print('sleeping')
            sleep(sleep_time)
        batch_number += 1
    kut.job_done(start=start)
    return pd.concat(result, ignore_index=True)


def extract_url(token, silent_mode=True):
    """
    description missing
    :param token:
    :param silent_mode:
    :return:
    """
    short_token = token.split("%3F")[0].split("\"")[0]
    short_token_alt = token.split("?")[0].split("\"")[0]
    clean_token = short_token.replace("%2F", "/").replace("%3A", ":").replace("%40", "@")

    if not silent_mode:
        kut.display_message('token')
        print(token)
        kut.display_message('shorten token (%3F)')
        print(short_token == short_token_alt)
        print(short_token)
        kut.display_message('cleaned token')
        print(clean_token)

    url_tokens = clean_token.split(':')
    if len(url_tokens) < 2:
        return
    url_token = url_tokens[1]
    if not silent_mode:
        kut.display_message('url token')
        print(url_token)
    return 'http:' + url_token


def extract_urls(url):
    """
    Extract urls of links in the about page
    :param url:  an url of an about page
    :return: a list of links in the page
    """
    try:
        about_page = urllib.request.urlopen(url)
    except Exception as e:
        print('url', url, e)
        return
    about_soup = BeautifulSoup(about_page)
    tokens = about_soup.decode('utf-8').split('q=http')
    return list(set([extract_url(token) for token in tokens if not pd.isnull(extract_url(token))]))


def extract_links(data, aboutURL_column, batch_size=100, sleep_time=3, links_column='links'):
    """
    Takes a dataframe representing accounts with their respective about page and adds the links contained
    The job has a cadence to avoid getting banned by youtube
    :param data: dataframe containing about pages
    :param aboutURL_column: about pages url
    :param batch_size:  number of consecutive calls
    :param sleep_time: time to sleep between consecutive calls
    :param links_column: the actual output is this column. You can specifyu the name
    :return: a dataframe enriched with a column containing arrays of links
    """
    kut.display_message('extracting links from about urls')
    start = kut.yet()
    result = []
    batch_number = 0
    for g, df in data.groupby(np.arange(len(data)) // batch_size):
        df[links_column] = df[aboutURL_column].apply(lambda x: extract_urls(x))
        result.append(df)
        if batch_number:
            print('batch', batch_number)
            print('sleeping')
        batch_number += 1
        sleep(sleep_time)
    kut.job_done(start=start)
    return pd.concat(result, ignore_index=True)


