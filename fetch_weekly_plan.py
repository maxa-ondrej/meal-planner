#!/usr/bin/env python3
"""
Fetch meal plans for specific weeks and optionally send to Discord webhook.
"""
import argparse
import os
import sys
from datetime import datetime
from nutrition.models import PersonalData
from nutrition import calculate_nutrition_intake
from fingrlix import prepare_next_menu
import requests


def create_day_embed(day: datetime, result, batch_name: str) -> dict:
    """Create a Discord embed for a single day's meal plan."""
    # Group meals by type
    meals_by_type = {}
    for food, qty in result.plan:
        if food.type not in meals_by_type:
            meals_by_type[food.type] = []
        meals_by_type[food.type].append((food, qty))
    
    # Create fields for each meal type
    fields = []
    for meal_type, meals in meals_by_type.items():
        meal_items = [f"{qty}× {food.name} ({food.variant})" for food, qty in meals]
        fields.append({
            "name": f"🍽️ {meal_type}",
            "value": "\n".join(meal_items),
            "inline": False
        })
    
    # Add nutrition field
    fields.append({
        "name": "📊 Nutrition",
        "value": f"**{result.totals.calories}** kcal | **{result.totals.protein}**g protein | **{result.totals.fat}**g fat | **{result.totals.carbohydrates}**g carbs",
        "inline": False
    })
    
    return {
        "title": f"📅 {day.strftime('%A, %B %d, %Y')}",
        "description": f"Batch: **{batch_name}**",
        "color": 3447003,  # Blue
        "fields": fields,
        "footer": {
            "text": f"💰 Daily Total: {result.totals.price_CZK} CZK"
        }
    }


def create_shopping_list_embed(batch_result) -> dict:
    """Create a Discord embed for a batch's shopping list."""
    # Sort shopping list
    sorted_list = sorted(
        batch_result.shopping_list,
        key=lambda x: (batch_result._TYPE_ORDER.get(x[0].type, 999), x[0].name, x[0].variant)
    )
    
    # Group items by type
    items_by_type = {}
    for food, qty in sorted_list:
        if food.type not in items_by_type:
            items_by_type[food.type] = []
        items_by_type[food.type].append(f"{qty}× {food.name} ({food.variant})")
    
    # Create fields for each type
    fields = []
    for food_type in ["Snídaně", "Svačina & dezert", "Hlavní jídlo", "Extras"]:
        if food_type in items_by_type:
            # Split into chunks if too many items
            items = items_by_type[food_type]
            value = "\n".join(items)
            # Discord field value limit is 1024 characters
            if len(value) > 1024:
                value = "\n".join(items[:10]) + f"\n... and {len(items) - 10} more"
            
            fields.append({
                "name": f"🛒 {food_type}",
                "value": value,
                "inline": False
            })
    
    return {
        "title": f"🛒 Shopping List - {batch_result.batch_name}",
        "color": 3066993,  # Green
        "fields": fields,
        "footer": {
            "text": f"💰 Batch Total: {batch_result.total_price} CZK"
        }
    }


def create_summary_embed(weeks, total_price, total_days, avg_price_per_day, 
                         avg_calories, avg_protein, avg_fat, avg_carbs,
                         target_nutrition) -> dict:
    """Create a Discord embed for the summary statistics."""
    fields = [
        {
            "name": "💰 Total Price",
            "value": f"{total_price} CZK",
            "inline": True
        },
        {
            "name": "💵 Avg Price/Day",
            "value": f"{avg_price_per_day:.0f} CZK",
            "inline": True
        },
        {
            "name": "📅 Total Days",
            "value": str(total_days),
            "inline": True
        },
        {
            "name": "📈 Average Daily Nutrition",
            "value": (
                f"**Calories:** {avg_calories:.0f} kcal _(target: {target_nutrition.calories})_\n"
                f"**Protein:** {avg_protein:.0f}g _(target: {target_nutrition.protein})_\n"
                f"**Fat:** {avg_fat:.0f}g _(target: {target_nutrition.fat})_\n"
                f"**Carbs:** {avg_carbs:.0f}g _(target: {target_nutrition.carbohydrates})_"
            ),
            "inline": False
        }
    ]
    
    return {
        "title": f"📊 Summary - Weeks {', '.join(map(str, weeks))}",
        "color": 10181046,  # Purple
        "fields": fields
    }


def send_embeds_to_discord(webhook_url: str, embeds: list):
    """Send embeds to Discord webhook. Discord allows max 10 embeds per request."""
    # Send embeds in batches of 10
    for i in range(0, len(embeds), 10):
        batch = embeds[i:i+10]
        payload = {"embeds": batch}
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()


