from fingrlix.menu import next_week_menu
from nutrition import PersonalData, calculate_nutrition_intake

def prepare_next_menu(personal_data: PersonalData):
    intake = calculate_nutrition_intake(personal_data)
    return next_week_menu(intake)