import csv
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import SKOS, OWL, SDO

# Define custom SKOS vocabulary
LECTURE = Namespace('https://oer.uni-muenster.de/OS/')
WIKIDATA = Namespace('https://www.wikidata.org/wiki/')
WIKIPEDIA = Namespace('https://en.wikipedia.org/?curid=')
DBPEDIA = Namespace('https://dbpedia.org/page/')


def create_rdf_graph(topics, g = Graph()):
    for row in topics:
        # Remove the first numbers before the first space
        label = row['section'].split(' ', 1)[1]
      
        # Create subject URI
        subject = URIRef(LECTURE[row['id']])

        # Create SKOS concept
        if row['meta_type'] is "structure":
            g.add((subject, RDF.type, SDO.CreativeWork))
            g.add((subject, SDO.name, Literal(label)))
            g.add((subject, SDO.url, Literal(row['url'])))
        else:
            g.add((subject, RDF.type, SKOS.Concept))
            g.add((subject, SKOS.prefLabel, Literal(label)))
            g.add((subject, OWL.sameAs, Literal(row['url'])))

        # Add relation to parent
        if row.get('parent_id') is not '':
            g.add((subject, SKOS.broader, LECTURE[row['parent_id']]))

        # Add beyond links to external resources
        for beyondLink in row['beyondlinks']:
            g.add((subject, SKOS.narrower, Literal(beyondLink)))
        # Add beyond links to external resources
        for basicLink in row['basiclinks']:
            g.add((subject, SKOS.related, Literal(basicLink)))

        # Add wikidata links
        # check if row has wikidata ids
        if row.get('wiki_ids') is not None:
            for index, wiki_id in enumerate(row['wiki_ids']):
                if wiki_id is not '':
                    match = URIRef(WIKIDATA[wiki_id])
                    g.add((subject, SKOS.relatedMatch, match))
                    g.add((match, RDF.type, SDO.Article))
                    g.add((match, SDO.name, Literal(row['wiki_labels'][index])))

        # Add wikipedia links
        # check if row has wikidata ids
        if row.get('wikipedia_ids') is not None:
            for index, wikipedia_id in enumerate(row['wikipedia_ids']):
                if wikipedia_id is not '' and wikipedia_id is not None:
                    match = URIRef(WIKIPEDIA[str(wikipedia_id)])
                    g.add((subject, SKOS.relatedMatch, match))
                    g.add((match, RDF.type, SDO.Article))
                    g.add((match, SDO.name, Literal(row['wikipedia_labels'][index])))

        # Add dbpedia links
        # check if row has wikidata ids
        if row.get('dbpedia_ids') is not None:
            for index, dbpedia_name in enumerate(row['dbpedia_ids']):
                if dbpedia_name is not '':
                    match = URIRef(DBPEDIA[dbpedia_name.replace(' ', '_')])
                    g.add((subject, SKOS.relatedMatch, match))
                    g.add((match, RDF.type, SDO.Article))
                    g.add((match, SDO.name, Literal(row['dbpedia_labels'][index])))

        # Add forward and backward links
        for forwardId in row.get('forwardIds'):
            if forwardId is not '':
                match = URIRef(LECTURE[forwardId])
                g.add((subject, SKOS.narrower, match))
        for backwardId in row.get('backwardIds'):
            if backwardId is not '':
                match = URIRef(LECTURE[backwardId])
                g.add((subject, SKOS.related, match))
        for lectureId in row.get('lectureIds'):
            if lectureId is not '':
                match = URIRef(LECTURE[lectureId])
                g.add((subject, SKOS.related, match))

    return g


def safe_dict_as_csv(d: dict, filename: str):
    try:
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=d[0].keys())
            writer.writeheader()
            for deck in d:
                writer.writerow(deck)
    except IOError:
        print("I/O error")


def safe_list_as_csv(d: dict, filename: str):
    try:
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=d[0].keys(), delimiter=';')
            writer.writeheader()
            for deck in d:
                writer.writerow(deck)
    except IOError:
        print("I/O error")

def safe_string_as_txt(s: str, filename: str):
    try:
        with open(filename, 'w') as txtfile:
            txtfile.write(s)
    except IOError:
        print("I/O error in safe_string_as_txt()")