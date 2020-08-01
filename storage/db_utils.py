from mongoengine import *
from models import *
from mongoengine.connection import _get_db
import sys

TEST_AZURE_DB_NAME = 'test_recipe_parser_db'
TEST_AZURE_DB_URL = 'mongodb' # need to test better with azure, local seems to work fine.



def test_db_connection():
    """Simple set of tests that will run on the test db to validate the db functions."""
    
    try:
        db = connect(TEST_AZURE_DB_NAME)
        ingredients = [
            Ingredient(name="white, granulated sugar", is_allergen=False),
            Ingredient(name="water", is_vegan=True),
            Ingredient(name="lemon juice"),
            Ingredient(name="cold water"),
        ]

        for ingredient in ingredients:
            ingredient.save()

        assert Ingredient.objects.count() == 4
        print(Ingredient.objects.all())

        RecipeTag(name="Sour").save()

        assert RecipeTag.objects(name__iexact="sour")

        for ingredient in Ingredient.objects.all():
            RecipeIngredient(ingredient=ingredient, amount=1, unit_measurement='Cup').save()

        print(RecipeIngredient.objects.all())

        tags = RecipeTag.objects(name__iexact="sour")[0]

        Recipe(
            name = "Lemonade",
            recipe_ingredients = RecipeIngredient.objects.all(),
            tags = [tags],
            instructions = [
                "Mix all that stuff!",
                "Enjoy :)"
            ],
            url = "https://www.simplyrecipes.com/recipes/perfect_lemonade/"
        ).save()

        print(Recipe.objects()[0].tags[0].name)

    except:
        print ("Unexpected error:", sys.exc_info()[0])
        raise
    finally:
        db.drop_database('test_recipe_parser_db')
        

test_db_connection()
