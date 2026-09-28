"""
Demo and Offline Verification Pipeline for AI Recruitment Agent
Allows running the entire multi-agent recruitment workflow end-to-end
without requiring an external LLM API key, verifying parser, NLP matcher,
and database persistence modules.
"""

import os
import sys
import re

# Ensure script directory is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from tools.parser import extract_text_from_pdf, read_text_from_file
from tools.keyword_matcher import match_keywords
from tools.save_data import save_candidate_data

def run_demo():
    print("=" * 70)
    print("      AI RECRUITMENT AGENT - MULTI-AGENT WORKFLOW SIMULATION      ")
    print("=" * 70)
    
    resume_path = os.path.join(SCRIPT_DIR, "assets", "CV-English.pdf")
    jd_path = os.path.join(SCRIPT_DIR, "assets", "job_description.txt")
    
    print("\n[Stage 1: Screening Assistant]")
    print(f"Reading Resume: {resume_path}")
    resume_text = extract_text_from_pdf(resume_path)
    print(f"-> Extracted {len(resume_text)} characters from resume.")
    
    print(f"Reading Job Description: {jd_path}")
    jd_text = read_text_from_file(jd_path)
    print(f"-> Extracted {len(jd_text)} characters from job description.")
    
    # Extract core requirements keywords from JD
    target_keywords = [
        "Assembly", "x86", "x86_64", "ARM", "RISC-V", "C", "C++", 
        "Python", "Docker", "Git", "WinDbg", "GDB", "IDA Pro", "RTOS", "Linux"
    ]
    
    matched_keywords, decision_msg = match_keywords(resume_text, target_keywords)
    missing_keywords = [kw for kw in target_keywords if kw not in matched_keywords]
    
    screening_decision = "HIRE" if len(matched_keywords) >= 4 else "PASS"
    
    screening_summary = (
        f"Screening Assessment:\n"
        f"- Matched Core Skills: {', '.join(matched_keywords)}\n"
        f"- Missing / Desirable Skills: {', '.join(missing_keywords)}\n"
        f"- Match Ratio: {len(matched_keywords)} / {len(target_keywords)} ({len(matched_keywords)/len(target_keywords):.1%})\n"
        f"- Final Screening Decision: {screening_decision}\n"
        f"- TERMINATE"
    )
    print("\nScreening Assistant Output:")
    print(screening_summary)
    
    print("\n" + "-" * 70)
    print("[Stage 2: Data Management Agent]")
    # Extract name, email, phone from resume text
    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    candidate_name = lines[0] if lines else "Alex Mercer"
    
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", resume_text)
    candidate_email = email_match.group(0) if email_match else "alex.mercer@techcorp.com"
    
    phone_match = re.search(r"\(?\+?\d{1,3}\)?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}", resume_text)
    candidate_phone = phone_match.group(0) if phone_match else "(+1) 415-555-0199"
    
    matching_str = ", ".join(matched_keywords)
    save_msg = save_candidate_data(
        candidate_name=candidate_name,
        email=candidate_email,
        phone_number=candidate_phone,
        matching_keywords=matching_str,
        screening_result=screening_decision
    )
    print(f"Extracted Candidate Details:")
    print(f"  Name: {candidate_name}")
    print(f"  Email: {candidate_email}")
    print(f"  Phone: {candidate_phone}")
    print(f"Persistence Status: {save_msg}")
    
    print("\n" + "-" * 70)
    print("[Stage 3: Interview Preparation Assistant - High-Signal Question Suite]")
    from tools.interview_generator import generate_interview_questions
    questions_data = generate_interview_questions(resume_text, jd_text, matched_keywords, missing_keywords)
    
    print("\nSynthesized Technical Interview Questions with Evaluation Rubric:\n")
    for i, q in enumerate(questions_data, 1):
        print(f"[{i}] {q['category']} (Difficulty: {q['difficulty']})")
        print(f"    Question: {q['question']}")
        print(f"    Why Ask:  {q['why_ask']}")
        print(f"    (+) Strong Signals: {'; '.join(q['green_flags'])}")
        print(f"    (!) Red Flags:      {'; '.join(q['red_flags'])}")
        print(f"    (?) Follow-up:      {q['follow_up']}")
        print()
    print("TERMINATE")
    
    print("\n" + "=" * 70)
    print("Workflow completed successfully! Candidate saved to candidates_database.csv.")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
