# Relevance AI Technical Guide  
_Hands-on reference for tool builders, Python coders & automation architects_

_Last updated 2025-07-07_

---

## 1. Tool Builder Anatomy

```
┌──────────────┐
│  Inputs      │  → `params['<name>']`
├──────────────┤
│  Steps       │
│   • LLM      │  prompt-completion
│   • Python   │  python_code_transformation
│   • Transform│  pre-built run_step("…")
│   • Email    │  send_email_step
├──────────────┤
│  Outputs     │  return {...} or automatic
└──────────────┘
```

### 1.1  Input Variables  
Create in **Inputs** panel.  
Access inside steps:  

```python
company_name = params['company_name']
```

### 1.2  Step Output Access  

```python
json_data = steps['extract_data']['json_data']
```

### 1.3  Secrets  
Workspace → **API Keys / Secrets**.  
Reference inside code or prompt with `'{{SENDGRID_KEY}}'`.

---

## 2. Python Code Step Deep-Dive

| Setting | Purpose | Typical RMS value |
|---------|---------|-------------------|
| **Backend** | Modal Labs (default) or e2b.dev | Modal |
| **PyPI Packages** | Add each: `playwright==1.44.0`, `pdfrw==0.4`, … | list items |
| **Runtime Commands** | Shell before Python | `playwright install chromium` |
| **Enable “Long Output”** | Allow >127 k chars | ON for debugging |
| **Memory / CPU / Timeout** | Resource limits | 2 GB RAM, 1 CPU, 300 s |

Return data for downstream use:

```python
return {
    "pdf_path": tmp_path,
    "premium": price
}
```

---

## 3. Transformation Catalogue (most used)

| Name | One-liner | Example call |
|------|-----------|--------------|
| `prompt_completion` | Chat/completion LLM | `run_step("prompt_completion",{…})` |
| `send_email_step` | Simple email send | recipients, subject, body |
| `browserless_scrape` | Scrape webpage content | limited – read-only |
| `api_call` | Generic HTTP request | GET/POST JSON |
| `pdf_to_text` | Extract text from PDF | OCR optional |
| `to_json` | Cast string → JSON | validate LLM output |
| `export_to_file` | Create temp download | CSV/PDF/JSON |
| `python_code_transformation` | Custom code (alias for Python step) | install pkgs, run cmds |

_See full list in Relevance docs → “Tool Builder Transformations”._

---

## 4. Prompt → Tool Workflow (“Prompting Hack”)

1. Write a **Master Prompt**  
   - Purpose, inputs, pipeline (table), secrets, packages, success criteria.  
2. In Tool Builder choose **“Build from prompt”**.  
3. Generator creates skeleton: inputs + steps wired.  
4. Manually fill:  
   - LLM prompts  
   - Python code / transformations  
   - PyPI packages & runtime commands  
5. Test → iterate.  
_Savings: 70-90 % less manual wiring._

---

## 5. Best Practices

### 5.1  Human-like Browser Automation (Playwright)
```
await page.type("#field", value, delay=random.randint(50,150))
await page.wait_for_timeout(random.randint(800,2000))
await page.hover("#submit")
await page.click("#submit")
```
• Random delays, subtle hovers, stop at review page.  
• Respect CAPTCHAs → fallback email alert.  

### 5.2  Error Handling Pattern
```python
try:
    ... main logic ...
except Exception as e:
    return {"error": str(e)}
```
Route error downstream; LLM or email step can notify.

### 5.3  Testing Tips
1. Run each step in isolation with sample data.  
2. Toggle “Long Output” for verbose debugging.  
3. Use `echo` transformation to inspect variable flow.  
4. Log key metrics (`start/end time`, `credits_cost`) to console.

### 5.4  Performance & Cost
| Tip | Reason |
|-----|--------|
| Set max_tokens on LLM steps | control spend |
| Use `split_and_map` for long docs | chunk processing |
| Offload emails to `send_email_step` | zero-code, no external API |

---

## 6. Reference Snippets

### 6.1  Prompt Completion with Validators
```python
response = run_step("prompt_completion", {
  "prompt": system_prompt + user_prompt,
  "model": "openai-gpt-4o-mini",
  "validators": {
     "shape": "json",
     "schema": {"name":"", "phone":""}
  },
  "temperature": 0.2
})
```

### 6.2  Send Email with Attachment
```python
run_step("send_email_step", {
  "recipientEmails": ["cynthia@rmstruckers.co"],
  "subject": subject,
  "body": email_body,
  "attachments": [{"url": steps['fill_pdf']['pdf_path']}]
})
```

### 6.3  Runtime Commands Example
```
pip install playwright==1.44.0
playwright install chromium
```

---

## 7. Checklist for New Tools

- [ ] Define **Inputs** & sample values.  
- [ ] Design pipeline table (LLM / code / transformation).  
- [ ] Draft Master Prompt → generate skeleton.  
- [ ] Add PyPI packages & runtime commands in each Python step.  
- [ ] Insert prompts & code; ensure `return {}`.  
- [ ] Store credentials in **Secrets** panel.  
- [ ] Unit-test each step; enable long output for debug.  
- [ ] End-to-end run with real data; measure latency & cost.  
- [ ] Document tool in `/docs/*.md`.

---

## 8. Resources

- Relevance Docs → “Python Helper Functions”, “Transformations”  
- Playwright Docs → human-like automation patterns  
- RMS repo docs:  
  - `docs/hybrid_methodology.md`  
  - `docs/rms_tool_completion_guide.md`

---

_Questions or improvements? PRs welcome!_  
