import os
import re
import json
import requests

RESUME_TEMPLATES = [
    {"id": "tpl-harvard", "name": "Harvard Classic", "desc": "Strict chronological, centered headers. 100% ATS safe."},
    {"id": "tpl-modern", "name": "Tech Minimalist", "desc": "Clean, left-aligned, highly readable sans-serif."},
    {"id": "tpl-corporate", "name": "Executive Corporate", "desc": "Heavy borders, strong section contrasts for finance/management."},
    {"id": "tpl-startup", "name": "Modern Startup", "desc": "Spacious, modern typography with subtle accent colors."},
    {"id": "tpl-academic", "name": "Academic Researcher", "desc": "Dense information formatting, standard serif fonts."},
    {"id": "tpl-engineering", "name": "Engineering Standard", "desc": "Technical precision, structured modular alignment."},
    {"id": "tpl-creative", "name": "Creative Professional", "desc": "Distinctive left-border accents, bold typography."},
    {"id": "tpl-quant", "name": "Finance Quant", "desc": "Compact spacing for high-volume technical data."},
    {"id": "tpl-elegance", "name": "Elegant Serif", "desc": "Classic aesthetics with high readability spacing."},
    {"id": "tpl-apex", "name": "Apex Bold", "desc": "Strong header background blocks, high impact."}
]

TEMPLATE_PRESETS = {
    "tpl-harvard": {
        "font": "'Times New Roman', serif",
        "color": "#000000",
        "align": "center",
        "sections": [
            {
                "id": "sec-summary", "type": "text", "title": "Professional Summary",
                "items": [{"title": "", "meta": "", "desc": "Methodical researcher and analyst with strong expertise in empirical data analysis, statistical modeling, and structured academic documentation."}]
            },
            {
                "id": "sec-edu", "type": "list", "title": "Education",
                "items": [{"title": "Degree Program", "meta": "Expected 2026", "desc": "Core Studies: Quantitative Methods, Applied Research, and Scientific Reporting."}]
            },
            {
                "id": "sec-proj", "type": "list", "title": "Academic Research & Capstones",
                "items": [
                    {
                        "title": "Empirical Methodology Investigation", "meta": "2025 - 2026",
                        "desc": "Formulated hypotheses and performed structured statistical testing across 12 control groups.\nSynthesized analytical findings into a formal 35-page peer-reviewed report."
                    }
                ]
            },
            {
                "id": "sec-pub", "type": "list", "title": "Publications & Presentations",
                "items": [
                    {
                        "title": "Annual Research Symposium", "meta": "Oct 2025",
                        "desc": "Delivered technical findings on empirical methodologies to an academic review committee of 8 faculty members."
                    }
                ]
            },
            {
                "id": "sec-skills", "type": "text", "title": "Core Competencies",
                "items": [{"title": "", "meta": "", "desc": "Statistical Analysis, Quantitative Modeling, Experimental Design, Research Writing, Data Synthesis"}]
            }
        ]
    },
    "tpl-modern": {
        "font": "'Arial', sans-serif",
        "color": "#2563eb",
        "align": "left",
        "sections": [
            {
                "id": "sec-summary", "type": "text", "title": "Profile",
                "items": [{"title": "", "meta": "", "desc": "Results-oriented software developer focused on modular architecture, clean APIs, and robust full-stack implementation."}]
            },
            {
                "id": "sec-skills", "type": "text", "title": "Technical Proficiencies",
                "items": [{"title": "", "meta": "", "desc": "Python (Flask), JavaScript (ES6+), SQLite, REST APIs, Git, Tailwind CSS, Docker"}]
            },
            {
                "id": "sec-proj", "type": "list", "title": "Technical Projects",
                "items": [
                    {
                        "title": "Autonomous Data Pipeline", "meta": "2025",
                        "desc": "Engineered modular ETL services handling over 5,000 requests per minute with 99.9% uptime.\nImplemented client-side vector rendering, eliminating server CPU load entirely."
                    },
                    {
                        "title": "Relational Career Portal", "meta": "2024 - 2025",
                        "desc": "Designed normalized SQLite schemas and REST APIs serving verified recruitment data.\nReduced client query response latency by 22% through index optimization."
                    }
                ]
            },
            {
                "id": "sec-edu", "type": "list", "title": "Education",
                "items": [{"title": "Computer Science / Engineering", "meta": "2022 - 2026", "desc": "Relevant Coursework: Database Systems, Algorithms, Distributed Networks."}]
            }
        ]
    },
    "tpl-corporate": {
        "font": "'Georgia', serif",
        "color": "#0f172a",
        "align": "left",
        "sections": [
            {
                "id": "sec-summary", "type": "text", "title": "Executive Summary",
                "items": [{"title": "", "meta": "", "desc": "Strategic operations specialist with a proven track record in workflow optimization, stakeholder communications, and team execution."}]
            },
            {
                "id": "sec-proj", "type": "list", "title": "Key Leadership Initiatives",
                "items": [
                    {
                        "title": "Cross-Functional Workflow Modernization", "meta": "2025 - Present",
                        "desc": "Audited departmental workflows across 4 teams, eliminating repetitive manual touchpoints.\nReduced end-to-end turnaround time by 18% through standardized pipeline tracking."
                    },
                    {
                        "title": "Resource Allocation Framework", "meta": "2024 - 2025",
                        "desc": "Structured performance benchmarks adopted across 6 concurrent project deliverables.\nEnsured 100% adherence to quality compliance milestones."
                    }
                ]
            },
            {
                "id": "sec-skills", "type": "text", "title": "Strategic Skills",
                "items": [{"title": "", "meta": "", "desc": "Process Optimization, Risk Management, Stakeholder Reporting, Team Coordination, KPIs"}]
            },
            {
                "id": "sec-edu", "type": "list", "title": "Education",
                "items": [{"title": "Management / Business Administration", "meta": "Expected 2026", "desc": "Concentration: Operational Leadership, Strategic Planning, Financial Analysis."}]
            }
        ]
    }
}
def build_default_resume_state(user, nlp_skills):
    course = (user['course_name'] or "").lower()
    
    if any(k in course for k in ['computer', 'software', 'it', 'tech', 'data']):
        tpl_key = "tpl-modern"
    elif any(k in course for k in ['business', 'commerce', 'management', 'mba', 'bba']):
        tpl_key = "tpl-corporate"
    else:
        tpl_key = "tpl-harvard"

    preset = TEMPLATE_PRESETS.get(tpl_key, TEMPLATE_PRESETS["tpl-harvard"])
    sections = json.loads(json.dumps(preset["sections"]))

    for sec in sections:
        if sec["id"] == "sec-edu":
            sec["items"][0]["title"] = user['course_name']
            sec["items"][0]["meta"] = f"Expected {user['passout_year']}"
            sec["items"][0]["desc"] = "College / University Name"
        elif sec["id"] == "sec-skills" and nlp_skills:
            sec["items"][0]["desc"] = ", ".join(nlp_skills)

    return {
        "template": tpl_key,
        "design": {
            "color": preset["color"],
            "font": preset["font"],
            "size": 10,
            "lineStyle": "solid",
            "lineThickness": 1,
            "align": preset["align"]
        },
        "personal": {
            "name": user['full_name'],
            "contact": f"{user['email']} | +91 XXXXX XXXXX | LinkedIn"
        },
        "sections": sections
    }

