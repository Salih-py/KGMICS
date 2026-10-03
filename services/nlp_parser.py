import re
import difflib
from data.taxonomy_graph import CAREER_TAXONOMY, COURSE_DISCIPLINES

# Comprehensive Alias Mapping (Tools & Abbreviations -> Canonical Taxonomy Skill)
SKILL_ALIASES = {
    # Tech & Tools
    "Python": ["python", "py", "pandas", "numpy", "matplotlib", "scikit-learn", "django"],
    "SQL": ["sql", "mysql", "postgresql", "database", "queries", "rdbms"],
    "Excel": ["excel", "spreadsheet", "spreadsheets", "csv", "google sheets", "ms excel"],
    "JavaScript": ["javascript", "js", "node.js", "nodejs", "react", "vue", "typescript"],
    "HTML/CSS": ["html", "css", "tailwind", "bootstrap", "web design"],
    "Machine Learning": ["machine learning", "ml", "supervised learning"],
    "Deep Learning": ["deep learning", "dl", "neural networks", "pytorch", "tensorflow"],
    "Data Structures": ["data structures", "dsa"],
    "Algorithms": ["algorithms", "algorithmic", "optimization"],
    "Tableau & PowerBI": ["tableau", "powerbi", "power bi", "dashboards"],
    
    # Economics & Commerce
    "Financial Accounting": ["financial accounting", "accounting", "bookkeeping", "ledger", "balance sheet"],
    "Corporate Taxation": ["corporate taxation", "taxation", "tax", "gst"],
    "Financial Modeling": ["financial modeling", "financial analysis", "valuation"],
    "Statistical Analysis": ["statistics", "statistical analysis", "spss", "data analysis"],
    "Microeconomics": ["microeconomics", "micro economics"],
    "Macroeconomics": ["macroeconomics", "macro economics"],
    "Public Policy": ["public policy", "policy"],
    
    # Sciences
    "Analytical Chemistry": ["analytical chemistry", "quantitative analysis", "qualitative analysis"],
    "Titration": ["titration", "volumetric analysis", "solution preparation"],
    "Spectroscopy": ["spectroscopy", "uv-vis", "ftir", "nmr"],
    "Chromatography": ["chromatography", "hplc", "gc", "tlc"],
    "Lab Safety & Quality Control": ["lab safety", "quality control", "qa", "qc", "chemical handling"],
    "Animal Biology": ["animal biology", "zoology", "fauna", "anatomy"],
    "Ecology": ["ecology", "ecosystem", "environmental science", "biodiversity"],
    "Microscopy": ["microscopy", "microscope", "slide preparation"],
    "Specimen Identification": ["specimen", "specimens", "identification", "taxonomy"],
    "Wildlife Conservation": ["wildlife", "conservation", "sanctuary"],
    "Laboratory Techniques": ["laboratory experiments", "wet lab", "lab techniques", "laboratory equipment"],
    "Mathematical Physics": ["physics", "mechanics", "classical mechanics"],
    "Thermodynamics": ["thermodynamics", "heat", "thermal"],
    "Electromagnetism": ["electromagnetism", "electricity", "magnetism"],
    "Optics": ["optics", "light", "lasers", "refraction"],
    "Laboratory Measurement": ["measurement", "error analysis", "data collection"],
    
    # Logistics
    "Supply Chain Analytics": ["supply chain", "logistics planning"],
    "Inventory Management": ["inventory management", "inventory"],
    "Forecasting": ["forecasting", "predicting demand"],
    
    # Soft Skills
    "Teamwork": ["teamwork", "collaboration", "team player"],
    "Communication": ["communication", "presentation", "presentations"],
    "Problem Solving": ["problem solving", "problem-solving"]
}

class ProductionNLPParser:
    def __init__(self):
        self.taxonomy_skills = set()
        for career in CAREER_TAXONOMY.values():
            for req in career["core_requirements"]:
                self.taxonomy_skills.add(req)
        
        # Build flat lookup for instant regex & fuzzy matching
        self.fuzzy_lookup = {}
        for canonical, aliases in SKILL_ALIASES.items():
            self.fuzzy_lookup[canonical.lower()] = canonical
            for alias in aliases:
                self.fuzzy_lookup[alias.lower()] = canonical
        for ts in self.taxonomy_skills:
            self.fuzzy_lookup[ts.lower()] = ts

    def clean_and_split_clauses(self, text):
        if not text: return []
        text = text.lower()
        # Protect special tech symbols before splitting
        text = text.replace("c++", "cplusplus").replace("c#", "csharp").replace("node.js", "nodejs")
        
        # Split by punctuation and conjunctions to isolate context (solves Negation & Parentheticals)
        clauses = re.split(r'[\.,;\(\)\n]| - | and | but | though | although |/|\+', text)
        return [c.strip() for c in clauses if c.strip()]

    def parse_student_bio(self, bio_text, registered_course):
        clauses = self.clean_and_split_clauses(bio_text)
        
        extracted_proficient = set()
        extracted_learning = set()
        
        # Context Window Keywords
        negation_terms = [r"don'?t know", r"not an expert", r"no experience", r"zero experience", r"never used"]
        learning_terms = [r"learning", r"interested in", r"exploring", r"want to learn", r"figuring out", r"familiar"]
        
        for clause in clauses:
            # 1. Negation Check: Skip clause entirely if negated
            if any(re.search(neg, clause) for neg in negation_terms):
                continue 
            
            # 2. Learning Check: Flag skills in this clause as "learning" (not proficient)
            is_learning = any(re.search(lt, clause) for lt in learning_terms)
            
            found_in_clause = set()
            
            # 3. Exact Word Boundary Matching (Fastest & Safest)
            for key, canonical in self.fuzzy_lookup.items():
                pattern = r'(?<!\w)' + re.escape(key) + r'(?!\w)'
                if re.search(pattern, clause):
                    found_in_clause.add(canonical)
            
            # 4. Fuzzy Typo Matching for Unmatched Words > 4 chars (e.g. Javscript, Pythn)
            words = clause.split()
            for w in words:
                if len(w) > 4:
                    matches = difflib.get_close_matches(w, self.fuzzy_lookup.keys(), n=1, cutoff=0.88)
                    if matches:
                        found_in_clause.add(self.fuzzy_lookup[matches[0]])
            
            # Route to correct bucket based on context
            if is_learning:
                extracted_learning.update(found_in_clause)
            else:
                extracted_proficient.update(found_in_clause)

        # Remove "learning" skills from "proficient" if they overlap
        extracted_proficient = extracted_proficient - extracted_learning

        # Detect effective course context
        bio_lower = bio_text.lower()
        effective_course = registered_course
        for course in COURSE_DISCIPLINES.keys():
            clean_name = course.lower().replace("bsc ", "").replace("ba ", "").replace("msc ", "").replace("phd ", "").strip()
            if clean_name in bio_lower or course.lower() in bio_lower:
                effective_course = course
                break
                
        is_low_signal = len(extracted_proficient) == 0

        return {
            "effective_course": effective_course,
            "extracted_skills": sorted(list(extracted_proficient)),
            "learning_skills": sorted(list(extracted_learning)),
            "is_low_signal": is_low_signal
        }

parser_instance = ProductionNLPParser()