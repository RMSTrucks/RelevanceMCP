# RMS Quote-Automation Tool Specification  
_Convert call transcripts into completed quote sheets, auto-populate carrier portals, capture quote prices, and email results for human review._

---

## 1. Purpose

Automate the repetitive, 30-60 min workflow RMS quoters perform for every new-venture trucking prospect:

1. Extract all underwriting data from the recorded call transcript.  
2. Apply RMS business rules (e.g., new ventures ⇒ “< 1 yr in business”; detect refrigerated cargo, Amazon work, etc.).  
3. Generate a filled PDF of the RMS **Trucking Quote Form**.  
4. Launch headless browsers, log in, and populate quote screens for:  
   - Progressive Commercial  
   - Geico Commercial  
   - Berkshire Hathaway GUARD  
   Stop at the premium display page; scrape the dollar amount.  
5. Compile an email with quote amounts, issues/notes, and attach the PDF.  
6. Send to: `cynthia@rmstruckers.co`, `liam@rmstruckers.com`.

Humans remain in-loop to create the Close CRM opportunity and verify data.

---

## 2. Interfaces

### 2.1 Inputs

| Field | Type | Description |
|-------|------|-------------|
| `call_transcript` | string (≈ 1–15 k tokens) | Verbatim transcript text from CRM. |
| `timestamp` | ISO-8601 | Call completion time (for filenames). |

### 2.2 Outputs

| Artifact | Format | Destination |
|----------|--------|-------------|
| Quote sheet | PDF (fillable form) | Email attachment |
| Carrier quote prices | JSON `{carrier: price}` | Email body & logs |
| Diagnostic log | JSON lines | S3 / object store |
| Screen captures | PNG | S3 (optional) |

---

## 3. Step Pipeline

> The tool is packaged as an **MCP server** exposing a single `generate_quotes` tool with the following internal steps.

| # | Step Id | Type | Description |
|---|---------|------|-------------|
| 1 | `extract_data` | LLM | Parse transcript → structured dict. |
| 2 | `enrich_logic` | LLM | Apply RMS heuristics & sanity checks. |
| 3 | `build_pdf` | Code | Fill Acrobat form, output PDF. |
| 4 | `quote_prog` | Browser | Playwright script, scrape price. |
| 5 | `quote_geico` | Browser | Playwright script, scrape price. |
| 6 | `quote_guard` | Browser | Playwright script, scrape price. |
| 7 | `compile_email` | LLM+Code | Draft body, attach PDF, embed prices. |
| 8 | `send_email` | Code | SES / SMTP send to recipients. |

### 3.1 Detailed Step Specs

#### 1. `extract_data`  –  LLM Prompt

_System_:  
```
You are an expert RMS intake assistant. Extract every data point needed to complete the “RMS Trucking Quote Form”. Return strict JSON following the provided schema.
```
_User_:  
```
<transcript>
{{call_transcript}}
</transcript>
```

**Expected schema** (partial):
```json
{
  "company": {
    "name": "", "address": "", "city": "", "state": "", "zip": "",
    "phone": "", "email": "", "dot": "", "mc": "", "ein": ""
  },
  "owner": {
    "name": "", "dob": "", "license_state": "", "license_no": "",
    "is_driver": true, "cdl": true, "cdl_year": 0
  },
  "operations": {
    "garaging_location": "", "goods_hauled": ["Refrigerated"], 
    "radius": "500", "eld": true, "amazon": false
  },
  "vehicles": [{...}],
  "drivers": [{...}],
  "coverage_prefs": {"liability": "", "cargo": "", "gl": ""}
}
```

#### 2. `enrich_logic` – Rules
* If DOT age ≤ 30 days ⇒ `"years_in_business": 0`  
* If `goods_hauled` includes *produce* or *frozen* ⇒ `"refrigerated_goods": true`  
* Default radius 500 mi if unspecified.  
* Normalize phone/email formats.

#### 3. `build_pdf`
* Template: updated PDF branded “Risk Management Strategies Corp”.  
* Use `pypdf` + `pdfrw` to map JSON values to AcroForm fields.  
* Output filename: `QuoteSheet_{{company.name | slug}}_{{timestamp}}.pdf`.

#### 4–6. Browser Automation

Common setup: Playwright (Chromium) in headless mode, Docker image with `--shm-size=2g`.

| Param | Progressive | Geico | Berkshire |
|-------|-------------|-------|-----------|
| Login URL | `https://foragents.progressivecommercial.com` | `https://partner.geico.com/...` | `https://www.guard.com/agents` |
| Credentials | ENV `PROG_USER/PASS` | `GEICO_USER/PASS` | `GUARD_USER/PASS` |
| End condition | Wait for selector containing `$` premium | Same | Same |
| Captured data | Premium text → float; screenshot | ... | ... |

All scripts must:
* Catch CAPTCHAs (alert ops via email)  
* Abort before final *Submit* button.  
* `await page.pdf()` if portal offers downloadable worksheet.

#### 7. `compile_email`

Prompt:
```
Write a concise email to RMS quoter summarizing carrier premiums.

Use this template:
Progressive: ${{prog}}
Geico: ${{geico}}
Berkshire Hathaway: ${{guard}}

Issues/Notes:
{{notes}}

Include a copy-paste block for Close CRM opportunity.
```
Attachment: generated PDF.

#### 8. `send_email`
* AWS SES or SendGrid, plain-text + attachment MIME.  
* To: Cynthia & Liam, cc: `quotes@rmstruckers.com`.  
* Subject: `Quote Results – {{company.name}} – {{date}}`.

---

## 4. Error Handling

| Failure | Action |
|---------|--------|
| Missing critical data in extraction | Email “Needs manual review” to quoter |
| Browser captcha / site down | Retry ×3 then alert |
| Premium not found | Include “N/A” and flag in email |
| Email send failure | Push to retry queue, escalate after 3 attempts |

---

## 5. Deployment Notes

* **Repo layout**  
  ```
  /server
    main.py  (FastAPI MCP)
    steps/
    playwright_scripts/
    templates/quote_form.pdf
  /Dockerfile
  ```
* Environment variables: carrier creds, SMTP keys, S3 bucket.  
* CI: GitHub Actions → Docker build → Render/Railway deploy (GPU not required).  
* Healthcheck: `GET /healthz` returns 200.

---

## 6. Security & Compliance

* PII encrypted in transit (HTTPS).  
* Logs redact SSN / license numbers.  
* Browser sessions run in isolated containers; credentials pulled from secrets manager.  
* Access limited to RMS IP ranges or VPN.

---

## 7. Future Enhancements

1. Auto-create Close CRM opportunity via Close API.  
2. Add additional carriers (Nationwide, Liberty).  
3. Feedback-loop to fine-tune extraction prompts on edge cases.  
4. Dashboard for quote throughput & success metrics.

---

_© 2025 Risk Management Strategies Corp – Internal Automation Specification_
