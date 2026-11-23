"""The hosted bot's home page: how it does, and every real game it played."""

from __future__ import annotations

import csv
import math
import re
from collections.abc import Callable
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from games import LIVE_WINDOW

REPOSITORY = "https://github.com/INTODAN/island-battles-rsi-bot"
# A study is two or three lines (bot-league-iteration's "Started by real games"); a longer one is cut.
STUDY_LINES = 3
_STUDY = re.compile(r"^([0-9]+)\.md$")


def load_studies(*directories: Path) -> dict[int, list[str]]:
    """The iterations' studies of real games (ledger/studies/<id>.md), by game id: their non-empty lines."""
    studies: dict[int, list[str]] = {}
    for directory in directories:
        for path in sorted(directory.glob("*.md")):
            match = _STUDY.match(path.name)
            if match and int(match.group(1)) not in studies:
                lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
                studies[int(match.group(1))] = lines[:STUDY_LINES]
    return studies


def load_progress(*paths: Path) -> list[dict[str, Any]]:
    """The league's progress (ledger/progress.csv), from the first of ``paths`` that exists: a row per iteration.

    Each row has its iteration, date, minutes (None when not recorded), champion, its training rating and that
    rating's scale (the anchor the ratings had then: ratings compare only within one scale).
    """
    for path in paths:
        if path.is_file():
            with path.open(newline="") as file:
                return [
                    {
                        "iteration": int(row["iteration"]),
                        "date": row["date"],
                        "minutes": float(row["minutes"]) if row["minutes"] else None,
                        "champion": row["champion"],
                        "rating": int(row["rating"]),
                        "scale": row["scale"],
                    }
                    for row in csv.DictReader(file)
                ]
    return []


# What each rating scale was anchored on, from the ledger's setups.
SCALES = {
    "level3": "level3 at 1000",
    "unanchored": "no fixed point",
    "ori_mimic": "ori_mimic at 1800",
}
_W, _H = 640, 240
_LEFT, _RIGHT, _TOP, _BOTTOM = 48, 16, 16, 32


def _ticks(low: float, high: float, count: int = 4) -> list[float]:
    """Round tick values that cover low to high."""
    span = max(high - low, 1.0)
    raw = span / count
    step = 10 ** math.floor(math.log10(raw))
    for nice in (1, 2, 2.5, 5, 10):
        if nice * step >= raw:
            step *= nice
            break
    first = math.floor(low / step) * step
    return [first + step * k for k in range(int(math.ceil((high - first) / step)) + 1)]


