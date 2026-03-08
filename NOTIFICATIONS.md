# Weekly Meal Plan Notifications

This repository includes a GitHub Action that automatically fetches meal plans and sends notifications to Discord every Monday at 8:00 AM using three separate webhooks for different types of content.

## Setup Instructions

### 1. Create Discord Webhooks

You can create up to 3 webhooks to send different types of information to different channels:

1. **Meal Plans Webhook** (optional): Daily meal plan embeds
2. **Shopping Lists Webhook** (optional): Shopping list embeds per batch
3. **Summary Webhook** (optional): Summary statistics embed

For each webhook you want to create:
1. Open your Discord server
2. Go to Server Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Give it a descriptive name (e.g., "Meal Plans", "Shopping Lists", "Summary")
5. Select the channel where you want that type of notification
6. Click "Copy Webhook URL"

**Tip:** You can send all types to the same channel by using the same webhook URL for all three, or split them across different channels.

### 2. Configure GitHub Secrets

Add the webhook URLs as GitHub secrets. You can add one, two, or all three:

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret" for each webhook:
   - Name: `DISCORD_WEBHOOK_MEALS` → Value: Paste webhook URL for meal plans
   - Name: `DISCORD_WEBHOOK_SHOPPING` → Value: Paste webhook URL for shopping lists
   - Name: `DISCORD_WEBHOOK_SUMMARY` → Value: Paste webhook URL for summary

### 3. Enable GitHub Actions

The workflow is defined in `.github/workflows/weekly-meal-plan.yml` and will:
- Run automatically every Monday at 8:00 AM UTC
- Fetch meal plans for weeks 2 and 3
- Send beautifully formatted Discord embeds with:
  - Individual embeds for each day's meal plan
  - Shopping list embeds per batch
  - Summary statistics embed

You can also trigger it manually:
1. Go to Actions tab in your GitHub repository
2. Select "Weekly Meal Plan Notification"
3. Click "Run workflow"
4. Optionally specify which weeks to fetch (e.g., "2 3")

## Manual Usage

You can also run the script locally:

```bash
# Fetch weeks 2 and 3 (console output only)
poetry run python fetch_weekly_plan.py --weeks 2 3

# Send to Discord (all types to same webhook)
poetry run python fetch_weekly_plan.py --weeks 2 3 \
  --discord-webhook-meals "YOUR_WEBHOOK_URL" \
  --discord-webhook-shopping "YOUR_WEBHOOK_URL" \
  --discord-webhook-summary "YOUR_WEBHOOK_URL"

# Send to different channels (separate webhooks)
poetry run python fetch_weekly_plan.py --weeks 2 3 \
  --discord-webhook-meals "MEALS_WEBHOOK_URL" \
  --discord-webhook-shopping "SHOPPING_WEBHOOK_URL" \
  --discord-webhook-summary "SUMMARY_WEBHOOK_URL"

# Send only specific types
poetry run python fetch_weekly_plan.py --weeks 2 3 \
  --discord-webhook-summary "SUMMARY_WEBHOOK_URL"
```

## Customization

### Change Schedule

Edit `.github/workflows/weekly-meal-plan.yml` and modify the cron expression:

```yaml
schedule:
  - cron: '0 8 * * 1'  # Minute Hour Day Month DayOfWeek
```

Examples:
- `'0 8 * * 1'` - Every Monday at 8:00 AM
- `'0 7 * * 1,4'` - Every Monday and Thursday at 7:00 AM
- `'30 9 * * 0'` - Every Sunday at 9:30 AM

### Change Weeks

Modify the default weeks in the workflow file or specify when running manually.

### Personal Data

Edit `fetch_weekly_plan.py` to update your personal nutrition parameters:

```python
personal_data = PersonalData(
    weight_kg=104,
    height_cm=189,
    age=22,
    gender="male",
    body_fat_percentage=14.8,
    activity_level="sedentary",
    weight_plan="lose_weight",
)
```

## Output Format

The Discord notification uses rich embeds for better visual presentation:

### 📅 Daily Meal Plan Embeds (Blue)
- Date and batch name
- Meals grouped by type (Snídaně, Hlavní jídlo, Extras, etc.)
- Nutrition information (calories, protein, fat, carbs)
- Daily price

### 🛒 Shopping List Embeds (Green)
- One embed per batch
- Items grouped by food type
- Batch total price

### 📊 Summary Embed (Purple)
- Total price and average price per day
- Total days covered
- Average daily nutrition with target values

For full details, run the script locally without the Discord webhook option.
