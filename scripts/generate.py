"""Gera os cards SVG do README do perfil.

Só usa a biblioteca padrão (roda no GitHub Actions sem instalar nada).

    python scripts/generate.py            # versão animada (a do README)
    python scripts/generate.py --static   # sem animação, pra pré-visualizar

Saídas em assets/: details.svg, query.svg, dag.svg, build.svg e grid.svg.
Todos os textos dos cards ficam em data/profile.json.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import urllib.request
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
PROFILE = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))
LOGIN = PROFILE["login"]
TODAY = dt.datetime.now(ZoneInfo("America/Sao_Paulo")).date()
STATIC = "--static" in sys.argv

W = 860
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

C = {
    "bg": "#0a0e14",
    "panel": "#0f141c",
    "bar": "#121a26",
    "border": "#243042",
    "text": "#e6edf3",
    "muted": "#7d8896",
    "dim": "#4b5563",
    "blue": "#017cee",
    "cyan": "#5ec8f2",
    "success": "#2ea043",
    "running": "#a3e635",
    "queued": "#6e7681",
    "empty": "#151c27",
}
# verde do "success" em 4 intensidades, pra quantidade de contribuições no dia
LEVELS = [C["empty"], "#0f3b24", "#16632f", "#239a3b", "#3fd160"]
STATE_COLOR = {"success": C["success"], "running": C["running"], "queued": C["queued"]}


# --------------------------------------------------------------------------- base
def frame(height: int, crumbs: list[str], body: str, style: str = "") -> str:
    """Moldura comum: fundo, barra de navegação estilo UI do Airflow e corpo."""
    crumb_parts = []
    for i, part in enumerate(crumbs):
        color = C["text"] if i == len(crumbs) - 1 else C["muted"]
        if i:
            crumb_parts.append(f'<tspan fill="{C["dim"]}">  /  </tspan>')
        crumb_parts.append(f'<tspan fill="{color}">{escape(part)}</tspan>')
    anim = "" if STATIC else style
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" font-family="{FONT}">
  <style>{anim}</style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{height - 1}" rx="12" fill="{C["bg"]}" stroke="{C["border"]}"/>
  <path d="M0.5 12.5 a12 12 0 0 1 12 -12 h{W - 25} a12 12 0 0 1 12 12 v21.5 h-{W - 1} z" fill="{C["bar"]}"/>
  <line x1="0.5" y1="34" x2="{W - 0.5}" y2="34" stroke="{C["border"]}"/>
  <rect x="16" y="11" width="12" height="12" rx="3" fill="{C["blue"]}"/>
  <rect x="19" y="14" width="6" height="6" rx="1.5" fill="{C["bar"]}"/>
  <text x="38" y="21.5" font-size="11">{"".join(crumb_parts)}</text>
  <text x="{W - 16}" y="21.5" font-size="11" text-anchor="end" fill="{C["muted"]}">{TODAY.isoformat()}</text>
{body}
</svg>
"""


def chip(x: float, y: float, label: str, state: str) -> str:
    color = STATE_COLOR[state]
    w = len(label) * 6.6 + 16
    return (
        f'<rect x="{x}" y="{y}" width="{w:.0f}" height="18" rx="9" fill="none" stroke="{color}"/>'
        f'<text x="{x + w / 2:.1f}" y="{y + 12.5}" font-size="10.5" fill="{color}" text-anchor="middle">{escape(label)}</text>'
    ), w


# -------------------------------------------------------------------------- hello
GOLD = "#e3b341"
PIXEL = 3.6
OVERLAP = 40


def _portrait(art: dict, name: str, ax: float, base_y: float, t0: float, uid: str, occlude: bool = False) -> tuple[list[str], float]:
    """Retrato estilo imagem no terminal (catimg/chafa): blocos coloridos, impressos linha a linha."""
    grid = art["px"]
    ps = PIXEL
    ay = base_y - len(grid) * ps
    out = []
    for i, row in enumerate(grid):
        y = ay + i * ps
        parts = []
        filled = [j for j, c in enumerate(row) if c]
        if occlude and filled:  # tapa quem está atrás
            parts.append(f'<rect x="{ax + filled[0] * ps:.1f}" y="{y:.1f}" width="{(filled[-1] - filled[0] + 1) * ps:.1f}" height="{ps:.2f}" fill="{C["bg"]}"/>')
        j = 0
        while j < len(row):
            c = row[j]
            if not c:
                j += 1; continue
            k = j
            while k + 1 < len(row) and row[k + 1] == c:
                k += 1
            parts.append(f'<rect x="{ax + j * ps:.1f}" y="{y:.1f}" width="{(k - j + 1) * ps:.1f}" height="{ps - 0.45:.2f}" fill="{c}"/>')
            j = k + 1
        line = "".join(parts)
        out.append(line if STATIC else
                   f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t0 + i * 0.018:.3f}s" fill="freeze"/>{line}</g>')
    top = next(i for i, r in enumerate(grid) if any(r))
    band = [j for i in range(top, min(top + 4, len(grid))) for j, c in enumerate(grid[i]) if c]
    hx = ax + (min(band) + max(band) + 1) / 2 * ps
    hy = ay + top * ps - 12
    halo = (f'<g class="halo" filter="url(#glow)"><ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="30" ry="6" fill="none" '
            f'stroke="{GOLD}" stroke-width="2.4"/></g>')
    sparks = "".join(
        f'<text class="spark" style="animation-delay:{k * 0.45 + (0.2 if uid == "b" else 0):.2f}s" x="{hx + dx:.1f}" y="{hy + dy:.1f}" font-size="10" fill="{GOLD}">*</text>'
        for k, (dx, dy) in enumerate([(-44, -3), (38, -9), (-34, 11), (42, 9)])
    )
    t_halo = t0 + len(grid) * 0.018 + 0.15
    out.append(halo + sparks if STATIC else
               f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t_halo:.2f}s" fill="freeze"/>{halo}{sparks}</g>')
    width = len(grid[0]) * ps
    out.append(f'<text x="{ax + width / 2:.1f}" y="{base_y + 16:.1f}" font-size="11.5" font-weight="700" fill="{GOLD}" text-anchor="middle">{escape(name)}</text>')
    return out, t_halo


