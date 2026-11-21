"""The hosted bot's home page: how it does, and every real game it played."""

from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

from games import LIVE_WINDOW

REPOSITORY = "https://github.com/INTODAN/island-battles-rsi-bot"

_STYLE = """
:root {
  --bg: #0a1322; --card: #0f1b2e; --line: #1d2b43; --text: #e8edf5; --muted: #8b9ab3;
  --won-bg: #12392a; --won: #6fe0a5; --lost-bg: #46201d; --lost: #ff9a8a; --draw-bg: #16233a; --draw: #d9e2f0;
  --live: #6fe0a5;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: 16px/1.5 Inter, system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 880px; margin: 0 auto; padding: 40px 16px 64px; }
h1, h2, .big { font-family: Fraunces, Georgia, "Times New Roman", serif; font-weight: 700; }
.eyebrow { color: var(--muted); text-transform: uppercase; letter-spacing: .12em; font-size: 13px; margin: 0; }
h1 { font-size: clamp(36px, 8vw, 56px); margin: 4px 0 8px; line-height: 1.1; overflow-wrap: anywhere; }
.intro { color: var(--muted); margin: 0 0 20px; }
.status { display: inline-flex; gap: 8px; align-items: center; border: 1px solid var(--line);
  border-radius: 999px; padding: 6px 14px; font-size: 15px; }
.dot { width: 9px; height: 9px; border-radius: 50%; background: var(--muted); }
.status.live .dot { background: var(--live); box-shadow: 0 0 0 4px rgba(111, 224, 165, .15); }
.stats { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin: 28px 0; }
@media (min-width: 760px) { .stats { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 22px; padding: 20px 22px; }
.label { color: var(--muted); text-transform: uppercase; letter-spacing: .1em; font-size: 13px; font-weight: 600; }
.big { font-size: clamp(30px, 6vw, 40px); line-height: 1.15; margin: 6px 0 4px; }
.sub { color: var(--muted); font-size: 15px; }
h2 { font-size: 30px; margin: 4px 0 8px; }
.game { padding: 22px 0; border-bottom: 1px solid var(--line); }
.game:last-child { border-bottom: 0; }
.game-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.game-head h3 { margin: 0; font-size: 21px; font-weight: 600; }
.zip { color: var(--text); text-decoration: none; border: 1px solid var(--line); border-radius: 14px;
  padding: 10px 22px; font-weight: 600; background: var(--bg); }
.zip:hover { border-color: var(--muted); }
.fields { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px 16px; margin-top: 14px; }
@media (min-width: 760px) { .fields { grid-template-columns: repeat(6, minmax(0, 1fr)); } }
.fields div { min-width: 0; overflow-wrap: anywhere; }
.value { font-size: 18px; }
.badge { display: inline-block; border-radius: 999px; padding: 2px 14px; font-weight: 600; font-size: 15px;
  margin-top: 2px; background: var(--draw-bg); color: var(--draw); border: 1px solid var(--line); }
.badge.won { background: var(--won-bg); color: var(--won); }
.badge.lost { background: var(--lost-bg); color: var(--lost); }
.badge.playing { background: transparent; color: var(--live); }
.note { color: var(--muted); font-size: 14px; margin-top: 10px; }
.empty { color: var(--muted); padding: 16px 0 4px; }
footer { color: var(--muted); font-size: 14px; margin-top: 32px; }
footer a { color: var(--text); }
"""

_SCRIPT = """
const when = new Intl.DateTimeFormat('en-GB', {day: 'numeric', month: 'short', year: 'numeric',
  hour: '2-digit', minute: '2-digit'});
for (const node of document.querySelectorAll('time[datetime]')) {
  node.textContent = when.format(new Date(node.getAttribute('datetime')));
}
document.addEventListener('click', (event) => {
  const link = event.target.closest('a.zip[data-key]');
  if (!link) return;
  let key = null;
  try { key = localStorage.getItem('games-key'); } catch (error) {}
  if (!key) {
    key = prompt("The owner's key, to download a game:");
    if (!key) { event.preventDefault(); return; }
    try { localStorage.setItem('games-key', key); } catch (error) {}
  }
  link.href = link.dataset.href + '?key=' + encodeURIComponent(key);
});
"""


def _time(text: str | None) -> str:
    if not text:
        return "–"
    stamp = datetime.fromisoformat(text)
    return f'<time datetime="{escape(text)}">{stamp:%d %b %Y, %H:%M} UTC</time>'


