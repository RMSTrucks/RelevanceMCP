# RMS Quote-Automation Tool – Relevance AI Implementation Guide  
*File: `relevance_ai_tool_implementation.md`*  

This guide walks you (Jake) through creating the **RMS Quote-Automation** tool entirely inside Relevance AI.  
You will copy-and-paste each block into the Tool Builder UI.

---

## 0. Prerequisites

| Item | Notes |
|------|-------|
| Relevance AI workspace | Owner access to create tools & secrets |
| Playwright headless browsers | Relevance “Code Step” runtime supports pip installs |
| Carrier credentials | Store as **workspace secrets**<br>`PROG_USER / PROG_PASS`<br>`GEICO_USER / GEICO_PASS`<br>`GUARD_USER / GUARD_PASS` |
| Email service key | e.g. SendGrid API key → secret `SENDGRID_KEY` |
| RMS PDF template | Upload `rms_quote_form.pdf` to Relevance File Storage; note the file id |

---

## 1. Create the Tool Shell

1. Navigate to **Tools → New Tool**  
2. Name: `rms_generate_quotes`  
3. Description: “Extract data from call transcript, auto-quote Progressive / Geico / Berkshire, produce PDF & email to RMS quoters.”  
4. Leave Auth blank (internal use only)  
5. Click **Add Step** and follow the sequence below.

---

## 2. Step-by-Step Configuration

> Each block shows **(Type)**, **Name**, config fields and copy-pastes.

### Step 1 – Extract Data  
**Type:** LLM  
**Name:** `extract_data`

Prompt (paste into “System + User”):

```
SYSTEM:
You are RMS’s intake assistant. Extract every data point required to complete the RMS Trucking Quote Form. 
Return JSON that strictly matches the provided schema. If data missing, set value "".

JSON schema:
{
  company:{name:"",address:"",city:"",state:"",zip:"",phone:"",email:"",dot:"",mc:"",ein:""},
  owner:{name:"",dob:"",license_state:"",license_no:"",is_driver:false,cdl:false,cdl_year:0},
  operations:{garaging_location:"",goods_hauled:[],radius:"",eld:false,amazon:false,refrigerated:false,years_in_business:0},
  vehicles:[], drivers:[],
  coverage:{liability:"",cargo:"",gl:""}
}

USER:
<transcript>
{{inputs.call_transcript}}
</transcript>
```

Outputs ➜ `json_data`

---

### Step 2 – Enrich Logic  
**Type:** LLM  
**Name:** `enrich_logic`

Prompt:

```
SYSTEM:
Apply RMS underwriting heuristics to the JSON below and output an updated JSON.

Rules:
- If DOT age ≤ 30 days ➔ years_in_business = 0
- If goods hauled indicate produce/frozen ➔ refrigerated = true
- Default radius "500" if empty.

USER:
{{steps.extract_data.json_data}}
```

Outputs ➜ `enhanced_json`

---

### Step 3 – Build PDF  
**Type:** Code  
**Name:** `build_pdf`  
Language: Python

```python
import json, tempfile, subprocess, os, datetime
from pdfrw import PdfReader, PdfWriter, PageMerge

data = json.loads(inputs["enhanced_json"])
template_path = "/workspace/files/{{your_file_id_here}}"  # replace with actual file id
output_name = f"QuoteSheet_{data['company']['name'].replace(' ','_')}_{datetime.date.today()}.pdf"
tmp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name

pdf = PdfReader(template_path)
# --- map fields (simplified) ---
field_map = {
    "Company Name": data["company"]["name"],
    "Address": data["company"]["address"],
    "City": data["company"]["city"],
    # add remaining mappings...
}
for page in pdf.pages:
    annotations = page.Annots or []
    for a in annotations:
        if a.T and a.T[1:-1] in field_map:
            a.V = field_map[a.T[1:-1]]
            a.AP = None
PdfWriter().write(tmp_pdf, pdf)

outputs["pdf_path"] = tmp_pdf
outputs["enhanced_json"] = inputs["enhanced_json"]
```