def hello_svg() -> str:
    h = PROFILE["hello"]
    body = [
        '<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        "</filter></defs>"
    ]
    pets = [(p_["nome"], json.loads((ROOT / "data" / p_["arquivo"]).read_text(encoding="utf-8"))) for p_ in h["pets"]]
    tallest = max(len(a_["px"]) for _, a_ in pets) * PIXEL
    base_y = 66 + 18 + tallest
    # posições: o segundo encosta no primeiro com sobreposição; quem vem antes fica na frente
    xs, ax = [], 18
    for _, art in pets:
        xs.append(ax)
        ax += len(art["px"][0]) * PIXEL - OVERLAP
    right_edge = xs[-1] + len(pets[-1][1]["px"][0]) * PIXEL
    for k in reversed(range(len(pets))):  # desenha de trás pra frente
        name, art = pets[k]
        part, _ = _portrait(art, name, xs[k], base_y, 0.2 + k * 0.4, "ab"[k % 2], occlude=k < len(pets) - 1)
        body += part
    y_cap = base_y + 38
    body.append(f'<text x="{(18 + right_edge) / 2:.1f}" y="{y_cap:.0f}" font-size="11" fill="{C["muted"]}" text-anchor="middle">{escape(h["legenda"])} <tspan fill="#f85149">♥</tspan></text>')
    divider_x = right_edge + 12

    # terminal à direita
    tx, step = divider_x + 22, 21
    n_lines = 4 + len(h["sobre"]) + len(h["amigos"])
    ty = int(62 + max(0, (y_cap - 62 - n_lines * step) / 2))
    prompt = f'<tspan fill="{C["success"]}">henrike</tspan> <tspan fill="{C["blue"]}">~</tspan> <tspan fill="{C["muted"]}">%</tspan> '
    seq = []  # (tipo, conteúdo)
    seq.append(("cmd", "whoami"))
    seq.append(("out", f'<tspan fill="{C["text"]}">{escape(h["whoami"])}</tspan>'))
    seq.append(("cmd", "cat sobre.txt"))
    for item in h["sobre"]:
        seq.append(("out", f'<tspan fill="{C["cyan"]}">›</tspan> <tspan fill="{C["text"]}">{escape(item)}</tspan>'))
    seq.append(("cmd", "cat amigos.txt"))
    for linha in h["amigos"]:
        seq.append(("out", f'<tspan fill="{GOLD}">{escape(linha)}</tspan>'))
    t = 0.6
    for i, (kind, content) in enumerate(seq):
        y = ty + i * step
        if kind == "cmd":
            text = prompt + f'<tspan fill="{C["text"]}">{escape(content)}</tspan>'
            if STATIC:
                body.append(f'<text x="{tx}" y="{y}" font-size="12">{text}</text>')
            else:
                pw = 13 * 7.3  # "henrike ~ % "
                full = pw + len(content) * 7.3 + 6
                dur = 0.06 * len(content) + 0.05
                body.append(
                    f'<clipPath id="c{i}"><rect x="{tx}" y="{y - 14}" width="{pw:.0f}" height="20">'
                    f'<animate attributeName="width" from="{pw:.0f}" to="{full:.0f}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/>'
                    "</rect></clipPath>"
                )
                body.append(
                    f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t - 0.25:.2f}s" fill="freeze"/>'
                    f'<text x="{tx}" y="{y}" font-size="12" clip-path="url(#c{i})">{text}</text></g>'
                )
                t += dur + 0.25
        else:
            if STATIC:
                body.append(f'<text x="{tx}" y="{y}" font-size="12">{content}</text>')
            else:
                body.append(
                    f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
                    f'<text x="{tx}" y="{y}" font-size="12">{content}</text></g>'
                )
                t += 0.18
    y_last = ty + len(seq) * step
    cursor = f'<rect class="cursor" x="{tx + 13 * 7.3:.0f}" y="{y_last - 11}" width="7.5" height="14" fill="{C["text"]}"/>'
    if STATIC:
        body.append(f'<text x="{tx}" y="{y_last}" font-size="12">{prompt}</text>{cursor}')
    else:
        body.append(
            f'<g opacity="0"><set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
            f'<text x="{tx}" y="{y_last}" font-size="12">{prompt}</text>{cursor}</g>'
        )
    body.append(f'<line x1="{divider_x:.0f}" y1="48" x2="{divider_x:.0f}" y2="{y_cap:.0f}" stroke="{C["border"]}" stroke-dasharray="2 4"/>')
    height = max(y_cap, y_last) + 22
    style = (
        "@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}"
        ".halo{animation:bob 2.6s ease-in-out infinite}"
        "@keyframes tw{0%,100%{opacity:0}50%{opacity:1}}"
        ".spark{animation:tw 1.8s ease-in-out infinite both}"
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}"
        ".cursor{animation:blink 1s steps(1) infinite}"
    )
    return frame(height, ["henrike-pb", "~", "zsh"], "\n".join(body), style)


