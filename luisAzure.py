from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import EntityLabelObject
from azure.cognitiveservices.language.luis.authoring.models import ExampleLabelObject
from msrest.authentication import CognitiveServicesCredentials

import datetime, json, os, time
import csv

authoring_key = 'c04d90e868b64a428447ce34dd941306'
authoring_endpoint = 'https://ingredient-parser-authoring.cognitiveservices.azure.com/'

'''
utterances = []

def create_entity_object(sentence, entity_name, value):
    # get the index for the beginning and end of the word.
    start = sentence.find(value)
    end = start + len(value) - 1
    if start == -1:
        return None
    else:
        return EntityLabelObject(entity_name=entity_name,
                                start_char_index = start,
                                end_char_index = end)
'''

class UtterenceObject:
    def __init__(self, sentence, quantity, unit, ingredient, comment):
        self.sentence = sentence.replace(",","").replace(")","").replace("(","")
        self.quantity = quantity.replace(",","").replace(")","").replace("(","")
        self.unit = unit.replace(",","").replace(")","").replace("(","")
        self.ingredient = ingredient.replace(",","").replace(")","").replace("(","")
        self.comment = comment.replace(",","").replace(")","").replace("(","")

utterances = []

with open('nyt-ingredients-snapshot-2015.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        sentence = row[1]
        unit = row[5]
        ingredient = row[2]
        comment = row[6]
        quantity = ""

        temp = sentence.split(' ')
        while(temp):
            t = temp.pop(0)
            if not t.isalpha():
                quantity += t
            else:
                break
        quantity.strip()

        if (unit not in sentence) or (ingredient not in sentence) or (quantity not in sentence):
            continue
        if (comment not in sentence):
            comment = sentence

        utterances.append(UtterenceObject(
            sentence, # sentence
            quantity, # quantity
            unit, # unit
            ingredient, # ingredient
            comment # comment
            )
        )

# instatiates a LUIS client
client = LUISAuthoringClient(authoring_endpoint, CognitiveServicesCredentials(authoring_key))

def create_app():
    # Create a new LUIS app
    app_name    = "Ingredient Parser{}".format(datetime.datetime.now())
    app_desc    = "Ingredient parser built with the LUIS Python SDK"
    app_version = "0.1"
    app_locale  = "en-us"

    app_id = client.apps.add(dict(name=app_name,
                                    initial_version_id=app_version,
                                    description=app_desc,
                                    culture=app_locale))

    print("Created LUIS app {}\n with ID {}".format(app_name, app_id))
    return app_id, app_version

def add_intents(app_id, app_version):
    intentId = client.model.add_intent(app_id, app_version, "FindIngredient")

    print("Intent FindIngredient {} added.".format(intentId))

def add_entities(app_id, app_version):
    quantityEntityId = client.model.add_entity(app_id, app_version, name="quantity")
    unitEntityId = client.model.add_entity(app_id, app_version, name="unit")
    ingredientEntityId = client.model.add_entity(app_id, app_version, name="ingredient")
    commentEntityId = client.model.add_entity(app_id, app_version, name="comment")

def create_utterance(intent, utterance, *labels):
    text = utterance.lower()

    def label(name, value):
        value = value.lower()
        start = text.index(value)
        return dict(entity_name=name, start_char_index=start, end_char_index = start + len(value))

    return dict(text=text, intent_name=intent, entity_labels = [label(n, v) for (n, v) in labels])

def add_utterances(app_id, app_version):
    azure_utterances = []
    for utterance in utterances[:2000]:
        if(utterance.sentence == ""):
            continue
        azure_utterances.append(create_utterance("FindIngredient", utterance.sentence,
                ("quantity", utterance.quantity),
                ("unit", utterance.unit),
                ("ingredient", utterance.ingredient),
                ("comment", utterance.comment)
                ))
    for i in range(len(utterances[:2000]) // 10):
        client.examples.batch(app_id, app_version, azure_utterances[i * 10:(i+1) * 10])
    print("{} example utterance(s) added.".format(len(azure_utterances)))

def train_app(app_id, app_version):
    response = client.train.train_version(app_id, app_version)
    waiting = True
    while waiting:
        info = client.train.get_status(app_id, app_version)

        waiting = any(map(lambda x: 'Queued' == x.details.status or 'InProgress' == x.details.status, info))
        if waiting:
            print("waiting 10 seconds for training to complete..")
            time.sleep(10)
