from typing import Generator
from fingrlix.optimizer import optimize_day, OptimizationResult, NoFeasibleSolution
from fingrlix.fetch import fetch
from datetime import datetime
from fingrlix.parser import parse_to_menu
from nutrition.models import Nutrition

def _fetch_menu(in_weeks: int, intake: Nutrition):
    iso_calendar = datetime.now().isocalendar()
    week_number = iso_calendar[1]
    for_week = week_number + in_weeks
    html = fetch(for_week)
    foods = parse_to_menu(html)
    tolerance = 0.05  # 5 % tolerance
    while True:
        try:
            result = optimize_day(foods, intake, tolerance_ratio=tolerance)
            break
        except NoFeasibleSolution:
            tolerance += 0.05  # increase tolerance by 5 %
    return for_week, result

def next_four_weeks_menus(intake: Nutrition) -> Generator[tuple[datetime, OptimizationResult]]:
    for i in range(1,5):
        week, menu = _fetch_menu(i, intake)
        sunday = datetime.fromisocalendar(datetime.now().year, week, 7)
        yield sunday, menu

def next_week_menu(intake: Nutrition) -> tuple[datetime, OptimizationResult]:
    week, menu = _fetch_menu(1, intake)
    sunday = datetime.fromisocalendar(datetime.now().year, week, 7)
    return sunday, menu