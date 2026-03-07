from fingrlix.menu import next_weeks_menus, next_week_menu
from nutrition import PersonalData, calculate_nutrition_intake

def prepare_next_menu(personal_data: PersonalData, weeks: int = 4):
    intake = calculate_nutrition_intake(personal_data)
    return next_weeks_menus(intake, weeks)