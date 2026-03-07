from attr import dataclass
from datetime import datetime
from collections import defaultdict
from typing import List, Tuple

from nutrition.models import Nutrition


@dataclass
class Food:
    name: str
    variant: str
    type: str
    description: str
    image: str
    price: int          # CZK per portion
    calories: int       # per portion
    fat: int            # g per portion
    carbohydrates: int  # g per portion
    protein: int        # g per portion

@dataclass
class Totals:
    calories: int
    fat: int
    carbohydrates: int
    protein: int
    price_CZK: int

@dataclass
class OptimizationResult:
    totals: Totals
    plan: list[tuple[Food, int]]  # List of (Food, quantity)
    ideal_nutrition: Nutrition
    
    def __str__(self) -> str:
        lines = []
        lines.append("Optimized Daily Meal Plan:")
        lines.append("--------------------------")
        for food, qty in self.plan:
            lines.append(f"{food.type}: {qty}x {food.name} ({food.variant})")
        lines.append("--------------------------")
        lines.append(f"Total Price: {self.totals.price_CZK:.2f} CZK")
        lines.append(f"Total Calories: {self.totals.calories:.2f} kcal (Ideal: {self.ideal_nutrition.calories:.2f} kcal)")
        lines.append(f"Total Fat: {self.totals.fat:.2f} g (Ideal: {self.ideal_nutrition.fat:.2f} g)")
        lines.append(f"Total Carbohydrates: {self.totals.carbohydrates:.2f} g (Ideal: {self.ideal_nutrition.carbohydrates:.2f} g)")
        lines.append(f"Total Protein: {self.totals.protein:.2f} g (Ideal: {self.ideal_nutrition.protein:.2f} g)")
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"OptimizationResult(totals={self.totals}, plan={self.plan}, ideal_nutrition={self.ideal_nutrition})"

@dataclass
class BatchResult:
    batch_name: str
    days: List[Tuple[datetime, OptimizationResult]]  # List of (date, result)
    
    @property
    def shopping_list(self) -> dict[str, int]:
        """Aggregate all foods across all days in the batch."""
        aggregated = defaultdict(int)
        for _, result in self.days:
            for food, qty in result.plan:
                # Use (name, variant) as key for precise aggregation
                key = f"{food.name} ({food.variant})"
                aggregated[key] += qty
        return dict(aggregated)
    
    @property
    def total_price(self) -> int:
        """Total price for the entire batch."""
        return sum(result.totals.price_CZK for _, result in self.days)
    
    def __str__(self) -> str:
        lines = []
        lines.append(f"{'='*60}")
        lines.append(f"BATCH: {self.batch_name}")
        lines.append(f"{'='*60}")
        lines.append("")
        
        # Show each day's meal plan
        for day, result in self.days:
            lines.append(f"📅 {day.strftime('%A, %B %d, %Y')}")
            lines.append("-" * 60)
            for food, qty in result.plan:
                lines.append(f"  {food.type:10} {qty}x {food.name} ({food.variant})")
            lines.append(f"  💰 Daily Total: {result.totals.price_CZK} CZK")
            lines.append(f"  📊 Cal: {result.totals.calories} | Protein: {result.totals.protein}g | Fat: {result.totals.fat}g | Carbs: {result.totals.carbohydrates}g")
            lines.append("")
        
        # Shopping list
        lines.append(f"{'='*60}")
        lines.append(f"🛒 SHOPPING LIST FOR {self.batch_name}")
        lines.append(f"{'='*60}")
        for item, qty in sorted(self.shopping_list.items()):
            lines.append(f"  {qty}x {item}")
        lines.append("")
        lines.append(f"💰 TOTAL BATCH PRICE: {self.total_price} CZK")
        lines.append(f"{'='*60}")
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"BatchResult(batch_name={self.batch_name}, days={len(self.days)}, total_price={self.total_price})"