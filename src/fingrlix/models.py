from attr import dataclass


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
    
    def __str__(self) -> str:
        lines = []
        lines.append("Optimized Daily Meal Plan:")
        lines.append("--------------------------")
        for food, qty in self.plan:
            lines.append(f"{food.type}: {qty}x {food.name} ({food.variant})")
        lines.append("--------------------------")
        lines.append(f"Total Price: {self.totals.price_CZK:.2f} CZK")
        lines.append(f"Total Calories: {self.totals.calories:.2f} kcal")
        lines.append(f"Total Fat: {self.totals.fat:.2f} g")
        lines.append(f"Total Carbohydrates: {self.totals.carbohydrates:.2f} g")
        lines.append(f"Total Protein: {self.totals.protein:.2f} g")
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"OptimizationResult(totals={self.totals}, plan={self.plan})"