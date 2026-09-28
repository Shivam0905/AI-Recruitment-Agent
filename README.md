# ⚡ TalentAgent AI: Autonomous Multi-Agent Recruitment Assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![AutoGen](https://img.shields.io/badge/orchestration-Microsoft%20AutoGen-purple.svg)](https://github.com/microsoft/autogen)
[![spaCy](https://img.shields.io/badge/NLP-spaCy%20v3-09A3D5.svg)](https://spacy.io/)
[![Streamlit](https://img.shields.io/badge/frontend-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Privacy](https://img.shields.io/badge/privacy-Multi--Tenant%20Isolated-success.svg)](#-enterprise-data-privacy--multi-tenancy)

An enterprise-grade autonomous recruitment platform powered by **Microsoft AutoGen**, **spaCy**, and **OpenAI GPT-4o-mini**. Specialized AI agents collaborate in a coordinated mesh to parse resumes, perform deterministic NLP skill verification, maintain isolated per-recruiter audit records, and synthesize high-signal technical interview strategies.

---

## 🏛️ System Architecture

```
                               ┌────────────────────────────────────────────────────────┐
                               │           🔐 Recruiter Authentication Gateway          │
                               │               (Gmail / Corporate Work Email)           │
                               └───────────────────────────┬────────────────────────────┘
                                                           │
                                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                           UserProxyAgent (Orchestrator)                                          │
│                   • Human Input Mode: NEVER (Automated Deterministic Production Execution)                        │
│                   • Programmatically Intercepts tool_calls & Executes Python Tools on Compute                     │
└───────────────────────────┬──────────────────────────────┬───────────────────────────────┬────────────────────────┘
                            │                              │                               │
                 1. Screening Task               2. Data Extraction Task           3. Interview Strategy Task
                            ▼                              ▼                               ▼
       ┌──────────────────────────────┐ ┌──────────────────────────────────────┐ ┌─────────────────────────────────┐
       │     Screening Assistant      │ │        Data Management Agent         │ │       Interview Strategist      │
       │ • pdfplumber Document Parser │ │ • Regex PII Parsing                  │ │ • Skill Gap Evaluation          │
       │ • spaCy Context Lemmatizer   │ │ • Strict Tenant-Partitioned Storage  │ │ • Evaluation Rubric Synthesis   │
       │ • C++ / C# Symbol Preserver  │ │ • PII De-Identification Shield       │ │ • Green/Red Flags + Depth Probe │
       │ • Deterministic Decision Gate│ │ • assets/users/{email}/candidates.csv│ │ • Live GPT-4o-mini or Offline   │
       └──────────────────────────────┘ └──────────────────────────────────────┘ └─────────────────────────────────┘
```

---

## ✨ Key Features

- **🔐 Multi-Tenant Authentication & Strict Database Isolation**:
  - Secure recruiter sign-in (Gmail or corporate email).
  - Every recruiter operates exclusively inside their own isolated database partition (`assets/users/{email}/candidates_database.csv`).
  - **Zero Cross-Tenant Data Leakage**: Users can only see, query, and export candidates evaluated under their own account.

- **🛡️ Automated PII De-Identification (Data Privacy Shield)**:
  - Built-in regex and NLP masking for candidate email addresses and phone numbers.
  - Aligns with **HIPAA**, **GDPR**, and **EEOC** non-bias hiring mandates.

- **📄 Layout-Aware Document Ingestion (`tools/parser.py`)**:
  - Employs `pdfplumber` to preserve visual column boundaries and eliminate horizontal text interleaving.
  - Supports both **PDF** and **DOCX** formats with null-safe stream handling.

- **🧠 spaCy Context-Aware Lemmatizer (`tools/keyword_matcher.py`)**:
  - Uses grammatical lemmatization (`token.lemma_`) instead of destructive algorithmic stemming.
  - **Technical Symbol Preservation**: Custom token filter preserves symbols in technical acronyms (e.g., `C++`, `C#`, `x86_64`, `CI/CD`), preventing standard `is_alpha` filters from corrupting technical keywords.

- **🎯 Rubric-Based Technical Interview Strategist (`tools/interview_generator.py`)**:
  - Synthesizes 5 structured scenario questions tailored to the candidate's verified competencies and identified gaps.
  - Generates actionable interview rubrics: **🟢 Positive Signals (Green Flags)**, **🔴 Warning Signs (Red Flags)**, and **🔍 Follow-up Depth Probes**.

- **⚡ Dual Runtime Engine (100% Offline by Default)**:
  - **Offline Mode**: Runs completely locally on CPU with zero internet egress costs, zero latency, and 100% data sovereignty.
  - **Online Cloud Mode**: Seamlessly activates live OpenAI GPT-4o-mini agents when an API key is provided.

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Agent Orchestration** | Microsoft AutoGen | Multi-agent coordination, tool execution mediation |
| **NLP Engine** | spaCy (`en_core_web_sm`) | Contextual lemmatization & token normalization |
| **Language Model** | OpenAI GPT-4o-mini | Live multi-agent reasoning & interview synthesis |
| **Document Parser** | `pdfplumber` & `docx2txt` | Layout-aware text extraction |
| **Web Interface** | Streamlit | Responsive recruiter web dashboard |
| **Persistence** | Tenant-Partitioned CSV | Isolated candidate audit records |

---

## 🚀 Quick Start Guide

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/Shivam0905/AI-Recruitment-Agent.git
cd AI-Recruitment-Agent

# Install dependencies
pip install -r requirements.txt

# Download spaCy English model (auto-downloads if missing)
python -m spacy download en_core_web_sm
```

### 2. Configuration (Optional for Live LLM Mode)

The system works **100% offline out-of-the-box** without any API key. If you wish to activate live GPT-4o-mini agents, configure `.env` in the project root:

```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key
```

*(Alternatively, you can paste your API key directly into the Web Dashboard sidebar at runtime).*

---

## 💻 Usage Options

### Option 1: Interactive Web Dashboard (Recommended)

Run the dashboard with Streamlit or double-click `run_web_app.bat`:

```bash
# From repository root:
streamlit run web_app.py
# or
py -m streamlit run web_app.py
```

Then open your browser to **`http://localhost:8501`**.

**Dashboard Features:**
1. **Recruiter Login**: Sign in with your Gmail or work email to mount your isolated database.
2. **Tab 1: Candidate Screening & Assessment**: Upload resumes, paste job descriptions, and view live multi-agent screening outcomes with candidate rubrics.
3. **Tab 2: Candidate Audit Database**: Search, filter, mask PII, and export your personal talent pool (`candidates_{email}.csv`).
4. **Tab 3: System Architecture & Engineering Suite**: Explore system architecture diagrams, enterprise domain adapters (Healthcare, Cloud, FinTech), and a technical interview cheatsheet.

---

### Option 2: Terminal / CLI Multi-Agent System

Run the AutoGen multi-agent system from the terminal or double-click `run_terminal_app.bat`:

```bash
cd AI-Recruitment-Agent
python app.py
```

The CLI will:
1. Extract candidate resume text from `assets/CV-English.pdf`.
2. Extract job requirements from `assets/job_description.txt`.
3. Orchestrate AutoGen agents across screening, persistence, and interview question synthesis.
4. Output structured screening results to the console.

---

### Option 3: Offline Pipeline Verification

Test the complete deterministic pipeline instantly with zero API keys:

```bash
cd AI-Recruitment-Agent
python demo_pipeline.py
```

---

## 📁 Repository Structure

```
AI-Recruitment-Agent/
├── app.py                      # Multi-Agent AutoGen orchestration CLI entrypoint
├── web_app.py                  # Interactive Streamlit recruiter dashboard
├── demo_pipeline.py            # Offline deterministic verification pipeline
├── requirements.txt            # Python dependencies
├── run_web_app.bat             # 1-click launcher for Web Dashboard
├── run_terminal_app.bat        # 1-click launcher for Terminal CLI
├── assets/                     # Input documents & database partitions
│   ├── CV-English.pdf          # Default sample technical resume
│   ├── job_description.txt     # Default sample job description
│   ├── candidates_database.csv # Base system audit storage
│   └── users/                  # Multi-tenant isolated recruiter databases
│       └── {sanitized_email}/  # Partitioned per recruiter account
│           └── candidates_database.csv
├── config/                     # AutoGen configuration
│   └── function_map.py         # Agent tool registration mappings
├── tools/                      # Specialized tool execution suite
│   ├── parser.py               # Layout-aware PDF/DOCX document parser
│   ├── keyword_matcher.py      # spaCy lemmatizer with technical symbol preservation
│   ├── interview_generator.py  # Adaptive 5-question interview strategist with rubrics
│   └── save_data.py            # Path-safe database persistence module
└── .streamlit/
    └── config.toml             # Enterprise light theme & server configuration
```

---

## 🔒 Enterprise Data Privacy & Multi-Tenancy

In multi-user or cloud deployments, data privacy is paramount:
1. **Zero Cross-Tenant Leakage**: Candidate profiles evaluated by Recruiter A are stored in `assets/users/recruiter_a/` and cannot be accessed, queried, or exported by Recruiter B.
2. **Built-in PII De-Identification**: Automated PII masking dynamically de-identifies candidate email addresses and phone numbers before rendering or downstream export, complying with **HIPAA**, **GDPR**, and **EEOC** non-bias mandates.
3. **Audit Trail Integrity**: All hiring screening rationales, match ratios, and timestamps are recorded in immutable audit logs.

---

## 📄 License & Acknowledgments

- Built with [Microsoft AutoGen](https://github.com/microsoft/autogen).
- NLP powered by [spaCy](https://spacy.io/).
- PDF extraction via [pdfplumber](https://github.com/jsvine/pdfplumber).
- Licensed under the **MIT License**.
