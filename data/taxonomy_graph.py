# data/taxonomy_graph.py

# Complete discipline mapping for the 14 college streams
COURSE_DISCIPLINES = {
    # UG Programmes (9)
    "BA Functional English": "Humanities & Linguistics",
    "BA Social Science-Economics": "Economics & Public Policy",
    "BCom": "Commerce, Finance & Accounting",
    "BSc Chemistry": "Chemical & Material Sciences",
    "BSc Computer Science": "Computer Science & Software",
    "BSc Data Science & Logistics": "Data Science, Supply Chain & Logistics",
    "BSc Physics": "Physical Sciences & Engineering",
    "BSc Mathematics": "Mathematical & Statistical Sciences",
    "BSc Zoology": "Biological & Ecological Sciences",
    # PG Programmes (2)
    "MSc Computer Science": "Computer Science & Software",
    "MSc Mathematics": "Mathematical & Statistical Sciences",
    # PhD Programmes (3)
    "PhD Computer Science": "Computer Science & Software",
    "PhD Mathematics": "Mathematical & Statistical Sciences",
    "PhD Zoology": "Biological & Ecological Sciences"
}

# Standardized Career Taxonomy (Derived from O*NET / ESCO categories)
# Semantic corpus enables dense vector cosine projection for any student bio
CAREER_TAXONOMY = {
    # --- Biological & Ecological Sciences (Zoology) ---
    "Wildlife Biologist": {
        "discipline": "Biological & Ecological Sciences",
        "semantic_profile": "wildlife biology fauna animal behavior conservation ecology biodiversity field surveys habitat management species identification census animal tracking telemetry zoology",
        "core_requirements": ["Animal Biology", "Ecology", "Biodiversity", "Field Research", "Wildlife Conservation", "Specimen Identification", "GIS Basics"]
    },
    "Zoological Researcher": {
        "discipline": "Biological & Ecological Sciences",
        "semantic_profile": "zoological research taxonomy comparative anatomy animal physiology genetics microscopy cell biology evolutionary biology histology wet lab protocols",
        "core_requirements": ["Animal Biology", "Genetics", "Cell Biology", "Physiology", "Microscopy", "Laboratory Techniques", "Specimen Identification"]
    },
    "Biodiversity Conservation Officer": {
        "discipline": "Biological & Ecological Sciences",
        "semantic_profile": "biodiversity conservation environmental policy ecosystem restoration endangered species protected areas wildlife protection community forestry ecological monitoring",
        "core_requirements": ["Biodiversity", "Wildlife Conservation", "Animal Biology", "Ecology", "Environmental Policy", "Data Collection"]
    },
    "Ecological Consultant": {
        "discipline": "Biological & Ecological Sciences",
        "semantic_profile": "ecological impact assessment flora fauna auditing environmental regulations biostatistics habitat restoration planning sustainability consultancy field sampling",
        "core_requirements": ["Ecology", "Biodiversity", "Wildlife Conservation", "Biostatistics", "Environmental Assessment", "Report Drafting"]
    },
    "Clinical Lab Technologist": {
        "discipline": "Biological & Ecological Sciences",
        "semantic_profile": "clinical pathology hematology specimen analysis diagnostic microscopy microbiology biochemical assays lab safety quality assurance diagnostic instrumentation",
        "core_requirements": ["Laboratory Techniques", "Microscopy", "Cell Biology", "Anatomy & Physiology", "Specimen Identification", "Quality Control"]
    },

    # --- Chemical & Material Sciences (Chemistry) ---
    "Quality Control Chemist": {
        "discipline": "Chemical & Material Sciences",
        "semantic_profile": "analytical chemistry chromatography hplc gc spectroscopy spectrophotometry quality control wet chemistry titration gmp standard operating procedures glp assays",
        "core_requirements": ["Analytical Chemistry", "Chromatography", "Spectroscopy", "Lab Safety & Quality Control", "Wet Chemistry", "Titration"]
    },
    "Pharmaceutical Formulation Scientist": {
        "discipline": "Chemical & Material Sciences",
        "semantic_profile": "pharmaceutical formulation organic chemistry drug delivery preformulation excipients chemical synthesis dissolution testing stability studies lab synthesis",
        "core_requirements": ["Organic Chemistry", "Analytical Chemistry", "Wet Chemistry", "Chemical Synthesis", "Formulation Science", "Lab Safety & Quality Control"]
    },
    "Analytical Chemist": {
        "discipline": "Chemical & Material Sciences",
        "semantic_profile": "spectroscopy nmr ftir mass spectrometry chromatography separation techniques quantitative chemical analysis instrument calibration data validation method development",
        "core_requirements": ["Analytical Chemistry", "Spectroscopy", "Chromatography", "Titration", "Instrument Calibration", "Data Modeling"]
    },
    "Chemical Safety Specialist": {
        "discipline": "Chemical & Material Sciences",
        "semantic_profile": "chemical safety hazard communication msds osha epa hazardous waste containment industrial hygiene toxic substances handling environmental compliance",
        "core_requirements": ["Lab Safety & Quality Control", "Inorganic Chemistry", "Organic Chemistry", "Hazardous Waste Management", "Regulatory Compliance"]
    },
    "Industrial R&D Chemist": {
        "discipline": "Chemical & Material Sciences",
        "semantic_profile": "applied research industrial chemistry organic synthesis catalyst design polymer reactions process optimization pilot plant scaleup reaction monitoring",
        "core_requirements": ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Chemical Synthesis", "Analytical Chemistry", "Process Optimization"]
    },

    # --- Computer Science & Software ---
    "Full Stack Developer": {
        "discipline": "Computer Science & Software",
        "semantic_profile": "full stack web development html css javascript react vue nodejs python sql rest api responsive design backend frontend database architecture git version control",
        "core_requirements": ["HTML/CSS", "JavaScript", "Python", "SQL", "Web Development", "Git", "REST APIs"]
    },
    "Frontend Engineer": {
        "discipline": "Computer Science & Software",
        "semantic_profile": "frontend engineering client side user interface ui ux react nextjs vue typescript tailwind javascript browser performance web design responsive web apps",
        "core_requirements": ["HTML/CSS", "JavaScript", "React or Vue", "Git", "Web Development", "UI/UX Design", "Responsive Layouts"]
    },
    "Backend Developer": {
        "discipline": "Computer Science & Software",
        "semantic_profile": "backend architecture server side python django flask fastapi relational databases postgresql mysql mongodb api microservices redis distributed caching",
        "core_requirements": ["Python", "SQL", "Database Management", "Algorithms", "Git", "REST APIs", "Data Structures"]
    },
    "Software Engineer": {
        "discipline": "Computer Science & Software",
        "semantic_profile": "software engineering algorithms data structures object oriented programming oop python c++ java unit testing debugging refactoring git system design",
        "core_requirements": ["Data Structures", "Algorithms", "Object Oriented Programming", "Git", "Python", "SQL", "Unit Testing"]
    },
    "Machine Learning Engineer": {
        "discipline": "Computer Science & Software",
        "semantic_profile": "machine learning deep learning pytorch tensorflow neural networks computer vision natural language processing predictive modeling model training scikit-learn",
        "core_requirements": ["Python", "Machine Learning", "Deep Learning", "Linear Algebra", "Algorithms", "PyTorch or TensorFlow", "Model Deployment"]
    },
    "AI Solutions Architect": {
        "discipline": "Computer Science & Software",
        "semantic_profile": "artificial intelligence system architecture scalable ml pipelines cloud ai distributed deep learning high performance computing llm enterprise deployment",
        "core_requirements": ["Machine Learning", "Deep Learning", "Distributed Systems", "Cloud Architecture", "Advanced Algorithms", "System Design"]
    },
    "Cloud DevOps Engineer": {
        "discipline": "Computer Science & Software",
        "semantic_profile": "cloud computing devops aws azure docker kubernetes ci cd automation linux scripting infrastructure as code terraform monitoring microservices",
        "core_requirements": ["Git", "Docker & Kubernetes", "Cloud Architecture", "Linux", "Automation Scripts", "Computer Networks"]
    },
    "Cybersecurity Analyst": {
        "discipline": "Computer Science & Software",
        "semantic_profile": "cybersecurity network security ethical hacking vulnerability assessment penetration testing firewalls cryptography incident response threat mitigation linux",
        "core_requirements": ["Computer Networks", "Information Security", "Linux", "Ethical Hacking", "Python", "Cryptography"]
    },

    # --- Data Science, Supply Chain & Logistics ---
    "Logistics Analyst": {
        "discipline": "Data Science, Supply Chain & Logistics",
        "semantic_profile": "logistics optimization supply chain analytics warehouse operations transportation freight planning inventory control sql operations research distribution network",
        "core_requirements": ["Supply Chain Analytics", "SQL", "Warehouse Optimization", "Inventory Management", "Operations Research", "Data Visualization"]
    },
    "Supply Chain Data Scientist": {
        "discipline": "Data Science, Supply Chain & Logistics",
        "semantic_profile": "supply chain forecasting predictive modeling python machine learning vehicle routing operations research simulation dashboarding supply risk analytics",
        "core_requirements": ["Supply Chain Analytics", "Predictive Modeling", "Python", "Operations Research", "SQL", "Dashboarding"]
    },
    "Business Intelligence Developer": {
        "discipline": "Data Science, Supply Chain & Logistics",
        "semantic_profile": "business intelligence power bi tableau etl pipelines sql data warehousing kpi reporting dashboard analytics data cleaning business metrics",
        "core_requirements": ["SQL", "Tableau & PowerBI", "Data Cleaning", "Data Modeling", "Predictive Modeling", "ETL Pipelines"]
    },
    "Inventory Demand Planner": {
        "discipline": "Data Science, Supply Chain & Logistics",
        "semantic_profile": "demand forecasting safety stock calculation inventory optimization procurement planning operations research mathematical modeling excel supply management",
        "core_requirements": ["Inventory Management", "Operations Research", "Supply Chain Analytics", "Predictive Modeling", "Excel", "Forecasting"]
    },

    # --- Mathematical & Statistical Sciences (Maths) ---
    "Quantitative Analyst": {
        "discipline": "Mathematical & Statistical Sciences",
        "semantic_profile": "quantitative finance financial modeling calculus linear algebra probability stochastic processes algorithmic trading time series risk analysis python",
        "core_requirements": ["Calculus", "Linear Algebra", "Probability Theory", "Python", "Financial Modeling", "Time Series Analysis"]
    },
    "Actuarial Trainee": {
        "discipline": "Mathematical & Statistical Sciences",
        "semantic_profile": "actuarial science risk assessment probability statistics mortality tables life insurance annuities financial mathematics financial projections",
        "core_requirements": ["Probability Theory", "Calculus", "Statistical Inference", "Financial Modeling", "Excel", "Risk Management"]
    },
    "Data Scientist": {
        "discipline": "Mathematical & Statistical Sciences",
        "semantic_profile": "data science applied statistics machine learning exploratory data analysis python sql hypothesis testing linear regression clustering predictive analytics",
        "core_requirements": ["Python", "SQL", "Probability Theory", "Linear Algebra", "Predictive Modeling", "Data Cleaning", "Statistical Modeling"]
    },
    "Cryptographic Specialist": {
        "discipline": "Mathematical & Statistical Sciences",
        "semantic_profile": "cryptography discrete mathematics number theory abstract algebra encryption algorithms public key infrastructure cryptographic protocols network security",
        "core_requirements": ["Discrete Mathematics", "Linear Algebra", "Cryptographic Algorithms", "Python", "Information Security"]
    },

    # --- Commerce, Finance & Accounting (BCom) ---
    "Chartered Accountant Trainee": {
        "discipline": "Commerce, Finance & Accounting",
        "semantic_profile": "chartered accountancy statutory audit financial accounting corporate taxation direct tax gst compliance bookkeeping ledger balance sheet ifrs",
        "core_requirements": ["Financial Accounting", "Corporate Taxation", "Auditing", "Cost Accounting", "GST Compliance", "Financial Reporting"]
    },
    "Financial Analyst": {
        "discipline": "Commerce, Finance & Accounting",
        "semantic_profile": "financial analysis corporate finance valuation discounted cash flow financial modeling excel balance sheet ratio analysis investment portfolio",
        "core_requirements": ["Financial Accounting", "Corporate Taxation", "Financial Modeling", "Auditing", "Excel", "Investment Analysis"]
    },
    "Corporate Tax Consultant": {
        "discipline": "Commerce, Finance & Accounting",
        "semantic_profile": "tax advisory corporate taxation income tax compliance indirect taxes gst filings transfer pricing cross border taxation audit representation",
        "core_requirements": ["Corporate Taxation", "GST Compliance", "Financial Accounting", "Direct Tax Laws", "Statutory Filings"]
    },
    "Statutory Audit Associate": {
        "discipline": "Commerce, Finance & Accounting",
        "semantic_profile": "statutory auditing internal controls substantive testing audit sampling documentation compliance audit verification risk assessment financial statements",
        "core_requirements": ["Auditing", "Financial Accounting", "Statutory Compliance", "Internal Controls", "Documentation"]
    },

    # --- Economics & Public Policy (BA Economics) ---
    "Economic Analyst": {
        "discipline": "Economics & Public Policy",
        "semantic_profile": "microeconomics macroeconomics econometrics statistical analysis economic indicators monetary policy fiscal analysis market forecasting data collection",
        "core_requirements": ["Microeconomics", "Macroeconomics", "Econometrics", "Statistical Analysis", "Data Collection", "Market Research"]
    },
    "Public Policy Researcher": {
        "discipline": "Economics & Public Policy",
        "semantic_profile": "public policy policy evaluation socioeconomic research governance development economics policy briefs qualitative research survey methodology",
        "core_requirements": ["Public Policy", "Econometrics", "Microeconomics", "Policy Evaluation", "Statistical Analysis", "Report Drafting"]
    },
    "Market Risk Analyst": {
        "discipline": "Economics & Public Policy",
        "semantic_profile": "market risk value at risk var financial econometrics macroeconomic volatility liquidity risk financial modeling regulatory capital stress testing",
        "core_requirements": ["Financial Modeling", "Macroeconomics", "Statistical Analysis", "Probability Theory", "Econometrics"]
    },

    # --- Humanities & Linguistics (BA Functional English) ---
    "Content Strategist": {
        "discipline": "Humanities & Linguistics",
        "semantic_profile": "content strategy creative writing copywriting seo digital content editorial planning brand storytelling marketing communications content auditing",
        "core_requirements": ["Content Writing", "Copywriting", "SEO Optimization", "Corporate Communications", "Editing", "Media Writing"]
    },
    "Technical Writer": {
        "discipline": "Humanities & Linguistics",
        "semantic_profile": "technical writing documentation api documentation user manuals software guides clear communication editing linguistics developer docs markdown",
        "core_requirements": ["Content Writing", "Linguistics", "Editing", "Technical Documentation", "Critical Reading", "API Basics"]
    },
    "Public Relations Specialist": {
        "discipline": "Humanities & Linguistics",
        "semantic_profile": "public relations corporate communications media outreach press release crisis management speechwriting stakeholder engagement reputation management",
        "core_requirements": ["Corporate Communications", "Public Relations", "Media Writing", "Creative Writing", "Editing", "Crisis Management"]
    },

    # --- Physical Sciences & Engineering (Physics) ---
    "Applied Physicist": {
        "discipline": "Physical Sciences & Engineering",
        "semantic_profile": "applied physics electromagnetism thermodynamics quantum mechanics computational physics numerical simulation mathematical modeling instrumentation",
        "core_requirements": ["Mathematical Physics", "Thermodynamics", "Electromagnetism", "Laboratory Measurement", "Optics", "Data Modeling"]
    },
    "Optical Systems Engineer": {
        "discipline": "Physical Sciences & Engineering",
        "semantic_profile": "optics photonics lasers lens design optical alignment instrumentation electromagnetic radiation fiber optics laboratory measurement optical testing",
        "core_requirements": ["Optics", "Electromagnetism", "Instrumentation", "Laboratory Measurement", "Mathematical Physics"]
    }
}