def _field(label: str, value: str) -> str:
    return f'<div><div class="label">{label}</div><div class="value">{value}</div></div>'


def _result(game: dict[str, Any]) -> str:
    if game.get("status") != "finished":
        return '<span class="badge playing">Playing</span>'
    result = game.get("result") or "draw"
    note = escape(f"Estimated: {game.get('result_note') or ''}", quote=True)
    return f'<span class="badge {result}" title="{note}">{result.capitalize()}</span>'


def _game(game: dict[str, Any], key_required: bool) -> str:
    game_id = int(game["game_id"])
    if game.get("zip"):
        href = f"/games/{game_id}.zip"
        if key_required:
            action = f'<a class="zip" href="{href}" data-href="{href}" data-key>Zip</a>'
        else:
            action = f'<a class="zip" href="{href}">Zip</a>'
    else:
        action = ""
    passed = f" ({game['passed']} passed)" if game.get("passed") else ""
    fields = [
        _field("Result", _result(game)),
        _field("Map", escape(str(game.get("map", "–")))),
        _field("Team", str(int(game["team_color"]))),
        _field("Turns", f"{int(game['turns'])}{passed}"),
        _field("Last turn", f"{int(game['last_turn'])} / {int(game['max_generations']) - 1}"),
        _field("Updated", _time(game.get("updated_at"))),
    ]
    note = ""
    if game.get("status") == "finished" and game.get("result_note"):
        note = f'<div class="note">≈ {escape(game["result_note"])}</div>'
    return (
        f'<article class="game"><div class="game-head"><h3>Game {game_id}</h3>{action}</div>'
        f'<div class="fields">{"".join(fields)}</div>{note}</article>'
    )


def render(bot: str, summary: dict[str, Any], games: list[dict[str, Any]], key_required: bool) -> str:
    """The home page as HTML."""
    latest = summary["latest"]
    record = summary["record"]
    seconds = int(LIVE_WINDOW.total_seconds())
    if summary["live"] and latest:
        status = f"Playing game {int(latest['game_id'])}, turn {int(latest['last_turn'])}"
        status_card = ("Playing", f"game {int(latest['game_id'])}")
    elif latest:
        status = f"Waiting for a game: no turn in the last {seconds} s"
        status_card = ("Idle", f"no turn in the last {seconds} s")
    else:
        status = "Waiting for its first game"
        status_card = ("Idle", "no game yet")
    cards = [
        ("Status", status_card[0], status_card[1]),
        (
            "Record",
            f"{record['won']}–{record['lost']}–{record['draw']}",
            f"won–lost–draw of {sum(record.values())} games",
        ),
        ("Turns", f"{summary['accepted']:,}", "played and accepted"),
        (
            "Last turn",
            f"T{int(latest['last_turn'])}" if latest else "–",
            _time(latest["updated_at"]) if latest else "no turn yet",
        ),
    ]
    stats = "".join(
        f'<div class="card"><div class="label">{label}</div><div class="big">{escape(big)}</div>'
        f'<div class="sub">{sub}</div></div>'
        for label, big, sub in cards
    )
    listed = "".join(_game(game, key_required) for game in games) or '<p class="empty">No games yet.</p>'
    live = " live" if summary["live"] else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(bot)} · Island Battles bot</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet"
  href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&family=Inter:wght@400;600&display=swap">
<style>{_STYLE}</style>
</head>
<body>
<main>
<p class="eyebrow">Island Battles bot</p>
<h1>{escape(bot)}</h1>
<p class="intro">The champion of an AI-run bot league. Every real game it plays is kept as a zip.</p>
<div class="status{live}"><span class="dot"></span>{escape(status)}</div>
<section class="stats">{stats}</section>
<section class="card"><h2>All games</h2>{listed}</section>
<footer>
<p>A hosted bot sees only the boards of its own turns and its own logs, so a result is estimated from the last
board it saw, and a game's demo ends there. Each zip holds <code>demo.json</code>, which
<code>league digest</code> and the demo viewer open, and <code>turns.jsonl</code>.</p>
<p><a href="{REPOSITORY}">The league's repository</a> · <a href="/api/games">JSON</a></p>
</footer>
</main>
<script>{_SCRIPT}</script>
</body>
</html>
"""
