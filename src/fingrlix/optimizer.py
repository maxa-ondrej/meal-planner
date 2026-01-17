from typing import List
import pulp
from fingrlix.models import Food, OptimizationResult, Totals
from fingrlix.errors import NoFeasibleSolution
from nutrition import Nutrition


def optimize_day(
    foods: List[Food],
    target: Nutrition,
    tolerance_ratio: float = 0.05,   # allow ±5 % around each target
    integer_portions: bool = True
):
    # Create LP problem: minimize total cost
    prob = pulp.LpProblem("DailyDietPlan", pulp.LpMinimize)

    # Decision variables: how many portions of each food
    var_cat = pulp.LpInteger if integer_portions else pulp.LpContinuous
    portions = {
        (food.name, food.variant): pulp.LpVariable(f"portions_{food.name}_{food.variant}", lowBound=0, upBound=1, cat=var_cat)
        for food in foods
    }

    # Objective: minimize total price (CZK)
    prob += pulp.lpSum(food.price * portions[(food.name, food.variant)] for food in foods), "Total_Cost"

    # Helper for ± tolerance
    def add_macro_constraint(prob: pulp.LpProblem, total_expr: pulp.LpAffineExpression, target: int, name: str):
        lower = (1 - tolerance_ratio) * target
        upper = (1 + tolerance_ratio) * target
        prob += total_expr >= lower, f"{name}_min"
        prob += total_expr <= upper, f"{name}_max"

    # Totals
    total_calories = pulp.lpSum(food.calories * portions[(food.name, food.variant)] for food in foods)
    total_fat       = pulp.lpSum(food.fat * portions[(food.name, food.variant)] for food in foods)
    total_carbs     = pulp.lpSum(food.carbohydrates * portions[(food.name, food.variant)] for food in foods)
    total_protein   = pulp.lpSum(food.protein * portions[(food.name, food.variant)] for food in foods)

    # Constraints for each macro
    add_macro_constraint(prob, total_calories, target.calories, "Calories")
    add_macro_constraint(prob, total_fat, target.fat, "Fat")
    add_macro_constraint(prob, total_carbs, target.carbohydrates, "Carbs")
    add_macro_constraint(prob, total_protein, target.protein, "Protein")

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
    )