Add `pdfrw` to “Python libraries”.

---

### Step 4 – Quote Progressive  
**Type:** Code  
**Name:** `quote_prog`

```python
from playwright.sync_api import sync_playwright
import json, os

data = json.loads(inputs["enhanced_json"])
price = "N/A"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://foragents.progressivecommercial.com")
    page.fill("#username", os.environ["PROG_USER"])
    page.fill("#password", os.environ["PROG_PASS"])
    page.click("button[type=submit]")
    # … navigate & fill form using `data` …
    page.wait_for_selector(".premium-amount")
    price = page.text_content(".premium-amount").strip().replace("$","").replace(",","")
    browser.close()

outputs["prog_price"] = price
```

Add Playwright to libs and include `playwright install chromium` in post-install.

Duplicate Step 4 for **Geico** (`quote_geico`) and **Berkshire** (`quote_guard`), adjusting URLs, selectors, env vars, output keys `geico_price`, `guard_price`.

---

### Step 7 – Compile Email  
**Type:** LLM  
**Name:** `compile_email`

Prompt:

```
SYSTEM:
Compose a concise plain-text email for RMS quoters summarizing quote results.

USER:
Company: {{json.loads(inputs.enhanced_json).company.name}}

Progressive: ${{steps.quote_prog.prog_price}}
Geico: ${{steps.quote_geico.geico_price}}
Berkshire Hathaway: ${{steps.quote_guard.guard_price}}

Provide:
1. Copy-paste block for Close CRM
2. Issues/Notes based on blank values or refrigerated flag.
```

Outputs ➜ `email_body`

---

### Step 8 – Send Email  
**Type:** Code  
**Name:** `send_email`

```python
import sendgrid, base64, os
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

sg = sendgrid.SendGridAPIClient(os.environ["SENDGRID_KEY"])
with open(inputs["pdf_path"], "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

att = Attachment(
    FileContent(encoded),
    FileName("QuoteSheet.pdf"),
    FileType("application/pdf"),
    Disposition("attachment")
)

message = Mail(
    from_email="no-reply@rmstruckers.com",
    to_emails=["cynthia@rmstruckers.co","liam@rmstruckers.com"],
    subject=f"Quote Results – {json.loads(inputs['enhanced_json'])['company']['name']}",
    plain_text_content=inputs["email_body"]
)
message.attachment = att
sg.send(message)
outputs["status"] = "sent"
```

---

## 3. Connect the Flow

In the **Tool Builder** canvas drag arrows:

`extract_data → enrich_logic → build_pdf → quote_prog → quote_geico → quote_guard → compile_email → send_email`

Ensure each step passes needed outputs via “Variables”.

---

## 4. Secrets & Libs

Settings → **Environment**  
```
PROG_USER, PROG_PASS
GEICO_USER, GEICO_PASS
GUARD_USER, GUARD_PASS
SENDGRID_KEY
```
Libraries:  
```
playwright==1.44.0
pdfrw==0.4
sendgrid==6.11.0
```
**Post-install script:** `playwright install chromium`

---

## 5. Testing

1. Use a **sample transcript** input (paste in Run panel).  
2. Verify JSON extraction looks correct (toggle “Outputs”).  
3. Temporarily disable browser steps to debug email render.  
4. Re-enable carriers one-by-one.  
5. Confirm Cynthia & Liam receive the PDF with prices.

---

## 6. Deployment & Usage

Once tests pass:  
• Click **Publish Tool**  
• Share internal URL with quoters – they paste transcript; tool emails them results within ~3 min.  
• Future upgrade: call this tool automatically from CRM webhook.

---

### Done!  
You now have a native Relevance AI tool that slashes 30-60 min of manual work per quote while keeping humans in control.
