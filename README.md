# Meal Planner

**Meal Planner** is an intelligent, data-driven tool for generating optimized daily and weekly meal plans. It fetches real-world menus, calculates your nutritional needs, and builds cost-effective meal plans tailored to your goals.

## Features

- **Personalized Nutrition**: Input your weight, height, age, gender, body fat, activity level, and weight goal.
- **Menu Fetching**: Automatically downloads and parses real menus from Fingrlix.
- **Optimization**: Uses linear programming to select the best combination of meals for your nutritional targets and budget.
- **Automated Notifications**: GitHub Action that sends meal plans to Discord every 2 weeks.
- **Extensible**: Modular codebase for easy extension and integration.

## How It Works

1. **User Profile**: Define your personal data and dietary goals.
2. **Menu Fetching**: The app fetches the current week's menu from Fingrlix.
3. **Parsing**: Menus are parsed into structured food items.
4. **Optimization**: The optimizer selects the best meal plan using your nutritional needs and price constraints.
5. **Result**: Get a daily or weekly meal plan, including total price and macro breakdown.

## Quick Start

### Requirements

- Python 3.13+
- See `pyproject.toml` for dependencies (install with Poetry or pip).

### Example Usage

```python
from nutrition.models import PersonalData
from fingrlix import prepare_next_menu

day, result = prepare_next_menu(
	PersonalData(
		weight_kg=104,
		height_cm=189,
		age=22,
		gender="male",
		body_fat_percentage=14.8,
		activity_level="sedentary",
		weight_plan="lose_weight",
	)
)
print(f"Menu for day {day}:")
print(result)
```

### Install

```sh
poetry install
# or
pip install -r requirements.txt
```

### Run

```sh
python -m fingrlix
```

## Automated Notifications

Set up bi-weekly meal plan notifications to Discord! See [NOTIFICATIONS.md](NOTIFICATIONS.md) for detailed setup instructions.

- Runs automatically every 2 weeks on Monday at 8:00 AM
- Fetches meal plans for upcoming weeks
- Sends summarized shopping lists to Discord

## Project Structure

- `src/fingrlix/`: Main logic (fetching, parsing, optimization)
- `src/food/`: Food and recipe models
- `src/meal_planner/`: Course and meal plan models
- `src/nutrition/`: Nutrition and user data models
- `data/`: Example menu and recipe data

## Contributing

Pull requests and issues are welcome!

## License

MIT License
