import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from match_parser import load_json_data, apply_roster

NUMERIC_COLS = ["Kill", "Death", "Damage Received", "Damage Dealt", "Heal", "Activated Altar"]
LABEL_FONT_SIZE = 24

st.set_page_config(page_title="Clan Wars Dashboard", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = load_json_data()
    df = apply_roster(df)
    return df


df = load_data()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.title("Filters")

if st.sidebar.button("Refresh Data", help="Reload data from clan-war-data.json"):
    load_data.clear()
    st.rerun()

days = sorted(df["day"].unique())
selected_days = st.sidebar.multiselect("Day", days, default=days)

matches = sorted(df[df["day"].isin(selected_days)]["match"].unique())
selected_matches = st.sidebar.multiselect("Match", matches, default=matches)

guilds = sorted(df["guild"].unique())
selected_guilds = st.sidebar.multiselect("Guild", guilds, default=guilds)

teams = sorted(df["team"].dropna().unique())
selected_teams = st.sidebar.multiselect("Team colour", teams, default=teams)

filtered = df[
    df["day"].isin(selected_days) &
    df["match"].isin(selected_matches) &
    df["guild"].isin(selected_guilds) &
    df["team"].isin(selected_teams)
].copy()

st.sidebar.markdown("---")
st.sidebar.metric("Players shown", len(filtered))

# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
st.title("Clan Wars Stats")

if filtered.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ---------------------------------------------------------------------------
# Match scorecards (kill-based TDM result)
# ---------------------------------------------------------------------------
match_base = df[df["match"].isin(selected_matches) & df["day"].isin(selected_days)]

match_kills = (
    match_base.groupby(["day", "match", "team"])["Kill"]
    .sum()
    .reset_index()
)
match_guilds = (
    match_base.groupby(["day", "match", "team"])["guild"]
    .first()
    .reset_index()
)

match_keys = (
    match_kills[["day", "match"]]
    .drop_duplicates()
    .sort_values(["day", "match"])
)

cols = st.columns(len(match_keys))
for col_widget, (_, row) in zip(cols, match_keys.iterrows()):
    day_val, match_num = row["day"], row["match"]

    mask = (match_kills["day"] == day_val) & (match_kills["match"] == match_num)
    kills_by_team = match_kills[mask].set_index("team")["Kill"]

    gmask = (match_guilds["day"] == day_val) & (match_guilds["match"] == match_num)
    guild_by_team = match_guilds[gmask].set_index("team")["guild"]

    blue_kills = int(kills_by_team.get("blue", 0))
    red_kills  = int(kills_by_team.get("red", 0))
    blue_guild = guild_by_team.get("blue", "Blue")
    red_guild  = guild_by_team.get("red", "Red")

    if blue_kills > red_kills:
        blue_label, red_label = "🏆 W", "L"
    elif red_kills > blue_kills:
        blue_label, red_label = "L", "🏆 W"
    else:
        blue_label, red_label = "Draw", "Draw"

    with col_widget:
        st.markdown(
            f"""
            <div style="border:1px solid #444;border-radius:8px;padding:10px;text-align:center">
                <div style="font-size:0.75rem;color:#aaa;margin-bottom:4px">Match {match_num} · {day_val}</div>
                <div style="display:flex;justify-content:space-around;align-items:center">
                    <div>
                        <div style="color:#4472C4;font-weight:bold;font-size:1.1rem">{blue_kills} kills</div>
                        <div style="color:#4472C4;font-size:0.8rem">{blue_guild} · {blue_label}</div>
                    </div>
                    <div style="color:#888;font-size:1.2rem">vs</div>
                    <div>
                        <div style="color:#C0392B;font-weight:bold;font-size:1.1rem">{red_kills} kills</div>
                        <div style="color:#C0392B;font-size:0.8rem">{red_guild} · {red_label}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# ---------------------------------------------------------------------------
# Tab layout
# ---------------------------------------------------------------------------
tab_summary, tab_players, tab_match, tab_raw = st.tabs([
    "Match Summary", "Player Leaderboard", "Guild Comparison", "Raw Data"
])

# ── Tab 1: Match Summary ────────────────────────────────────────────────────
with tab_summary:
    st.subheader("Totals per Guild per Match")

    summary = (
        filtered.groupby(["day", "match", "guild", "team"])[NUMERIC_COLS]
        .sum()
        .reset_index()
    )
    summary["K/D"] = (summary["Kill"] / summary["Death"].replace(0, 1)).round(2)
    summary = summary.sort_values(["day", "match", "guild"])

    st.dataframe(
        summary.style.format({col: "{:,.0f}" for col in NUMERIC_COLS} | {"K/D": "{:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Damage Dealt by Guild (per Match)")
    fig = px.bar(
        summary,
        x=summary["day"].astype(str) + " · M" + summary["match"].astype(str),
        y="Damage Dealt",
        color="guild",
        barmode="group",
        labels={"x": "Match"},
        text_auto=".3s",
    )
    fig.update_traces(textposition="outside", textfont_size=LABEL_FONT_SIZE)
    fig.update_layout(
        xaxis_title="Match",
        legend_title="Guild",
        yaxis_range=[0, summary["Damage Dealt"].max() * 1.2],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Kill / Death Ratio by Guild (per Match)")
    fig2 = px.bar(
        summary,
        x=summary["day"].astype(str) + " · M" + summary["match"].astype(str),
        y="K/D",
        color="guild",
        barmode="group",
        labels={"x": "Match"},
        text_auto=".2f",
    )
    fig2.update_traces(textposition="outside", textfont_size=LABEL_FONT_SIZE)
    fig2.update_layout(
        xaxis_title="Match",
        legend_title="Guild",
        yaxis_range=[0, summary["K/D"].max() * 1.2],
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab 2: Player Leaderboard ───────────────────────────────────────────────
with tab_players:
    st.subheader("Player Leaderboard")

    sort_col = st.selectbox("Sort by", NUMERIC_COLS, index=NUMERIC_COLS.index("Damage Dealt"))

    leaderboard = (
        filtered.groupby(["Player", "guild", "team"])[NUMERIC_COLS]
        .sum()
        .reset_index()
        .sort_values(sort_col, ascending=False)
        .reset_index(drop=True)
    )
    leaderboard.index += 1  # 1-based rank
    leaderboard["K/D"] = (leaderboard["Kill"] / leaderboard["Death"].replace(0, 1)).round(2)

    st.subheader(f"Top 10 Players by {sort_col}")
    top10 = leaderboard.head(10)
    team_colors = {"blue": "#4472C4", "red": "#C0392B", "unknown": "#888888"}
    bar_colors = [team_colors.get(t, "#888888") for t in top10["team"]]

    fig3 = go.Figure(go.Bar(
        x=top10["Player"],
        y=top10[sort_col],
        marker_color=bar_colors,
        text=top10[sort_col].apply(lambda v: f"{v:,.0f}"),
        textposition="outside",
        textfont={"size": LABEL_FONT_SIZE},
    ))
    fig3.update_layout(
        xaxis_title="Player",
        yaxis_title=sort_col,
        yaxis_range=[0, top10[sort_col].max() * 1.2],
        showlegend=False,
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.dataframe(
        leaderboard.style.format({col: "{:,.0f}" for col in NUMERIC_COLS} | {"K/D": "{:.2f}"}),
        use_container_width=True,
    )

# ── Tab 3: Guild Comparison ─────────────────────────────────────────────────
with tab_match:
    st.subheader("Head-to-Head Guild Comparison")

    match_labels = (
        filtered[["day", "match"]]
        .drop_duplicates()
        .sort_values(["day", "match"])
        .assign(label=lambda d: d["day"].astype(str) + " · Match " + d["match"].astype(str))
    )

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        selected_label = st.selectbox("Match", match_labels["label"].tolist())
    with filter_col2:
        stat = st.selectbox("Stat", NUMERIC_COLS, index=NUMERIC_COLS.index("Damage Dealt"),
                            key="match_stat")

    sel_row = match_labels[match_labels["label"] == selected_label].iloc[0]

    match_df = filtered[(filtered["day"] == sel_row["day"]) & (filtered["match"] == sel_row["match"])].copy()
    match_df["K/D"] = (match_df["Kill"] / match_df["Death"].replace(0, 1)).round(2)

    col_a, col_b = st.columns(2)
    for col_widget, guild in zip([col_a, col_b], sorted(match_df["guild"].unique())):
        gdf = match_df[match_df["guild"] == guild].sort_values("K/D", ascending=False)
        with col_widget:
            st.markdown(f"**{guild}** ({gdf['team'].iloc[0] if not gdf.empty else ''})")
            st.dataframe(
                gdf[["Player", "team"] + NUMERIC_COLS + ["K/D"]]
                .style.format({c: "{:,.0f}" for c in NUMERIC_COLS} | {"K/D": "{:.2f}"}),
                use_container_width=True,
                hide_index=True,
            )

    st.subheader(f"Player {stat} — Side by Side")
    plot_df = match_df.sort_values(stat, ascending=False)
    fig4 = px.bar(
        plot_df,
        x="Player",
        y=stat,
        color="guild",
        barmode="group",
        text_auto=".3s",
    )
    fig4.update_traces(textposition="outside", textfont_size=LABEL_FONT_SIZE)
    fig4.update_layout(
        xaxis_tickangle=-45,
        yaxis_range=[0, plot_df[stat].max() * 1.2],
    )
    st.plotly_chart(fig4, use_container_width=True)

# ── Tab 4: Raw Data ─────────────────────────────────────────────────────────
with tab_raw:
    st.subheader("Raw Player Data")
    st.dataframe(
        filtered.style.format({col: "{:,.0f}" for col in NUMERIC_COLS}),
        use_container_width=True,
        hide_index=True,
    )
    csv = filtered.to_csv(index=False).encode()
    st.download_button("Download as CSV", csv, "clan_wars_stats.csv", "text/csv")