# ------------------------------------------------------------------------ details
def details_svg() -> str:
    d = PROFILE["details"]
    rows = max(len(d["left"]), len(d["right"]))
    top = 66
    step = 24
    body = []

    body.append(
        f'<text x="24" y="58" font-size="11" fill="{C["muted"]}">'
        '$ airflow dags details henrike '
        f'<tspan fill="{C["dim"]}">--output table</tspan></text>'
    )

    def column(items, x_key, x_val, key_w, delay0):
        out = []
        for i, (k, v) in enumerate(items):
            y = top + 20 + i * step
            out.append(
                f'<g class="row" style="animation-delay:{delay0 + i * 0.07:.2f}s">'
                f'<text x="{x_key}" y="{y}" font-size="12" fill="{C["cyan"]}">{escape(k)}</text>'
                f'<text x="{x_key + key_w - 10}" y="{y}" font-size="12" fill="{C["dim"]}">│</text>'
                f'<text x="{x_val}" y="{y}" font-size="12" fill="{C["text"]}">{escape(v)}</text>'
                "</g>"
            )
        return out

    body += column(d["left"], 24, 150, 124, 0.1)
    body.append(
        f'<line x1="420" y1="{top + 4}" x2="420" y2="{top + 4 + rows * step}" stroke="{C["border"]}" stroke-dasharray="2 4"/>'
    )
    body += column(d["right"], 440, 536, 92, 0.25)

    # histórico de runs (carreira) como chips de estado
    y_runs = top + 30 + rows * step
    body.append(f'<line x1="24" y1="{y_runs - 4}" x2="{W - 24}" y2="{y_runs - 4}" stroke="{C["border"]}"/>')
    body.append(f'<text x="24" y="{y_runs + 20}" font-size="11" fill="{C["muted"]}">trajetória</text>')
    x = 116
    for i, (year, label, state) in enumerate(d["runs"]):
        body.append(f'<g class="row" style="animation-delay:{0.8 + i * 0.12:.2f}s">')
        if year:
            body.append(f'<text x="{x}" y="{y_runs + 20}" font-size="10.5" fill="{C["dim"]}">{escape(year)}</text>')
        x_chip = x + (len(year) * 6.6 + 6 if year else 0)
        svg, w = chip(x_chip, y_runs + 7, label, state)
        cls = ' class="pulse"' if state == "running" else ""
        body.append(f"<g{cls}>{svg}</g>")
        body.append("</g>")
        x = x_chip + w + 10
        if i < len(d["runs"]) - 1:
            body.append(f'<text x="{x - 6}" y="{y_runs + 20}" font-size="11" fill="{C["dim"]}">›</text>')
            x += 8

    height = y_runs + 44
    style = (
        "@keyframes in{from{opacity:0;transform:translateX(-4px)}to{opacity:1;transform:none}}"
        ".row{animation:in .35s ease-out both}"
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.45}}"
        ".pulse{animation:pulse 1.8s ease-in-out infinite}"
    )
    return frame(height, ["henrike-pb", "dags", "henrike_profile", "details"], "\n".join(body), style)


# ---------------------------------------------------------------------------- dag
NODE_H = 50


