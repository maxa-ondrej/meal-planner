from food.models.ingredient import Ingredient
from nutrition.models import Nutrition


class Recipe:
    def __init__(
        self,
        name: str,
        ingredients: list[Ingredient],
        nutrition: Nutrition,
        instructions: str,
        time_mins: float,
    ):
        self.name = name
        self.ingredients = ingredients
        self.nutrition = nutrition
        self.instructions = instructions
        self.time_mins = time_mins

    def __repr__(self):
        return f"Recipe(name={self.name}, ingredients={repr(self.ingredients)}, nutrition={repr(self.nutrition)}, instructions={self.instructions}, time_mins={self.time_mins})"

    def __str__(self):
        return f"{self.name} with ingredients {', '.join(map(str, self.ingredients))} and nutrition {self.nutrition}"

    def __mul__(self, factor: float) -> "Recipe":
        """Scale the recipe by a factor."""
        scaled_ingredients = [ing * factor for ing in self.ingredients]
        scaled_nutrition = self.nutrition * factor
        return Recipe(
            name=self.name,
            ingredients=scaled_ingredients,
            nutrition=scaled_nutrition,
            instructions=self.instructions,
            time_mins=self.time_mins,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        ingredients = [Ingredient.from_dict(ing) for ing in data["ingredients"]]
        nutrition = Nutrition.from_dict(data["nutrition"])
        return cls(
            name=data["name"],
            ingredients=ingredients,
            nutrition=nutrition,
            instructions=data["instructions"],
            time_mins=data["time_mins"],
        )

    def display(self, indents: int = 0) -> str:
        indent_str = " " * (indents * 2)
        return (
            f"{self.name}\n{indent_str}Ingredients:\n"
            + "\n".join(
                f"{indent_str}  - {ing.display(indents + 3)}"
                for ing in self.ingredients
            )
            + f"\n{indent_str}Nutrition: {self.nutrition}\n{indent_str}Instructions: {self.instructions}\n{indent_str}Time: {self.time_mins} mins"
        )
