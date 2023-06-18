def filter_topics(flattened_topics, FILTER_STRINGS):
    filtered_list = []
    for d in flattened_topics.values():
        if d is not None:
            if not any(filter_string.lower() in d.get('section').lower() for filter_string in FILTER_STRINGS):
                filtered_list.append(d)
    return filtered_list

def resolve_links_to_topics(topics):
    for topic in topics:
        topic['backwardIds'] = []
        topic['forwardIds'] = []
        topic['lectureIds'] = []
        if topic.get('forwardlinks') is not None and len(topic.get('forwardlinks')) > 0:
            forwardIds = []
            for link in topic.get('forwardlinks'):
                # add a / infront of the html id
                revealjs_link = link.replace('#', '#/')
                row_of_linked_topic = [x for x in topics if x.get('url') == revealjs_link]
                forwardIds.append(row_of_linked_topic[0].get('id'))
            topic['forwardIds'] = forwardIds
        if topic.get('backwardlinks') is not None and len(topic.get('backwardlinks')) > 0:
            backwardIds = []
            for link in topic.get('backwardlinks'):
                # add a / infront of the html id
                revealjs_link = link.replace('#', '#/')
                row_of_linked_topic = [x for x in topics if x.get('url') == revealjs_link]
                backwardIds.append(row_of_linked_topic[0].get('id'))
            topic['backwardIds'] = backwardIds
        if topic.get('lecturelinks') is not None and len(topic.get('lecturelinks')) > 0:
            lectureIds = []
            for link in topic.get('lecturelinks'):
                # add a / infront of the html id
                revealjs_link = link.replace('#', '#/')
                row_of_linked_topic = [x for x in topics if x.get('url') == revealjs_link]
                # CAUTION! if the link is not found, then the actual url is diffenrent than the on in the link
                if len(row_of_linked_topic) > 0:
                    lectureIds.append(row_of_linked_topic[0].get('id'))
            topic['lectureIds'] = lectureIds
    return topics