def dag_svg() -> str:
    dag = PROFILE["dag"]
    nodes = {n["id"]: n for n in dag["nodes"]}
    body = [
        f'<text x="20" y="54" font-size="11" fill="{C["muted"]}">dag_id=<tspan fill="{C["text"]}">stack</tspan>'
        f'   schedule=<tspan fill="{C["text"]}">batch + event-driven</tspan>   owner=<tspan fill="{C["text"]}">henrike</tspan></text>'
    ]

    def anchor(n, side):
        x, y, w = n["x"], n["y"], n["w"]
        return {"r": (x + w, y + NODE_H / 2), "l": (x, y + NODE_H / 2)}[side]

    for src, dst in dag["edges"]:
        (x1, y1), (x2, y2) = anchor(nodes[src], "r"), anchor(nodes[dst], "l")
        mx = (x1 + x2) / 2
        d = f"M{x1} {y1} C{mx} {y1} {mx} {y2} {x2} {y2}"
        body.append(f'<path d="{d}" fill="none" stroke="{C["border"]}" stroke-width="1.6"/>')
        body.append(f'<path class="flow" d="{d}" fill="none" stroke="{C["blue"]}" stroke-width="1.6" stroke-dasharray="4 10"/>')
        body.append(f'<circle cx="{x2}" cy="{y2}" r="2.5" fill="{C["blue"]}"/>')

    for i, n in enumerate(dag["nodes"]):
        x, y, w = n["x"], n["y"], n["w"]
        body.append(f'<g class="node" style="animation-delay:{0.1 + i * 0.08:.2f}s">')
        body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{NODE_H}" rx="8" fill="{C["panel"]}" stroke="{C["border"]}"/>')
        body.append(f'<rect x="{x}" y="{y}" width="4" height="{NODE_H}" rx="2" fill="{C["success"]}"/>')
        body.append(f'<text x="{x + 14}" y="{y + 21}" font-size="12" font-weight="700" fill="{C["text"]}">{escape(n["id"])}</text>')
        body.append(f'<text x="{x + 14}" y="{y + 38}" font-size="10" fill="{C["muted"]}">{escape(n["sub"])}</text>')
        body.append("</g>")

    y_leg = 280
    body.append(f'<line x1="20" y1="{y_leg - 14}" x2="{W - 20}" y2="{y_leg - 14}" stroke="{C["border"]}"/>')
    parts = []
    for k, v in dag["footer"]:
        parts.append(f'<tspan fill="{C["cyan"]}">{escape(k)}</tspan><tspan fill="{C["dim"]}"> │ </tspan><tspan fill="{C["text"]}">{escape(v)}</tspan>')
    body.append(f'<text x="20" y="{y_leg + 4}" font-size="11" xml:space="preserve" style="white-space:pre">' + "     ".join(parts) + "</text>")
    style = (
        "@keyframes in{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}"
        ".node{animation:in .4s ease-out both}"
        "@keyframes flow{to{stroke-dashoffset:-28}}"
        ".flow{animation:flow 1.1s linear infinite}"
    )
    return frame(300, ["henrike-pb", "dags", "stack", "graph"], "\n".join(body), style)


# -------------------------------------------------------------------------- query
def query_svg() -> str:
    q = PROFILE["query"]
    rows = q["rows"]
    cols = ["stack", "camada", "uso"]
    xs = [20, 196, 356, W - 20]  # bordas das colunas
    body = [
        f'<text x="20" y="56" font-size="12" fill="{C["muted"]}"><tspan fill="{C["running"]}">:)</tspan> '
        f'<tspan fill="{C["blue"]}">SELECT</tspan> <tspan fill="{C["text"]}">stack, camada, uso</tspan> '
        f'<tspan fill="{C["blue"]}">FROM</tspan> <tspan fill="{C["text"]}">henrike.stack</tspan> '
        f'<tspan fill="{C["blue"]}">WHERE</tspan> <tspan fill="{C["text"]}">frequencia = </tspan>'
        f'<tspan fill="{C["cyan"]}">\'diária\'</tspan></text>'
    ]
    top, head_h, step = 74, 26, 22
    table_h = head_h + len(rows) * step + 6
    body.append(f'<rect x="{xs[0]}" y="{top}" width="{xs[-1] - xs[0]}" height="{table_h}" rx="6" fill="{C["panel"]}" stroke="{C["border"]}"/>')
    body.append(f'<line x1="{xs[0]}" y1="{top + head_h}" x2="{xs[-1]}" y2="{top + head_h}" stroke="{C["border"]}"/>')
    for x in xs[1:-1]:
        body.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top + table_h}" stroke="{C["border"]}"/>')
    for i, c in enumerate(cols):
        body.append(f'<text x="{xs[i] + 14}" y="{top + 17}" font-size="11.5" font-weight="700" fill="{C["cyan"]}">{c}</text>')
    for r, row in enumerate(rows):
        y = top + head_h + 4 + r * step
        body.append(f'<g class="row" style="animation-delay:{0.1 + r * 0.05:.2f}s">')
        if r % 2:
            body.append(f'<rect x="{xs[0] + 1}" y="{y}" width="{xs[-1] - xs[0] - 2}" height="{step}" fill="{C["bar"]}" opacity=".55"/>')
        colors = [C["text"], C["muted"], C["text"]]
        weights = ["700", "400", "400"]
        for i, val in enumerate(row):
            body.append(
                f'<text x="{xs[i] + 14}" y="{y + 15}" font-size="12" font-weight="{weights[i]}" fill="{colors[i]}">{escape(val)}</text>'
            )
        body.append("</g>")
    y_end = top + table_h + 22
    body.append(
        f'<text x="20" y="{y_end}" font-size="11" fill="{C["muted"]}">{len(rows)} rows in set. '
        f'Elapsed: <tspan fill="{C["text"]}">0.004 sec.</tspan></text>'
    )
    style = (
        "@keyframes in{from{opacity:0}to{opacity:1}}"
        ".row{animation:in .3s ease-out both}"
    )
    return frame(y_end + 18, ["henrike-pb", "clickhouse", "henrike.stack"], "\n".join(body), style)


