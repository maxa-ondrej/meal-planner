# Weekly Meal Plan Notifications

This repository includes a GitHub Action that automatically fetches meal plans and sends notifications to Discord every Monday at 8:00 AM.

## Setup Instructions

### 1. Create a Discord Webhook

1. Open your Discord server
2. Go to Server Settings → Integrations → Webhooks
3. Click "New Webhook"
4. Give it a name (e.g., "Meal Planner")
5. Select the channel where you want notifications
6. Click "Copy Webhook URL"

### 2. Configure GitHub Secret

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `DISCORD_WEBHOOK_URL`
5. Value: Paste the webhook URL from Discord
6. Click "Add secret"

### 3. Enable GitHub Actions

The workflow is defined in `.github/workflows/weekly-meal-plan.yml` and will:
- Run automatically every Monday at 8:00 AM UTC
- Fetch meal plans for weeks 2 and 3
- Send a summary to your Discord channel

You can also trigger it manually:
1. Go to Actions tab in your GitHub repository
2. Select "Weekly Meal Plan Notification"
3. Click "Run workflow"
4. Optionally specify which weeks to fetch (e.g., "2 3")

## Manual Usage

You can also run the script locally:

```bash
# Fetch weeks 2 and 3 (console output)
poetry run python fetch_weekly_plan.py --weeks 2 3

# Send to Discord
poetry run python fetch_weekly_plan.py --weeks 2 3 --discord-webhook "YOUR_WEBHOOK_URL"
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

The Discord notification includes:
- Batch name and total price
- Shopping list (first 5 items, with count of remaining items)

For full details, run the script locally without the Discord webhook option.
