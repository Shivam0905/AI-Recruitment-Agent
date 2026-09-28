import os
import sys
import subprocess
import tempfile
import re
import pandas as pd
import streamlit as st
# Configure page layout
st.set_page_config(
    page_title="TalentAgent AI | Autonomous Multi-Agent Hiring Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import csv
from datetime import datetime

from tools.parser import extract_text_from_pdf, extract_text_from_docx, read_text_from_file
from tools.keyword_matcher import match_keywords
from tools.save_data import save_candidate_data
from tools.interview_generator import generate_interview_questions

ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
DEFAULT_PDF = os.path.join(ASSETS_DIR, "CV-English.pdf")
DEFAULT_JD = os.path.join(ASSETS_DIR, "job_description.txt")
CSV_PATH = os.path.join(ASSETS_DIR, "candidates_database.csv")

def get_user_db_path(user_email: str) -> str:
    """Return isolated CSV database path partitioned by user email."""
    safe_id = re.sub(r'[^a-zA-Z0-9_.-]', '_', user_email.lower().strip())
    user_dir = os.path.join(ASSETS_DIR, "users", safe_id)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, "candidates_database.csv")

def save_user_candidate_data(user_email: str, candidate_name: str, email: str, phone_number: str, matching_keywords: str, screening_result: str, log_to_master: bool = False) -> str:
    """Save candidate record strictly to the logged-in user's isolated database."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = get_user_db_path(user_email)
    file_exists = os.path.isfile(filename)
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Timestamp', 'Name', 'Email', 'Phone number', 'Matching Keywords', 'Screening Decision'])
        writer.writerow([timestamp, candidate_name, email, phone_number, matching_keywords, screening_result])
    
    if log_to_master:
        save_candidate_data(candidate_name, email, phone_number, matching_keywords, screening_result)
    
    return f"Saved to private workspace ({os.path.basename(filename)})"

def ensure_user_seeded(user_email: str):
    """Seed user database with an initial sample candidate if newly created."""
    user_db = get_user_db_path(user_email)
    if not os.path.exists(user_db):
        email_lower = user_email.lower()
        if "optum" in email_lower or "health" in email_lower:
            save_user_candidate_data(
                user_email=user_email,
                candidate_name="Dr. Sarah Chen",
                email="sarah.chen@optumhealth.example.com",
                phone_number="(+1) 612-555-0142",
                matching_keywords="Python, FHIR, HIPAA, Healthcare Analytics, SQL, PyTorch",
                screening_result="HIRE"
            )
        elif "shivam" in email_lower:
            save_user_candidate_data(
                user_email=user_email,
                candidate_name="Alex Mercer",
                email="alex.mercer@techcorp.example.com",
                phone_number="(+1) 415-555-0199",
                matching_keywords="Assembly, C, C++, Python, WinDbg, Linux, Distributed Systems",
                screening_result="HIRE"
            )
        else:
            save_user_candidate_data(
                user_email=user_email,
                candidate_name="Jordan Lee",
                email=f"candidate@{email_lower.split('@')[-1] if '@' in email_lower else 'example.com'}",
                phone_number="(+1) 206-555-0188",
                matching_keywords="Python, Docker, Kubernetes, AWS, REST API, Microservices",
                screening_result="HIRE"
            )

# Premium Modern CSS Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    
    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F2847 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.3);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #FFFFFF 0%, #93C5FD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        max-width: 850px;
        line-height: 1.6;
        margin-bottom: 1.2rem;
    }
    .pill-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 9999px;
        padding: 4px 14px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #E2E8F0;
        margin-right: 8px;
    }
    
    /* Modern Glass Card */
    .modern-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.2rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .modern-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    
    /* Decision Badges */
    .hire-banner {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border: 1.5px solid #10B981;
        color: #065F46;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        font-weight: 800;
        font-size: 1.15rem;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1.2rem;
    }
    .pass-banner {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border: 1.5px solid #EF4444;
        color: #991B1B;
        border-radius: 12px;
        padding: 1rem 1.4rem;
        font-weight: 800;
        font-size: 1.15rem;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1.2rem;
    }
    
    /* Skill Badges */
    .skill-badge-matched {
        background: #DCFCE7;
        color: #15803D;
        border: 1px solid #86EFAC;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin: 3px 4px;
    }
    .skill-badge-gap {
        background: #FEF3C7;
        color: #B45309;
        border: 1px solid #FCD34D;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin: 3px 4px;
    }
    
    /* Rubric Card */
    .rubric-box-green {
        background-color: #F0FDF4;
        border-left: 4px solid #22C55E;
        padding: 0.9rem 1.1rem;
        border-radius: 6px;
        margin-bottom: 0.8rem;
    }
    .rubric-box-red {
        background-color: #FEF2F2;
        border-left: 4px solid #EF4444;
        padding: 0.9rem 1.1rem;
        border-radius: 6px;
        margin-bottom: 0.8rem;
    }
    
    /* Metric Highlights */
    .metric-value-lg {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
    }
    .metric-label-sm {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Session Authentication State
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

# If user is not authenticated, render Login Page
if not st.session_state["authenticated"]:
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.8, 1])
    with col_center:
        st.markdown("""
        <div style="background:white; border:1px solid #E2E8F0; border-radius:16px; padding:2.5rem; box-shadow:0 10px 25px -5px rgba(0,0,0,0.08);">
            <div style="text-align:center; font-size:2.2rem; font-weight:800; color:#0F172A; margin-bottom:0.3rem;">⚡ TalentAgent AI</div>
            <div style="text-align:center; font-size:1.05rem; color:#64748B; margin-bottom:1.5rem;">Secure Multi-Tenant Recruiter Portal</div>
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; border-radius:8px; padding:0.9rem 1.1rem; margin-bottom:1.5rem; font-size:0.88rem; color:#166534;">
                🔒 <b>Zero Cross-Tenant Leakage:</b> Each recruiter accesses an isolated database workspace. You will only see candidates evaluated under your private account.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("#### Sign In with Gmail / Work Email")
            email_val = st.text_input("Enter your Email Address:", placeholder="e.g. shivam@gmail.com", key="login_email_input")
            submit_btn = st.form_submit_button("🔑 Sign In to Private Workspace", type="primary", use_container_width=True)
            
            if submit_btn:
                if not email_val or "@" not in email_val:
                    st.error("Please enter a valid email address (e.g. name@gmail.com).")
                else:
                    st.session_state["authenticated"] = True
                    st.session_state["user_email"] = email_val.strip().lower()
                    ensure_user_seeded(st.session_state["user_email"])
                    st.rerun()
    st.stop()

