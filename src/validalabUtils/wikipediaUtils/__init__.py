import pandas as pd
from bs4 import BeautifulSoup
import requests
import warnings
import karmahutils as kut

warnings.filterwarnings('ignore')


def get_wiki_banlist(banlist_url="https://fr.wikipedia.org/wiki/MediaWiki:Spam-blacklist"):
    """
    scrap wikipedia banlist and creates a dataframe representation of the information
    :param banlist_url: the url of wikipedia spam blacklist
    :return: a dataframe with 'entry' 'regex' 'reason' for each entry in the banlist.
    """
    res_ = requests.get(banlist_url)
    soup_ = BeautifulSoup(res_.content, "html.parser")
    blacklist = soup_.select('pre')[1].text.split('\n')[8:]
    return pd.DataFrame([{**{'entry': entry}, **extract_regex(entry)} for entry in blacklist if entry])


def extract_regex(wikipedia_banlist_entry):
    """
    Extract regex from wiki banlist page entry.
    :param wikipedia_banlist_entry: a soup formatted version of wiki banlist page row
    :return: a dict containing the *regex* and the ban reason
    """
    if pd.isnull(wikipedia_banlist_entry) or not wikipedia_banlist_entry:
        return {'regex': None, 'reason': None}
    entry = wikipedia_banlist_entry.split('#')
    return {'regex':shape_regex(entry[0]) , 'reason':entry[1]}


def shape_regex(regex):
    """
    structure a regex to match properties values.
    for instance properties in neo4j have no word boundaries.
    :param regex: a classic regex
    :return: a version of regex compatible for cypher matching
    """
    return regex.replace('\\b', '').replace('.\\com', '\\.com').strip()


def link_checklist(checklist, regex):
    """
    QoL function to help compare automatic vs manual treatment
    :param checklist: an array of manual entries deemed present
    :param regex:  a regex entry in the dataframe resulting of wikipedia banlist scraping
    :return: nothing :)
    """
    keywords = [{'key': X.split('.')[0], 'name': X} for X in checklist]
    for keyword in keywords:
        if keyword['key'] in regex:
            return keyword['name']
    return None


def check_db(graph, wiki_banlist_entry=None, regex=None, regex_column='regex', silent_mode=True):
    """
    check if a regex from wikipedia banlist has corresponding website nodes in db
    :param graph:  a connection to the neo4j validalab db
    :param wiki_banlist_entry: a row in the dataframe resulting of wikipedia banlist scraping
    :param regex: a regex to check over
    :param regex_column: name of the column containing the regex
    :param silent_mode: QoL for tracking results and bugs
    :return: a dict with *matches* as an array of entity names matched and a boolean indicating if there was a match

    """
    if regex is None:
        if wiki_banlist_entry is None:
            print("please provide either a regex or a dataframe row")
            return
        regex = wiki_banlist_entry[regex_column]

    results = graph.run(
        f"""MATCH(n:Website)
        WHERE n.name =~ '{regex}'
        RETURN n.name"""
    )
    result = list(results.data())
    if not len(result):
        return {'inDb': False, 'matches': None}

    if not silent_mode:
        print(result)
    return {'inDb': True, 'matches': [X['n.name'] for X in result]}


def compare_with_db(wiki_blacklist_entries, graph):
    """
    enrich with match
    :param wiki_blacklist_entries:
    :param graph:
    :return:
    """
    kut.display_message('find nodes matching the wikipedia banlist entries')
    start = kut.yet()
    wiki_blacklist_entries = wiki_blacklist_entries.merge(
        wiki_blacklist_entries.apply(
            lambda row: pd.Series(check_db(graph=graph, wiki_banlist_entry=row)),
            axis=1
        ),
        left_index=True,
        right_index=True
    )
    kut.job_done(start=start)
    return wiki_blacklist_entries.sort_values(by='inDb', ascending=False)
