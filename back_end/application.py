import flask
from flask import request, jsonify
# from googlesearch import search
# from google.cloud import language_v1
# from google.cloud.language_v1 import enums
# import heapq

import json
import requests
from bs4 import BeautifulSoup

#Library Files used for the Speech To Text parts.
import subprocess
# from pydub import AudioSegment
import io
import os
# from google.cloud import speech
# from google.cloud.speech import enums as en
# from google.cloud.speech import types
# import wave
# from google.cloud import storage

app = flask.Flask(__name__)
app.config["DEBUG"] = True

#sample function
def analyze_article(text_content):
