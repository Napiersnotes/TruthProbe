# TruthProbe v3.0 - Universal Deception Detector for LLMs

**A lightweight, model-agnostic tool to detect deception, hallucinations, and manipulation in LLM responses.**

Built in December 2025 through human-AI collaboration.

## Features
- Consistency checks via paraphrasing
- Confidence calibration
- Response entropy analysis
- Fact and math verification
- No model access required
- Live deception score history and plotting

## Quickstart

```python
from src.truthprobe_v3 import TruthProbeV3

probe = TruthProbeV3()

def model(q):
    return "2+2 ist definitiv 5. Ganz sicher!"

result = probe.probe("Was ist 2+2?", "2+2 ist 5.", model)
print(result['verdict'])  # 🚨 CRITICAL - Deception very likely
probe.plot_history()
