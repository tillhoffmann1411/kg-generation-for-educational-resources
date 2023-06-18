import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse
from tqdm import tqdm

BASE_URL = 'https://oer.gitlab.io/OS/'


##########################
# Base level functions
###########################

def get_html_from_url(url: str) -> str:
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')

def get_a_from_html(html: str) -> list:
    """
    Retrieves all <a> tags from the given url and returns a list of dictionaries containing their href attribute and text.

    Args:
    - url (str): The URL to retrieve <a> tags from.

    Returns:
    - list: A list of dictionaries containing href and text attributes of each <a> tag.
    """
    a_tags = []
    a_tags += html.find_all('a')
    # Extract the href attribute and text from the a tags
    a_tags = [{'href': a.get('href'), 'text': a.text, 'class': a.get('class'), 'html_id': a.get('id')} for a in a_tags]
    return a_tags
  
def filter_links(links: list, classFilter: str, pageLink: str) -> list:
    filteredLinks = []
    # Check if classFilter is in the class attribute of the link
    for link in links:
        if link.get('class') is not None and classFilter in link.get('class'):
            # if href is relative, make it absolute by removing existing anchor and replacing it with the href
            href = link.get('href') if link.get('href').startswith('http') else urlunparse(urlparse(pageLink)._replace(fragment=link.get('href').replace('#', '')))
            filteredLinks.append(href)
    return filteredLinks

def get_lecture_links(links: list, pageLink: str) -> list:
    filteredLinks = []
    # Check if class is None and if href starts with 'Operating-Systems'
    for link in links:
        if link.get('class') is None and link.get('href') is not None and link.get('href').startswith('Operating-Systems'):
            # if href is relative, make it absolute by removing existing anchor and replacing it with the href
            href = BASE_URL + link.get('href')
            filteredLinks.append(href)
    return filteredLinks
  
def add_links_to_page(page: dict, html: str) -> dict:
    """
    Adds the given list of <a> tags to the given page dictionary.

    Args:
    - page (dict): The page dictionary to add the <a> tags to.
    - a_tags (list): The list of <a> tags to add to the page dictionary.

    Returns:
    - dict: The page dictionary with the <a> tags added.
    """
    links = get_a_from_html(html)
    page['beyondlinks'] = filter_links(links, 'beyondlink', page.get('url'))
    page['forwardlinks'] = filter_links(links, 'forwardlink', page.get('url'))
    page['backwardlinks'] = filter_links(links, 'backwardlink', page.get('url'))
    page['basiclinks'] = filter_links(links, 'basiclink', page.get('url'))
    page['lecturelinks'] = get_lecture_links(links, page.get('url'))
    return page

def add_links_to_topics(slides: list) -> list:
    for deck in tqdm(slides, desc='Identify relations in slide decks'):
        html = get_html_from_url(deck.get('topics')[0].get('url'))
        for topic in tqdm(deck.get('topics'), desc=deck.get('title'), leave=False, colour='green'):
            section = html.find('section', {'id': 'slide-' + topic.get('html_id')})
            if section is not None:
                topic = add_links_to_page(topic, section)
    return slides

def add_parent_ids(slides: list) -> list:
    for deck in slides:
        h1_num = None
        h2_nums = {}
        h3_nums = {}
        for topic in deck.get('topics'):
            if topic.get('tag') == 'h1':
                # Get the third and fourth number of the h1 title because it corresponds to the section number
                h1_num = topic.get('text')[2] + topic.get('text')[3]
                # if the h1_num is not made out of numbers quit the for loop
                if h1_num.isdigit():
                    topic['id'] = h1_num
                    topic['url'] = topic['url'] + '#/slide-' + topic['html_id']
                else:
                    break

            elif topic.get('tag') == 'h2':
                # add the h2 id to the list of h2 ids
                if len(topic.get('text').split('.')) >= 2:
                    topic_num = topic.get('text').split('.')[0]
                    if topic_num.isdigit():
                      id = h1_num + '.' + topic_num
                      h2_nums[id] = topic
                      topic['parent_id'] = h1_num
                      topic['id'] = id
                      topic['url'] = topic['url'] + '#/slide-' + topic['html_id']

            elif topic.get('tag') == 'h3':
                # add the h3 id to the list of h3 ids
                if len(topic.get('text').split('.')) >= 3:
                    topic_num = topic.get('text').split('.')[1]
                    if topic_num.isdigit():
                        parent_topic_num = h1_num + '.' + topic.get('text').split('.')[0]
                        id = h2_nums[parent_topic_num].get('id') + '.' + topic_num
                        h3_nums[id] = topic
                        topic['parent_id'] = h2_nums[parent_topic_num].get('id')
                        topic['id'] = id
                        topic['url'] = topic['url'] + '#/slide-' + topic['html_id']

            elif topic.get('tag') == 'h4':
                if len(topic.get('text').split('.')) >= 3:
                    topic_num = topic.get('text').split('.')[2]
                    if topic_num.isdigit():
                        parent_topic_num = h1_num + '.' + topic.get('text').split('.')[0] + '.' + topic.get('text').split('.')[1]
                        id = h3_nums[parent_topic_num].get('id') + '.' + topic_num
                        topic['parent_id'] = h3_nums[parent_topic_num].get('id')
                        topic['id'] = id
                        topic['url'] = topic['url'] + '#/slide-' + topic['html_id']
    return slides