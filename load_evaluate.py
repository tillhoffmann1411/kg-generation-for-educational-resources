import ast
import pandas as pd

def count_entries_with_links(df, column):
    # Assuming NaN or empty lists are considered as "no links"
    # If the column contains list-like structures as strings, you might need to convert them to lists first
    return df[df[column].str.len() > 0].shape[0]

def count_total_links(df, column):
    # If the column contains list-like structures as strings, you might need to convert them to lists first
    # Assuming each link corresponds to an element in the list
    return df[column].str.len().sum()


# Calculate percentage of correctly found wiki topics in the list
def get_perc_of_found_wikidata(df):
    total_count = len(df)
    m_count = len(df[df['Match'] == 'm'])
    m_percent = (m_count / total_count) * 100
    # Print results
    print(f"Nr of correct found wikidata topics - count: {m_count}")
    print(f"Nr of correct found wikidata topics - percentage: {m_percent:.2f}%")
    return m_percent

def get_perc_of_found_dbpedia(df):
    total_count = len(df)    
    m_count_d = len(df[df['wiki_dbpedia'] == 'd'])
    m_count_b = len(df[df['wiki_dbpedia'] == 'b'])
    m_count = m_count_d + m_count_b
    m_percent = (m_count / total_count) * 100
    # Print results
    print(f"Nr of correct found dbpedia topics - count: {m_count}")
    print(f"Nr of correct found dbpedia topics - percentage: {m_percent:.2f}%")
    return m_percent

def get_perc_of_found_wikipedia(df):
    total_count = len(df)
    m_count_w = len(df[df['wiki_dbpedia'] == 'w'])
    m_count_b = len(df[df['wiki_dbpedia'] == 'b'])
    m_count = m_count_w + m_count_b
    m_percent = (m_count / total_count) * 100
    # Print results
    print(f"Nr of correct found wikipedia topics - count: {m_count}")
    print(f"Nr of correct found wikipedia topics - percentage: {m_percent:.2f}%")
    return m_percent

# Calculate percentage of lecture topics where a corresponding wiki topic exists
def get_possible_wiki(df):
    total_count = len(df)
    m_count = len(df[df['wiki_exists'] == 'y'])
    m_percent = (m_count / total_count) * 100
    # Print results
    print(f"Nr of possible wiki topics - count: {m_count}")
    print(f"Nr of possible wiki topics - percentage: {m_percent:.2f}%")
    return df[df['wiki_exists'] == 'y']

# Get the number of entries which have at least one wikipedia ID
def get_wikipedia_entries(df):
    return df[df['wikipedia_ids'].str.len() > 0].shape[0]

# Get the number of entries which have at least one dbpedia ID
def get_dbpedia_entries(df):
    return df[df['dbpedia_ids'].str.len() > 0].shape[0]

# Get the number of entries which have at least one wikidata ID
def get_wikidata_entries(df):
    return df[df['wiki_ids'].str.len() > 0].shape[0]




df = pd.read_csv('topics_v2.csv')
link_types = ['beyondlinks', 'forwardlinks', 'backwardlinks', 'basiclinks', 'lecturelinks']
for i, row in df.iterrows():
    for column in link_types:
        if row.get(column) is not '' and not pd.isna(row.get(column)):
            row[column] = ast.literal_eval(row.get(column))
        else:
            row[column] = []
# Fill NaN values in parent_id with empty string
df['parent_id'] = df['parent_id'].fillna('')
parent_id_count = df[df['parent_id'] != ""].shape[0]
print(f'Number of entries with at least one parent id: {parent_id_count}')
for link_type in link_types:
    num_entries = count_entries_with_links(df, link_type)
    print(f'Number of entries with at least one {link_type}: {num_entries}')
    
    total_links = count_total_links(df, link_type)
    print(f'Total number of {link_type}: {total_links}')


# Wikidata Part
df = pd.read_excel('./evaluated/eval_enhanced_topics.xlsx')
link_types = ['wiki_ids']
df['wiki_ids'] = df['wiki_ids'].fillna('[]')
for i, row in df.iterrows():
    for column in link_types:
        if row.get(column) is not '[]':
            row[column] = ast.literal_eval(row.get(column))
        else:
            row[column] = []
print(f"Total count for all topics: {len(df)}")
print('# Wikidata Part')
print(f"Total count for all wikidata topics: {count_total_links(df, 'wiki_ids')}")
print(f"Total count for all wikidata topics: {get_wikidata_entries(df)}")
get_perc_of_found_wikidata(df)
df_wiki_exist = get_possible_wiki(df)
print(f"Now check percentage of topics where a wikidata topic exists - Nr of lecture topics: {len(df_wiki_exist)}")
get_perc_of_found_wikidata(df_wiki_exist)

# DBPediea Part
df_2 = pd.read_excel('./evaluated/eval_enhanced_topics_2.xlsx')
link_types = ['dbpedia_ids', 'wikipedia_ids']
df_2['dbpedia_ids'] = df_2['dbpedia_ids'].fillna('[]')
df_2['wikipedia_ids'] = df_2['wikipedia_ids'].fillna('[]')
for i, row in df_2.iterrows():
    for column in link_types:
        if row.get(column) is not '[]':
            row[column] = ast.literal_eval(row.get(column))
        else:
            row[column] = []
print('# DBPedia Part')
print(f"Total count for all dbpedia topics: {count_total_links(df_2, 'dbpedia_ids')}")
print(f"Total count for all dbpedia topics: {get_dbpedia_entries(df_2)}")
get_perc_of_found_dbpedia(df_2)
df_wiki_exist_2 = get_possible_wiki(df_2)
print(f"Now check percentage of topics where a wiki topic exists - Nr of lecture topics: {len(df_wiki_exist_2)}")
get_perc_of_found_dbpedia(df_wiki_exist_2)

# wikipedia Part
print('# Wikipedia Part')
print(f"Total count for all wikipedia topics: {count_total_links(df_2, 'wikipedia_ids')}")
print(f"Total count for all wikipedia topics: {get_wikipedia_entries(df_2)}")
get_perc_of_found_wikipedia(df_2)
print(f"Now check percentage of topics where a wiki topic exists - Nr of lecture topics: {len(df_wiki_exist_2)}")
get_perc_of_found_wikipedia(df_wiki_exist_2)