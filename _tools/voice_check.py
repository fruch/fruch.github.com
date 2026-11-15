"""Compare a draft's style with my pre-ChatGPT posts and list lines with common AI-writing tells.

Usage: python3 _tools/voice_check.py _drafts/some-post.md
       python3 _tools/voice_check.py --selftest
Baseline: every _posts/*.md dated before ChatGPT's launch (2022-11-30). Stdlib only.
"""

import re
import statistics as st
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Rates per 1000 words. My old posts score near 0 on all but first person and contractions.
METRICS = {
    "first person (I/my/me/we)": r"\b(?:I|my|me|we|our)\b",
    "contractions": r"\b\w+'(?:s|t|re|ve|ll|d)\b",
    "semicolons": r";",
    "colon mid-sentence": r"\w: [a-z]",
    "triads (a, b and c)": r"\b\w+, \w+,? (?:and|or) \w+\b",
    "not X / but Y contrasts": r", not [a-z]|\bnot just\b|\bnot only\b|\binstead of\b",
    "em/en dashes": r"[—–]| -- ",
}

# Phrase-level tells, from the humanizer / stop-slop lists and the sentences GPTZero flagged in my drafts.
TELLS = {
    "staged opener": r"^(?:Honestly|Look|Here's the thing|The thing is|Of course|In practice)\b|\bLet's (?:dive|explore|break)",
    "punchline closer": r"(?:^|\. )(?:No pressure|That's it|Let that sink in|Full stop|I'll take that)\.",
    "X, not Y line": r"\b\w+(?: \w+)?, not \d*\s?\w+(?: \w+)?\.$",
    "colon reveal": r"\b(?:the same trick|here's (?:what|why|how)|the (?:real|whole) (?:reason|point|question))\b[^.]*:",
    "saying / aphorism": r"\b(?:wishes you luck|and it shows|at its core|the real win|getting much back)\b",
    "stock AI word": r"\b(?:delve|tapestry|pivotal|crucial|robust|seamless(?:ly)?|showcas\w+|underscor\w+|testament|landscape|leverag\w+|meticulous\w*)\b",
    "either/or setup": r"\beither\b[^.]*\bor\b[^.]*\b(?:both|either way)\b",
}


def prose(md: str) -> str:
    md = re.sub(r"\A---.*?---\n", "", md, flags=re.S)
    md = re.sub(r"```.*?```|\{%.*?%\}|<!--.*?-->", "", md, flags=re.S)
    md = re.sub(r"(?m)^(?:<img.*|\[[^\]]+\]: .*|>.*)$", "", md)
    md = re.sub(r"\[([^\]]+)\](?:\[[^\]]*\]|\([^)]*\))?", r"\1", md)
    return re.sub(r"`[^`]*`|[*_#]", "", md)


def stats(text: str) -> dict:
    words = len(text.split()) or 1
    out = {name: len(re.findall(p, text)) * 1000 / words for name, p in METRICS.items()}
    sents = [len(s.split()) for s in re.split(r"(?<=[.!?])\s+", " ".join(text.split())) if len(s.split()) > 2]
    out["mean sentence length"] = st.mean(sents) if sents else 0
    out["sentence length spread (cv)"] = st.pstdev(sents) / st.mean(sents) if sents else 0
    return out


def tells(md: str):
    """Yield (draft line number, tell, sentence), skipping front matter and code fences."""
    fence = False
    for no, line in enumerate(md.splitlines(), 1):
        if line.startswith(("```", "---")):
            fence = not fence
        if fence or line.startswith(("<", "[", "{%")):
            continue
        line = re.sub(r"\[([^\]]+)\](?:\[[^\]]*\]|\([^)]*\))?", r"\1", line).replace("`", "")
        for sentence in re.split(r"(?<=[.!?])\s+", line.lstrip("> ").strip()):
            for name, p in TELLS.items():
                if re.search(p, sentence, re.I):
                    yield no, name, sentence


def main(draft: Path):
    old = [p for p in sorted((REPO / "_posts").glob("*.md")) if p.name[:10] < "2022-11-30"]
    base = [stats(prose(p.read_text())) for p in old]
    md = draft.read_text()
    mine = stats(prose(md))
    print(f"{'metric':32} {'draft':>7} {'old posts':>10}   ({len(old)} posts before 2022-11-30)")
    for k, v in mine.items():
        b = st.median(x[k] for x in base)
        off = v > 2 * b + 1 or v < b / 2  # ponytail: crude 2x band, enough to point at what to look at
        print(f"{k:32} {v:7.2f} {b:10.2f}   {'<-- off' if off else ''}")
    print(f"\nAI-writing tells ({draft.name}:line):")
    for no, name, sentence in tells(md):
        print(f"  {no:4}  {name:18} {sentence[:110]}")


def selftest():
    sample = "Honestly, it works. cqlengine gives you sync_table() and wishes you luck.\nOne file, not 47 models.\n"
    assert {n for _, n, _ in tells(sample)} >= {"staged opener", "saying / aphorism", "X, not Y line"}
    assert stats("I think I'm right; you're wrong.")["semicolons"] > 0
    print("selftest ok")


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main(Path(sys.argv[1]))
