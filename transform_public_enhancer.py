import requests
import re
from tqdm import tqdm

####################################################################################################
# Helper functions
####################################################################################################
def remove_special_chars_numbers(string):
    """
    Removes special characters and numbers from a string.
    """
    return re.sub(r"[^A-Za-z\s]", "", string)

def get_ngrams(text):
    words = text.split("_")
    ngrams = []
    for i in range(len(words) - 1):
        ngrams.append(words[i] + " " + words[i + 1])
    return ngrams

def split_results(results):
    wiki_ids = []
    wiki_labels = []
    wiki_description = []
    
    for result in results:
        wiki_ids.append(result['id'])
        wiki_labels.append(result['label'])
        wiki_description.append(result['description'])
        
    return wiki_ids, wiki_labels, wiki_description

####################################################################################################
# DBpedia part - not in use right now
####################################################################################################
def get_dbpedia_info(search_term):
    # Clean the search term by removing certain characters
    clean_term = search_term.strip().replace(" ", "_")
    
    if clean_term == "" or len(clean_term) <= 3:
        return None

    # Search for the term in Wikidata
    api_url = f"http://lookup.dbpedia.org/api/search?query={clean_term}&maxResults=1&format=json"
    response = requests.get(api_url).json()
    docs = response.get("docs", [])
    # Check if there is a result for the term
    if len(docs) > 0:
        result = docs[0]
        entity_id = remove_b_tags(result.get("label")[0])
        label = remove_b_tags(result.get("label")[0])
        # Take description from the result if it exists, otherwise use the label
        description = remove_b_tags(result.get("comment")[0] if "comment" in result and result.get("comment")[0] else "")
        
        # Otherwise, return the result for the search term
        return [{"id": entity_id, "label": label, "description": description}]
    elif len(clean_term.split("_")) > 2:
        terms = clean_term.split("_") + get_ngrams(clean_term)
        results = []
        for term in tqdm(terms, desc=f"Get DBpedia of {search_term}", leave=False, colour="green"):
            result = get_dbpedia_info(term)
            if result:
                results += result
        return results
    else:
        return None
    
    
def add_dbpedia_result_to_topics(topics: list) -> list:
    enhanced_topics = []
    for topic in tqdm(topics, desc="Getting DBpedia articles", leave=True):
        query = remove_special_chars_numbers(topic.get("section"))
        dbpedia_result = get_dbpedia_result(query)
        if dbpedia_result is not None:
            topic["dbpedia"] = dbpedia_result
        else:
            topic["dbpedia"] = None
            print(f"No DBpedia result for {query}")
        enhanced_topics.append(topic)
    return topics

def get_dbpedia_result(query):
    results = search_dbpedia(query)
    filtered_results = filter_results(results, query)
    return filtered_results[0] if len(filtered_results) > 0 else None

def search_dbpedia(query, max_results=5):
    url = f"http://lookup.dbpedia.org/api/search?query={query}&maxResults={max_results}&format=json"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)

    results = []
    if response.ok:
        data = response.json()
        docs = data.get("docs", [])
        if len(docs) == 0:
            return results
        for doc in docs:
            if "label" not in doc:
                continue
            result = {}
            result["label"] = remove_b_tags(doc.get("label", [])[0])
            result["score"] = doc.get("score", [])[0]
            result["resource"] = doc.get("resource", [])[0]
            result["description"] = remove_b_tags(
                doc.get("comment", [])[0] if doc.get("comment") else "")
            result["categories"] = doc.get("category", [])
            results.append(result)

    return results

def filter_results(results_list, search_term):
    matching_results = []
    for result in results_list:
        if search_term.lower() in result["label"].lower():
            matching_results.append(result)
    return matching_results

def remove_b_tags(s):
    s = s.replace("<B>", "")
    s = s.replace("</B>", "")
    return s

    
def add_dbpedia_to_topics(topics: list, prefix='dbpedia') -> list:
    enhanced_topics = []
    no_result_counter = 0
    for topic in tqdm(topics, desc="Getting dbpedia topics", leave=True):
        query = remove_special_chars_numbers(topic.get("section"))
        wiki_results = get_dbpedia_info(query)
        if wiki_results is not None and len(wiki_results) > 0:
            ids, labels, descriptions = split_results(wiki_results)
            topic[f"{prefix}_ids"] = ids
            topic[f"{prefix}_labels"] = labels
            topic[f"{prefix}_descriptions"] = descriptions
        else:
            topic[f"{prefix}_ids"] = None
            topic[f"{prefix}_labels"] = None
            topic[f"{prefix}_descriptions"] = None
            no_result_counter += 1
        enhanced_topics.append(topic)
    print(f"No {prefix} result for {no_result_counter} topics")
    return topics


