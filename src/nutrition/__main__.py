# Example usage
from nutrition.calculator import calculate_nutrition_intake
from nutrition.models import PersonalData

nutrition = calculate_nutrition_intake(
    PersonalData(
            weight_kg=104,
            height_cm=189,
            age=22,
            gender="male",
            body_fat_percentage=14.8,
        )
    )
print(nutrition)