from dataclasses import dataclass
from typing import Literal, Self

type ActivityLevel = Literal[
    "sedentary",
    "lightly_active",
    "moderately_active",
    "very_active",
    "extra_active",
]

type WeightPlan = Literal[
    "lose_weight",
    "maintain_weight",
    "gain_weight",
]

@dataclass
class PersonalData:
    weight_kg: float
    height_cm: float
    age: int
    gender: Literal["male", "female"]
    body_fat_percentage: float
    activity_level: ActivityLevel = "sedentary"
    weight_plan: WeightPlan = "lose_weight"


class Nutrition:
    def __init__(self, calories: int, protein: int, fat: int, carbohydrates: int):
        self.calories = calories
        self.protein = protein
        self.fat = fat
        self.carbohydrates = carbohydrates

    def __repr__(self):
        return (
            f"Nutrition(calories={self.calories}, protein={self.protein}, "
            f"fat={self.fat}, carbohydrates={self.carbohydrates})"
        )

    def __str__(self) -> str:
        return (
            f"{self.calories} kcal, {self.protein} g protein, "
            f"{self.fat} g fat, {self.carbohydrates} g carbohydrates"
        )

    def __add__(self, other: Self):
        return Nutrition(
            self.calories + other.calories,
            self.protein + other.protein,
            self.fat + other.fat,
            self.carbohydrates + other.carbohydrates,
        )

    def __mul__(self, factor: float):
        return Nutrition(
            int(self.calories * factor),
            int(self.protein * factor),
            int(self.fat * factor),
            int(self.carbohydrates * factor),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Nutrition):
            return False
        return (
            self.calories == other.calories
            and self.protein == other.protein
            and self.fat == other.fat
            and self.carbohydrates == other.carbohydrates
        )

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(
            calories=data["calories"],
            protein=data["protein"],
            fat=data["fat"],
            carbohydrates=data["carbohydrates"],
        )

    @classmethod
    def empty(cls) -> Self:
        return cls(0, 0, 0, 0)