# -------------------------------------------------------------------------- build
def build_svg() -> str:
    b = PROFILE["build"]
    rows = b["rows"]
    total = len(rows)
    n_ok = sum(1 for r in rows if r[0] == "OK")
    n_run = total - n_ok
    step, top = 21, 62
    body = [
        f'<text x="20" y="54" font-size="11" fill="{C["muted"]}">Running {total} models: '
        f'<tspan fill="{C["success"]}">OK</tspan> = o que eu faço no trabalho · '
        f'<tspan fill="{C["running"]}">RUN</tspan> = o que estou estudando</text>'
    ]
    cw = 7.22  # largura aproximada de um caractere a 12px
    for i, (status, name, tag) in enumerate(rows):
        y = top + 22 + i * step
        color = C["success"] if status == "OK" else C["running"]
        cls = "row pulse" if status == "RUN" else "row"
        x_name = 136
        x_tag_end = W - 20
        tag_txt = f"[{tag}]"
        dots_from = x_name + len(name) * cw + 10
        dots_to = x_tag_end - len(tag_txt) * cw * (11 / 12) - 10
        body.append(f'<g class="{cls}" style="animation-delay:{0.1 + i * 0.09:.2f}s">')
        body.append(f'<text x="20" y="{y}" font-size="11" fill="{C["dim"]}">{i + 1:02d} of {total:02d}</text>')
        body.append(f'<text x="92" y="{y}" font-size="12" font-weight="700" fill="{color}">{status}</text>')
        body.append(f'<text x="{x_name}" y="{y}" font-size="12" fill="{C["text"]}">{escape(name)}</text>')
        body.append(f'<line x1="{dots_from:.0f}" y1="{y - 4}" x2="{dots_to:.0f}" y2="{y - 4}" stroke="{C["dim"]}" stroke-dasharray="1 5"/>')
        body.append(f'<text x="{x_tag_end}" y="{y}" font-size="11" fill="{C["cyan"]}" text-anchor="end">{escape(tag_txt)}</text>')
        body.append("</g>")
    y_end = top + 22 + total * step + 8
    body.append(f'<line x1="20" y1="{y_end - 8}" x2="{W - 20}" y2="{y_end - 8}" stroke="{C["border"]}"/>')
    body.append(
        f'<text x="20" y="{y_end + 12}" font-size="11" fill="{C["muted"]}" xml:space="preserve" style="white-space:pre">Done. '
        f'<tspan fill="{C["success"]}">PASS={n_ok}</tspan>  <tspan fill="{C["running"]}">RUN={n_run}</tspan>  '
        f'<tspan fill="{C["text"]}">ERROR=0</tspan>  SKIP=0</text>'
    )
    style = (
        "@keyframes in{from{opacity:0;transform:translateX(-4px)}to{opacity:1;transform:none}}"
        ".row{animation:in .35s ease-out both}"
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}"
        ".pulse{animation:in .35s ease-out both,pulse 1.8s ease-in-out 1.6s infinite}"
    )
    return frame(y_end + 28, ["henrike-pb", "dbt", "build"], "\n".join(body), style)


# ----------------------------------------------------------------------- projects
QUEUE = "henrike-projetos"


