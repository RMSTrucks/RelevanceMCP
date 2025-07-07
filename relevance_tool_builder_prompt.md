# Prompt for Relevance AI Tool Builder  
Create a fully-functional tool named **`rms_generate_quotes`** that automates RMS’s trucking-insurance quote workflow.

---

## 1. Purpose  
Automate the 30-60 min manual workflow RMS quoters perform for every new-venture trucking prospect:

1. Take a **call transcript** as input.  
2. Extract all data needed for the “RMS Trucking Quote Form”.  
3. Apply basic RMS underwriting heuristics.  
4. Generate a filled PDF quote sheet.  
5. Launch headless browsers, log in, and fill quote pages for **Progressive Commercial, Geico Commercial, Berkshire Hathaway GUARD**.  
   • Stop at the premium page, never click *Submit*.  
   • Scrape the displayed dollar amount.  
6. Email Cynthia and Liam the PDF plus a plain-text summary of carrier premiums.

Humans will review and enter the opportunity in Close CRM.

---

## 2. Inputs  
| name | type | description | required |
|------|------|-------------|----------|
| `call_transcript` | string | Raw transcript text of the phone interview | yes |

---

## 3. Outputs  
1. **Email** → `cynthia@rmstruckers.co`, `liam@rmstruckers.com`  
   • Subject: `Quote Results – <Company>`  
   • Body template:  
     ```
     Progressive: $<prog>
     Geico: $<geico>
     Berkshire Hathaway: $<guard>

     [Copy-paste block for Close CRM]

     Issues/Notes:
     - ...
     ```  
   • Attachment: filled PDF quote sheet.  
2. **Logs**: JSON including scraped premiums and any errors.

---

## 4. Step Pipeline  
Create these steps in order and connect outputs → inputs.

| # | Step id | Type | Key details |
|---|---------|------|-------------|
| 1 | `extract_data` | LLM | Parse transcript → strict JSON (see schema below). |
| 2 | `enrich_logic` | LLM | Apply rules: new DOT ⇒ years_in_business 0; produce/frozen ⇒ refrigerated true; default radius 500 mi. |
| 3 | `build_pdf` | Code | Use uploaded template `rms_quote_form.pdf`; fill AcroFields; output temp PDF. |
| 4 | `quote_prog` | Code (Playwright) | Login with `PROG_USER/PASS`, fill quote, wait selector `.premium-amount`, scrape price. |
| 5 | `quote_geico` | Code (Playwright) | Same pattern with `GEICO_USER/PASS`. |
| 6 | `quote_guard` | Code (Playwright) | Same pattern with `GUARD_USER/PASS`. |
| 7 | `compile_email` | LLM | Draft email body using scraped prices & notes. |
| 8 | `send_email` | Code | Send via SendGrid using `SENDGRID_KEY`. |

### JSON schema for steps 1–2  
```
{
  company:{name:"",address:"",city:"",state:"",zip:"",phone:"",email:"",dot:"",mc:"",ein:""},
  owner:{name:"",dob:"",license_state:"",license_no:"",is_driver:false,cdl:false,cdl_year:0},
  operations:{garaging_location:"",goods_hauled:[],radius:"",eld:false,amazon:false,refrigerated:false,years_in_business:0},
  vehicles:[], drivers:[],
  coverage:{liability:"",cargo:"",gl:""}
}
```

---

## 5. Secrets & Environment  
```
PROG_USER, PROG_PASS
GEICO_USER, GEICO_PASS
GUARD_USER, GUARD_PASS
SENDGRID_KEY
```

---

## 6. Python Libraries  
```
playwright==1.44.0
pdfrw==0.4
sendgrid==6.11.0
```
Post-install command: `playwright install chromium`

---

## 7. Error Handling  
* If critical data missing ⇒ email “Needs manual review”.  
* On CAPTCHA or site failure ⇒ retry 3× then include “N/A” in results and flag note.  
* Email send failure ⇒ retry queue 3× then alert.

---

## 8. Success Criteria  
• Email arrives with PDF + three dollar amounts inside 5 min.  
• Browsers never advance past quote screen.  
• Logs redact PII and store success/failure for each carrier.

---

**Build this tool now, exposing a single public endpoint that accepts `call_transcript` and triggers the pipeline.**
