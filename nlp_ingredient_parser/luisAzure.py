from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import EntityLabelObject
from azure.cognitiveservices.language.luis.authoring.models import ExampleLabelObject
from msrest.authentication import CognitiveServicesCredentials

import datetime, json, os, time
import csv
from tqdm import tqdm
import re
import time

authoring_key = 'c04d90e868b64a428447ce34dd941306'
authoring_endpoint = 'https://ingredient-parser-authoring.cognitiveservices.azure.com/'

# instatiates a LUIS client
client = LUISAuthoringClient(authoring_endpoint, CognitiveServicesCredentials(authoring_key))

class UtterenceObject:
    def __init__(self, sentence, quantity, unit, ingredient, comment):
        self.sentence = re.sub(',|(|)', '', sentence)
        if quantity:
            self.quantity = re.sub(',|(|)', '', quantity)
        else:
            self.quantity = None
        if unit:
            self.unit = re.sub(',|(|)', '', unit)
        else:
            self.unit = None
        self.ingredient = re.sub(',|(|)', '', ingredient)
        if comment:
            self.comment = []
            for c in comment:
                self.comment.append(re.sub(',|(|)', '', c))
        else:
            self.comment = None

def get_list_of_contiguous_comments(comment, sentence):
    ''' This function is meant to extract the contiguous comments found within the  '''
    c_arr, s_arr = comment.split(" "), sentence.split(" ")
    contiguous_comments = []
    current_contiguous_comment = []
    while(len(s_arr)):
        if s_arr[0] != c_arr[0]:
            s_arr.pop(0)
        else:
            break
    while(len(c_arr) and len(s_arr)):
        temp_c = c_arr.pop(0)
        if temp_c == s_arr.pop(0):
            current_contiguous_comment.append(temp_c)
        else:
            contiguous_comments.append(" ".join(current_contiguous_comment))
            current_contiguous_comment = []
            while(len(s_arr)):
                if temp_c == s_arr.pop(0):
                    current_contiguous_comment.append(temp_c)
                    break
    if len(current_contiguous_comment):
        contiguous_comments.append(" ".join(current_contiguous_comment))
    return contiguous_comments
            

def get_first_continuous_comment(comment, sentence):
    # TODO - we need to change the behavior to return a list of strings that are all of the contiguous comment strings
    # -> if we do this, we need to change behavior when adding utterances.
    c_arr, s_arr = comment.split(" "), sentence.split(" ")
    out = []
    while(len(s_arr)): #makes sentence start with first word in the comment
        if s_arr[0] != c_arr[0]:
            s_arr.pop(0)
        else:
            break
    while(len(c_arr) and len(s_arr)): #if the word in comment matches word in sentence, append it to out - this would be better optimized as a doWhile loop, when that stops happening, break out
        temp_c = c_arr.pop(0)
        if temp_c == s_arr.pop(0):
            out.append(temp_c)
        else:
            break
    return " ".join(out) #Return it as a string, space separated

def create_utterance_object_list():
    utterances = []

    with open('nyt-ingredients-snapshot-2015.csv') as csvfile:
        # with open('ManualIngredientDataSet.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            sentence = re.sub(',|(|)', '', row[1].lower())
            unit = row[5].lower()
            ingredient = row[2].lower()
            comment = [row[6].lower()]

            def stupid_quantity(sentence):
                quantity = ""
                temp = sentence.split(' ')
                while(temp):    # appends any numbers found in the sentence to the quantity string
                    t = temp.pop(0)
                    if not t.isalpha():
                        quantity += t + " "
                    else:
                        break
                return quantity.strip()

            quantity = row[3] if row[3].find(".") == -1 else stupid_quantity(sentence)

            if (unit and unit not in sentence) or (ingredient not in sentence) or (quantity and quantity not in sentence): # if it's missing anything, pass
                # print("Printing cause we're missing this: {}; {}; {}; {}; {}".format(sentence, unit, ingredient, comment, quantity))
                continue
            if (comment[0] not in sentence and comment):
                # TODO - when this is redone, make sure comment is treated as a list
                comment = get_list_of_contiguous_comments(comment[0], sentence)

            # print("adding the following object: {}; {}; {}; {}; {}".format(sentence, quantity, unit, ingredient, comment))
            # time.sleep(1)

            utterances.append(UtterenceObject( # adds an utterance to the list given above
                sentence, 
                quantity, 
                unit,
                ingredient,
                comment
                )
            )
    return utterances

def create_app():
    # Create a new LUIS app
    app_name    = "Ingredient Parser {}".format(datetime.datetime.now())
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
    # manually add these to the intents
    # TODO - attach these to intent
    quantityEntityId = client.model.add_entity(app_id, app_version, name="quantity")
    unitEntityId = client.model.add_entity(app_id, app_version, name="unit")
    ingredientEntityId = client.model.add_entity(app_id, app_version, name="ingredient")
    commentEntityId = client.model.add_entity(app_id, app_version, name="comment")

def create_utterance(intent, utterance, labels):
    # when things becomes a list, update this.
    text = utterance.lower()

    def label(name, value):
        value = value.lower()
        start = text.index(value)
        return dict(entity_name=name, start_char_index=start, end_char_index = start + len(value))

    return dict(text=text, intent_name=intent, entity_labels = [label(n, v) for (n, v) in labels if v])

def add_utterances(app_id, app_version, utterances):
    azure_utterances = []
    for utterance in utterances[:10000]: # CHANGED THIS
        if(utterance.sentence == ""):
            continue
        # when things becomes a list, update this.
        labels = []
        if(utterance.quantity):
            labels.append(("quantity", utterance.quantity))
        if(utterance.unit):
            labels.append(("unit", utterance.unit))
        if(utterance.ingredient):
            labels.append(("ingredient", utterance.ingredient))
        if(utterance.comment):
            for comment in utterance.comment:
                labels.append(("comment", comment))

        azure_utterances.append(
            create_utterance("FindIngredient", utterance.sentence, labels))

    for i in tqdm(range(len(azure_utterances) // 10 - 1)):
        client.examples.batch(app_id, app_version, azure_utterances[i * 10:(i+1) * 10])
    print("{} example utterance(s) added.".format(len(azure_utterances)))

def run_application():
    print("creating utterances.")
    utterances = create_utterance_object_list()

    print("creating application.")
    app_id, app_version = create_app()

    print("create intents.")
    add_intents(app_id, app_version)

    print("add entities.")
    add_entities(app_id, app_version)

    print("add utterances.")
    add_utterances(app_id, app_version, utterances)