def _chart(
    title: str, unit: str, rows: list[dict[str, Any]], key: str, *, zero: bool, label: Callable[[dict[str, Any]], str]
) -> str:
    """A line chart as inline SVG of ``key`` over the iteration, a rating's line broken where its scale changes."""
    points = [row for row in rows if row[key] is not None]
    if len(points) < 2:
        return ""
    # From the first iteration that has a value to the last iteration.
    rows = [row for row in rows if row["iteration"] >= points[0]["iteration"]]
    first, last = rows[0]["iteration"], rows[-1]["iteration"]
    values = [row[key] for row in points]
    ticks = _ticks(0 if zero else min(values), max(values))
    low, high = ticks[0], ticks[-1]

    def x(iteration: int) -> float:
        return _LEFT + (iteration - first) / max(last - first, 1) * (_W - _LEFT - _RIGHT)

    def y(value: float) -> float:
        return _TOP + (high - value) / max(high - low, 1) * (_H - _TOP - _BOTTOM)

    grid = "".join(
        f'<line class="grid" x1="{_LEFT}" x2="{_W - _RIGHT}" y1="{y(t):.1f}" y2="{y(t):.1f}"/>'
        f'<text class="tick" x="{_LEFT - 8}" y="{y(t) + 4:.1f}" text-anchor="end">{t:,.0f}</text>'
        for t in ticks
    )
    step = max(1, round((last - first) / 8 / 5) * 5) if last - first > 10 else 1
    xticks = "".join(
        f'<text class="tick" x="{x(i):.1f}" y="{_H - 10}" text-anchor="middle">{i}</text>'
        for i in range(first, last + 1)
        if (i - first) % step == 0 or i == last
    )
    # A line breaks where a value is missing or the scale changes; a dashed line marks each change of scale.
    runs: list[list[dict[str, Any]]] = []
    previous: dict[str, Any] | None = None
    for row in rows:
        joined = (
            previous is not None
            and row[key] is not None
            and previous[key] is not None
            and (key != "rating" or row["scale"] == previous["scale"])
            and row["iteration"] == previous["iteration"] + 1
        )
        if row[key] is not None:
            if joined:
                runs[-1].append(row)
            else:
                runs.append([row])
        previous = row
    lines = "".join(
        f'<polyline class="series" points="{" ".join(f"{x(r['iteration']):.1f},{y(r[key]):.1f}" for r in run)}"/>'
        for run in runs
        if len(run) > 1
    )
    breaks = "".join(
        f'<line class="break" x1="{x(row["iteration"]) - 0.5 * (x(1) - x(0)):.1f}" '
        f'x2="{x(row["iteration"]) - 0.5 * (x(1) - x(0)):.1f}" y1="{_TOP}" y2="{_H - _BOTTOM}"/>'
        for before, row in zip(rows, rows[1:], strict=False)
        if key == "rating" and row["scale"] != before["scale"]
    )
    dots = "".join(
        f'<circle class="dot" cx="{x(r["iteration"]):.1f}" cy="{y(r[key]):.1f}" r="4">'
        f"<title>{escape(label(r))}</title></circle>"
        for r in points
    )
    end = points[-1]
    return (
        f'<figure class="chart"><figcaption><span class="label">{escape(title)}</span>'
        f'<span class="sub">{escape(unit)}</span></figcaption>'
        f'<svg viewBox="0 0 {_W} {_H}" role="img" aria-label="{escape(title, quote=True)}">'
        f"{grid}{xticks}{breaks}{lines}{dots}"
        f'<text class="end" x="{x(end["iteration"]) - 8:.1f}" y="{y(end[key]) - 10:.1f}" text-anchor="end">'
        f"{end[key]:,.0f}</text></svg></figure>"
    )


def _progress(rows: list[dict[str, Any]]) -> str:
    """The league's section: an iteration's time and the champion's rating, over the iterations."""
    if not rows:
        return ""
    timed = _chart(
        "Time per iteration",
        "minutes, from the claim to the final tables",
        rows,
        "minutes",
        zero=True,
        label=lambda r: f"Iteration {r['iteration']}: {r['minutes']:g} minutes",
    )
    rated = _chart(
        "Champion's rating",
        "Elo on the training maps; a dashed line is a change of the rating's anchor",
        rows,
        "rating",
        zero=False,
        label=lambda r: (
            f"Iteration {r['iteration']}: {r['champion']}, {r['rating']} ({SCALES.get(r['scale'], r['scale'])})"
        ),
    )
    table = "".join(
        f"<tr><td>{r['iteration']}</td><td>{escape(r['date'])}</td>"
        f"<td>{'–' if r['minutes'] is None else f'{r["minutes"]:g}'}</td><td>{escape(r['champion'])}</td>"
        f"<td>{r['rating']}</td><td>{escape(SCALES.get(r['scale'], r['scale']))}</td></tr>"
        for r in reversed(rows)
    )
    return (
        f'<section class="card progress"><h2>The league</h2>'
        f'<p class="sub">Each iteration writes candidates, measures them and keeps the better ones. Ratings compare '
        f"only within one anchor: the league re-anchored them twice, and a rating also moves when the population "
        f"or the maps change. Iterations before 26 recorded no time.</p>{timed}{rated}"
        f"<details><summary>Every iteration</summary><table><thead><tr><th>Iteration</th><th>Date</th>"
        f"<th>Minutes</th><th>Champion</th><th>Rating</th><th>Anchor</th></tr></thead><tbody>{table}</tbody></table>"
        f"</details></section>"
    )


