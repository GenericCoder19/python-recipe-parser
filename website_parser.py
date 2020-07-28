from bs4 import BeautifulSoup
from ingredient import *
from recipe import *
import requests

def parse_ingredient_string(ingredient_string):
    Ingredient ingredient = new Ingredient()

    information = ingredient_string.split("\n")[1].strip().split(" ")

    word = ""
    while(word = information.pop(0)):
        if(not word.isalpha):
            ingredient.amount

# TODO - dynamically get addresses, and not just hardcode this.
main_recipe_url = 'https://www.allrecipes.com/recipe/'

for i in range(1000000):
    url = main_recipe_url + str(i)

    r = requests.get(url)
    print(url)
    if r.status_code == 200:
        recipe_content = r.content
        soup = BeautifulSoup(recipe_content, 'html.parser')

        name = soup.find("h1", {"class": "headline heading-content"}).text
        print('HIT: ' + name)

recipes = ["https://www.allrecipes.com/recipe/231026/keema-aloo-ground-beef-and-potatoes/?internalSource=rotd&referringContentType=Homepage&clickId=cardslot%201"]

for recipe in recipes:
    # get the request information
    r = requests.get(recipe)
    recipe_content = r.content

    soup = BeautifulSoup(recipe_content, 'html.parser')

    ingredients = soup.find("ul", { "class": "ingredients-section"})

    for ingredient_string in ingredients.findAll("span", {"class": "ingredients-item-name"}):
        print("ingredient: {}\n\n\n".format(ingredient_string))
    # print(type(ingredients))


