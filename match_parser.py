import json
import os

import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
COLUMN_NAMES = [
    "Player", "Kill", "Death",
    "Damage Received", "Damage Dealt",
    "Heal", "Activated Altar",
]
NUMERIC_COLS = ["Kill", "Death", "Damage Received", "Damage Dealt", "Heal", "Activated Altar"]

JSON_PATH  = r"d:\Gamedev\IdleMMO_Plans\Quinfall\clan-war-data.json.json"
ROSTER_PATH = r"d:\Gamedev\IdleMMO_Plans\Quinfall\player_roster.json"


# ---------------------------------------------------------------------------
# JSON loader
# ---------------------------------------------------------------------------
def load_json_data(json_path: str = JSON_PATH) -> pd.DataFrame:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    day = data["date"]
    for match in data["matches"]:
        match_num = match["match"]
        for guild_entry in match["guilds"]:
            guild = guild_entry["guild"]
            team  = guild_entry["flag"]
            for p in guild_entry["players"]:
                rows.append({
                    "day":              day,
                    "match":            match_num,
                    "guild":            guild,
                    "team":             team,
                    "Player":           p["player"],
                    "Kill":             p["kill"],
                    "Death":            p["death"],
                    "Damage Received":  p["damage_received"],
                    "Damage Dealt":     p["damage_dealt"],
                    "Heal":             p["heal"],
                    "Activated Altar":  p["activated_altar"],
                })

    ordered_cols = ["day", "match", "guild", "team"] + COLUMN_NAMES
    df = pd.DataFrame(rows, columns=ordered_cols)
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    return df


# ---------------------------------------------------------------------------
# Roster helpers
# ---------------------------------------------------------------------------
def load_roster() -> dict[str, str]:
    if not os.path.exists(ROSTER_PATH):
        return {}
    with open(ROSTER_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_roster(roster: dict[str, str]) -> None:
    with open(ROSTER_PATH, "w", encoding="utf-8") as f:
        json.dump(roster, f, indent=2, ensure_ascii=False)


def apply_roster(df: pd.DataFrame) -> pd.DataFrame:
    roster = load_roster()
    if roster:
        df = df.copy()
        df["team"] = df["Player"].map(roster).fillna(df["team"])
    return df


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df = load_json_data()
    print(f"Loaded {len(df)} player rows from {df['match'].nunique()} match(es).")
    print(df.to_string())
