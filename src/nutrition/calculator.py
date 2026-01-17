from nutrition.models import Nutrition, PersonalData, ActivityLevel
import numpy as np

_IDEAL_PROPORTIONS = {
    "protein": 0.32,
    "fat": 0.28,
    "carbohydrates": 0.40,
}

_NUTRITION_CAL_PER_G = {
    "protein": 4,
    "fat": 9,
    "carbohydrates": 4,
}

_ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extra_active": 1.9,
}

_WEIGHT_PLAN_MULTIPLIERS = {
    "lose_weight": 0.8,
    "maintain_weight": 1.0,
    "gain_weight": 1.2,
}


def total_nutrition(foods: list[Nutrition]) -> Nutrition:
    total_nutrition = Nutrition.empty()
    for food in foods:
        total_nutrition += food
    return total_nutrition



def calculate_nutrition_intake(data: PersonalData) -> Nutrition:
    bmr = _calculate_bmr(data)
    tdee = int(_apply_activity_level(bmr, data.activity_level) * 0.8) # 20 % deficit
    fat_intake = int(tdee * _IDEAL_PROPORTIONS["fat"] / _NUTRITION_CAL_PER_G["fat"])
    protein_intake = int(
        tdee * _IDEAL_PROPORTIONS["protein"] / _NUTRITION_CAL_PER_G["protein"]
    )
    carbs_intake = int(
        tdee
        * _IDEAL_PROPORTIONS["carbohydrates"]
        / _NUTRITION_CAL_PER_G["carbohydrates"]
    )
    return Nutrition(
        calories=tdee,
        protein=protein_intake,
        fat=fat_intake,
        carbohydrates=carbs_intake,
    )


def _calculate_bmr(data: PersonalData):
    bmrs: list[float] = []
    if data.gender == "male":
        bmrs.append(10 * data.weight_kg + 6.25 * data.height_cm - 5 * data.age + 5)
    else:
        bmrs.append(10 * data.weight_kg + 6.25 * data.height_cm - 5 * data.age - 161)

    if data.gender == "male":
        bmrs.append(13.397 * data.weight_kg + 4.799 * data.height_cm - 5.677 * data.age + 88.362)
    else:
        bmrs.append(9.247 * data.weight_kg + 3.098 * data.height_cm - 4.330 * data.age + 447.593)

    bmrs.append(370 + 21.6 * (1 - data.body_fat_percentage / 100) * data.weight_kg)

    return float(np.mean(bmrs))


def _apply_activity_level(bmr: float, activity_level: ActivityLevel) -> float:
    return bmr * _ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)

