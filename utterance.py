import csv

utterances = []

class Utterance_Object:
    def __init__(self, sentence, quantity, unit, ingredient, comment):
        self.sentence = sentence
        self.intent = "FindIngredient"
        self.unit = unit
        self.quantity = quantity
        self.ingredient = ingredient
        self.comment = comment

with open('nyt-ingredients-snapshot-2015.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        utterances.append(Utterance_Object(
            row[1],
            row[3],
            row[5],
            row[2],
            row[6])
        )

utterances.pop(0)

'''
for utterance in utterances[:10]:
    print("Sentence: {}\nIngredient: {}".format(utterance.sentence, utterance.ingredient))
'''
