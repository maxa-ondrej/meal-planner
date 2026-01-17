from nutrition.models import PersonalData
from fingrlix import prepare_next_menu


day, result = prepare_next_menu(
    PersonalData(
        weight_kg=104,
        height_cm=189,
        age=22,
        gender="male",
        body_fat_percentage=14.8,
        activity_level="sedentary",
        weight_plan="lose_weight",
    )
)
print(f"Menu for day {day}:")
print(result)