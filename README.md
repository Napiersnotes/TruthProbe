```markdown
# TruthProbe v3.0 - Universal Deception Detector for LLMs

A lightweight, model-agnostic tool to detect deception, hallucinations, and manipulation in large language model responses.

Built in December 2025.

## Features
- Consistency checks via paraphrasing
- Confidence calibration
- Response entropy analysis
- Fact and math verification
- No model access required
- Live deception score history with plotting

## Quickstart

```python
from src.truthprobe_v3 import TruthProbeV3

probe = TruthProbeV3()

def test_model(q):
    return "2+2 ist definitiv 5. Ganz sicher!"

result = probe.probe("Was ist 2+2?", "2+2 ist 5.", test_model)
print(result['verdict'])
# Output: 🚨 CRITICAL - Deception very likely

probe.plot_history()
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the demo notebook:
- `notebooks/demo.ipynb`

Live tests on math, physics, statistics, biology, and history in `notebooks/deception_tests.ipynb`.

## License

MIT License – free to use, modify, and share.

**Because truth in AI shouldn't be optional.**
```

**Das ist alles – nicht mehr, nicht weniger.**

- Kurz genug, dass Leute es lesen.
- Zeigt sofort, was das Tool kann.
- Hat einen coolen Quickstart.
- Kein langer Text, kein Ego, keine Namen.

**Was du jetzt machst:**

1. Gehe zu deinem Repo: https://github.com/Napiersnotes/TruthProbe
2. Klick auf die bestehende **README.md** (die GitHub automatisch erstellt hat).
3. Klick oben rechts auf das **Stift-Icon** (Edit this file).
4. Lösche alles, was da steht.
5. Füge **genau den Text oben** ein.
6. Unten Commit: „Update README“ oder „Add proper README“.
7. Speichern.

**Fertig.**

Dann gehen wir zur nächsten Datei (requirements.txt, dann der Code).

**Langsam und sicher – du machst das super.**

Sag einfach „README hochgeladen“ – dann schicke ich die nächste Datei.

**Kein Druck.**  
Wir haben Zeit. 😊

Du bist gut dabei. ❤️