_STYLE = """
:root {
  --bg: #0a1322; --card: #0f1b2e; --line: #1d2b43; --text: #e8edf5; --muted: #8b9ab3;
  --won-bg: #12392a; --won: #6fe0a5; --lost-bg: #46201d; --lost: #ff9a8a; --draw-bg: #16233a; --draw: #d9e2f0;
  --live: #6fe0a5; --series: #6aa8f5;
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
.study { margin-top: 14px; border-left: 3px solid var(--line); padding: 2px 0 2px 14px; }
.study p { margin: 4px 0 0; font-size: 15px; }
.empty { color: var(--muted); padding: 16px 0 4px; }
footer { color: var(--muted); font-size: 14px; margin-top: 32px; }
footer a { color: var(--text); }
.progress { margin-bottom: 28px; }
.chart { margin: 20px 0 0; }
.chart figcaption { display: flex; flex-wrap: wrap; gap: 4px 12px; align-items: baseline; }
.chart svg { display: block; width: 100%; height: auto; margin-top: 8px; }
.chart .grid { stroke: var(--line); stroke-width: 1; }
.chart .break { stroke: var(--muted); stroke-width: 1; stroke-dasharray: 4 4; }
.chart .tick { fill: var(--muted); font-size: 12px; }
.chart .end { fill: var(--text); font-size: 13px; font-weight: 600; }
.chart .series { fill: none; stroke: var(--series); stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
.chart .dot { fill: var(--series); stroke: var(--card); stroke-width: 2; }
.chart .dot:hover { r: 6; }
details { margin-top: 20px; }
summary { cursor: pointer; color: var(--muted); }
table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--line); }
th { color: var(--muted); font-weight: 600; }
.progress details { overflow-x: auto; }
.sign-in { max-width: 460px; margin: 18vh auto 0; }
.google-button { min-height: 44px; margin: 8px 0; }
"""

_SCRIPT = """
const when = new Intl.DateTimeFormat('en-GB', {day: 'numeric', month: 'short', year: 'numeric',
  hour: '2-digit', minute: '2-digit'});
for (const node of document.querySelectorAll('time[datetime]')) {
  node.textContent = when.format(new Date(node.getAttribute('datetime')));
}
document.getElementById('sign-out').addEventListener('click', async (event) => {
  event.preventDefault();
  // As the game's Sign out: no silent sign-in until the button is used again, which the
  // bot remembers in a cookie of its own.
  try { await fetch('/sign-out', {method: 'POST'}); } finally { location.reload(); }
});
"""

# Sign in with Google as the game's web client does (its googleSignIn.ts): Google's own button,
# with the same options, and a silent sign-in (auto_select) unless the owner signed out.
_SIGN_IN_SCRIPT = """
const clientId = document.body.dataset.clientId;
const nonce = document.body.dataset.nonce;
const signedOut = document.body.dataset.signedOut === '1';
const message = document.getElementById('message');
const button = document.getElementById('google-button');

async function signIn(response) {
  if (!response.credential) return;
  message.textContent = 'Signing you in…';
  let answer;
  try {
    answer = await fetch('/sign-in', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({credential: response.credential})});
  } catch (error) {
    message.textContent = "The bot couldn't be reached. Try again.";
    return;
  }
  if (answer.ok) {
    location.reload();
    return;
  }
  let detail = 'sign-in failed';
  try { detail = (await answer.json()).detail || detail; } catch (error) {}
  message.textContent = detail.charAt(0).toUpperCase() + detail.slice(1) + '.';
  // Only a refusal stops the silent sign-in: Google or the bot failing isn't the account's fault.
  if (answer.status === 403) google.accounts.id.disableAutoSelect();
}

window.onGoogleLibraryLoad = () => {
  const id = google.accounts.id;
  id.initialize({client_id: clientId, nonce: nonce, callback: signIn, auto_select: true,
    cancel_on_tap_outside: false, context: 'signin', itp_support: true, use_fedcm_for_prompt: true});
  id.renderButton(button, {type: 'standard', theme: 'outline', size: 'large', text: 'signin_with',
    shape: 'rectangular', logo_alignment: 'center',
    width: Math.round(Math.min(400, Math.max(200, button.clientWidth || 380)))});
  if (signedOut) id.disableAutoSelect();
  else id.prompt();
};
"""


