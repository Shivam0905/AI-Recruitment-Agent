"""
Intelligent Interview Question Generation Module
Generates high-signal, practical technical interview questions tailored to candidate
experience, job description requirements, and identified skill gaps.
Supports both live LLM synthesis (GPT-4o-mini) and high-quality offline rule/NLP synthesis.
"""

import os
import re
import json

def generate_interview_questions(resume_text: str, jd_text: str, matched_keywords: list[str], missing_keywords: list[str], api_key: str = None) -> list[dict]:
    """
    Generate 5 structured, high-signal technical interview questions.
    Returns a list of dicts:
    [
        {
            "category": "...",
            "difficulty": "Senior / Mid / Lead",
            "question": "...",
            "why_ask": "...",
            "green_flags": ["...", "..."],
            "red_flags": ["...", "..."],
            "follow_up": "..."
        },
        ...
    ]
    """
    openai_key = api_key or os.environ.get("OPENAI_API_KEY")
    
    if openai_key and not openai_key.startswith("your_"):
        try:
            return _generate_with_llm(resume_text, jd_text, matched_keywords, missing_keywords, openai_key)
        except Exception as e:
            print(f"[!] LLM Generation failed ({e}), falling back to intelligent contextual engine.")
    
    return _generate_contextual_questions(resume_text, jd_text, matched_keywords, missing_keywords)

