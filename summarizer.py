"""
summarizer.py
Summarizes a set of posts.
"""

from google.cloud.language import enums
from google.cloud.language import types

def summarizer(posts, client, cut_off=0.01):
    summary = {
        'q_about': [],
        'q_interest': [],
        'q_challenges': [],
        'q_change': [],
        'q_helpful': [],
        'q_other': []
    }
    for question in summary.keys():
        content = []
        for post in posts:
            content.append(getattr(post, question))
        content = ' '.join(content)
        document = types.Document(
            content = content,
            type = enums.Document.Type.PLAIN_TEXT)
        results = client.analyze_entities(document=document)
        summarized = []
        for result in results.entities:
            if result.salience >= cut_off or result.mentions[0].type == 1 or result.type == 1:
                summarized.append(result.name)
            else:
                break
        summary[question] = summarized

    return summary