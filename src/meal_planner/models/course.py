from typing import Literal, TypeGuard

from food.models import Meal
from nutrition import Nutrition, total_nutrition

type CourseType = Literal["breakfast", "lunch", "dinner", "snack"]


class Course:
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

    @classmethod
    def choices(cls) -> list[CourseType]:
        return [cls.BREAKFAST, cls.LUNCH, cls.DINNER, cls.SNACK]

    @classmethod
    def is_valid(cls, course: str) -> TypeGuard[CourseType]:
        return course in cls.choices()

    @classmethod
    def get_courses(cls) -> list[CourseType]:
        return cls.choices()

    def __init__(
        self,
        meals: dict[CourseType, Meal] = {},
    ):
        self.meals = meals

    def __repr__(self):
        return f"Course(meals={repr(self.meals)})"

    def __str__(self):
        return f"Course with meals{''.join(f'\n  {course}: {meal}' for course, meal in self.meals.items())}"

    def display(self, indents: int = 0) -> str:
        indent_str = " " * (indents * 2)
        return f"{indent_str}{self.total_nutrition()}\n{"\n\n".join(
            f"{indent_str}{course}: {meal.display(indents + 1)}"
            for course, meal in self.meals.items()
        )}"

    def add_meal(self, course: str, meal: Meal):
        if not self.is_valid(course):
            raise ValueError(f"Invalid course: {course}")
        self.meals[course] = meal

    def get_meal(self, course: str) -> Meal | None:
        if not self.is_valid(course):
            raise ValueError(f"Invalid course: {course}")
        return self.meals.get(course)

    def remove_meal(self, course: str):
        if not self.is_valid(course):
            raise ValueError(f"Invalid course: {course}")
        if course in self.meals:
            del self.meals[course]

    def total_nutrition(self) -> Nutrition:
        return total_nutrition(
            list(map(lambda meal: meal.total_nutrition(), self.meals.values()))
        )