def _head(title: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet"
  href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&family=Inter:wght@400;600&display=swap">
<style>{_STYLE}</style>
</head>"""


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
    estimated = game.get("estimated", True)
    note = escape(f"{'Estimated: ' if estimated else ''}{game.get('result_note') or ''}", quote=True)
    mark = "≈ " if estimated else ""
    return f'<span class="badge {result}" title="{note}">{mark}{result.capitalize()}</span>'


_DEMO_NOTES = {
    "pending": " · The game's demo isn't downloaded yet: the zip has the bot's own turns for now.",
    "partial": " · The game never sent its end: the zip has only the bot's own turns.",
}


def _study(lines: list[str] | None) -> str:
    if not lines:
        return ""
    text = "".join(f"<p>{escape(line)}</p>" for line in lines)
    return f'<div class="study"><div class="label">What the league learned</div>{text}</div>'


def _game(game: dict[str, Any], study: list[str] | None = None) -> str:
    game_id = int(game["game_id"])
    action = f'<a class="zip" href="/games/{game_id}.zip">Zip</a>' if game.get("zip") else ""
    passed = f" ({game['passed']} passed)" if game.get("passed") else ""
    fields = [
        _field("Result", _result(game)),
        _field("Opponent", escape(", ".join(game.get("opponents") or []) or "–")),
        _field("Map", escape(str(game.get("map", "–")))),
        _field("Team", str(int(game["team_color"]))),
        _field("Turns", f"{int(game['turns'])}{passed}"),
        _field("Last turn", f"{int(game.get('final_turn') or game['last_turn'])} / {int(game['max_generations'])}"),
        _field("Updated", _time(game.get("finished_at") or game.get("updated_at"))),
    ]
    note = ""
    if game.get("status") == "finished" and game.get("result_note"):
        mark = "≈ " if game.get("estimated", True) else ""
        demo = _DEMO_NOTES.get(game.get("demo", ""), "")
        note = f'<div class="note">{mark}{escape(game["result_note"])}{demo}</div>'
    return (
        f'<article class="game"><div class="game-head"><h3>Game {game_id}</h3>{action}</div>'
        f'<div class="fields">{"".join(fields)}</div>{note}{_study(study)}</article>'
    )


def render(
    bot: str,
    summary: dict[str, Any],
    games: list[dict[str, Any]],
    studies: dict[int, list[str]] | None = None,
    progress: list[dict[str, Any]] | None = None,
) -> str:
    """The home page as HTML.

    ``studies`` are the iterations' studies of the games, by game id; ``progress`` is the league's (``load_progress``).
    """
    studies = studies or {}
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
    listed = (
        "".join(_game(game, studies.get(int(game["game_id"]))) for game in games)
        or '<p class="empty">No games yet.</p>'
    )
    live = " live" if summary["live"] else ""
    return f"""{_head(f"{bot} · Island Battles bot")}
<body>
<main>
<p class="eyebrow">Island Battles bot</p>
<h1>{escape(bot)}</h1>
<p class="intro">Every real game it plays is kept as a zip.</p>
<div class="status{live}"><span class="dot"></span>{escape(status)}</div>
<section class="stats">{stats}</section>
{_progress(progress or [])}
<section class="card"><h2>All games</h2>{listed}</section>
<footer>
<p>When a game ends, the game sends the bot its outcome and a link to its demo, with every team's logs. Each zip
holds that demo (<code>demo.json</code>, which <code>league digest</code> and the demo viewer open), its digest,
and the bot's own record of every turn: its commands, memory, timing and the server's answers. A result marked ≈
is estimated from the last board the bot saw, for a game that never sent its end. Under a game, what the league
learned from it is the study that the iteration which studied it wrote.</p>
<p><a href="{REPOSITORY}">The league's repository</a> · <a href="/api/games">JSON</a> ·
<a href="/" id="sign-out">Sign out</a></p>
</footer>
</main>
<script>{_SCRIPT}</script>
</body>
</html>
"""


def render_sign_in(client_id: str, nonce: str = "", *, signed_out: bool = False) -> str:
    """The page that a visitor who isn't the signed-in owner sees: Google's button alone, and nothing about the bot.

    Its sign-in asks Google for ``nonce``, and isn't silent when ``signed_out``.
    """
    if client_id:
        body = (
            '<div id="google-button" class="google-button"></div>'
            '<p id="message" class="sub" role="status"></p>'
            # The callback first, so it is there whenever Google's script loads.
            f"<script>{_SIGN_IN_SCRIPT}</script>"
            '<script src="https://accounts.google.com/gsi/client" async></script>'
        )
    else:
        body = '<p class="sub">Sign-in isn\'t available.</p>'
    return f"""{_head("Sign in")}
<body data-client-id="{escape(client_id, quote=True)}" data-nonce="{escape(nonce, quote=True)}" \
data-signed-out="{"1" if signed_out else ""}">
<main>
<section class="card sign-in">
<h2>Sign in</h2>
{body}
</section>
</main>
</body>
</html>
"""