####################################################################################################
# Wikidata part
####################################################################################################
def get_wikidata_info(search_term):
    # Clean the search term by removing certain characters
    clean_term = search_term.strip().replace(" ", "_")
    
    if clean_term == "" or len(clean_term) <= 3:
        return None

    # Search for the term in Wikidata
    api_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={clean_term}&format=json&language=en"
    response = requests.get(api_url).json()

    # Check if there is a result for the term
    if len(response["search"]) > 0:
        result = response["search"][0]
        entity_id = result["id"]
        label = result["label"]
        # Take description from the result if it exists, otherwise use the label
        description = result["description"] if "description" in result else label
        
        # Otherwise, return the result for the search term
        return [{"id": entity_id, "label": label, "description": description}]
    elif len(clean_term.split("_")) > 2:
        terms = clean_term.split("_") + get_ngrams(clean_term)
        results = []
        for term in tqdm(terms, desc=f"Get Wikidata of {search_term}", leave=False, colour="green"):
            result = get_wikidata_info(term)
            if result:
                results += result
        return results
    else:
        return None
    
def add_wikidata_to_topics(topics: list, prefix='wiki') -> list:
    enhanced_topics = []
    no_result_counter = 0
    for topic in tqdm(topics, desc="Getting Wikidata ids", leave=True):
        if topic.get("section") is None:
            continue
        query = remove_special_chars_numbers(topic.get("section"))
        wiki_results = get_wikidata_info(query)
        if wiki_results is not None and len(wiki_results) > 0:
            ids, labels, descriptions = split_results(wiki_results)
            topic[f"{prefix}_ids"] = ids
            topic[f"{prefix}_labels"] = labels
            topic[f"{prefix}_descriptions"] = descriptions
        else:
            topic[f"{prefix}_ids"] = None
            topic[f"{prefix}_labels"] = None
            topic[f"{prefix}_descriptions"] = None
            no_result_counter += 1
        enhanced_topics.append(topic)
    print(f"No {prefix} result for {no_result_counter} topics")
    return topics

####################################################################################################
# Wikipedia part
####################################################################################################
def get_wikipedia_info(search_term):
    # Clean the search term by removing certain characters
    clean_term = search_term.strip().replace(" ", "_")
    
    if clean_term == "" or len(clean_term) <= 3:
        return None

    # Search for the term in Wikipedia
    api_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={clean_term}&srlimit=3"
    response = requests.get(api_url).json()

    # Check if there is a result for the term
    if len(response["query"]["search"]) > 0:
        result = response["query"]["search"][0]
        entity_id = result["pageid"]
        label = result["title"]
        # Take description from the result if it exists, otherwise use the label
        description = result["snippet"] if "snippet" in result else label
        
        # Otherwise, return the result for the search term
        return [{"id": entity_id, "label": label, "description": description}]
    elif len(clean_term.split("_")) > 2:
        terms = clean_term.split("_") + get_ngrams(clean_term)
        results = []
        for term in tqdm(terms, desc=f"Get Wikipedia data of {search_term}", leave=False, colour="green"):
            result = get_wikipedia_info(term)
            if result:
                results += result
        return results
    else:
        return None

def add_wikipedia_to_topics(topics: list, prefix='wikipedia') -> list:
    enhanced_topics = []
    no_result_counter = 0
    for topic in tqdm(topics, desc="Getting Wikidata ids", leave=True):
        query = remove_special_chars_numbers(topic.get("section"))
        wiki_results = get_wikipedia_info(query)
        if wiki_results is not None and len(wiki_results) > 0:
            ids, labels, descriptions = split_results(wiki_results)
            topic[f"{prefix}_ids"] = ids
            topic[f"{prefix}_labels"] = labels
            topic[f"{prefix}_descriptions"] = descriptions
        else:
            topic[f"{prefix}_ids"] = None
            topic[f"{prefix}_labels"] = None
            topic[f"{prefix}_descriptions"] = None
            no_result_counter += 1
        enhanced_topics.append(topic)
    print(f"No {prefix} result for {no_result_counter} topics")
    return topics

####################################################################################################
# Main function
####################################################################################################
def add_public_data_to_topics(topics: list, sources: list) -> list:
    if 'wikidata' in sources:
        topics = add_wikidata_to_topics(topics)
    if 'wikipedia' in sources:
        topics = add_wikipedia_to_topics(topics)
    if 'dbpedia' in sources:
        topics = add_dbpedia_to_topics(topics)
    return topics