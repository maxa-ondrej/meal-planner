import argparse
from nutrition.models import PersonalData
from fingrlix import prepare_next_menu


def main():
    parser = argparse.ArgumentParser(description="Generate optimized meal plans from Fingrlix menu")
    parser.add_argument(
        "--weeks",
        "-w",
        type=int,
        default=1,
        help="Number of weeks to plan (default: 1)"
    )
    args = parser.parse_args()

    menu = prepare_next_menu(
        PersonalData(
            weight_kg=104,
            height_cm=189,
            age=22,
            gender="male",
            body_fat_percentage=14.8,
            activity_level="sedentary",
            weight_plan="lose_weight",
        ),
        weeks=args.weeks
    )
    for batch_result in menu:
        if batch_result is None:
            continue
        print(batch_result)
        print("\n")


if __name__ == "__main__":
    main()