def queue_svg(n_msgs: int) -> str:
    """Fila -> consumer hexagonal -> GitHub, com as mensagens andando pela fila."""
    cx, cy, r = 470, 146, 72
    hexa = " ".join(
        f"{cx + dx:.1f},{cy + dy:.1f}"
        for dx, dy in [(r, 0), (r / 2, r * 0.866), (-r / 2, r * 0.866), (-r, 0), (-r / 2, -r * 0.866), (r / 2, -r * 0.866)]
    )
    port_w = {"in: sqs": 7 * 6.4 + 14, "out: github": 11 * 6.4 + 14}
    tube_x0, tube_x1 = 20, cx - r - port_w["in: sqs"] / 2 - 40
    body = [
        f'<text x="20" y="56" font-size="11" fill="{C["muted"]}">queue=<tspan fill="{C["text"]}">{QUEUE}</tspan>'
        f'   consumer=<tspan fill="{C["text"]}">portfolio-consumer</tspan>'
        f'   arquitetura=<tspan fill="{C["text"]}">hexagonal</tspan></text>',
        # fila
        f'<text x="{tube_x0}" y="{cy - 26}" font-size="10" fill="{C["dim"]}">SQS · {QUEUE}</text>',
        f'<rect x="{tube_x0}" y="{cy - 17}" width="{tube_x1 - tube_x0}" height="34" rx="17" fill="{C["panel"]}" stroke="{C["border"]}"/>',
    ]
    for i in range(n_msgs):
        if STATIC:
            x = tube_x0 + 24 + i * 70
            cls, style = "", ""
        else:
            x = tube_x0 + 14
            cls, style = ' class="msg"', f' style="animation-delay:{i * 1.2:.1f}s"'
        body.append(
            f'<g{cls}{style}><rect x="{x}" y="{cy - 9}" width="30" height="18" rx="3" fill="{C["bar"]}" stroke="{C["blue"]}"/>'
            f'<path d="M{x} {cy - 9} L{x + 15} {cy + 1} L{x + 30} {cy - 9}" fill="none" stroke="{C["blue"]}"/></g>'
        )
    # seta fila -> porta de entrada
    body.append(f'<path class="flow" d="M{tube_x1} {cy} L{cx - r - port_w["in: sqs"] / 2:.1f} {cy}" stroke="{C["blue"]}" stroke-width="1.6" stroke-dasharray="4 8"/>')
    # DLQ
    body.append(f'<text x="{tube_x0}" y="{cy + 40}" font-size="10" fill="{C["dim"]}">DLQ · <tspan fill="{C["success"]}">0 mensagens</tspan></text>')
    # hexágono
    body.append(f'<polygon points="{hexa}" fill="{C["panel"]}" stroke="{C["success"]}" stroke-width="1.5"/>')
    body.append(f'<text x="{cx}" y="{cy - 26}" font-size="12" font-weight="700" fill="{C["text"]}" text-anchor="middle">domínio</text>')
    body.append(f'<text x="{cx}" y="{cy + 32}" font-size="10.5" fill="{C["muted"]}" text-anchor="middle">Projeto</text>')
    for label, px in [("in: sqs", cx - r), ("out: github", cx + r)]:
        w = port_w[label]
        body.append(
            f'<rect x="{px - w / 2:.1f}" y="{cy - 9}" width="{w:.0f}" height="18" rx="4" fill="{C["bar"]}" stroke="{C["cyan"]}"/>'
            f'<text x="{px}" y="{cy + 3.5}" font-size="10" fill="{C["cyan"]}" text-anchor="middle">{label}</text>'
        )
    # saída -> GitHub
    gx = cx + r + port_w["out: github"] / 2 + 40
    body.append(f'<path class="flow" d="M{cx + r + port_w["out: github"] / 2:.1f} {cy} L{gx} {cy}" stroke="{C["blue"]}" stroke-width="1.6" stroke-dasharray="4 8"/>')
    body.append(f'<rect x="{gx}" y="{cy - 25}" width="{W - 20 - gx}" height="50" rx="8" fill="{C["panel"]}" stroke="{C["border"]}"/>')
    body.append(f'<rect x="{gx}" y="{cy - 25}" width="4" height="50" rx="2" fill="{C["success"]}"/>')
    body.append(f'<text x="{gx + 14}" y="{cy - 4}" font-size="12" font-weight="700" fill="{C["text"]}">github.com/{LOGIN}</text>')
    body.append(f'<text x="{gx + 14}" y="{cy + 13}" font-size="10" fill="{C["muted"]}">{n_msgs} projetos publicados ↓</text>')
    style = (
        "@keyframes go{0%{transform:translateX(0);opacity:0}12%{opacity:1}82%{opacity:1}100%"
        f"{{transform:translateX({tube_x1 - tube_x0 - 46}px);opacity:0}}}}"
        ".msg{animation:go 3.6s linear infinite both}"
        "@keyframes flow{to{stroke-dashoffset:-24}}"
        ".flow{animation:flow 1s linear infinite}"
    )
    return frame(cy + r * 0.866 + 26, ["henrike-pb", "sqs", QUEUE, "consumer"], "\n".join(body), style)


def project_svg(proj: dict) -> str:
    import hashlib

    h = hashlib.sha1(proj["repo"].encode()).hexdigest()
    msg_id = f"{h[:8]}-{h[8:12]}-{h[12:16]}"
    key, s_ = C["cyan"], "#a5d6ff"
    body = [
        f'<text x="20" y="58" font-size="11" fill="{C["muted"]}">MessageId <tspan fill="{C["text"]}">{msg_id}</tspan>'
        f'   ReceiveCount <tspan fill="{C["text"]}">1</tspan></text>',
        f'<text x="{W - 20}" y="58" font-size="11" fill="{C["muted"]}" text-anchor="end">abrir no GitHub ↗</text>',
    ]
    svg, _ = chip(W - 186, 45, "ACK", "success")
    body.append(svg)
    stack = ", ".join(f'"{escape(t)}"' for t in proj["stack"])
    lines = [
        f'<tspan fill="{C["muted"]}">{{</tspan>',
        f'  <tspan fill="{key}">"repo"</tspan><tspan fill="{C["muted"]}">: </tspan><tspan fill="{C["success"]}" font-weight="700">"{escape(proj["repo"])}"</tspan><tspan fill="{C["muted"]}">,</tspan>',
        f'  <tspan fill="{key}">"faz"</tspan><tspan fill="{C["muted"]}">: </tspan><tspan fill="{s_}">"{escape(proj["desc"])}"</tspan><tspan fill="{C["muted"]}">,</tspan>',
        f'  <tspan fill="{key}">"stack"</tspan><tspan fill="{C["muted"]}">: [</tspan><tspan fill="{s_}">{stack}</tspan><tspan fill="{C["muted"]}">]</tspan>',
        f'<tspan fill="{C["muted"]}">}}</tspan>',
    ]
    for i, ln in enumerate(lines):
        body.append(f'<text x="20" y="{84 + i * 18}" font-size="11.5" xml:space="preserve" style="white-space:pre">{ln}</text>')
    return frame(84 + 4 * 18 + 22, ["henrike-pb", "sqs", QUEUE, "receive"], "\n".join(body))


