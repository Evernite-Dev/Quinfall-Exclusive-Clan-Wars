## Screenshot Parsing Instructions — Clan War Statistics

**Source format:** In-game Clan War Statistics scoreboard screenshots. Each match has two screenshots, one per guild.

**File naming convention:** `{match_number} - {guild_name}.png` — the match number and guild name are encoded in the filename. Use these to assign players to the correct match and guild.

**Flag color rules:**
- Blue flag next to a player = member of Exclusive
- Red flag next to a player = member of the enemy guild named in that screenshot's filename

**Guild assignment rules:**
- Read the flag color on each row independently. Do not assume all players in a screenshot belong to the same guild.
- The scoreboard is shared — both guilds appear on the same scrollable list. Screenshots taken at different scroll positions will show a mix of blue and red flagged players.
- A player's guild is determined solely by their flag color, not by which screenshot they appear in.

**Scroll overlap handling:**
- When two screenshots cover the same match, the scroll positions often overlap, causing some players to appear in both screenshots.
- Each player must appear exactly once per match across both guilds. Duplicates caused by scroll overlap must be removed.
- A player's correct guild is always determined by their flag color. If a player appears in both screenshots, keep them in the guild matching their flag color and remove them from the other.

**Output format:** JSON with the following structure:

```json
{
  "date": "YYYY-MM-DD",
  "matches": [
    {
      "match": 2,
      "guilds": [
        {
          "guild": "Exclusive",
          "flag": "blue",
          "players": [
            {
              "player": "PlayerName",
              "kill": 0,
              "death": 0,
              "damage_received": 0,
              "damage_dealt": 0,
              "heal": 0,
              "activated_altar": 0
            }
          ]
        },
        {
          "guild": "EnemyGuildName",
          "flag": "red",
          "players": []
        }
      ]
    }
  ]
}
```

**Validation checks to run after parsing:**
- No player name appears more than once within a single guild's player list in a match
- No player name appears in both guilds within the same match
- Every blue-flagged player is in Exclusive, every red-flagged player is in the enemy guild
- Match numbers are sourced from filenames, not inferred from content

**Date:** Provide the match date separately — it is not visible in the screenshots.