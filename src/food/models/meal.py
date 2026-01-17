from food.models.recipe import Recipe
from nutrition.models import Nutrition


class Meal:
    def __init__(self, recipe: Recipe, portions: float):
        self.recipe = recipe
        self.portions = portions

    def __repr__(self):
        return f"Meal(recipe={repr(self.recipe)}, portions={self.portions})"

    def __str__(self):
        return f"Recipe ({self.total_nutrition()}): {self.portions}x {self.recipe}"

    def total_nutrition(self) -> Nutrition:
        return self.recipe.nutrition * self.portions

    def display(self, indents: int = 0) -> str:
        return (self.recipe * self.portions).display(indents)
