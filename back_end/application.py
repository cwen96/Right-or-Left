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
import urllib.request
import spacy
from collections import Counter
from google.cloud import automl
# import en_core_web_sm

os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "hackthenortheast-301907-6c2890f0557c.json"

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Render sample HTML file
@app.route("/")
def init_extension():
    return render_template("index.html")


@app.route("/getBiasResult", methods=["POST"])
def getResult():
    project_id = "hackthenortheast-301907"
    model_id = "TCN1082317464940838912"
    # nlp = en_core_web_sm.load()
    nlp = spacy.load("en_core_web_sm")

    json_data = request.get_json()
    contents = json_data["article_text"]
    print(contents)

    # contents='''
    #     An internal FBI bulletin disseminated to law enforcement this week warned that "armed protests" are being planned at all 50 state capitols and in Washington in the days leading up to Biden's swearing in. Federal law enforcement agencies issued urgent bulletins calling for assistance securing the nation's capital, which now bristles with road blocks and steel barriers to wall off the "People's House" and will host as many as 25,000 National Guard -- a stronger military footprint than the US has in Afghanistan, Iraq and Syria combined.
    #     By Friday, the FBI had received 140,000 digital tips regarding the attack, including photos and video, federal officials had opened 275 criminal investigations, charged roughly 98 individuals, and taken 100 individuals into custody.
    #     As senior administration leaders who would normally take the lead remained silent for days -- including the heads of the Justice Department, the Department of Homeland Security and the President himself -- federal officials launched the most extensive counterterrorism probe since September 11, 2001, and continued planning to fortify Washington.
    #     "Our posture is aggressive. It's going to stay that way through the inauguration," FBI Director Christopher Wray said at a Thursday briefing on inauguration security. He added that the agency was monitoring "extensive" online chatter about further potential armed protests and issued a warning to the men and woman who wreaked havoc on the Capitol.
    #     "We know who you are, if you're out there," Wray said, "and FBI agents are coming to find you."
    #     The domestic terrorists struck at a time when the US government is confronting the worst known cyberattack by a foreign adversary in its history, with Russia suspected of penetrating hundreds of businesses and numerous federal agencies. Their bloodshed and destruction come as Covid-19 claims record daily death tolls and a jobs crisis is brewing, with nearly 1 million people filing for unemployment benefits for the first time last week.
    #     The insurrection, fueled by Trump's lies about his definitive election loss, exposed the reach of baseless conspiracy theories that have radicalized Americans to the point that they laid siege to their own Capitol.'''

    doc = nlp(contents)

    # sentences is an array of tokens that can be individually converted into strings by appending '.text' to each element.
    sentences = list(doc.sents)
    results = list()
    strArray = ""
    count = 0
    right_sum = 0
    left_sum = 0

    for sentence in sentences:
        content = sentence.text

        if count < 5:
            strArray += content
            count += 1
        else:
            prediction_client = automl.PredictionServiceClient()
            # Get the full path of the model.
            model_full_id = automl.AutoMlClient.model_path(
                project_id, "us-central1", model_id
            )
            # Supported mime_types: 'text/plain', 'text/html'
            # content = (strArray, mime_type) = "text/plain"
            # https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#textsnippet
            text_snippet = automl.TextSnippet(content=content, mime_type="text/plain")
            payload = automl.ExamplePayload(text_snippet=text_snippet)

            response = prediction_client.predict(name=model_full_id, payload=payload)

            for annotation_payload in response.payload:
                print(
                    u"Predicted class name: {}".format(annotation_payload.display_name)
                )
                print(
                    u"Predicted class score: {}".format(
                        annotation_payload.classification.score
                    )
                )
                if annotation_payload.display_name == "right":
                    right_sum += annotation_payload.classification.score
                else:
                    left_sum += annotation_payload.classification.score

            strArray = ""
            count = 0
    label = "Right" if right_sum > left_sum else "Left"
    total_sum = right_sum + left_sum
    percentage = (
        round(
            right_sum / total_sum if right_sum > left_sum else left_sum / total_sum,
            3,
        )
        * 100
    )
    return json.dumps(
        {
            "data": {"label": label, "percentage": percentage},
            "content-type": "application/json",
        }
    )


# Get urls of relevant articles based on the current article's title
@app.route("/getSearchResultsFromArticleTitle", methods=["POST"])
def getSearchResultsFromArticleTitle():

    results = list()
    BASE_URL = "https://www.google.com/search?"
    # Max number of urls generated
    MAX_RESULTS_PER_QUERY = 3
    json_data = request.get_json()
    biased_article_title = json_data["title"]

    # Sample article title
    # biased_article_title = 'Chocolate Chip Cookies'
    # biased_article_title = 'Biden inauguration: All 50 US states on alert for armed protests'
    try:
        page = requests.get(
            "https://www.google.com/search?q={biased_article_title}".format(
                biased_article_title=biased_article_title
            )
        )
        soup = BeautifulSoup(page.content)
        # soup = BeautifulSoup(page.content, "html.parser", parse_only=SoupStrainer('a'))
        links = soup.findAll("a")
        count = 0
        urls = list()
        for link in links:
            link_href = link.get("href")
            if "url?q=" in link_href and not "webcache" in link_href:
                article_url = link.get("href").split("?q=")[1].split("&sa=U")[0]

                ar_page = requests.get(article_url)

                url_soup = BeautifulSoup(ar_page.content)

                article_title = url_soup.title.string

                print(article_title)
                if checkForInvalidTitle(article_title, biased_article_title) == True:
                    results.append({"title": article_title, "url": article_url})
                    count += 1

            if count == MAX_RESULTS_PER_QUERY:
                break
    except Exception as e:
        raise Exception(e.message())
    return json.dumps({"data": results, "content-type": "application/json"})


def checkForNonArticleUrl(url):
    irrelevant_urls = ["wikipedia", "dictionary"]
    for word in irrelevant_urls:
        if word in url:
            return True
    return False


def checkForInvalidTitle(test_title, demo_title):
    if test_title.find(demo_title) == -1:
        if test_title.find("403 Forbidden") == -1:
            if test_title.find("unavailable") == -1:
                if test_title.find("youtube") == -1:
                    return True
    return False


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

    response = client.analyze_entities(
        request={"document": document, "encoding_type": encoding_type}
    )

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
    # Get the n (= num_results) keywords of largest salience score
    return [entity[1] for entity in heapq.nlargest(num_results, results)]


if __name__ == "__main__":
    HOST = environ.get("SERVER_HOST", "localhost")
    try:
        PORT = int(environ.get("SERVER_PORT", "5000"))
    except ValueError:
        PORT = 5000
    app.run(HOST, PORT, debug=True)