def main():
    parser = argparse.ArgumentParser(description="Generate meal plans for specific weeks")
    parser.add_argument(
        "--weeks",
        "-w",
        type=int,
        nargs="+",
        default=[2, 3],
        help="Which weeks to fetch (default: 2 3)"
    )
    parser.add_argument(
        "--discord-webhook-meals",
        type=str,
        help="Discord webhook URL for daily meal plan embeds"
    )
    parser.add_argument(
        "--discord-webhook-shopping",
        type=str,
        help="Discord webhook URL for shopping list embeds"
    )
    parser.add_argument(
        "--discord-webhook-summary",
        type=str,
        help="Discord webhook URL for summary embed"
    )
    args = parser.parse_args()

    # Personal data configuration
    personal_data = PersonalData(
        weight_kg=104,
        height_cm=189,
        age=22,
        gender="male",
        body_fat_percentage=14.8,
        activity_level="sedentary",
        weight_plan="lose_weight",
    )
    
    # Calculate target nutrition
    target_nutrition = calculate_nutrition_intake(personal_data)

    # Get the max week we need
    max_week = max(args.weeks)
    
    # Fetch all weeks up to max
    all_batches = list(prepare_next_menu(personal_data, weeks=max_week))
    
    # Filter to only the weeks we care about
    # Each week has 3 batches (FR_SA_SU, MO_TU, WE_TH)
    selected_batches = []
    for week_num in sorted(args.weeks):
        # Week 1 = indices 0-2, Week 2 = indices 3-5, etc.
        start_idx = (week_num - 1) * 3
        end_idx = start_idx + 3
        week_batches = all_batches[start_idx:end_idx]
        selected_batches.extend(week_batches)
    
    # Calculate totals and averages
    total_price = 0
    total_days = 0
    sum_calories = 0
    sum_protein = 0
    sum_fat = 0
    sum_carbs = 0
    
    for batch in selected_batches:
        if batch is None:
            continue
        total_price += batch.total_price
        for _, result in batch.days:
            total_days += 1
            sum_calories += result.totals.calories
            sum_protein += result.totals.protein
            sum_fat += result.totals.fat
            sum_carbs += result.totals.carbohydrates
    
    # Calculate averages
    avg_calories = sum_calories / total_days if total_days > 0 else 0
    avg_protein = sum_protein / total_days if total_days > 0 else 0
    avg_fat = sum_fat / total_days if total_days > 0 else 0
    avg_carbs = sum_carbs / total_days if total_days > 0 else 0
    avg_price_per_day = total_price / total_days if total_days > 0 else 0
    
    # Generate console output
    output_lines = []
    output_lines.append(f"📅 **Meal Plans for Weeks {', '.join(map(str, args.weeks))}**\n")
    
    for batch in selected_batches:
        if batch is None:
            continue
        output_lines.append(str(batch))
        output_lines.append("")
    
    # Add summary statistics
    output_lines.append("=" * 60)
    output_lines.append("📊 SUMMARY")
    output_lines.append("=" * 60)
    output_lines.append(f"💰 Total Price: {total_price} CZK")
    output_lines.append(f"💵 Average Price per Day: {avg_price_per_day:.0f} CZK")
    output_lines.append(f"📅 Total Days: {total_days}")
    output_lines.append("")
    output_lines.append("📈 Average Daily Nutrition:")
    output_lines.append(f"   Calories: {avg_calories:.0f} kcal (target: {target_nutrition.calories})")
    output_lines.append(f"   Protein:  {avg_protein:.0f} g (target: {target_nutrition.protein})")
    output_lines.append(f"   Fat:      {avg_fat:.0f} g (target: {target_nutrition.fat})")
    output_lines.append(f"   Carbs:    {avg_carbs:.0f} g (target: {target_nutrition.carbohydrates})")
    output_lines.append("=" * 60)
    
    output = "\n".join(output_lines)
    
    # Print to console
    print(output)
    
    # Send to Discord if webhooks provided
    any_webhook = args.discord_webhook_meals or args.discord_webhook_shopping or args.discord_webhook_summary
    if any_webhook:
        try:
            # Send daily meal plan embeds
            if args.discord_webhook_meals:
                meal_embeds = []
                for batch in selected_batches:
                    if batch is None:
                        continue
                    for day, result in batch.days:
                        meal_embeds.append(create_day_embed(day, result, batch.batch_name))
                
                if meal_embeds:
                    send_embeds_to_discord(args.discord_webhook_meals, meal_embeds)
                    print(f"✅ Sent {len(meal_embeds)} meal plan embeds to Discord!", file=sys.stderr)
            
            # Send shopping list embeds
            if args.discord_webhook_shopping:
                shopping_embeds = []
                for batch in selected_batches:
                    if batch is None:
                        continue
                    shopping_embeds.append(create_shopping_list_embed(batch))
                
                if shopping_embeds:
                    send_embeds_to_discord(args.discord_webhook_shopping, shopping_embeds)
                    print(f"✅ Sent {len(shopping_embeds)} shopping list embeds to Discord!", file=sys.stderr)
            
            # Send summary embed
            if args.discord_webhook_summary:
                summary_embed = create_summary_embed(
                    args.weeks, total_price, total_days, avg_price_per_day,
                    avg_calories, avg_protein, avg_fat, avg_carbs, target_nutrition
                )
                send_embeds_to_discord(args.discord_webhook_summary, [summary_embed])
                print("✅ Sent summary embed to Discord!", file=sys.stderr)
            
        except Exception as e:
            print(f"\n❌ Failed to send to Discord: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
