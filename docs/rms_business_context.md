# RMS – Business Context & Operations Overview
*Prepared 2025-07-07*

---

## 1. Company Snapshot
| Key | Detail |
|-----|--------|
| Legal name | **Risk Management Strategies Corp** (RMS) |
| Industry | Trucking insurance & compliance services |
| Core offer | Commercial auto / motor-carrier policies for new-venture trucking companies (“pre-truckers”) |
| Geographic focus | United States |
| Differentiator | Proactive outreach to brand-new DOT registrants; fast quote turnaround; planned AI-powered compliance add-ons |

---

## 2. Team Structure
| Role | Name / Contact | Responsibilities |
|------|----------------|------------------|
| Founder / System Architect | **Jake Deaton** | Vision, platform design, automation strategy |
| Quoter | **Cynthia** – cynthia@rmstruckers.co | Cold-calling, information intake, quote generation |
| Quoter | **Liam** – liam@rmstruckers.com | Same as above |
| Sales Department | Multiple agents | Converts approved quotes to bound policies, customer success |
| Future roles | Compliance coaches, platform support | To be staffed as platform grows |

---

## 3. Current Quote Workflow (Manual)
1. **Lead Generation**  
   • Dialer system calls newly issued DOT numbers (same-day / next-day).  
2. **Interview / Data Capture**  
   • Quoter questions prospect and fills the “RMS Trucking Quote Form” PDF (company, owner, vehicles, drivers, operations).  
   • Call is recorded & auto-transcribed by Close CRM.  
3. **File Storage**  
   • Completed PDF saved to a shared drive folder.  
4. **Carrier Webforms**  
   • Quoter logs into **Progressive Commercial**, **Geico Commercial**, **Berkshire Hathaway GUARD** portals.  
   • Manually re-types all data; applies judgment for fields not asked during call (e.g., “years in business” = 0 for new ventures).  
   • Stops at the premium screen; records quote amount.  
   · Time spent here: **10-20 min per carrier → 30-60 min per prospect**.  
5. **CRM Entry**  
   • Creates “Quote” opportunity in **Close CRM**.  
   • Marks status = *Quoted*; notes carrier names & premiums; assigns salesperson.  
6. **Sales Handoff**  
   • Sales team follows up, negotiates, binds coverage.

---

## 4. Pain Points & Inefficiencies
| Area | Issue | Impact |
|------|-------|--------|
| Duplicate data entry | Same info typed into 3 portals | Wasted time, typos |
| Quote latency | 30-60 min delays | Fewer daily quotes, missed leads |
| Context switching | Multiple systems (dialer, PDF, portals, CRM) | User fatigue, training overhead |
| Tracking | Premiums noted only in free-text CRM notes | Hard to report conversion metrics |
| Scalability | Quoter capacity limited to ~10 complete quotes / day | Growth bottleneck |

---

## 5. Business Goals (12-month horizon)
1. **Efficiency** – Cut quote generation time from 30-60 min → **< 5 min** with AI automation.  
2. **Volume** – Reach **100 successful registrations in 100 days**; scale quoting capacity 5× without extra headcount.  
3. **Platform Expansion** – Launch integrated **Registration & Compliance** service that feeds warm insurance leads.  
4. **Data Quality** – Structured capture of quote data for analytics (conversion, pricing trends).  
5. **User Experience** – Provide prospects with faster, clearer quote options; improve close rate.

Key KPIs:  
`Quotes / day`, `Quote-to-bind ratio`, `Average handle time`, `Customer satisfaction`, `Time-to-compliance completion`.

---

## 6. Technology & Tools in Use
- **Close CRM** – lead dialer, call recording, transcription, opportunity tracking.  
- **Shared Drive** – quote PDFs storage.  
- **Carrier Portals** – Progressive, Geico, Berkshire GUARD.  
- **Relevance AI** – vector knowledge, agent & tool platform (current automation initiative).  
- **Playwright / Python** (planned) – human-like browser automation for carrier quotes.  
- **GitHub** – source & knowledge repositories (`KDS`, MCP servers).  
- **Hybrid Tool-Building Methodology** – Design → Prompt → Auto-Generate → Polish.

---

## 7. Automation Vision
1. **Transcript-Driven Intake**  
   Call transcript → LLM extraction → structured JSON → auto-filled PDF.
2. **Human-like Browser Automation**  
   Playwright scripts log in, populate carrier forms, stop at premium page.
3. **Instant Email Summary**  
   Email Cynthia & Liam with PDF + premium table for review.
4. **CRM Enrichment**  
   Future: auto-create Close opportunity via API.
5. **Compliance Platform Synergy**  
   Data flows into FMCSA registration agent, creating cross-sell opportunities.

---

## 8. Strategic Roadmap
| Phase | Milestone | Target Date |
|-------|-----------|-------------|
| P0 | Quote-Automation Tool live (internal) | Q3 2025 |
| P1 | Close CRM auto-integration | Q4 2025 |
| P2 | Full Registration/Compliance agent | Q1 2026 |
| P3 | Multi-carrier expansion (Nationwide, Liberty) | 2026 |
| P4 | Marketplace of cognitive agents for trucking ecosystem | 2027 |

---

## 9. Glossary
| Term | Definition |
|------|------------|
| **Pre-trucker** | Prospect that has applied for DOT but not yet operational |
| **Quoter** | RMS employee who collects risk data and obtains premiums |
| **Hybrid Method** | Design ⇒ Prompt ⇒ Auto-Generate ⇒ Polish workflow for Relevance AI tools |
| **MCP** | Model Context Protocol – standard for tool access by LLM agents |

---

*Document owner: Jake Deaton – please PR updates as processes evolve.*  
