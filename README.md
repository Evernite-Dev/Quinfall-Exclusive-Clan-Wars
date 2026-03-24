# Quinfall Clan Wars Dashboard

A static web dashboard for tracking Quinfall clan war match statistics. View match results, player leaderboards, and guild comparisons — hosted on GitHub Pages with no server required.

## Features

- **Match scorecards** — kill-based TDM win/loss result per match
- **Match Summary** — per-guild totals, damage charts, and K/D ratio charts
- **Player Leaderboard** — sortable stats with top 10 bar chart
- **Guild Comparison** — head-to-head player breakdown for a selected match
- **Raw Data** — full data table with CSV export

## Usage

Open `index.html` in a browser, or visit the GitHub Pages URL. The dashboard loads data from `clan-war-data.json.json` automatically.

Use the filter toggles at the top to narrow results by day, match, guild, or team.

## Data Format

Match data lives in `clan-war-data.json.json`. Structure:

```json
{
  "date": "2026-03-23",
  "matches": [
    {
      "match": 2,
      "guilds": [
        {
          "guild": "GuildName",
          "flag": "blue",
          "players": [
            {
              "player": "PlayerName",
              "kill": 6,
              "death": 3,
              "damage_received": 355319,
              "damage_dealt": 1113660,
              "heal": 0,
              "activated_altar": 3
            }
          ]
        }
      ]
    }
  ]
}
```

`flag` must be `"blue"` or `"red"` to assign team colour.

## Deployment

See [GitHub Pages setup](https://docs.github.com/en/pages/getting-started-with-github-pages) — enable Pages from the repo root on the `main` branch. The `index.html` and `clan-war-data.json.json` files must both be present at the root.