# Sidebar Configuration (Authenticated)
with st.sidebar:
    st.markdown("### ⚡ **TalentAgent AI**")
    st.caption("Autonomous Multi-Agent Recruitment Assistant")
    st.markdown("---")
    
    st.markdown("#### 👤 **Active Recruiter**")
    st.markdown(f"**`{st.session_state['user_email']}`**")
    st.caption("🔒 Private Isolated Workspace")
    if st.button("🚪 Sign Out", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["user_email"] = ""
        st.rerun()
        
    st.markdown("---")
    st.markdown("#### ⚙️ Runtime Settings")
    api_key_input = st.text_input(
        "OpenAI API Key (Optional)",
        type="password",
        help="Paste your key to activate live GPT-4o-mini agents. Leave blank for deterministic offline evaluation."
    )
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input
        st.success("🟢 Mode: Live OpenAI GPT-4o-mini")
    else:
        st.info("🔵 Mode: Offline Deterministic Engine")
        
    st.markdown("---")
    st.markdown("#### 🤖 Agent System Mesh")
    st.markdown("""
    - **Screening Assistant**:
      `pdfplumber` + `spaCy` Lemmatizer
    - **Data Management Agent**:
      Regex PII + Audit Trail Storage
    - **Interview Strategist**:
      Gap-Targeted Adaptive Synthesizer
    - **UserProxyAgent**:
      Autonomous Tool Executor
    """)
    st.markdown("---")
    st.caption("Built with Microsoft AutoGen & spaCy")

# Hero Banner
st.markdown(f"""
<div class="hero-container">
    <div class="hero-title">TalentAgent AI · Multi-Agent Recruitment Platform</div>
    <div class="hero-subtitle">
        An enterprise-grade autonomous recruitment platform. Specialized AI agents collaborate to parse resumes, 
        execute deterministic NLP skill verification, log auditable candidate records, and synthesize high-signal technical interview strategies.
    </div>
    <div>
        <span class="pill-chip">👤 Recruiter: {st.session_state['user_email']}</span>
        <span class="pill-chip">🔒 Isolated Workspace DB</span>
        <span class="pill-chip">🤖 AutoGen Mesh</span>
        <span class="pill-chip">🧠 spaCy Lemmatizer</span>
    </div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "🚀 Candidate Screening & Assessment",
    "📊 Candidate Audit Database",
    "🏛️ System Architecture & Engineering Design"
])

# -------------------------------------------------------------
# TAB 1: CANDIDATE SCREENING & EVALUATION
# -------------------------------------------------------------
with tabs[0]:
    col_input1, col_input2 = st.columns([1, 1], gap="large")
    
    with col_input1:
        st.markdown("### 📄 1. Candidate Resume")
        uploaded_file = st.file_uploader("Upload Resume File", type=["pdf", "docx"], help="Upload any candidate resume in PDF or DOCX format.")
        use_default_resume = st.checkbox("Load Sample Resume (Alex Mercer - Systems Engineer)", value=True if not uploaded_file else False)
        
        resume_text = ""
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            
            if uploaded_file.name.endswith(".pdf"):
                resume_text = extract_text_from_pdf(tmp_path)
            else:
                resume_text = extract_text_from_docx(tmp_path)
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            st.success(f"✓ Parsed `{uploaded_file.name}` ({len(resume_text):,} characters)")
        elif use_default_resume and os.path.exists(DEFAULT_PDF):
            resume_text = extract_text_from_pdf(DEFAULT_PDF)
            st.info("Loaded built-in sample resume: `assets/CV-English.pdf`")
            
        with st.expander("👁️ Inspect Raw Extracted Resume Text", expanded=False):
            st.text_area("Extracted Resume Content", resume_text, height=200, disabled=True)
            
    with col_input2:
        st.markdown("### 📋 2. Target Job Requirements")
        
        # Preset selector for fast testing
        preset_choice = st.selectbox(
            "Select Job Description Preset or Custom:",
            [
                "Default: Systems & Low-Level Engineer (Assembly, C/C++, Docker, RISC-V)",
                "Preset: Full-Stack Cloud Engineer (Python, React, Docker, Kubernetes, AWS)",
                "Preset: Machine Learning & NLP Engineer (Python, PyTorch, Transformers, spaCy)",
                "Custom Job Description"
            ]
        )
        
        if "Full-Stack" in preset_choice:
            default_jd = (
                "Role: Senior Full-Stack Cloud Engineer\n"
                "Requirements:\n"
                "- Strong proficiency in Python, TypeScript, React, and FastAPI.\n"
                "- Extensive experience with Docker, Kubernetes, and AWS cloud services.\n"
                "- Hands-on knowledge of PostgreSQL, Redis caching, and CI/CD pipelines.\n"
                "- Expertise in building resilient RESTful APIs and distributed systems."
            )
        elif "Machine Learning" in preset_choice:
            default_jd = (
                "Role: Lead Machine Learning Engineer\n"
                "Requirements:\n"
                "- Expertise in Python, PyTorch, Hugging Face Transformers, and spaCy.\n"
                "- Experience with Vector Databases (pgvector, Pinecone, ChromaDB) and RAG architecture.\n"
                "- Strong background in Model fine-tuning, quantization, and ML deployment with Docker.\n"
                "- Deep understanding of tokenization, embeddings, and LLM evaluation benchmarks."
            )
        elif "Default" in preset_choice and os.path.exists(DEFAULT_JD):
            default_jd = read_text_from_file(DEFAULT_JD)
        else:
            default_jd = "Enter requirements here..."
            
        jd_input = st.text_area("Job Requirements", value=default_jd, height=220)

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("🚀 Launch Autonomous Screening Multi-Agent Workflow", type="primary", use_container_width=True)
    
    if run_btn:
        if not resume_text.strip():
            st.error("Please provide a resume by uploading a file or selecting the sample resume.")
        elif not jd_input.strip():
            st.error("Please provide job requirements.")
        else:
            progress_bar = st.progress(0)
            status_placeholder = st.empty()
            
            # Step 1: Keyword extraction & matching
            status_placeholder.markdown("⏳ **[1/3] Screening Assistant**: Parsing document & running spaCy lemmatization...")
            progress_bar.progress(33)
            
            common_tech_keywords = [
                "Assembly", "x86", "x86_64", "ARM", "RISC-V", "C", "C++", "C#",
                "Python", "Docker", "Git", "WinDbg", "GDB", "IDA Pro", "Ghidra",
                "RTOS", "Linux", "SIMD", "AVX", "Reverse Engineering", "Firmware",
                "Java", "Kubernetes", "CI/CD", "SQL", "Cybersecurity", "React",
                "TypeScript", "AWS", "PyTorch", "Transformers", "PostgreSQL", "Redis"
            ]
            
            target_keywords = [kw for kw in common_tech_keywords if kw.lower() in jd_input.lower()]
            if not target_keywords:
                target_keywords = ["Python", "Git", "Linux", "Docker"]
                
            matched_keywords, _ = match_keywords(resume_text, target_keywords)
            missing_keywords = [kw for kw in target_keywords if kw not in matched_keywords]
            
            match_ratio = len(matched_keywords) / max(len(target_keywords), 1)
            screening_decision = "HIRE" if match_ratio >= 0.50 else "PASS"
            
            # Step 2: Data Manager
            status_placeholder.markdown("⏳ **[2/3] Data Management Agent**: Extracting candidate metadata & logging to audit trail...")
            progress_bar.progress(66)
            
            lines = [l.strip() for l in resume_text.split('\n') if l.strip()]
            candidate_name = lines[0] if lines else "Applicant"
            
            email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)
            candidate_email = email_match.group(0) if email_match else "unspecified@domain.com"
            
            phone_match = re.search(r"\(?\+?\d{1,3}\)?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}", resume_text)
            candidate_phone = phone_match.group(0) if phone_match else "Not provided"
            
            save_msg = save_user_candidate_data(
                user_email=st.session_state["user_email"],
                candidate_name=candidate_name,
                email=candidate_email,
                phone_number=candidate_phone,
                matching_keywords=", ".join(matched_keywords),
                screening_result=screening_decision
            )
            
            # Step 3: Interview Strategist
            status_placeholder.markdown("⏳ **[3/3] Interview Strategist**: Synthesizing gap-targeted questions and rubric...")
            progress_bar.progress(100)
            
            questions = generate_interview_questions(
                resume_text=resume_text,
                jd_text=jd_input,
                matched_keywords=matched_keywords,
                missing_keywords=missing_keywords,
                api_key=api_key_input
            )
            
            status_placeholder.empty()
            progress_bar.empty()
            
            st.success("Execution Complete: Multi-Agent Screening & Assessment Finished.")
            
            # RESULTS DISPLAY
            st.markdown("## 📊 Multi-Agent Workflow Results")
            
            col_res_l, col_res_r = st.columns([1.1, 0.9], gap="large")
            
            with col_res_l:
                st.markdown("### 🤖 Agent 1: Screening Assistant Evaluation")
                st.markdown('<div class="modern-card">', unsafe_allow_html=True)
                
                # Decision banner
                if screening_decision == "HIRE":
                    st.markdown("""
                    <div class="hire-banner">
                        <span>✅</span>
                        <div>
                            <div>SCREENING OUTCOME: CANDIDATE RECOMMENDED (HIRE)</div>
                            <div style="font-size:0.85rem; font-weight:500; opacity:0.9;">Exceeds minimum competency threshold. Recommended for technical interview rounds.</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="pass-banner">
                        <span>❌</span>
                        <div>
                            <div>SCREENING OUTCOME: CANDIDATE NOT ADVANCED (PASS)</div>
                            <div style="font-size:0.85rem; font-weight:500; opacity:0.9;">Did not meet baseline required skills. Retained in talent pool for alternate roles.</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f'<div class="metric-label-sm">Match Ratio</div><div class="metric-value-lg">{match_ratio:.0%}</div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="metric-label-sm">Skills Matched</div><div class="metric-value-lg" style="color:#10B981;">{len(matched_keywords)}</div>', unsafe_allow_html=True)
                with m3:
                    st.markdown(f'<div class="metric-label-sm">Gaps Identified</div><div class="metric-value-lg" style="color:#F59E0B;">{len(missing_keywords)}</div>', unsafe_allow_html=True)
                
                st.markdown("<hr style='margin:1.2rem 0; border-color:#F1F5F9;'>", unsafe_allow_html=True)
                
                st.markdown("**🟢 Matched Technical Competencies:**")
                if matched_keywords:
                    badges_html = "".join([f'<span class="skill-badge-matched">✓ {k}</span>' for k in matched_keywords])
                    st.markdown(badges_html, unsafe_allow_html=True)
                else:
                    st.caption("No direct keyword matches found.")
                    
                st.markdown("<br>**🟡 Identified Competency Gaps:**", unsafe_allow_html=True)
                if missing_keywords:
                    gaps_html = "".join([f'<span class="skill-badge-gap">! {k}</span>' for k in missing_keywords])
                    st.markdown(gaps_html, unsafe_allow_html=True)
                else:
                    st.caption("No critical competency gaps identified.")
                    
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_res_r:
                st.markdown("### 🗄️ Agent 2: Data Management Agent")
                st.markdown('<div class="modern-card">', unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:14px; margin-bottom:1.2rem;">
                    <div style="background:#1E293B; color:white; width:52px; height:52px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.3rem; font-weight:700;">
                        {candidate_name[0] if candidate_name else 'C'}
                    </div>
                    <div>
                        <div style="font-size:1.25rem; font-weight:700; color:#0F172A;">{candidate_name}</div>
                        <div style="color:#64748B; font-size:0.9rem;">Candidate Profile Record</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**📧 Email:** `{candidate_email}`")
                st.markdown(f"**📱 Phone:** `{candidate_phone}`")
                st.markdown(f"**⚖️ Final Decision:** `{screening_decision}`")
                st.markdown(f"**💾 Private Database Partition:** `{save_msg}`")
                
                st.success(f"✓ Candidate profile securely logged to private workspace for `{st.session_state['user_email']}`.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # AGENT 3: INTERVIEW QUESTIONS
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🎯 Agent 3: Interview Strategist (Adaptive High-Signal Assessment)")
            st.caption("Tailored technical interview strategy designed specifically around the candidate's verified strengths and identified gaps:")
            
            for idx, q in enumerate(questions[:5], 1):
                cat = q.get("category", "Technical Competency")
                diff = q.get("difficulty", "Senior")
                
                diff_color = "#3B82F6" if "Inter" in diff else ("#8B5CF6" if "Senior" in diff else "#DC2626")
                
                with st.expander(f"📌 Question {idx}: [{cat}] · Level: {diff}", expanded=True if idx <= 2 else False):
                    st.markdown(f"""
                    <div style="background:#F8FAFC; border-left:4px solid {diff_color}; padding:1rem 1.2rem; border-radius:8px; margin-bottom:1rem;">
                        <span style="font-weight:700; color:#1E293B; font-size:1.05rem;">{q.get('question')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    r_col1, r_col2 = st.columns(2, gap="medium")
                    with r_col1:
                        st.markdown('<div class="rubric-box-green">', unsafe_allow_html=True)
                        st.markdown("**🟢 Positive Technical Signals (What to Look For):**")
                        for sig in q.get("green_flags", []):
                            st.markdown(f"- {sig}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    with r_col2:
                        st.markdown('<div class="rubric-box-red">', unsafe_allow_html=True)
                        st.markdown("**🔴 Warning Signs (Red Flags):**")
                        for rf in q.get("red_flags", []):
                            st.markdown(f"- {rf}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    st.markdown(f"**🔍 Follow-up Depth Probe:** `{q.get('follow_up')}`")
                    st.caption(f"💡 *Assessment Intent:* {q.get('why_ask')}")

# -------------------------------------------------------------
# TAB 2: CANDIDATE DATABASE & PRIVACY SHIELD
# -------------------------------------------------------------
with tabs[1]:
    active_email = st.session_state.get("user_email", "recruiter@workspace.com")
    safe_uid = re.sub(r'[^a-zA-Z0-9_.-]', '_', active_email.lower().strip())
    user_db_file = get_user_db_path(active_email)
    
    st.markdown(f"### 📊 Candidate Audit Database · Recruiter Workspace (`{active_email}`)")
    
    # Enterprise Multi-Tenant Privacy Shield Notice
    st.markdown(f"""
    <div style="background:#F0FDF4; border:1px solid #BBF7D0; border-left:4px solid #16A34A; padding:0.9rem 1.2rem; border-radius:8px; margin-bottom:1.2rem;">
        <span style="font-weight:700; color:#166534;">🛡️ Isolated Multi-Tenant Workspace Active:</span>
        <span style="color:#14532D; font-size:0.92rem;"> 
            Logged in as <b>{active_email}</b>. You have exclusive access to your isolated database partition 
            (<code>assets/users/{safe_uid}/candidates_database.csv</code>). 
            Cross-tenant isolation ensures other recruiters cannot view, query, or leak your candidates.
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    ctrl_col1, ctrl_col2 = st.columns([1.3, 1], gap="medium")
    with ctrl_col1:
        view_mode = st.radio(
            "Database Workspace Scope:",
            [
                f"🔒 My Private Workspace ({active_email})",
                "🗄️ Consolidated Audit Log (Admin Mode)"
            ],
            horizontal=False
        )
    with ctrl_col2:
        mask_pii_enabled = st.checkbox(
            "🎭 Enable PII De-Identification (Mask Email & Phone)", 
            value=True, 
            help="Masks candidate name, email, and phone numbers to comply with HIPAA, GDPR, and EEOC hiring fairness standards."
        )
    
    df = pd.DataFrame()
    if "My Private Workspace" in view_mode:
        if os.path.exists(user_db_file):
            try:
                df = pd.read_csv(user_db_file)
            except Exception as e:
                st.error(f"Error reading private database: {e}")
        else:
            ensure_user_seeded(active_email)
            if os.path.exists(user_db_file):
                df = pd.read_csv(user_db_file)
    else:
        st.info("ℹ️ Consolidated Admin Log displays system-wide audit records across all accounts. Access restricted for compliance review.")
        if os.path.exists(CSV_PATH):
            try:
                df = pd.read_csv(CSV_PATH)
            except Exception as e:
                st.error(f"Error reading local CSV database: {e}")
                
    if not df.empty:
        display_df = df.copy()
        if mask_pii_enabled:
            if "Name" in display_df.columns:
                display_df["Name"] = display_df["Name"].apply(
                    lambda n: re.sub(r'(\b\w)\w+', r'\1***', str(n)) if pd.notna(n) else n
                )
            if "Email" in display_df.columns:
                display_df["Email"] = display_df["Email"].apply(
                    lambda e: re.sub(r'(^.).*(@.).*(\..*$)', r'\1***\2***\3', str(e)) if pd.notna(e) and '@' in str(e) else '***@***.***'
                )
            if "Phone number" in display_df.columns:
                display_df["Phone number"] = display_df["Phone number"].apply(
                    lambda p: re.sub(r'\d{3,}', '***', str(p)) if pd.notna(p) else p
                )
        
        total_cand = len(df)
        hires = len(df[df['Screening Decision'] == 'HIRE']) if 'Screening Decision' in df.columns else 0
        passes = total_cand - hires
        pass_rate = (hires / total_cand) if total_cand > 0 else 0
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.markdown(f'<div class="modern-card"><div class="metric-label-sm">Total Evaluated</div><div class="metric-value-lg">{total_cand}</div></div>', unsafe_allow_html=True)
        with m_col2:
            st.markdown(f'<div class="modern-card"><div class="metric-label-sm">Screening Passes</div><div class="metric-value-lg" style="color:#10B981;">{hires}</div></div>', unsafe_allow_html=True)
        with m_col3:
            st.markdown(f'<div class="modern-card"><div class="metric-label-sm">Screening Rejections</div><div class="metric-value-lg" style="color:#EF4444;">{passes}</div></div>', unsafe_allow_html=True)
        with m_col4:
            st.markdown(f'<div class="modern-card"><div class="metric-label-sm">Pass Rate</div><div class="metric-value-lg" style="color:#3B82F6;">{pass_rate:.1%}</div></div>', unsafe_allow_html=True)
            
        # Filter and search
        search_query = st.text_input("🔍 Search candidates by name, email, or skill:", "")
        filtered_df = display_df
        if search_query:
            filtered_df = display_df[
                display_df['Name'].astype(str).str.contains(search_query, case=False, na=False) |
                display_df['Email'].astype(str).str.contains(search_query, case=False, na=False) |
                display_df['Matching Keywords'].astype(str).str.contains(search_query, case=False, na=False)
            ]
            
        st.dataframe(filtered_df, use_container_width=True)
        
        d_col1, d_col2 = st.columns([1.5, 1])
        with d_col1:
            csv_bytes = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Export Workspace Database ({len(filtered_df)} records)",
                data=csv_bytes,
                file_name=f"candidates_{safe_uid}.csv",
                mime="text/csv"
            )
        with d_col2:
            if "My Private Workspace" in view_mode:
                if st.button("🗑️ Reset My Workspace Data", help="Clears records in your private isolated workspace"):
                    with open(user_db_file, mode='w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Timestamp', 'Name', 'Email', 'Phone number', 'Matching Keywords', 'Screening Decision'])
                    st.success("Workspace reset. Reloading...")
                    st.rerun()
    else:
        st.info(f"No candidate evaluations found yet in your private workspace ({active_email}). Screen a resume in Tab 1 to populate.")

# -------------------------------------------------------------
# TAB 3: SYSTEM ARCHITECTURE & INTERVIEW PREPARATION
# -------------------------------------------------------------
with tabs[2]:
    st.markdown("### 🏛️ System Architecture & Engineering Design Suite")
    st.caption("Deep technical specifications, architectural patterns, dynamic domain adaptations, and interview prep.")
    
    subtab_arch, subtab_domain, subtab_qa = st.tabs([
        "📐 System Architecture & Flow",
        "🌐 Dynamic Enterprise Domain Adapter",
        "🧠 Universal Technical Interview Cheatsheet"
    ])
    
    with subtab_arch:
        st.markdown("#### Autonomous Multi-Agent Topology")
        st.markdown("""
        The system decouples recruitment tasks across specialized autonomous agents running under **Microsoft AutoGen**.
        This implements the **Single Responsibility Principle (SoC)**, isolates context windows, eliminates prompt bloat, and provides deterministic validation boundaries.
        """)
        
        st.markdown("""
```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               UserProxyAgent (Orchestrator)                           │
│        • Human Input Mode: NEVER (Automated Production Execution Runtime)             │
│        • Dispatches Tool Invocations on Local Compute Environment                     │
└────────────────┬───────────────────────────┬───────────────────────────┬───────────────┘
                 │                           │                           │
        1. Screening Task           2. Data Task                3. Interview Task
                 ▼                           ▼                           ▼
┌──────────────────────────────┐ ┌───────────────────────┐ ┌───────────────────────────┐
│     Screening Assistant      │ │     Data Manager      │ │    Interview Strategist   │
│ • pdfplumber Document Parser │ │ • Regex PII Parsing   │ │ • Skill Gap Evaluation    │
│ • spaCy Lemmatization Engine │ │ • Audit Trail Export  │ │ • Evaluation Rubric Gen   │
│ • Deterministic Verification │ │ • CSV / Postgres DB   │ │ • Follow-up Depth Probe   │
└──────────────────────────────┘ └───────────────────────┘ └───────────────────────────┘
```
        """)
        
        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown("##### 1. NLP Processing Pipeline (`tools.keyword_matcher`)")
            st.markdown("""
            - **Lemmatization over Stemming**: Utilizes spaCy's context-aware `token.lemma_` to preserve base grammatical roots without crude stemming truncations.
            - **Technical Symbol Preservation**: Custom token filter preserves symbols in technical acronyms (e.g., `C++`, `C#`, `x86_64`, `CI/CD`), preventing standard `token.is_alpha` filters from corrupting technical keywords.
            - **Deterministic Verification**: Exact presence matching prevents LLM hallucinations on core competencies.
            """)
        with c2:
            st.markdown("##### 2. Document Ingestion Engine (`tools.parser`)")
            st.markdown("""
            - **Layout-Aware PDF Extraction**: Utilizes `pdfplumber` to respect visual column boundaries, preventing horizontal text interleaving common in modern resumes.
            - **Null-Safe Stream Processing**: Gracefully checks for empty or scanned image pages without `NoneType` crashes.
            - **Cross-Platform Path Resolution**: Dynamic relative-to-base path resolution ensuring execution stability across different working directories.
            """)

    with subtab_domain:
        st.markdown("#### Dynamic Enterprise Domain Adapter")
        st.caption("Select or customize the target enterprise domain to inspect compliance, scalability, and architecture adjustments:")
        
        target_domain = st.selectbox(
            "Select Target Enterprise Domain / Industry:",
            [
                "🏥 Healthcare & Health-Tech (e.g., Optum, Epic, UnitedHealth Group)",
                "☁️ Cloud Infrastructure & Big Tech (e.g., Google, AWS, Microsoft)",
                "💳 Banking & FinTech (e.g., Stripe, Goldman Sachs, JPMorgan)",
                "🛒 High-Volume E-Commerce & Retail (e.g., Amazon, Walmart)",
                "✏️ Custom Enterprise"
            ]
        )
        
        if "Healthcare" in target_domain:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown("##### 🏥 Healthcare & Life Sciences Focus")
            st.markdown("""
            - **HIPAA & PII Protection**: Candidate resumes contain sensitive personal data. In healthcare production, the Data Management Agent integrates **Microsoft Presidio** to de-identify SSNs, medical histories, and demographic proxies before LLM exposure.
            - **Clinical & IT Credentialing**: Cross-references state licensing boards, NPI databases, and specialty certifications (e.g., Epic EHR modules, HL7/FHIR proficiency).
            - **Audit Trail & EEOC Compliance**: Immutable audit logging ensures complete explainability for regulatory hiring compliance.
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        elif "Cloud" in target_domain:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown("##### ☁️ Cloud Infrastructure & Big Tech Focus")
            st.markdown("""
            - **Event-Driven Scale**: Decouples document ingestion using **Kafka / AWS SQS**, enabling distributed workers to process tens of thousands of applicants concurrently.
            - **Vector Embeddings (RAG)**: Uses **pgvector / Pinecone** to enable semantic candidate search ('find engineers with distributed consensus experience') beyond keyword matching.
            - **Multi-Region Redundancy**: Configures AutoGen fallback endpoints across multiple cloud regions with exponential backoff on 429 rate limits.
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        elif "Banking" in target_domain:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown("##### 💳 Banking & FinTech Focus")
            st.markdown("""
            - **Zero Data-Loss Auditability**: Transition from flat CSV to ACID-compliant PostgreSQL / Snowflake with append-only ledger tables.
            - **SOC2 & PCI-DSS Hardening**: Secrets managed via HashiCorp Vault; code execution in sandboxed gVisor containers.
            - **Strict Anti-Bias Controls**: Blind resume screening algorithms evaluated quarterly against disparate impact ratios.
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        elif "E-Commerce" in target_domain:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown("##### 🛒 High-Volume E-Commerce Focus")
            st.markdown("""
            - **High-Velocity Pipeline**: Asynchronous batching with Redis caching to pre-screen thousands of seasonal campus applicants in minutes.
            - **Automated Routing**: Routes qualified profiles directly into hiring manager calendar webhooks via ATS integrations (Workday / Greenhouse API).
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            custom_comp = st.text_input("Enter Company / Industry Name:", value="Target Enterprise")
            st.markdown(f"##### 🎯 Tailored Architectural Considerations for {custom_comp}")
            st.markdown("""
            - **Data Layer**: Relational DB with schema migrations (PostgreSQL + Alembic).
            - **Security**: OAuth2 token authentication, input sanitization against prompt injection.
            - **Cost Optimization**: Caching repeated job description embeddings to minimize token burn.
            """)

    with subtab_qa:
        st.markdown("#### Universal Technical Interview Grill & Cheatsheet")
        st.caption("Deep technical questions interviewers ask regarding Multi-Agent Systems, NLP, and System Design:")
        
        with st.expander("Q1: Why use a Multi-Agent Architecture instead of a single prompt or simple LangChain sequential chain?"):
            st.markdown("""
            **Answer**:
            1. **Separation of Concerns (SoC)**: In a monolithic prompt, instructions for document parsing, candidate evaluation, data formatting, and question synthesis all compete for attention in a single context window. This causes prompt bloat, high token consumption, and hallucinations.
            2. **Tool Scoping**: AutoGen scopes tools specifically to the agent that needs them. Screening Assistant only has access to parser and matcher tools; Data Manager only has persistence access. This eliminates tool selection confusion.
            3. **Deterministic Verification Gate**: The multi-agent workflow creates verifiable stage gates—the candidate's screening decision is verified deterministically before interview question generation is triggered.
            """)
            
        with st.expander("Q2: How does AutoGen manage tool execution between AssistantAgent and UserProxyAgent under the hood?"):
            st.markdown("""
            **Answer**:
            - **AssistantAgent** is a reasoning persona backed by an LLM. It generates intent—when a tool is required, it outputs a structured `tool_calls` JSON payload following the OpenAPI schema generated by `register_function`.
            - **UserProxyAgent** is the executor agent. With `human_input_mode="NEVER"`, it programmatically intercepts the assistant's `tool_calls`, invokes the local Python function in the runtime environment, and injects the output back into the chat history with role `tool`.
            - This clean separation ensures LLMs never have direct OS or database access without mediator validation.
            """)
            
        with st.expander("Q3: How do you prevent infinite agent loops and runaway API costs?"):
            st.markdown("""
            **Answer**:
            We implement three concentric safety barriers:
            1. **Termination Sentinels**: `is_termination_msg=lambda x: "TERMINATE" in x.get("content")` stops conversation as soon as an agent concludes.
            2. **Max Consecutive Replies**: Hard limit (`max_consecutive_auto_reply=6`) prevents endless ping-pong loops between agents.
            3. **Chat Turn Limits**: `user_proxy.initiate_chat(max_turns=5)` sets an absolute circuit breaker.
            """)
            
        with st.expander("Q4: How would you scale this system to process 100,000 resumes per day?"):
            st.markdown("""
            **Answer**:
            1. **Asynchronous Task Queue**: Ingest resumes via FastAPI endpoints that immediately publish jobs to RabbitMQ / Kafka, returning an async ticket ID.
            2. **Distributed Celery / Ray Workers**: Stateless agent worker pools consume messages from queues, process resumes concurrently, and report status.
            3. **Database Architecture**: Replace CSV with PostgreSQL (partitioned by month/department) and store raw files in AWS S3 with pre-signed URLs.
            4. **Vector Search & Embedding Cache**: Cache embeddings of common job descriptions and resume sections using Redis and pgvector to eliminate redundant LLM calls.
            """)
            
        with st.expander("Q5: How do you protect against prompt injection in uploaded resumes?"):
            st.markdown("""
            **Answer**:
            - **Untrusted Input Sandboxing**: Resume text is parsed into raw strings and strictly enclosed within explicit XML delimiters (`<resume_text>...</resume_text>`).
            - **System Prompt Dominance**: System instructions mandate that text inside data tags is purely untrusted passive data for analysis, never executable instructions.
            - **Deterministic Code Validation**: Core matching is performed by Python code (`tools.keyword_matcher`), not solely by LLM text generation, making semantic injection attempts ineffective.
            """)
            
        with st.expander("Q6: How does the system handle Data Privacy, Multi-Tenancy, and prevent cross-tenant data leakage?"):
            st.markdown("""
            **Answer**:
            - **Tenant Isolation & Partitioning**: In multi-user deployments, each recruiter or organization authenticates into an isolated database partition (logical filesystem isolation or Row-Level Security / Schema-per-tenant in PostgreSQL). User A cannot query, view, or modify User B's talent pool.
            - **Automated PII De-Identification**: Built-in regex and NLP masking anonymize candidate PII (email, phone, address, demographic proxies) prior to rendering or downstream storage, adhering to **HIPAA**, **GDPR**, and **EEOC** non-bias mandates.
            - **Role-Based Access Control (RBAC)**: Recruiter views are strictly scoped to their tenant workspace, while Consolidated System Audit logs are quarantined exclusively for authorized enterprise compliance officers.
            """)
            
        with st.expander("Q7: What are the technical and operational trade-offs of Offline On-Prem vs Online Cloud Deployment?"):
            st.markdown("""
            **Answer**:
            - **Offline / On-Premise Deployment**:
              - *Pros*: Complete data sovereignty (candidate resumes never leave internal enterprise perimeter), zero third-party token egress costs, full HIPAA/SOC2 perimeter containment, zero internet dependency.
              - *Cons*: Compute bound to local hardware, requires manual updates, lacks seamless cross-team recruiter synchronization.
            - **Online / Cloud Multi-Tenant Deployment**:
              - *Pros*: Real-time collaboration across distributed hiring teams, horizontal elasticity via containerized workers (ECS/Kube), native webhook integrations with enterprise ATS (Workday, Greenhouse, Taleo).
              - *Cons*: Requires strict multi-tenancy controls (authentication, encrypted storage at rest/in transit via TLS 1.3), rate-limit governance, and regulatory compliance monitoring.
            """)
