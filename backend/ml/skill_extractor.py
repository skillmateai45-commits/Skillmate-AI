"""
Skill Extraction Module
Uses NLP techniques (TF-IDF + keyword matching) to identify
the skill or topic the user wants to learn from their text.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json


# Comprehensive skill taxonomy
SKILL_TAXONOMY = {
    # Programming Languages
    "python": {
        "keywords": ["python", "py", "django", "flask", "fastapi", "pandas", "numpy", "pip"],
        "category": "Programming Language",
        "description": "Python is a versatile, high-level programming language known for its simplicity and readability. It is widely used in web development, data science, machine learning, automation, and scripting."
    },
    "javascript": {
        "keywords": ["javascript", "js", "node", "nodejs", "react", "vue", "angular", "npm", "typescript"],
        "category": "Programming Language",
        "description": "JavaScript is the most popular programming language for web development. It powers interactive websites, server-side applications with Node.js, and mobile apps with React Native."
    },
    "java": {
        "keywords": ["java", "jvm", "spring", "spring boot", "maven", "gradle", "android"],
        "category": "Programming Language",
        "description": "Java is a robust, object-oriented programming language used for enterprise applications, Android development, and large-scale systems. It follows the 'Write Once, Run Anywhere' principle."
    },
    "c programming": {
        "keywords": ["c programming", "c language", "gcc", "pointers", "structs"],
        "category": "Programming Language",
        "description": "C is a foundational programming language that provides low-level memory access. It is the basis for many modern languages and is essential for system programming and embedded systems."
    },
    "c++": {
        "keywords": ["c++", "cpp", "stl", "object oriented", "oop"],
        "category": "Programming Language",
        "description": "C++ is an extension of C with object-oriented features. It is widely used in game development, system software, competitive programming, and performance-critical applications."
    },
    "rust": {
        "keywords": ["rust", "cargo", "ownership", "borrowing"],
        "category": "Programming Language",
        "description": "Rust is a systems programming language focused on safety, speed, and concurrency. It prevents memory errors at compile time and is increasingly used for web assembly and systems programming."
    },
    "go": {
        "keywords": ["go", "golang", "goroutine"],
        "category": "Programming Language",
        "description": "Go (Golang) is a statically typed language designed at Google. It excels at building scalable network services, cloud infrastructure, and concurrent applications."
    },

    # Web Development
    "web development": {
        "keywords": ["web development", "web dev", "website", "html", "css", "frontend", "front end", "backend", "back end", "full stack", "fullstack"],
        "category": "Web Development",
        "description": "Web Development involves building websites and web applications using HTML, CSS, and JavaScript. It includes frontend (user interface), backend (server logic), and full-stack development."
    },
    "react": {
        "keywords": ["react", "reactjs", "react.js", "hooks", "jsx", "redux", "next.js", "nextjs"],
        "category": "Web Framework",
        "description": "React is a popular JavaScript library by Facebook for building dynamic user interfaces. It uses a component-based architecture and virtual DOM for efficient rendering."
    },
    "html css": {
        "keywords": ["html", "css", "tailwind", "bootstrap", "sass", "scss", "flexbox", "grid"],
        "category": "Web Development",
        "description": "HTML and CSS are the foundation of web pages. HTML provides structure and content, while CSS handles styling and layout. Modern CSS includes Flexbox, Grid, and frameworks like TailwindCSS."
    },

    # Data Science & AI
    "data science": {
        "keywords": ["data science", "data analysis", "data analytics", "statistics", "visualization", "tableau", "power bi"],
        "category": "Data Science",
        "description": "Data Science combines statistics, programming, and domain expertise to extract insights from data. It involves data collection, cleaning, analysis, visualization, and storytelling."
    },
    "machine learning": {
        "keywords": ["machine learning", "ml", "deep learning", "neural network", "ai", "artificial intelligence", "tensorflow", "pytorch", "scikit", "sklearn"],
        "category": "Artificial Intelligence",
        "description": "Machine Learning is a branch of AI where computers learn patterns from data. It includes supervised learning, unsupervised learning, and deep learning with neural networks."
    },
    "artificial intelligence": {
        "keywords": ["artificial intelligence", "ai", "nlp", "natural language", "computer vision", "chatbot", "generative ai"],
        "category": "Artificial Intelligence",
        "description": "Artificial Intelligence enables machines to simulate human intelligence. Key areas include Natural Language Processing, Computer Vision, Robotics, and Generative AI."
    },

    # Database
    "database": {
        "keywords": ["database", "sql", "mysql", "postgresql", "postgres", "mongodb", "nosql", "sqlite", "oracle", "db"],
        "category": "Database",
        "description": "Databases store and manage structured data. SQL databases like PostgreSQL use tables, while NoSQL databases like MongoDB use documents. Database skills include design, querying, and optimization."
    },

    # Cloud & DevOps
    "cloud computing": {
        "keywords": ["cloud", "aws", "azure", "gcp", "google cloud", "amazon web services", "cloud computing"],
        "category": "Cloud Computing",
        "description": "Cloud Computing provides on-demand computing resources over the internet. Major platforms include AWS, Azure, and Google Cloud, offering services for compute, storage, AI, and more."
    },
    "devops": {
        "keywords": ["devops", "docker", "kubernetes", "k8s", "ci/cd", "jenkins", "terraform", "ansible", "git", "github"],
        "category": "DevOps",
        "description": "DevOps combines development and operations practices to automate deployment, testing, and infrastructure. Key tools include Docker, Kubernetes, Jenkins, and Terraform."
    },

    # Mobile Development
    "android development": {
        "keywords": ["android", "kotlin", "android studio", "mobile app", "play store"],
        "category": "Mobile Development",
        "description": "Android Development involves building mobile applications for Android devices using Kotlin or Java. Android Studio is the official IDE, and apps are distributed via the Google Play Store."
    },
    "ios development": {
        "keywords": ["ios", "swift", "swiftui", "xcode", "iphone", "app store", "apple"],
        "category": "Mobile Development",
        "description": "iOS Development involves building applications for Apple devices using Swift and Xcode. SwiftUI provides a modern declarative framework for building user interfaces."
    },

    # Cybersecurity
    "cybersecurity": {
        "keywords": ["cybersecurity", "security", "hacking", "ethical hacking", "penetration testing", "encryption", "firewall", "vulnerability"],
        "category": "Cybersecurity",
        "description": "Cybersecurity protects systems, networks, and data from digital attacks. It covers areas like ethical hacking, network security, cryptography, and incident response."
    },

    # Design
    "ui ux design": {
        "keywords": ["ui", "ux", "design", "figma", "user interface", "user experience", "wireframe", "prototype"],
        "category": "Design",
        "description": "UI/UX Design focuses on creating intuitive and visually appealing user interfaces. It involves user research, wireframing, prototyping, and visual design using tools like Figma."
    },
    "graphic design": {
        "keywords": ["graphic design", "photoshop", "illustrator", "canva", "adobe", "logo", "branding"],
        "category": "Design",
        "description": "Graphic Design creates visual content for communication. It uses tools like Adobe Photoshop, Illustrator, and Canva for creating logos, posters, social media graphics, and branding materials."
    },

    # Soft Skills
    "communication": {
        "keywords": ["communication", "speaking", "presentation", "public speaking", "debate"],
        "category": "Soft Skills",
        "description": "Communication skills encompass speaking, writing, and presenting ideas effectively. Strong communication is essential for leadership, teamwork, and professional success."
    },
    "leadership": {
        "keywords": ["leadership", "management", "team", "project management", "agile", "scrum"],
        "category": "Soft Skills",
        "description": "Leadership involves guiding teams toward goals, making decisions, and inspiring others. It includes project management methodologies like Agile and Scrum."
    },

    # Other Technical Skills
    "blockchain": {
        "keywords": ["blockchain", "crypto", "ethereum", "solidity", "smart contract", "web3", "bitcoin"],
        "category": "Blockchain",
        "description": "Blockchain is a decentralized ledger technology enabling secure, transparent transactions. It powers cryptocurrencies, smart contracts, and decentralized applications (DApps)."
    },
    "data structures": {
        "keywords": ["data structures", "algorithms", "dsa", "sorting", "searching", "tree", "graph", "linked list", "array", "stack", "queue", "leetcode", "competitive programming"],
        "category": "Computer Science",
        "description": "Data Structures and Algorithms form the foundation of computer science. They include arrays, linked lists, trees, graphs, and algorithms for sorting, searching, and optimization."
    },
    "networking": {
        "keywords": ["networking", "tcp", "ip", "http", "dns", "router", "switch", "network", "protocols", "osi"],
        "category": "Networking",
        "description": "Computer Networking covers how devices communicate over networks. It includes protocols like TCP/IP, HTTP, DNS, and concepts like routing, switching, and the OSI model."
    },
    "operating systems": {
        "keywords": ["operating system", "os", "linux", "unix", "windows", "kernel", "process", "thread", "memory management"],
        "category": "Computer Science",
        "description": "Operating Systems manage computer hardware and software resources. Key concepts include process management, memory management, file systems, and kernel architecture."
    },
}


class SkillExtractor:
    """Extract skills from text using NLP techniques."""

    def __init__(self):
        # Build TF-IDF vectors from skill descriptions + keywords
        self.skill_names = list(SKILL_TAXONOMY.keys())
        skill_docs = []
        for name in self.skill_names:
            skill = SKILL_TAXONOMY[name]
            doc = f"{name} {' '.join(skill['keywords'])} {skill['description']}"
            skill_docs.append(doc)

        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=3000
        )
        self.skill_vectors = self.vectorizer.fit_transform(skill_docs)

    def extract_skill(self, text):
        """
        Extract the most relevant skill from input text.

        Args:
            text: English text (already translated)

        Returns:
            dict with 'skill', 'category', 'description', 'confidence'
        """
        if not text or not text.strip():
            return {
                'skill': 'programming',
                'category': 'General',
                'description': 'Programming is the process of creating instructions for computers.',
                'confidence': 0.0
            }

        text_lower = text.lower().strip()

        # Method 1: Direct keyword matching (highest priority)
        best_match = None
        best_score = 0

        for skill_name, skill_data in SKILL_TAXONOMY.items():
            for keyword in skill_data['keywords']:
                if keyword.lower() in text_lower:
                    # Score based on keyword specificity (longer = more specific)
                    score = len(keyword) / max(len(text_lower), 1)
                    if score > best_score:
                        best_score = score
                        best_match = skill_name

        if best_match and best_score > 0.02:
            skill = SKILL_TAXONOMY[best_match]
            return {
                'skill': best_match,
                'category': skill['category'],
                'description': skill['description'],
                'confidence': min(round(best_score * 10, 3), 0.99)
            }

        # Method 2: TF-IDF cosine similarity
        try:
            text_vector = self.vectorizer.transform([text_lower])
            similarities = cosine_similarity(text_vector, self.skill_vectors)[0]
            best_idx = similarities.argmax()
            best_similarity = similarities[best_idx]

            if best_similarity > 0.05:
                skill_name = self.skill_names[best_idx]
                skill = SKILL_TAXONOMY[skill_name]
                return {
                    'skill': skill_name,
                    'category': skill['category'],
                    'description': skill['description'],
                    'confidence': round(float(best_similarity), 3)
                }
        except Exception:
            pass

        # Fallback: Return a general programming skill
        return {
            'skill': 'programming',
            'category': 'General',
            'description': 'Programming is the art of writing instructions for computers to perform specific tasks. Start with Python or JavaScript for a beginner-friendly experience.',
            'confidence': 0.1
        }

    def get_all_skills(self):
        """Return list of all available skills."""
        return [
            {
                'skill': name,
                'category': data['category'],
                'keywords': data['keywords']
            }
            for name, data in SKILL_TAXONOMY.items()
        ]


# Singleton instance
_extractor = None

def get_extractor():
    global _extractor
    if _extractor is None:
        _extractor = SkillExtractor()
    return _extractor


def extract_skill(text):
    """Convenience function for skill extraction."""
    return get_extractor().extract_skill(text)