def _generate_with_llm(resume_text: str, jd_text: str, matched_keywords: list[str], missing_keywords: list[str], api_key: str) -> list[dict]:
    """Generate dynamic questions via OpenAI GPT-4o-mini."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
You are a Staff Software Engineer and Technical Hiring Assessor.
Review the candidate's resume text and the job description:

<JOB_DESCRIPTION>
{jd_text[:2500]}
</JOB_DESCRIPTION>

<CANDIDATE_RESUME>
{resume_text[:2500]}
</CANDIDATE_RESUME>

<SCREENING_DATA>
Matched Technical Skills: {', '.join(matched_keywords)}
Identified Skill Gaps: {', '.join(missing_keywords)}
</SCREENING_DATA>

Generate exactly 5 targeted, high-signal technical interview questions.
Rules:
1. NEVER ask generic HR questions like "Can you tell me about a time..." or "What are your strengths?"
2. Ground each question in real engineering trade-offs, architecture, failure scenarios, or claimed resume projects.
3. Address the identified skill gaps using realistic engineering contexts.
4. Output strictly a JSON list of 5 objects with keys:
   - "category": Short domain tag (e.g., "Architecture Trade-offs", "Skill Gap: Docker", "Low-Level Debugging", "Concurrency", "System Reliability")
   - "difficulty": "Intermediate", "Senior", or "Staff / Principal"
   - "question": The exact scenario-based technical question.
   - "why_ask": Why this question is critical for this specific role and candidate.
   - "green_flags": List of 2-3 specific technical indicators of a strong answer.
   - "red_flags": List of 1-2 warning signs or misconceptions.
   - "follow_up": A sharp follow-up probe to test depth.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a pragmatic, elite technical hiring lead. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        response_format={"type": "json_object"}
    )
    
    content = response.choices[0].message.content
    parsed = json.loads(content)
    if "questions" in parsed and isinstance(parsed["questions"], list):
        return parsed["questions"]
    elif isinstance(parsed, list):
        return parsed
    elif isinstance(parsed, dict):
        for v in parsed.values():
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                return v
    return _generate_contextual_questions(resume_text, jd_text, matched_keywords, missing_keywords)

def _generate_contextual_questions(resume_text: str, jd_text: str, matched_keywords: list[str], missing_keywords: list[str]) -> list[dict]:
    """Generate high-signal, context-aware questions deterministically from JD and Resume text."""
    questions = []
    
    # 1. Primary Skill Gap Question (Transferable knowledge probe)
    primary_gap = missing_keywords[0] if missing_keywords else "Containerization & Cloud Infrastructure"
    questions.append({
        "category": f"Skill Gap: {primary_gap}",
        "difficulty": "Senior",
        "question": (
            f"The job requires hands-on experience with **{primary_gap}**, which is not explicitly evident on your resume. "
            f"Assuming our production environment heavily leverages {primary_gap}, walk us through how you would architect, test, "
            f"or troubleshoot an existing codebase transitioning into this stack. What transferable patterns from your past projects apply here?"
        ),
        "why_ask": f"Probes candidate's ability to bridge the technical gap in {primary_gap} and assess self-learning velocity.",
        "green_flags": [
            f"Acknowledges lack of direct exposure honestly and highlights foundational parallels.",
            f"Demonstrates mental model of {primary_gap}'s underlying runtime, trade-offs, and failure modes.",
            "Discusses rapid ramp-up methodology and risk mitigation during technology transitions."
        ],
        "red_flags": [
            f"Pretends to know {primary_gap} deeply despite lack of resume evidence.",
            "Dismisses the requirement as trivial without appreciating operational gotchas."
        ],
        "follow_up": f"If an unexpected production latency spike or crash occurs within the {primary_gap} layer, what is your initial triage workflow?"
    })

    # 2. Core Technical Strengths Deep-Dive
    top_skill = matched_keywords[0] if matched_keywords else "Low-Level Systems"
    questions.append({
        "category": f"Core Competency: {top_skill}",
        "difficulty": "Senior",
        "question": (
            f"Your background emphasizes deep expertise in **{top_skill}**. Can you walk us through the most technically complex challenge "
            f"you solved using {top_skill}? Specifically, what performance constraints or edge-case bugs did you encounter, "
            f"and how did you quantify the efficiency gains?"
        ),
        "why_ask": f"Validates that the candidate's claimed proficiency in {top_skill} represents genuine depth rather than surface-level familiarity.",
        "green_flags": [
            "Details specific low-level bottlenecks (e.g., CPU cache misses, locking overhead, memory alignment, I/O bottlenecks).",
            "Quotes quantitative metrics (e.g., 'reduced tail latency by 40%', 'cut memory footprint from 4GB to 800MB').",
            "Discusses diagnostic tooling used to measure performance (e.g., GDB, perf, Valgrind, flame graphs)."
        ],
        "red_flags": [
            "Gives a vague high-level overview without technical specifics.",
            "Cannot articulate the specific trade-offs made during implementation."
        ],
        "follow_up": "What alternative approach did you consider, and what made your chosen solution superior in that specific architecture?"
    })

    # 3. Production Debugging & Incident Triage
    questions.append({
        "category": "Incident Response & System Debugging",
        "difficulty": "Staff",
        "question": (
            "Suppose a critical service running in production experiences intermittent silent data corruption or an elusive deadlock "
            "that only manifests under heavy concurrent traffic (less than 0.1% of requests). You cannot replicate it locally. "
            "How do you methodically isolate, diagnose, and resolve this without degrading live user traffic?"
        ),
        "why_ask": "Evaluates systematic debugging methodologies under ambiguity and pressure, distinguishing seniors from juniors.",
        "green_flags": [
            "Formulates hypotheses methodically rather than guessing or blindly inserting print statements.",
            "Mentions non-intrusive observability: structured telemetry, core dump analysis, distributed tracing, eBPF probes.",
            "Implements phased rollouts, feature flags, or defensive assertions with automated alerts."
        ],
        "red_flags": [
            "Suggests restarting the server repeatedly as a primary long-term fix.",
            "Lacks understanding of race conditions, memory barriers, or thread synchronization primitives."
        ],
        "follow_up": "Once the root cause is resolved, what systemic safeguards (e.g., fuzz testing, architectural redesign) would you implement to prevent regression?"
    })

    # 4. System Architecture & Performance Trade-offs
    questions.append({
        "category": "Architecture & Engineering Trade-offs",
        "difficulty": "Senior",
        "question": (
            "When designing a high-throughput, low-latency processing pipeline, software engineers constantly balance modularity and clean abstractions "
            "against raw computational efficiency (e.g., avoiding dynamic dispatch, memory allocations, or excessive IPC). "
            "How do you decide where to make concessions in abstraction for the sake of speed?"
        ),
        "why_ask": "Tests engineering maturity and the ability to balance code maintainability against performance requirements.",
        "green_flags": [
            "Emphasizes profiling before prematurely optimizing.",
            "Explains data-oriented design, cache locality, and zero-copy data passing.",
            "Advocates for isolating high-performance micro-kernels behind clean, well-tested interfaces."
        ],
        "red_flags": [
            "Dogmatically claims that clean code should never be sacrificed for performance, or conversely, writes unmaintainable code everywhere.",
            "Unaware of the performance cost of virtual methods, heap allocations, or context switches."
        ],
        "follow_up": "How do you document and communicate deliberate abstraction compromises so future team members don't refactor them away?"
    })

    # 5. Secondary Skill Gap or Security/Reliability
    second_gap = missing_keywords[1] if len(missing_keywords) > 1 else "Security & Resiliency"
    questions.append({
        "category": f"Resilience & Standards: {second_gap}",
        "difficulty": "Intermediate / Senior",
        "question": (
            f"In enterprise production environments, resilience and security standards around **{second_gap}** are critical. "
            f"What automated quality gates, linting checks, security audits, or static analysis tools do you mandate in a CI/CD pipeline "
            f"to guarantee stability before code hits production?"
        ),
        "why_ask": "Assesses the candidate's software craftsmanship, enterprise security awareness, and production readiness.",
        "green_flags": [
            "Cites concrete tools (e.g., SonarQube, AddressSanitizer, Clang-Tidy, Trivy, Dependabot).",
            "Understands Shift-Left security and automated regression testing.",
            "Values automated reproducibility through hermetic builds and infrastructure-as-code."
        ],
        "red_flags": [
            "Relies solely on manual QA and visual inspection.",
            "Views automated security and linting tools as annoying impediments rather than quality guarantees."
        ],
        "follow_up": "How do you handle a scenario where a high-severity vulnerability is detected in an upstream open-source dependency with no patch available?"
    })

    return questions
