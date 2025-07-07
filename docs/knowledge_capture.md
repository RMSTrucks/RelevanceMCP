# Knowledge Capture – Relevance AI + RMS Tool-Building Project

_Last updated: 2025-07-07_

---

## 1. Business Context

| Item | Details |
|------|---------|
| Company | **RMS – Risk Management Strategies Corp** |
| Product | Truck-insurance agency + forthcoming DOT/Compliance platform |
| Current Pain Point | Quoters (Cynthia & Liam) spend **30-60 min** filling three carrier webforms per prospect |
| Vision | Convert every repeatable business process into a Relevance AI tool/agent |

### Quote Workflow (as-is)

1. Dial newly registered trucking companies → conduct interview  
2. Populate RMS Trucking Quote PDF  
3. Manually fill webforms for **Progressive, Geico, Berkshire Hathaway**  
4. Create opportunity in Close CRM  
5. Hand off to Sales

---

## 2. Hybrid Tool-Building Methodology

| Phase | Description | Artifacts |
|-------|-------------|-----------|
| **Design** | Interview SME, decompose workflow, define inputs/outputs, rules | Markdown spec |
| **Prompt** | Write a **Master Prompt** describing tool purpose, pipeline, secrets, dependencies | Prompt text |
| **Generate** | Paste prompt into **Relevance “Build from prompt”** → auto-creates skeleton steps | Tool draft |
| **Polish** | Fill LLM prompts, add Python or transformation steps, configure secrets & packages | Final tool |
| **Iterate** | Test → refine spec/prompt → regenerate or tweak | Versioned docs |

_Time saving: ~70-90 % of scaffolding produced automatically._

---

## 3. Technical Discoveries (Relevance AI)

### 3.1 Python Code Step Essentials
- **Variable access**  
  - Inputs: `params['call_transcript']`  
  - Step outputs: `steps['extract_data']['json_data']`  
  - Secrets: `'{{SENDGRID_KEY}}'`
- **Return values**: must `return {...}` to expose downstream.
- **PyPI packages**: add each under **“PyPI Packages → + New item”**.
- **Runtime Commands**: shell commands before code runs (e.g. `playwright install chromium`).
- **Advanced settings**: memory, CPUs, timeout, long-output toggle.

### 3.2 Transformations Library Highlights
Useful built-ins that can replace custom code:
| Transformation | Use-case in RMS Tool |
|----------------|----------------------|
| `send_email_step` | Email PDF + quote summary (no SendGrid code) |
| `browserless_scrape` | Simple page scraping (not full form filling) |
| `pdf_to_text`, `to_json` | Data extraction / conversion |
| `api_call` | Generic HTTPS calls |

> **Limitation:** `browserless_scrape` is read-only; complex interactive form filling still requires Playwright/Selenium.

### 3.3 Tool Builder AI Findings
- Understands pipeline tables & headings; creates correct step types.
- Leaves prompts/code blank – human must fill.
- Makes smart UX decisions (e.g. credential objects as inputs).

---

## 4. RMS Quote-Automation Tool Snapshot

| Step | Type | Purpose |
|------|------|---------|
| 1. `extract_data` | LLM | Parse call transcript → JSON |
| 2. `apply_rules` | LLM | RMS heuristics (new venture, refrigerated, radius) |
| 3. `build_pdf` | Python (`pdfrw`) | Fill RMS quote form PDF |
| 4-6. `quote_*` | Playwright code | Human-like login & form fill for carriers, stop at premium |
| 7. `draft_email` | LLM | Compose summary & CRM copy-paste block |
| 8. `send_email` | Transformation `send_email_step` | Deliver PDF + premiums to Cynthia/Liam |

Human in the loop: review email → create Close CRM opportunity.

---

## 5. Human-Like Automation Guidelines

- **Random delays** `1-3 s`; character typing delay `50-150 ms`.  
- **Hover+click** sequences to mimic users.  
- **Respect rate limits**; one quote cycle per carrier login session.  
- **Stop before final “Submit”**; capture premium via DOM text or screenshot.  
- **Fallback handling**: CAPTCHA detection → email alert with “N/A”.

---

## 6. Repository Convention

```
/docs
  knowledge_capture.md   <-- this file
  rms_quote_tool_spec.md
  hybrid_methodology.md
/tool_prompts
  rms_generate_quotes_prompt.md
/server
  playwright_scripts/
  ...
```

---

## 7. Next Actions

1. **Fill missing code/prompts** in generated tool using `docs/rms_tool_completion_guide.md`.  
2. Commit this knowledge capture to repo for future onboarding.  
3. Pilot first live transcript → measure time saved.  
4. Expand hybrid method to FMCSA registration workflow.

---

*End of Knowledge Capture*  