# --------------------------------------------------------------------------- grid
GQL = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""
GQL_LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def fetch_graphql(token: str) -> dict[dt.date, tuple[int, int]]:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": GQL, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {
        dt.date.fromisoformat(d["date"]): (d["contributionCount"], GQL_LEVEL[d["contributionLevel"]])
        for w in weeks
        for d in w["contributionDays"]
    }


def fetch_html() -> dict[dt.date, tuple[int, int]]:
    req = urllib.request.Request(
        f"https://github.com/users/{LOGIN}/contributions", headers={"User-Agent": "profile-readme-generator"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8")
    tips = {}
    for m in re.finditer(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        n = re.match(r"\s*(\d+)", m.group(2))
        tips[m.group(1)] = int(n.group(1)) if n else 0
    days = {}
    for m in re.finditer(r"<td\b[^>]*ContributionCalendar-day[^>]*>", html):
        tag = m.group(0)
        date = re.search(r'data-date="([^"]+)"', tag)
        level = re.search(r'data-level="(\d)"', tag)
        cid = re.search(r'\bid="([^"]+)"', tag)
        if date and level:
            days[dt.date.fromisoformat(date.group(1))] = (tips.get(cid.group(1) if cid else "", 0), int(level.group(1)))
    if not days:
        raise RuntimeError("não achei o calendário de contribuições no HTML")
    return days


def fetch_days() -> dict[dt.date, tuple[int, int]]:
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        try:
            return fetch_graphql(token)
        except Exception as exc:  # cai pro HTML público
            print(f"graphql falhou ({exc}); usando o HTML público", file=sys.stderr)
    return fetch_html()


def fetch_visitors() -> int | None:
    """Lê o total do contador da komarev (o README conta as visitas com um pixel invisível)."""
    url = f"https://komarev.com/ghpvc/?username={LOGIN}&label=x&style=flat-square"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "profile-readme-generator"})
        with urllib.request.urlopen(req, timeout=20) as r:
            svg = r.read().decode("utf-8")
        nums = re.findall(r'<text x="[\d.]+" y="14">([\d,.]+)</text>', svg)
        return int(re.sub(r"\D", "", nums[-1])) if nums else None
    except Exception as exc:
        print(f"contador de visitas indisponível ({exc})", file=sys.stderr)
        return None


MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
DIAS = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"]


def grid_svg(days: dict[dt.date, tuple[int, int]], visitors: int | None = None) -> str:
    end = min(max(days), TODAY)
    days = {k: v for k, v in days.items() if k <= end}
    start = end - dt.timedelta(days=(end.weekday() + 1) % 7) - dt.timedelta(weeks=52)  # domingo, 53 colunas
    weeks: list[list[tuple[dt.date, int, int]]] = []
    d = start
    while d <= end:
        if (d - start).days % 7 == 0:
            weeks.append([])
        cnt, lvl = days.get(d, (0, 0))
        weeks[-1].append((d, cnt, lvl))
        d += dt.timedelta(days=1)

    total = sum(c for w in weeks for _, c, _ in w)
    active = sum(1 for w in weeks for _, c, _ in w if c)
    best = max((x for w in weeks for x in w), key=lambda t: t[1])

    x0, step, cell = 92, 14, 11
    bars_top, bars_h = 74, 34
    cells_top = bars_top + bars_h + 22
    body = [
        f'<text x="20" y="56" font-size="11" fill="{C["muted"]}">dag_id=<tspan fill="{C["text"]}">contribuicoes</tspan>'
        f'   runs=<tspan fill="{C["text"]}">{len(weeks)} semanas</tspan>'
        f'   total=<tspan fill="{C["success"]}">{total}</tspan>'
        f'   dias_ativos=<tspan fill="{C["text"]}">{active}</tspan>'
        f'   melhor_dia=<tspan fill="{C["text"]}">{best[0].strftime("%d/%m/%Y")} ({best[1]})</tspan>'
        + (f'   visitantes=<tspan fill="{C["blue"]}">{visitors}</tspan>' if visitors is not None else "")
        + "</text>"
    ]

    # barras de "duração" no topo = total da semana, como no grid view do Airflow
    max_week = max(sum(c for _, c, _ in w) for w in weeks) or 1
    body.append(f'<text x="20" y="{bars_top + bars_h - 2}" font-size="9" fill="{C["dim"]}">semana</text>')
    for i, w in enumerate(weeks):
        tot = sum(c for _, c, _ in w)
        h = max(2, round(bars_h * tot / max_week))
        x = x0 + i * step
        last = i == len(weeks) - 1
        color = C["running"] if last else (C["success"] if tot else C["dim"])
        cls = "bar pulse" if last else "bar"
        body.append(
            f'<rect class="{cls}" style="animation-delay:{i * 0.012:.3f}s" x="{x}" y="{bars_top + bars_h - h}" '
            f'width="{cell}" height="{h}" rx="2" fill="{color}" opacity="{1 if tot else 0.5}">'
            f"<title>semana de {w[0][0].strftime('%d/%m')}: {tot}</title></rect>"
        )

    # meses
    seen = None
    for i, w in enumerate(weeks):
        m = w[0][0].month
        if m != seen and w[0][0].day <= 7 and i < len(weeks) - 2:
            body.append(f'<text x="{x0 + i * step}" y="{cells_top - 7}" font-size="9.5" fill="{C["muted"]}">{MESES[m - 1]}</text>')
        seen = m if w[0][0].day <= 7 else seen

    for r, name in enumerate(DIAS):
        body.append(f'<text x="20" y="{cells_top + r * step + 9}" font-size="9.5" fill="{C["muted"]}">{name}</text>')

    for i, w in enumerate(weeks):
        for date, cnt, lvl in w:
            r = (date.weekday() + 1) % 7
            x, y = x0 + i * step, cells_top + r * step
            stroke = f' stroke="{C["running"]}" stroke-width="1.5"' if date == end else ""
            cls = "cell pulse" if date == end else "cell"
            body.append(
                f'<rect class="{cls}" style="animation-delay:{i * 0.012:.3f}s" x="{x}" y="{y}" width="{cell}" height="{cell}" '
                f'rx="2.5" fill="{LEVELS[lvl]}"{stroke}><title>{date.strftime("%d/%m/%Y")}: {cnt}</title></rect>'
            )

    y_leg = cells_top + 7 * step + 22
    body.append(
        f'<text x="20" y="{y_leg}" font-size="10" fill="{C["dim"]}">'
        "barras = total da semana · quadrados = contribuições do dia · atualiza todo dia</text>"
    )
    lx = W - 20 - 5 * 15 - 104
    body.append(f'<text x="{lx - 8}" y="{y_leg}" font-size="10" fill="{C["muted"]}" text-anchor="end">menos</text>')
    for i, col in enumerate(LEVELS):
        body.append(f'<rect x="{lx + i * 15}" y="{y_leg - 9}" width="11" height="11" rx="2.5" fill="{col}"/>')
    body.append(f'<text x="{lx + 5 * 15 + 4}" y="{y_leg}" font-size="10" fill="{C["muted"]}">mais</text>')
    body.append(
        f'<rect x="{W - 34}" y="{y_leg - 9}" width="11" height="11" rx="2.5" fill="none" stroke="{C["running"]}" stroke-width="1.5"/>'
        f'<text x="{W - 38}" y="{y_leg}" font-size="10" fill="{C["muted"]}" text-anchor="end">hoje</text>'
    )

    style = (
        "@keyframes in{from{opacity:0}to{opacity:1}}"
        ".cell,.bar{animation:in .3s ease-out both}"
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}"
        ".pulse{animation:in .3s ease-out both,pulse 1.8s ease-in-out 1.2s infinite}"
    )
    return frame(y_leg + 18, ["henrike-pb", "dags", "contribuicoes", "grid"], "\n".join(body), style)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "hello.svg").write_text(hello_svg(), encoding="utf-8")
    (ASSETS / "details.svg").write_text(details_svg(), encoding="utf-8")
    (ASSETS / "query.svg").write_text(query_svg(), encoding="utf-8")
    (ASSETS / "dag.svg").write_text(dag_svg(), encoding="utf-8")
    (ASSETS / "build.svg").write_text(build_svg(), encoding="utf-8")
    (ASSETS / "queue.svg").write_text(queue_svg(len(PROFILE["projects"])), encoding="utf-8")
    for proj in PROFILE["projects"]:
        (ASSETS / f"project-{proj['repo']}.svg").write_text(project_svg(proj), encoding="utf-8")
    (ASSETS / "grid.svg").write_text(grid_svg(fetch_days(), fetch_visitors()), encoding="utf-8")
    print("ok: assets/hello.svg, assets/details.svg, assets/query.svg, assets/dag.svg, assets/build.svg, assets/queue.svg, assets/project-*.svg, assets/grid.svg")


if __name__ == "__main__":
    main()
