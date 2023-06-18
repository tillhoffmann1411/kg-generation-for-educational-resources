import csv
import ast
import pandas as pd
from dotenv import load_dotenv
import os

# Import functions to extract educational resources topics
from extract_topic import *
# Import functions to extract relations between educational resources
from extract_relation import *

# Import functions to load articels from wikipedia, wikidata, and dbpedia
from transform_public_enhancer import *
# Import functions from the transform level to filter topics and relations
from transform_filter import *

# Import functions to create and export rdf and kg
from load_rdf import *

# Load .env file
load_dotenv()


# This is used to load already processed data (can be found in the repository in the /data folder)
ENHANCED_TOPIC_SRC = './final_data/final_data.csv'


## This base url is the place where all slide decks are linked
BASE_URL = 'https://oer.gitlab.io/OS/'
## This is the lecture identifier that we will use to filter links
LECTURE_IDENTIFIER = 'Operating-Systems'
## Safe intermediate steps as csv
SECURITY_SAVES = False
## Save the final data as an CSV before generating the knowledge graph
SAFE_AS_CSV = False
## If the data should be persisted in a Neo4j database (True/Flase)
LOAD_IN_DB = True
## If the data should be persisted in a .ttl file (True/Flase)
LOAD_AS_TURTLE = True

# Neo4j Config
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')











def main():
    enhanced_topics = []
    ##########################################################################################
    # Extract
    ##########################################################################################
    if ENHANCED_TOPIC_SRC is None or ENHANCED_TOPIC_SRC == '':
        #############################################
        # Extract Topics from the slides
        #############################################
        # Define the URL to retrieve
        slides = get_links_from_main_page('')
        # Get the topics for all slides
        slide_topics = get_topics_for_all_slides(slides)

        #############################################
        # Add relations between topics
        #############################################
        # Add the parent ids to the topics
        topics_with_parent = add_parent_ids(slide_topics)
        # Add links to the topics
        related_topics = add_links_to_topics(topics_with_parent)
        # Flatten the topics
        enhanced_topics = flatten_topics(related_topics)
        # Filter out topics with None id
        enhanced_topics = [d for d in enhanced_topics.values() if d.get('id') is not None]
        # Save the topics as CSV
        safe_dict_as_csv(enhanced_topics, 'enhanced_topics.csv')
    else:
        print('Loading enhanced topics from file')
        columns_with_list = ['beyondlinks', 'forwardlinks', 'backwardlinks', 'lecturelinks',
                             'basiclinks', 'wiki_ids', 'wiki_labels', 'wiki_descriptions',
                             'dbpedia_ids', 'dbpedia_labels', 'dbpedia_descriptions', 'wikipedia_ids', 'wikipedia_labels', 'wikipedia_descriptions']
        with open(ENHANCED_TOPIC_SRC, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                for column in columns_with_list:
                    if row.get(column) is not '' and not pd.isna(row.get(column)):
                        row[column] = ast.literal_eval(row.get(column))
                enhanced_topics.append(row)

                
    ##########################################################################################
    # Transform
    ##########################################################################################
    topic_df = pd.DataFrame.from_dict(enhanced_topics)

    # Get articles from Wikipedia, Wikidata, and DBpedia
    if 'wiki_ids' not in topic_df.columns or 'wikipedia_ids' not in topic_df.columns or 'dbpedia_ids' not in topic_df.columns:
        print('# Add data from Wikipedia, Wikidata, and DBpedia...')
        enhanced_topics = add_public_data_to_topics(enhanced_topics, ['wikipedia', 'dbpedia', 'wikidata'])
        if SECURITY_SAVES:
            safe_list_as_csv(enhanced_topics, 'article_data_export.csv')
    
    # Resolve the links to topic IDs
    if 'backwardIds' not in topic_df.columns or 'forwardIds' not in topic_df.columns or 'lectureIds' not in topic_df.columns:
        print('# Resolve relations from backwardlinks, forwardlinks, and lecturelinks...')
        enhanced_topics = resolve_links_to_topics(enhanced_topics)
        if SECURITY_SAVES:
            safe_list_as_csv(enhanced_topics, 'resolved_data_export.csv')
    
    # Classify the topics to structure and content topics
    if 'meta_type' not in topic_df.columns:
        print('# Classify topics extracted from lecture into structural and content topics...')
        enhanced_topics = mark_meta_topics(enhanced_topics)
        if SECURITY_SAVES:
            safe_list_as_csv(enhanced_topics, 'classified_data_export.csv')
    
    # Safe the resulting data  
    if SAFE_AS_CSV:
        print('# Safe final data as csv...')
        safe_list_as_csv(enhanced_topics, 'final_data_export.csv')




    ##########################################################################################
    # Load
    ##########################################################################################
    if LOAD_IN_DB:
        # Initialize the graph
        neo4j_config = {'uri': NEO4J_URI, 'database': 'neo4j', 'auth': {'user': NEO4J_USER, 'pwd': NEO4J_PASSWORD}}
        g = Graph(store='neo4j-cypher')
        g.open(neo4j_config)
        g.store.startBatchedWrite()
        g = create_rdf_graph(enhanced_topics, g)
        g.store.endBatchedWrite()
    
    if LOAD_AS_TURTLE:
        # Print the graph in Turtle format
        g = Graph()
        g = create_rdf_graph(enhanced_topics, g)
        safe_string_as_txt(g.serialize(format='turtle'), 'topics.ttl')


if __name__ == '__main__':
    main()
