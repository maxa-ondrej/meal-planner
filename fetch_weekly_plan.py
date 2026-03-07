#!/usr/bin/env python3
"""
Fetch meal plans for specific weeks and optionally send to Discord webhook.
"""
import argparse
import os
import sys
from nutrition.models import PersonalData
from nutrition import calculate_nutrition_intake
from fingrlix import prepare_next_menu
import requests


def format_batch_summary(batch_result) -> str:
    """Format batch result as a concise summary for Discord."""
    if batch_result is None:
        return ""
    
    lines = []
    lines.append(f"**{batch_result.batch_name}** - {batch_result.total_price} CZK")
    
    # Show shopping list
    sorted_list = sorted(
        batch_result.shopping_list,
        key=lambda x: (batch_result._TYPE_ORDER.get(x[0].type, 999), x[0].name, x[0].variant)
    )
    
    shopping_items = [f"{qty}x {food.name} ({food.variant})" for food, qty in sorted_list]
    lines.append("🛒 " + ", ".join(shopping_items[:5]))  # Show first 5 items
    if len(shopping_items) > 5:
        lines.append(f"   ... and {len(shopping_items) - 5} more items")
    
    return "\n".join(lines)


def send_to_discord(webhook_url: str, content: str):
    """Send message to Discord webhook."""
    # Discord has a 2000 character limit per message
    chunks = []
    current_chunk = ""
    
    for line in content.split("\n"):
        if len(current_chunk) + len(line) + 1 > 1900:  # Leave some buffer
            chunks.append(current_chunk)
            current_chunk = line
        else:
            if current_chunk:
                current_chunk += "\n" + line
            else:
                current_chunk = line
    
    if current_chunk:
        chunks.append(current_chunk)
    
    # Send each chunk
    for chunk in chunks:
        payload = {"content": chunk}
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
        "--discord-webhook",
        type=str,
        help="Discord webhook URL to send results to"
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
    
    # Generate output
    output_lines = []
    output_lines.append(f"📅 **Meal Plans for Weeks {', '.join(map(str, args.weeks))}**\n")
    
    for batch in selected_batches:
        if batch is None:
            continue
        
        if args.discord_webhook:
            # Concise format for Discord
            summary = format_batch_summary(batch)
            output_lines.append(summary)
            output_lines.append("")
        else:
            # Full format for console
            output_lines.append(str(batch))
            output_lines.append("")
    
    # Add summary statistics
    avg_price_per_day = total_price / total_days if total_days > 0 else 0
    
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
    
    # Send to Discord if webhook provided
    if args.discord_webhook:
        try:
            send_to_discord(args.discord_webhook, output)
            print("\n✅ Successfully sent to Discord!", file=sys.stderr)
        except Exception as e:
            print(f"\n❌ Failed to send to Discord: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
