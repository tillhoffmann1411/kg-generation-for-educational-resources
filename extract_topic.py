import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


# Impoort constants from main.py
from main import LECTURE_IDENTIFIER, BASE_URL

##########################
# Base level functions
###########################


def get_a_from_page(url: str) -> list:
    """
    Retrieves all <a> tags from the given url and returns a list of dictionaries containing their href attribute and text.

    Args:
    - url (str): The URL to retrieve <a> tags from.

    Returns:
    - list: A list of dictionaries containing href and text attributes of each <a> tag.
    """
    a_tags = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    a_tags += soup.find_all("a")
    # Extract the href attribute and text from the a tags
    a_tags = [{"href": a.get("href"), "text": a.text, "class": a.get(
        "class"), "html_id": a.get("id")} for a in a_tags]
    return a_tags


def get_anchor_links_from_page(url: str) -> list:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    anchor_links = []
    for a in soup.find_all("a", href=True):
        if a["href"].startswith("#"):
            anchor_links.append(a)
    a_tags = [{"href": a.get("href"), "text": a.text, "class": a.get(
        "class"), "html_id": a.get("id")} for a in anchor_links]
    return a_tags


def get_h_from_page(url: list) -> list:
    """
    Retrieves all <h1>, <h2>, <h3>, and <h4> tags from the given url and returns a list of dictionaries containing their id, text, tag, and url attributes.

    Args:
    - url (list): The URL to retrieve <h> tags from.

    Returns:
    - list: A list of dictionaries containing id, text, tag, and url attributes of each <h> tag.
    """
    h_tags = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    h_tags += soup.find_all("h1")
    h_tags += soup.find_all("h2")
    h_tags += soup.find_all("h3")
    h_tags += soup.find_all("h4")
    # Extract the id attribute and text from the h tags
    # If the id attribute is not present, set it to an empty string
    clean_h_tags = [{
        "text": h.text,
        "html_id": h.get("id") if h.get("id") is not None else "",
        "tag": h.name,
        "url": url
    } for h in h_tags]
    return clean_h_tags


##########################
# Page level functions
##########################

def get_links_from_main_page(path: str, base_url=BASE_URL) -> list:
    """
    Retrieves all <a> tags from the given URL and filters them to keep only those whose href contains "Operating-Systems" and ends with ".html". Returns a list of the filtered <a> tags.

    Args:
    - path (str): The path to retrieve <a> tags from.
    - base_url (str): The base URL to use for the request. Defaults to BASE_URL constant.

    Returns:
    - list: A list of dictionaries containing href and text attributes of each <a> tag that meets the filtering criteria.
    """
    main_page_a = get_a_from_page(base_url + path)

    # Filter the links to keep only those whose href contains "Operating-Systems" and ends with ".html"
    html_links = [link for link in main_page_a
                  if LECTURE_IDENTIFIER in link.get("href")
                  and link.get("href").endswith(".html")
                  ]

    return html_links


def get_topics_of_slide(path: str, base_url=BASE_URL) -> list:
    """
    Given a URL path and a base URL, returns the list of main topics in the slide.

    Args:
        path (str): The URL path.
        base_url (str, optional): The base URL. Defaults to BASE_URL.

    Returns:
        list: The list of main topics in the slide.
    """
    main_topics = get_h_from_page(base_url + path)
    return main_topics


##########################
# Iteration functions for all slides
##########################

def get_topics_for_all_slides(a_tags: list) -> list:
    """
    Given a list of "a" tags, returns a list of dictionaries, where each dictionary
    contains the title of a slide and its topics.

    Args:
        a_tags (list): The list of "a" tags.

    Returns:
        list: The list of dictionaries.
    """
    topics = []
    for a in tqdm(a_tags, desc="Scraping topics"):
        topics.append({"title": a.get("text"),
                      "topics": get_topics_of_slide(a.get("href"))})
    return topics


def flatten_topics(topics: list) -> list:
    flattened_topics = {}
    for topic in topics:
        for section in topic.get("topics"):
            # Check if section starts with a number or is h1 topic
            if section.get("text")[0].isdigit() or section.get("tag") == "h1":
                clean_topic = {
                    "id": section.get("id"),
                    "title": topic.get("title"),
                    "section": section.get("text"),
                    "html_id": section.get("html_id"),
                    "tag": section.get("tag"),
                    "url": section.get("url"),
                    "parent_id": section.get("parent_id"),
                    "beyondlinks": section.get("beyondlinks"),
                    "forwardlinks": section.get("forwardlinks"),
                    "backwardlinks": section.get("backwardlinks"),
                    "basiclinks": section.get("basiclinks"),
                    "lecturelinks": section.get("lecturelinks"),
                }
                flattened_topics[section.get("id")] = clean_topic
    return flattened_topics


def mark_meta_topics(topics: list) -> list:
    # Meta topics are: Introdiction, Conclusion, Summary, References, and Further Reading
    meta_topics = ["Introduction", "Conclusion", "Previously", "Summary", "References", "Further Reading", "Learning Objectives", "Quiz", "Question", "Recall"]

    for topic in topics:
        if any(meta_topic.lower() in topic["section"].lower() for meta_topic in meta_topics):
            topic["meta_type"] = "structure"
        else:
            topic["meta_type"] = "topic"

    return topics
