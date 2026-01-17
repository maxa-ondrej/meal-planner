class Ingredient:
    def __init__(self, name: str, quantity: float, unit: str):
        self.name = name
        self.quantity = quantity
        self.unit = unit

    def __repr__(self):
        return (
            f"Ingredient(name={self.name}, quantity={self.quantity}, unit={self.unit})"
        )

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.name}"

    def __mul__(self, factor: float) -> "Ingredient":
        return Ingredient(
            name=self.name,
            quantity=self.quantity * factor,
            unit=self.unit,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Ingredient":
        return cls(
            name=data["name"],
            quantity=data["quantity"],
            unit=data["unit"],
        )

    def display(self, _indents: int = 0) -> str:
        return f"{self.quantity} {self.unit} of {self.name}"
