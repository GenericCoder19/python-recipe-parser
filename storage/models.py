from mongoengine import *

class Ingredient(Document):
    """Model for storing Ingredient information."""
    name = StringField(required=True)
    is_allergen = BooleanField()
    is_vegan = BooleanField()
    
class RecipeTag(Document):
    """Model for storing Recipe Tags."""
    name = StringField(required=True)

class RecipeIngredient(Document):
    """Model that connects Ingredients to Recipes."""
    ingredient = ReferenceField(Ingredient, required=True)
    amount = IntField(required=True)
    unit_measurement = StringField(required=True)
    comment = StringField()

class Recipe(Document):
    """Model for storing Recipe information.""" 
    name = StringField(required=True)
    recipe_ingredients = ListField(ReferenceField(RecipeIngredient), required=True)
    tags = ListField(ReferenceField(RecipeTag), required=True)
    notes = StringField()
    url = URLField()
    prep_time_minutes = IntField(required=True)
    cook_time_minutes = IntField(required=True)