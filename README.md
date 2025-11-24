# ReevaluatingCoCo-LLM

Replication study of CoCo static analysis on 197,088 Chrome Web Store extensions, evaluating precision through manual analysis and exploring LLM-based automated validation.

## Overview

Master's thesis supplementary materials (LMU Munich, November 2025)

## Dataset

- **197,088** Chrome Web Store extensions crawled by my colleagues (February 2025)
- **1,887** flagged as vulnerable by CoCo (0.96%)
- **239** manually validated (90% confidence, ±5% margin, 50% Population Proportion)

## Key Results

### RQ1: CoCo Precision

**36.4% precision** (90% CI: 32-42%) under refined threat model

**Top false positive patterns:**
- Hardcoded backend communications (trusted infrastructure)
- Incomplete storage exploitation chains
- Attacker parameters to conditional statements

### RQ2: LLM Validation Effectiveness

**Claude Sonnet 4.5** analyzed all 1,887 flagged extensions 

| Metric 			| Result |
|-------------------------------|--------|
| Agreement with Manual 	| 81.6%  |
| Sensitivity (True Positives)  | 55.2%  |
| Specificity (False Positives) | 96.1%  |
| False Negative Rate 		| 43.7%  |

**LLM Failure Modes:**
- Cross-file dependency tracking (31.6%)
- Threat model reasoning errors (26.3%)
- Code complexity barriers (23.7%)

**Takeaway:** LLMs excel at filtering false positives but miss complex vulnerabilities. Best used as first-pass triage, not standalone validation.

### RQ3: Multi-Tool Agreement

74 extensions flagged by both CoCo and DoubleX:

**89.2% precision** — 2.5× improvement over CoCo's baseline

Multi-tool agreement filters tool-specific false positives and identifies clearer exploitation patterns.

## Repository Contents

- `coco_2021_replication/` - Original CoCo tool and dataset from 2021
- `llm_analysis_1887/` - Complete LLM analysis files for all 1,887 extensions flagged by CoCo
- `llm_methodology_logs/` - LLM prompts and execution logs
- `manual_validation_239/` - Ground truth dataset with 239 manually validated extensions
- `multi_tool_overlap_74/` - Analysis of 74 extensions flagged by both CoCo and DoubleX
- `scripts/` - Analysis and processing scripts

## Citation

```bibtex
@mastersthesis{teofanescu2025coco,
  author = {Tudor Teofănescu},
  title = {Reevaluating Message-Passing Vulnerabilities in Chrome Extensions:
           A Replication Study of CoCo},
  school = {Ludwig-Maximilians-Universität München},
  year = {2025},
  month = {November}
}
```

## Related Work

- **CoCo** - [GitHub](https://github.com/Suuuuuzy/CoCo) | [Paper](https://doi.org/10.1145/3576915.3616584)
- **DoubleX** - [Paper](https://doi.org/10.1145/3460120.3484745)
- **Claude Sonnet 4.5** - [Announcement](https://www.anthropic.com/news/claude-sonnet-4-5)

## License

Research data provided for academic purposes.
