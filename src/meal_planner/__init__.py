from meal_planner.models import Course
from food.models import Ingredient, Recipe, Meal
from nutrition.models import Nutrition
import io
import json
from datetime import date


def _load_recipe(name: str) -> Recipe:
    with io.open(f"data/recipes/{name}.json") as f:
        return Recipe.from_dict(json.loads(f.read()))


def _parse_course(d: dict) -> Course:
    course = Course()
    for course_name, meal_data in d.items():
        if meal_data is None:
            continue
        meal = Meal(
            recipe=_load_recipe(meal_data["recipe"]),
            portions=float(meal_data["portions"]),
        )
        course.add_meal(course_name, meal)
    return course


def _load_course(date: date) -> Course:
    with io.open(f"data/courses/{date}.json") as f:
        return _parse_course(json.loads(f.read()))


def load_courses():
    """Load recipes from JSON files."""
    return [_load_course(date.today())]


if __name__ == "__main__":
    for course in load_courses():
        print(course.display())
