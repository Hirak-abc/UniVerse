import os

def get_academic_corner_page():
    # Project ideas section
    project_ideas = [
        "Build a Social Media Platform",
        "Create a PUBG-style Multiplayer Game",
        "AI-based Adaptive Learning System",
        "Image-based Product Search Engine",
        "Fake News Detection System",
        "Create a Search Engine for a Specific Domain",
        "OCR and Summarization Tool for Notes",
        "AI-Powered Meme Generator",
        "E-Commerce Price Comparison + Tracker",
        "Multiplayer Coding + Reasoning Battle Platform"
    ]

    project_ideas_html = "<h2 class='text-xl font-bold mb-4'>Here are some ideas for you to work upon in the next 4 years:</h2><ul class='list-disc pl-6 mb-8'>"
    for idea in project_ideas:
        project_ideas_html += f"<li>{idea}</li>\n"
    project_ideas_html += "</ul>"

    # Novel list
    novels = [
        "The Conch Bearer",
        "The Alchemist",
        "The Diary of a Young Girl",
        "The Art of Happiness",
        "The White Tiger",
        "Life of Pi",
        "Educated",
        "Ikigai",
        "Eat That Frog",
        "Atomic Habits"
    ]

    novels_html = ""
    for novel in novels:
        novels_html += f"<li>{novel}</li>\n"

    # Curriculum data
    curriculum = [
        {
            "semester": "Semester 1",
            "credits": "21 Credits",
            "Mathematics": "Math 113 (4): Linear Algebra",
            "Communication & Ethics": "LE 101 (4): Intro to Communication and Ethics<br>LE 101P (1): Books, Club and Social Emotional Intelligence",
            "Programming": "CS 106 (5): Programming Methodology in Python",
            "Core/Data": "CS 105 (4): Introduction to Computers",
            "Systems/Security": "",
            "AI/ML": "",
            "Project": "CS 106P (3): CS 106 Python Project Course"
        },
        {
            "semester": "Semester 2",
            "credits": "20 Credits",
            "Mathematics": "Math 119 (4): Calculus<br>CS 103 (4): Mathematical Foundations of Computing",
            "Communication & Ethics": "LE 102 (3): Communication and Ethics<br>LE 102P (1): Books, Club and Social Emotional Intelligence 2",
            "Programming": "CS 110 (4): Data Handling in Python",
            "Core/Data": "CS 161 (4): Data Structures and Algorithms",
            "Systems/Security": "",
            "AI/ML": "",
            "Project": ""
        },
        {
            "semester": "Semester 3",
            "credits": "24 Credits",
            "Mathematics": "CS 109 (4): Probability for Computer Science",
            "Communication & Ethics": "LE 103P (1): Communication and Book Club",
            "Programming": "CS 108A (5): Object Oriented Programming",
            "Core/Data": "CS 162 (4): Advanced Data Structures and Algorithms<br>CS 145 (4): Database Management Systems",
            "Systems/Security": "",
            "AI/ML": "CS 221 (4): Artificial Intelligence",
            "Project": "CoCo Summer (2)"
        },
        {
            "semester": "Semester 4",
            "credits": "21 Credits",
            "Mathematics": "",
            "Communication & Ethics": "",
            "Programming": "CS 108B (5): Advanced Object Oriented Programming",
            "Core/Data": "CS 276 (4): Search Engines and Information Retrieval<br>CS 246 (4): Mining Massive Datasets",
            "Systems/Security": "CS 107 (4): Computer Organization and Systems",
            "AI/ML": "CS 229 (4): Machine Learning",
            "Project": ""
        },
        {
            "semester": "Semester 5",
            "credits": "24 Credits",
            "Mathematics": "",
            "Communication & Ethics": "",
            "Programming": "CS 142 (4): Web Applications Development",
            "Core/Data": "Cornell CS 305 (4): Creative Problem Solving",
            "Systems/Security": "CS 111 (4): Operating Systems Principles",
            "AI/ML": "CS 230 (4): Deep Learning",
            "Project": "Internship (4)<br>CS 250 (4): Software Engineering Project, Including Technical Writing"
        },
        {
            "semester": "Semester 6",
            "credits": "20 Credits",
            "Mathematics": "LE 300 (4): Economics for Computer Science",
            "Communication & Ethics": "",
            "Programming": "CS 147 (4): Human Computer Interaction",
            "Core/Data": "",
            "Systems/Security": "CS 144 (4): Computer Networks",
            "AI/ML": "CS 231 (4): Applications of Deep Learning",
            "Project": "CS 251 (4): Machine Learning Project"
        },
        {
            "semester": "Semester 7",
            "credits": "20 Credits",
            "Mathematics": "",
            "Communication & Ethics": "",
            "Programming": "",
            "Core/Data": "",
            "Systems/Security": "",
            "AI/ML": "",
            "Project": "Industry Research Project and Internship"
        },
        {
            "semester": "Semester 8",
            "credits": "20 Credits",
            "Mathematics": "",
            "Communication & Ethics": "",
            "Programming": "",
            "Core/Data": "",
            "Systems/Security": "",
            "AI/ML": "",
            "Project": "Industry Research Project and Internship"
        },
    ]

    headers = [
        "Semester", "Mathematics", "Communication & Ethics", "Programming",
        "Core/Data", "Systems/Security", "AI/ML", "Project"
    ]

    curriculum_html = '<table class="w-full text-sm text-left text-gray-700 bg-white shadow-md rounded overflow-hidden">'
    curriculum_html += '<thead class="bg-gray-200"><tr>' + ''.join(f"<th class='p-3'>{h}</th>" for h in headers) + '</tr></thead><tbody>'

    for row in curriculum:
        curriculum_html += '<tr>'
        for h in headers:
            curriculum_html += f"<td class='p-3 align-top'>{row.get(h, '')}</td>"
        curriculum_html += '</tr>'

    curriculum_html += '</tbody></table>'

    # Read base HTML template
    template_path = os.path.join("templates", "academic_corner.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    # Inject HTML fragments
    html_filled = (
        html_template
        .replace("{{ project_ideas_html }}", project_ideas_html)
        .replace("{{ novels_html }}", novels_html)
        .replace("{{ curriculum_html }}", curriculum_html)
    )

    return html_filled
