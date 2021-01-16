import flask
from flask import request, jsonify, render_template, redirect, url_for
import json
import requests
from bs4 import BeautifulSoup, SoupStrainer
import io
import os
from os import environ
from google.cloud import language_v1
import heapq

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Render sample HTML file
@app.route('/')
def init_extension():
    return render_template(
        'index.html'
    )

# Extract keywords from long texts using Google NLP API
def analyze_entity_for_keywords(text_content):
    """
    Analyzing Entities in a String

    Args:
      text_content The text content to analyze
    """
    client = language_v1.LanguageServiceClient()
    TOP_SALIENCE_PC = 4
    MAX_RESULTS = 10

    # Available types: PLAIN_TEXT, HTML
    type_ = language_v1.Document.Type.PLAIN_TEXT

    # Optional. If not specified, the language is automatically detected.
    # For list of supported languages:
    # https://cloud.google.com/natural-language/docs/languages
    language = "en"
    document = {"content": text_content, "type_": type_, "language": language}

    # Available values: NONE, UTF8, UTF16, UTF32
    encoding_type = language_v1.EncodingType.UTF8

    response = client.analyze_entities(request = {'document': document, 'encoding_type': encoding_type})
    
    # Get the language of the text, which will be the same as
    # the language specified in the request or, if not specified,
    # the automatically-detected language.
    print(u"Language of the text: {}".format(response.language))

    results = list()
    resultset = set()
    # Loop through entitites returned from the API
    for entity in response.entities:

        if entity.name in resultset:
            continue
        heapq.heappush(results, (entity.salience, entity.name))
        resultset.add(entity.name)

    num_results = min(MAX_RESULTS, int((TOP_SALIENCE_PC * len(results)) / 100))
    #Get the n (= num_results) keywords of largest salience score
    return [entity[1] for entity in heapq.nlargest(num_results, results)]

# Get urls of relevant articles based on the current article's title
@app.route('/getSearchResultsFromBiasedArticle')
def getSearchResultsFromBiasKeywords():
    #TODO: Replace this sample text with article title.

    text='''
    An internal FBI bulletin disseminated to law enforcement this week warned that "armed protests" are being planned at all 50 state capitols and in Washington in the days leading up to Biden's swearing in. Federal law enforcement agencies issued urgent bulletins calling for assistance securing the nation's capital, which now bristles with road blocks and steel barriers to wall off the "People's House" and will host as many as 25,000 National Guard -- a stronger military footprint than the US has in Afghanistan, Iraq and Syria combined.
By Friday, the FBI had received 140,000 digital tips regarding the attack, including photos and video, federal officials had opened 275 criminal investigations, charged roughly 98 individuals, and taken 100 individuals into custody.
As senior administration leaders who would normally take the lead remained silent for days -- including the heads of the Justice Department, the Department of Homeland Security and the President himself -- federal officials launched the most extensive counterterrorism probe since September 11, 2001, and continued planning to fortify Washington.
"Our posture is aggressive. It's going to stay that way through the inauguration," FBI Director Christopher Wray said at a Thursday briefing on inauguration security. He added that the agency was monitoring "extensive" online chatter about further potential armed protests and issued a warning to the men and woman who wreaked havoc on the Capitol.
"We know who you are, if you're out there," Wray said, "and FBI agents are coming to find you."
The domestic terrorists struck at a time when the US government is confronting the worst known cyberattack by a foreign adversary in its history, with Russia suspected of penetrating hundreds of businesses and numerous federal agencies. Their bloodshed and destruction come as Covid-19 claims record daily death tolls and a jobs crisis is brewing, with nearly 1 million people filing for unemployment benefits for the first time last week.
The insurrection, fueled by Trump's lies about his definitive election loss, exposed the reach of baseless conspiracy theories that have radicalized Americans to the point that they laid siege to their own Capitol.'''
    
    # keywords = analyze_entity_for_keywords(text)

    # print("Keywords are {}".format(keywords))
    results = list()
    BASE_URL = 'https://www.google.com/search?'
    #Max number of urls per keyword
    MAX_RESULTS_PER_QUERY = 2

    #Sample article title 
    keyword = "internal FBI bulletin disseminated to law enforcement"
    # for keyword in keywords:
    try:
        page = requests.get("https://www.google.com/search?q={keyword}".format(keyword=keyword, num=MAX_RESULTS_PER_QUERY))
        soup = BeautifulSoup(page.content, "html.parser", parse_only=SoupStrainer('a'))
        count = 0
        urls = list()
        for link in soup:
            link_href = link.get('href')
            if "url?q=" in link_href and not "webcache" in link_href:
                if(checkForNonArticleUrl(link_href) != True):
                    print(" link href is {}".format(link_href))  
                    urls.append(link.get('href').split("?q=")[1].split("&sa=U")[0])
                    count += 1
            if count == MAX_RESULTS_PER_QUERY:
                break
        results.append({'keyword': keyword, 'urls': urls})
    except Exception as e:
        raise Exception(e.message())
    return json.dumps({'data': results, 'content-type': 'application/json'})

def checkForNonArticleUrl(url):
    irrelevant_urls = ['wikipedia', 'dictionary']
    for word in irrelevant_urls:
        if(word in url):
            return True
        return False

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)