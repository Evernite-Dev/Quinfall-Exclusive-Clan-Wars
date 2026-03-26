## Screenshot Parsing Instructions — Clan War Statistics

**Source format:** In-game Clan War Statistics scoreboard screenshots. Each match has two screenshots, one per guild.

**File naming convention:** `{match_number} - {guild_name}.png` — the match number and guild name are encoded in the filename. Use these to assign players to the correct match and guild.

**File Notes**
- The `{guild name}` in the file name will help identify which team the players are on.
  - A majority of the `{guild name}` players should be present within their respective file.
  - Verify the correct team using the flag color rules.
  - Sort order is the same for screenshots in the same match.
    - Two screenshots are required because the visible frame only shows a limited number of players.

**Flag color rules:**
- Flag colors can change between matches, so teams should be established on a per-match basis.
- Determine which team is 'Exclusive' by checking the flag color next to any of the following players:
  - Evernite
  - Antlion
  - Blank
  - Ezzy
- That flag's color belongs to guild = Exclusive
- The other flag color marks a member of the enemy guild named in that screenshot's filename
- Flag colors can either be red or blue.

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