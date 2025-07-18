# RMS Quote-Automation Tool — **Completion Guide**
This guide contains **copy-paste-ready** content for every empty step generated by Relevance AI’s “Build-from-Prompt” wizard.  
Follow it top-to-bottom and your tool will be production-ready in <30 minutes.

---

## 0. Quick Setup
1. **Open** the generated tool `rms_generate_quotes` in Relevance AI.  
2. On the right-hand pane choose **“Dependencies”** and add:
   ```
   playwright==1.44.0
   pdfrw==0.4
   sendgrid==6.11.0
   ```
   Then add a Post-install command:  
   ```
   playwright install chromium
   ```
3. In **Workspace → Secrets** add:
   ```
   PROG_USER, PROG_PASS
   GEICO_USER, GEICO_PASS
   GUARD_USER, GUARD_PASS
   SENDGRID_KEY
   ```
4. Upload your blank **RMS Quote Form** PDF to *Files* and copy its **file-id** (looks like `file_abc123`). You’ll paste it in Step 3.

---

## 1. Input Definitions
| Input | Type | Example | Notes |
|-------|------|---------|-------|
| `call_transcript` | string | (paste full transcript) | Required |
| `progressive_commercial_login` | object | `{ "user": "", "pass": "" }` | Can be left blank—credentials come from secrets |
| `geico_commercial_login` | object | idem | optional |
| `berkshire_hathaway_guard_login` | object | idem | optional |

*(Leaving the login objects blank lets the **Code** steps read from environment secrets instead.)*

---

## 2. Step-by-Step Fill-ins

### 2.1 Extract Quote Data   *(LLM Step → “Prompt” field)*
```text
SYSTEM:
You are RMS’s intake assistant. Extract every data point required for the **RMS Trucking Quote Form** from the call transcript.  
Return STRICT JSON conforming to this schema (no extra keys, empty string if unknown):
{
  "company": {"name":"","address":"","city":"","state":"","zip":"","phone":"","email":"","dot":"","mc":"","ein":""},
  "owner": {"name":"","dob":"","license_state":"","license_no":"","is_driver":false,"cdl":false,"cdl_year":0},
  "operations": {"garaging_location":"","goods_hauled":[],"radius":"","eld":false,"amazon":false,"refrigerated":false,"years_in_business":0},
  "vehicles": [], "drivers": [],
  "coverage": {"liability":"","cargo":"","gl":""}
}

USER:
<transcript>
{{ call_transcript }}
</transcript>
```
Output variable: `json_data`

---

### 2.2 Apply Underwriting Rules   *(LLM Step)*
```text
SYSTEM:
Refine the extracted JSON using RMS underwriting heuristics.  
Rules:  
• If DOT age ≤ 30 days → "years_in_business": 0  
• If goods include *produce* or *frozen* → "refrigerated": true  
• Default "radius":"500" when blank.  
Return the **updated JSON only**.

USER:
{{ steps.extract_quote_data.json_data }}
```
Output variable: `enhanced_json`

---

### 2.3 Fill PDF Quote Form   *(Python Code Step)*
Paste entire block in **Code** and replace `<FILE_ID>` with your uploaded PDF id.
```python
import json, tempfile, datetime, os
from pdfrw import PdfReader, PdfWriter

data = json.loads(inputs["enhanced_json"])

TEMPLATE = "/workspace/files/<FILE_ID>"
tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

# Map JSON → PDF field names here
field_map = {
    "Company Name": data["company"]["name"],
    "Effective Date": datetime.date.today().isoformat(),
    "Address": data["company"]["address"],
    "City": data["company"]["city"],
    "State": data["company"]["state"],
    "Zip": data["company"]["zip"],
    "Phone #": data["company"]["phone"],
    "Email": data["company"]["email"],
    "DOT #": data["company"]["dot"],
    # (...add remaining mappings...)
}

pdf = PdfReader(TEMPLATE)
for page in pdf.pages:
    anns = page.Annots or []
    for a in anns:
        key = (a.T or "").strip("()")
        if key in field_map:
            a.V = field_map[key]
            a.AP = None

PdfWriter().write(tmp_path, pdf)

# Make path available to later steps
outputs["pdf_path"] = tmp_path
outputs["enhanced_json"] = inputs["enhanced_json"]
```

---

### 2.4 Scrape Progressive Premium   *(Python Code Step)*
```python
from playwright.sync_api import sync_playwright
import os, json, re

data = json.loads(inputs["enhanced_json"])
price = "N/A"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://foragents.progressivecommercial.com")
    page.fill("#username", os.environ["PROG_USER"])
    page.fill("#password", os.environ["PROG_PASS"])
    page.click("button[type=submit]")
    # TODO: navigate & fill quote form using `data`
    page.wait_for_selector("text=$")
    raw = page.inner_text("text=$")
    price = re.sub(r"[^\d.]", "", raw)
    browser.close()

outputs["prog_price"] = price
```
Add the same pattern for **Geico** and **GUARD** (change URLs, env vars, selectors).  
Set each step’s output var: `geico_price`, `guard_price`.

---

### 2.5 Draft Email Body   *(LLM Step)*
```text
SYSTEM:
Create a concise plain-text email for RMS quoters summarising carrier premiums and issues.

USER:
Company: {{ json.loads(steps.apply_underwriting_rules.enhanced_json).company.name }}

Progressive: ${{ steps.scrape_progressive_premium.prog_price }}
Geico: ${{ steps.scrape_geico_premium.geico_price }}
Berkshire Hathaway: ${{ steps.scrape_guard_premium.guard_price }}

Copy-paste for Close CRM:
Company: {{ json.loads(steps.apply_underwriting_rules.enhanced_json).company.name }}
Progressive: ${{ steps.scrape_progressive_premium.prog_price }}
Geico: ${{ steps.scrape_geico_premium.geico_price }}
BH GUARD: ${{ steps.scrape_guard_premium.guard_price }}
Status: Quoted (3)

Issues/Notes:
- Flag refrigerated goods if {{ json.loads(steps.apply_underwriting_rules.enhanced_json).operations.refrigerated }}
```
Output variable: `email_body`

---

### 2.6 Send Email   *(SendGrid Email Step)*
• **Account**: choose your connected SendGrid  
• **To email**: `cynthia@rmstruckers.co`, `liam@rmstruckers.com`  
• **Subject**:  
  ```
  Quote Results – {{ json.loads(steps.apply_underwriting_rules.enhanced_json).company.name }}
  ```  
• **Body**: `{{ steps.draft_email_body.email_body }}`  
• **Attachment**: add `{{ steps.fill_pdf_quote_form.pdf_path }}`

---

## 3. Testing Checklist
1. Click **Run Tool** → paste a sample transcript → Run.  
2. Confirm `json_data` & `enhanced_json` look correct.  
3. Temporarily skip carrier steps, ensure email arrives with PDF.  
4. Re-enable carriers one by one, validate scraped premiums.  
5. Celebrate a **30-60 min** time-savings per quote! 🎉

---

### Need Help?
Ping the assistant with any errors, screenshots, or questions.

.