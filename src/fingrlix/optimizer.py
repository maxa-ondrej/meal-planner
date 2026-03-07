from typing import List, Tuple
from collections import defaultdict
import pulp
from fingrlix.models import Food, OptimizationResult, Totals
from fingrlix.errors import NoFeasibleSolution
from nutrition import Nutrition

def list_to_id(foods: List[Food], portions: List[Tuple[Tuple[str, str], int]]) -> str:
    return "".join([
        [str(portion[1]) for portion in portions if portion[0] == food][0]
        if any(portion[0] == food for portion in portions)
        else "0"
    for food in foods])

# Helper for ± tolerance
def add_macro_constraint(prob: pulp.LpProblem, tolerance_ratio: float, total_expr: pulp.LpAffineExpression, target: int, name: str, allow_more: bool = True):
    lower = (1 - tolerance_ratio) * target
    upper = (1 + tolerance_ratio) * target
    prob += total_expr >= lower, f"{name}_min"
    if not allow_more:
        prob += total_expr <= upper, f"{name}_max"


def optimize_day(
    foods: List[Food],
    target: Nutrition,
    ignored_results: List[OptimizationResult] = [],
    integer_portions: bool = True,
    max_repetitions: int = 0
):
    """Optimize daily meal plan.
    
    Args:
        foods: Available foods to choose from
        target: Target nutrition goals
        ignored_results: Previous optimization results in the batch
        integer_portions: Whether to use integer portions
        max_repetitions: Maximum times a food can appear across the batch (0 = no repetition)
    """
    ignored_meals: List[List[Tuple[Food, int]]] = [result.plan for result in ignored_results]
    # Create LP problem: minimize total cost
    prob = pulp.LpProblem("DailyDietPlan")

    # Decision variables: how many portions of each food
    var_cat = pulp.LpInteger if integer_portions else pulp.LpContinuous
    portions = {
        (food.name, food.variant): pulp.LpVariable(f"portions_{food.name}_{food.variant}", lowBound=0, upBound=1, cat=var_cat)
        for food in foods
    }

    ignored_meals: List[List[Tuple[Food, int]]] = [result.plan for result in ignored_results]
    # Create LP problem: minimize total cost
    prob = pulp.LpProblem("DailyDietPlan")

    # Decision variables: how many portions of each food
    var_cat = pulp.LpInteger if integer_portions else pulp.LpContinuous
    portions = {
        (food.name, food.variant): pulp.LpVariable(f"portions_{food.name}_{food.variant}", lowBound=0, upBound=1, cat=var_cat)
        for food in foods
    }        

    # Objective: minimize nutrition deviation (sum of squared differences from target)
    total_calories = pulp.lpSum(food.calories * portions[(food.name, food.variant)] for food in foods)
    total_fat      = pulp.lpSum(food.fat * portions[(food.name, food.variant)] for food in foods)
    total_carbs    = pulp.lpSum(food.carbohydrates * portions[(food.name, food.variant)] for food in foods)
    total_protein  = pulp.lpSum(food.protein * portions[(food.name, food.variant)] for food in foods)

    # Minimize sum of absolute deviations from target nutrition
    # Calories and Carbs as constraints (±10%)
    cal_lower = 0.9 * target.calories
    cal_upper = 1.1 * target.calories
    carb_lower = 0.9 * target.carbohydrates
    carb_upper = 1.1 * target.carbohydrates
    prob += total_calories >= cal_lower, "Calories_min"
    prob += total_calories <= cal_upper, "Calories_max"
    prob += total_carbs >= carb_lower, "Carbs_min"
    prob += total_carbs <= carb_upper, "Carbs_max"

    # Fat: minimize
    # Protein: maximize (by minimizing negative protein)
    # Price: minimize
    total_price = pulp.lpSum(food.price * portions[(food.name, food.variant)] for food in foods)
    fat_weight = 3.0  # Increased to penalize fat more strongly
    price_weight = 2.0  # Increased to prioritize cheaper meals
    protein_weight = -6.0  # Stronger negative to maximize protein

    # Add minimum protein constraint (80% of target)
    prob += total_protein >= 0.8 * target.protein, "Protein_min"

    prob += (
        fat_weight * total_fat
        + price_weight * total_price
        + protein_weight * total_protein
    ), "FatPriceProteinObjective"

    # Add constraints to limit repetition of meals across the batch
    # Count how many times each food has been used in previous days
    food_usage_count = defaultdict(int)
    for ignored_plan in ignored_meals:
        for food, qty in ignored_plan:
            food_usage_count[(food.name, food.variant)] += qty
    
    # Exclude foods that have reached their max repetition limit
    for (name, variant), count in food_usage_count.items():
        if count >= max_repetitions:
            prob += portions[(name, variant)] <= 0, f"MaxRepetition_{name}_{variant}"

    # Enforce uniqueness by base name: at most one variant of each food per day
    foods_by_name = defaultdict(list)
    for food in foods:
        foods_by_name[food.name].append(food)
    
    for name, variants in foods_by_name.items():
        prob += (
            pulp.lpSum(portions[(f.name, f.variant)] for f in variants) <= 1,
            f"UniqueBaseName_{name}"
        )

    # Totals
    total_calories = pulp.lpSum(food.calories * portions[(food.name, food.variant)] for food in foods)
    total_fat       = pulp.lpSum(food.fat * portions[(food.name, food.variant)] for food in foods)
    total_carbs     = pulp.lpSum(food.carbohydrates * portions[(food.name, food.variant)] for food in foods)
    total_protein   = pulp.lpSum(food.protein * portions[(food.name, food.variant)] for food in foods)

    # Constraints for fat and protein only (if needed)
    # add_macro_constraint(prob, tolerance_ratio, total_fat, target.fat, "Fat")
    # add_macro_constraint(prob, tolerance_ratio, total_protein, target.protein, "Protein", allow_more=True)

    # Solve
    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if pulp.LpStatus[status] != "Optimal":
        raise NoFeasibleSolution("No feasible solution found for the given nutritional targets.")

    # Build result
    plan = []
    for food in foods:
        qty = portions[(food.name, food.variant)].value()
        if qty is None:
            qty = 0
        if qty > 1e-6:
            plan.append((food, int(qty)))

    total_cost = sum(food.price * qty for food, qty in plan)
    total_cals = sum(food.calories * qty for food, qty in plan)
    total_f    = sum(food.fat * qty for food, qty in plan)
    total_c    = sum(food.carbohydrates * qty for food, qty in plan)
    total_p    = sum(food.protein * qty for food, qty in plan)

    return OptimizationResult(
        plan=plan,
        totals=Totals(
            price_CZK=total_cost,
            calories=total_cals,
            fat=total_f,
            carbohydrates=total_c,
            protein=total_p,
        ),
        ideal_nutrition=target,
    )