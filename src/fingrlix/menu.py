from typing import Generator, List, Tuple
from fingrlix.errors import NoMenuFoundError
from fingrlix.optimizer import optimize_day, OptimizationResult, NoFeasibleSolution
from fingrlix.models import BatchResult
from fingrlix.fetch import Batch, fetch
from datetime import datetime
from fingrlix.parser import parse_to_menu
from nutrition.models import Nutrition

def _fetch_menu(week: int, batch: Batch, intake: Nutrition, start_day: int = 1) -> BatchResult:
    html = fetch(week, batch)
    foods = parse_to_menu(html)
    meals: List[OptimizationResult] = []
    days: List[Tuple[datetime, OptimizationResult]] = []
    
    # Allow foods to repeat in 50% of the batch (e.g., 3 days -> can appear in 2 days max)
    import math
    max_repetitions = math.ceil(batch.meals_count * 0.5)
    
    for i in range(batch.meals_count):
        result = optimize_day(foods, intake, ignored_results=meals, max_repetitions=max_repetitions)
        meals.append(result)
        day = datetime.fromisocalendar(datetime.now().year, week, start_day + i)
        days.append((day, result))
    
    return BatchResult(batch_name=batch.name, days=days)

def next_weeks_menus(intake: Nutrition, weeks: int = 4) -> Generator[BatchResult | None]:
    for i in range(1, weeks + 1):
        day_of_week = 1  # Monday
        for batch in Batch:
            iso_calendar = datetime.now().isocalendar()
            week_number = iso_calendar[1]
            week = week_number + i
            try:
                batch_result = _fetch_menu(week, batch, intake, start_day=day_of_week)
                yield batch_result
                day_of_week += batch.meals_count
            except NoMenuFoundError:
                yield None
                day_of_week += batch.meals_count

def next_week_menu(intake: Nutrition) -> BatchResult:
    iso_calendar = datetime.now().isocalendar()
    week_number = iso_calendar[1]
    week = week_number + 1
    return _fetch_menu(week, Batch.FR_SA_SU, intake, start_day=5)