def process_bullet_improvement(text, section_title, entry_title, target_role):
    clean = text.rstrip('. ')
    lower_text = clean.lower()

    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        try:
            prompt = (
                f"You are an ATS resume optimization engine. Rewrite this single bullet point using the XYZ impact formula "
                f"(Accomplished [X] as measured by [Y], by doing [Z]).\n"
                f"Section: {section_title} | Entry: {entry_title} | Role: {target_role}\n"
                f"Original: {text}\n"
                f"Return ONLY the single polished sentence without quotes."
            )
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {groq_api_key}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 120},
                timeout=4
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"].strip(), "llama-3.1-groq"
        except Exception:
            pass

    verbs_map = {
        'did': 'Executed',
        'worked on': 'Spearheaded development of',
        'helped': 'Collaborated on',
        'made': 'Engineered',
        'managed': 'Directed and optimized',
        'studied': 'Researched and evaluated',
        'analyzed': 'Synthesized and benchmarked',
        'handled': 'Orchestrated'
    }
    for weak, strong in verbs_map.items():
        if lower_text.startswith(weak):
            clean = strong + clean[len(weak):]
            break

    strong_verbs = ('engineered', 'developed', 'spearheaded', 'collaborated', 'synthesized', 'orchestrated', 'executed', 'designed', 'formulated', 'directed')
    if not clean.lower().startswith(strong_verbs):
        if any(k in section_title.lower() or k in entry_title.lower() for k in ['chemistry', 'lab', 'science', 'research']):
            clean = f"Formulated and analyzed {clean[:1].lower() + clean[1:]}"
        else:
            clean = f"Engineered and deployed {clean[:1].lower() + clean[1:]}"

    if not re.search(r'\d+%', clean) and not re.search(r'\b\d+\b', clean):
        if any(k in section_title.lower() or k in entry_title.lower() for k in ['chemistry', 'lab', 'science']):
            clean += ", achieving 98% compound purity and standardizing laboratory documentation."
        elif 'project' in section_title.lower():
            clean += ", reducing operational turnaround time by 18% across 4 release iterations."
        else:
            clean += ", improving process efficiency by 15% and boosting team deliverables."

    return clean.strip(), "domain-heuristic"