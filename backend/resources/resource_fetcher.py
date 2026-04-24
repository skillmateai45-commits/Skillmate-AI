"""
Resource Fetcher Module
Provides curated learning resources for detected skills:
- Official documentation links
- YouTube video/playlist links
- Wikipedia article links
"""

import requests
import urllib.parse


# Curated resource database for each skill
RESOURCE_DATABASE = {
    "python": {
        "docs": [
            {"title": "Python Official Documentation", "url": "https://docs.python.org/3/", "type": "official"},
            {"title": "Python Tutorial — W3Schools", "url": "https://www.w3schools.com/python/", "type": "tutorial"},
            {"title": "Real Python Tutorials", "url": "https://realpython.com/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Python for Beginners — freeCodeCamp", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw", "type": "video"},
            {"title": "Python Full Course — Bro Code", "url": "https://www.youtube.com/watch?v=XKHEtdqhLK8", "type": "video"},
            {"title": "Python Tutorial — Programming with Mosh", "url": "https://www.youtube.com/watch?v=_uQrJ0TkZlc", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Python_(programming_language)"
    },
    "javascript": {
        "docs": [
            {"title": "MDN JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "type": "official"},
            {"title": "JavaScript.info", "url": "https://javascript.info/", "type": "tutorial"},
            {"title": "JavaScript — W3Schools", "url": "https://www.w3schools.com/js/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "JavaScript Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=PkZNo7MFNFg", "type": "video"},
            {"title": "JavaScript Tutorial — Bro Code", "url": "https://www.youtube.com/watch?v=8dWL3wF_OMw", "type": "video"},
            {"title": "JavaScript Crash Course — Traversy Media", "url": "https://www.youtube.com/watch?v=hdI2bqOjy3c", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/JavaScript"
    },
    "java": {
        "docs": [
            {"title": "Oracle Java Documentation", "url": "https://docs.oracle.com/javase/tutorial/", "type": "official"},
            {"title": "Java — W3Schools", "url": "https://www.w3schools.com/java/", "type": "tutorial"},
            {"title": "Baeldung Java Tutorials", "url": "https://www.baeldung.com/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Java Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=grEKMHGYyns", "type": "video"},
            {"title": "Java Tutorial — Bro Code", "url": "https://www.youtube.com/watch?v=xk4_1vDrzzo", "type": "video"},
            {"title": "Java Programming — Telusko", "url": "https://www.youtube.com/watch?v=BGTx91t8q50", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Java_(programming_language)"
    },
    "c programming": {
        "docs": [
            {"title": "C Programming — cppreference", "url": "https://en.cppreference.com/w/c", "type": "official"},
            {"title": "C Tutorial — W3Schools", "url": "https://www.w3schools.com/c/", "type": "tutorial"},
            {"title": "Learn C — Programiz", "url": "https://www.programiz.com/c-programming", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "C Programming Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=KJgsSFOSQv0", "type": "video"},
            {"title": "C Programming — Bro Code", "url": "https://www.youtube.com/watch?v=87SH2Cn0s9A", "type": "video"},
            {"title": "C Language Tutorial — Neso Academy", "url": "https://www.youtube.com/watch?v=rLf3jnHxSmU", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/C_(programming_language)"
    },
    "c++": {
        "docs": [
            {"title": "C++ Reference", "url": "https://en.cppreference.com/w/cpp", "type": "official"},
            {"title": "C++ Tutorial — W3Schools", "url": "https://www.w3schools.com/cpp/", "type": "tutorial"},
            {"title": "LearnCpp.com", "url": "https://www.learncpp.com/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "C++ Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=vLnPwxZdW4Y", "type": "video"},
            {"title": "C++ Tutorial — Bro Code", "url": "https://www.youtube.com/watch?v=-TkoO8Z07hI", "type": "video"},
            {"title": "C++ Programming — The Cherno", "url": "https://www.youtube.com/watch?v=18c3MTI0balw", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/C%2B%2B"
    },
    "web development": {
        "docs": [
            {"title": "MDN Web Docs", "url": "https://developer.mozilla.org/en-US/", "type": "official"},
            {"title": "freeCodeCamp Curriculum", "url": "https://www.freecodecamp.org/", "type": "tutorial"},
            {"title": "The Odin Project", "url": "https://www.theodinproject.com/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Web Development Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=nu_pCVPKzTk", "type": "video"},
            {"title": "HTML CSS JavaScript — SuperSimpleDev", "url": "https://www.youtube.com/watch?v=G3e-cpL7ofc", "type": "video"},
            {"title": "Frontend Web Development — Traversy Media", "url": "https://www.youtube.com/watch?v=zJSY8tbf_ys", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Web_development"
    },
    "react": {
        "docs": [
            {"title": "React Official Documentation", "url": "https://react.dev/", "type": "official"},
            {"title": "React Tutorial — W3Schools", "url": "https://www.w3schools.com/react/", "type": "tutorial"},
            {"title": "React Patterns", "url": "https://reactpatterns.com/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "React Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8", "type": "video"},
            {"title": "React Tutorial — Net Ninja", "url": "https://www.youtube.com/watch?v=j942wKiXFu8", "type": "video"},
            {"title": "React JS Crash Course — Traversy Media", "url": "https://www.youtube.com/watch?v=LDB4uaJ87e0", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/React_(software)"
    },
    "html css": {
        "docs": [
            {"title": "MDN HTML Reference", "url": "https://developer.mozilla.org/en-US/docs/Web/HTML", "type": "official"},
            {"title": "MDN CSS Reference", "url": "https://developer.mozilla.org/en-US/docs/Web/CSS", "type": "official"},
            {"title": "CSS Tricks", "url": "https://css-tricks.com/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "HTML & CSS Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=mU6anWqZJcc", "type": "video"},
            {"title": "HTML CSS Tutorial — SuperSimpleDev", "url": "https://www.youtube.com/watch?v=G3e-cpL7ofc", "type": "video"},
            {"title": "CSS Crash Course — Traversy Media", "url": "https://www.youtube.com/watch?v=yfoY53QXEnI", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/CSS"
    },
    "data science": {
        "docs": [
            {"title": "Kaggle Learn", "url": "https://www.kaggle.com/learn", "type": "tutorial"},
            {"title": "DataCamp", "url": "https://www.datacamp.com/", "type": "tutorial"},
            {"title": "Towards Data Science", "url": "https://towardsdatascience.com/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Data Science Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=ua-CiDNNj30", "type": "video"},
            {"title": "Data Science Tutorial — Simplilearn", "url": "https://www.youtube.com/watch?v=-ETQ97mXXF0", "type": "video"},
            {"title": "Data Analysis with Python — freeCodeCamp", "url": "https://www.youtube.com/watch?v=r-uOLxNrNk8", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Data_science"
    },
    "machine learning": {
        "docs": [
            {"title": "scikit-learn Documentation", "url": "https://scikit-learn.org/stable/", "type": "official"},
            {"title": "TensorFlow Documentation", "url": "https://www.tensorflow.org/", "type": "official"},
            {"title": "Google ML Crash Course", "url": "https://developers.google.com/machine-learning/crash-course", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Machine Learning Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=NWONeJKn6kc", "type": "video"},
            {"title": "ML Tutorial — StatQuest", "url": "https://www.youtube.com/watch?v=Gv9_4yMHFhI", "type": "video"},
            {"title": "Machine Learning — Andrew Ng (Stanford)", "url": "https://www.youtube.com/watch?v=jGwO_UgTS7I", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Machine_learning"
    },
    "artificial intelligence": {
        "docs": [
            {"title": "AI — Google Developers", "url": "https://ai.google/", "type": "official"},
            {"title": "OpenAI Documentation", "url": "https://platform.openai.com/docs", "type": "official"},
            {"title": "Elements of AI", "url": "https://www.elementsofai.com/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Artificial Intelligence Full Course — Edureka", "url": "https://www.youtube.com/watch?v=JMUxmLyrhSk", "type": "video"},
            {"title": "AI for Everyone — Andrew Ng", "url": "https://www.youtube.com/watch?v=4lSwtIjAv4s", "type": "video"},
            {"title": "AI Crash Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=aircAruvnKk", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Artificial_intelligence"
    },
    "database": {
        "docs": [
            {"title": "PostgreSQL Documentation", "url": "https://www.postgresql.org/docs/", "type": "official"},
            {"title": "SQL Tutorial — W3Schools", "url": "https://www.w3schools.com/sql/", "type": "tutorial"},
            {"title": "MongoDB Documentation", "url": "https://www.mongodb.com/docs/", "type": "official"},
        ],
        "youtube": [
            {"title": "SQL Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY", "type": "video"},
            {"title": "MySQL Tutorial — Bro Code", "url": "https://www.youtube.com/watch?v=5OdVJbNCSso", "type": "video"},
            {"title": "MongoDB Crash Course — Traversy Media", "url": "https://www.youtube.com/watch?v=-56x56UppqQ", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Database"
    },
    "cloud computing": {
        "docs": [
            {"title": "AWS Documentation", "url": "https://docs.aws.amazon.com/", "type": "official"},
            {"title": "Google Cloud Docs", "url": "https://cloud.google.com/docs", "type": "official"},
            {"title": "Azure Documentation", "url": "https://learn.microsoft.com/en-us/azure/", "type": "official"},
        ],
        "youtube": [
            {"title": "Cloud Computing Full Course — Simplilearn", "url": "https://www.youtube.com/watch?v=EN4fEbcFZ_E", "type": "video"},
            {"title": "AWS Certified Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=SOTamWNgDKc", "type": "video"},
            {"title": "Cloud Computing Explained", "url": "https://www.youtube.com/watch?v=M988_fsOSWo", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Cloud_computing"
    },
    "devops": {
        "docs": [
            {"title": "Docker Documentation", "url": "https://docs.docker.com/", "type": "official"},
            {"title": "Kubernetes Documentation", "url": "https://kubernetes.io/docs/", "type": "official"},
            {"title": "DevOps Roadmap", "url": "https://roadmap.sh/devops", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "DevOps Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=j5Zsa_eOXeY", "type": "video"},
            {"title": "Docker Tutorial — TechWorld with Nana", "url": "https://www.youtube.com/watch?v=3c-iBn73dDE", "type": "video"},
            {"title": "Kubernetes Course — TechWorld with Nana", "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/DevOps"
    },
    "android development": {
        "docs": [
            {"title": "Android Developers", "url": "https://developer.android.com/", "type": "official"},
            {"title": "Kotlin Documentation", "url": "https://kotlinlang.org/docs/home.html", "type": "official"},
            {"title": "Android Codelabs", "url": "https://developer.android.com/codelabs", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Android Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=fis26HvvDII", "type": "video"},
            {"title": "Kotlin for Android — Philipp Lackner", "url": "https://www.youtube.com/watch?v=EExSSotojVI", "type": "video"},
            {"title": "Android Development for Beginners", "url": "https://www.youtube.com/watch?v=tZvjSl9dswg", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Android_(operating_system)"
    },
    "cybersecurity": {
        "docs": [
            {"title": "OWASP Top 10", "url": "https://owasp.org/www-project-top-ten/", "type": "official"},
            {"title": "TryHackMe", "url": "https://tryhackme.com/", "type": "tutorial"},
            {"title": "HackTheBox", "url": "https://www.hackthebox.com/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Cybersecurity Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=U_P23SqJaDc", "type": "video"},
            {"title": "Ethical Hacking Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=3Kq1MIfTWCE", "type": "video"},
            {"title": "Cybersecurity for Beginners — NetworkChuck", "url": "https://www.youtube.com/watch?v=rcDO8km6R6c", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Computer_security"
    },
    "ui ux design": {
        "docs": [
            {"title": "Figma Learn", "url": "https://help.figma.com/hc/en-us", "type": "official"},
            {"title": "Laws of UX", "url": "https://lawsofux.com/", "type": "tutorial"},
            {"title": "Google Material Design", "url": "https://m3.material.io/", "type": "official"},
        ],
        "youtube": [
            {"title": "UI/UX Design Tutorial — freeCodeCamp", "url": "https://www.youtube.com/watch?v=c9Wg6Cb_YlU", "type": "video"},
            {"title": "Figma Full Course — DesignCourse", "url": "https://www.youtube.com/watch?v=jwCmIBJ8Jtc", "type": "video"},
            {"title": "UX Design Course — Google", "url": "https://www.youtube.com/watch?v=4EZz-Hrjb7Q", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/User_experience_design"
    },
    "data structures": {
        "docs": [
            {"title": "GeeksforGeeks DSA", "url": "https://www.geeksforgeeks.org/data-structures/", "type": "tutorial"},
            {"title": "LeetCode", "url": "https://leetcode.com/", "type": "tutorial"},
            {"title": "Visualgo — Visualize Algorithms", "url": "https://visualgo.net/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "DSA Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=8hly31xKli0", "type": "video"},
            {"title": "Data Structures — Abdul Bari", "url": "https://www.youtube.com/watch?v=0IAPZzGSbME", "type": "video"},
            {"title": "Algorithms Course — MIT OpenCourseWare", "url": "https://www.youtube.com/watch?v=HtSuA80QTyo", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Data_structure"
    },
    "rust": {
        "docs": [
            {"title": "The Rust Book", "url": "https://doc.rust-lang.org/book/", "type": "official"},
            {"title": "Rust by Example", "url": "https://doc.rust-lang.org/rust-by-example/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Rust Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=BpPEoZW5IiY", "type": "video"},
            {"title": "Rust Programming — Let's Get Rusty", "url": "https://www.youtube.com/watch?v=OX9HJsJUDxA", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Rust_(programming_language)"
    },
    "go": {
        "docs": [
            {"title": "Go Official Documentation", "url": "https://go.dev/doc/", "type": "official"},
            {"title": "Go by Example", "url": "https://gobyexample.com/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Go Programming — freeCodeCamp", "url": "https://www.youtube.com/watch?v=un6ZyFkqFKo", "type": "video"},
            {"title": "Go Tutorial — TechWorld with Nana", "url": "https://www.youtube.com/watch?v=yyUHQIec83I", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Go_(programming_language)"
    },
    "blockchain": {
        "docs": [
            {"title": "Ethereum Documentation", "url": "https://ethereum.org/en/developers/docs/", "type": "official"},
            {"title": "Solidity Documentation", "url": "https://docs.soliditylang.org/", "type": "official"},
        ],
        "youtube": [
            {"title": "Blockchain Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=gyMwXuJrbJQ", "type": "video"},
            {"title": "Blockchain Explained — 3Blue1Brown", "url": "https://www.youtube.com/watch?v=bBC-nXj3Ng4", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Blockchain"
    },
    "graphic design": {
        "docs": [
            {"title": "Adobe Creative Cloud Tutorials", "url": "https://helpx.adobe.com/creative-cloud/tutorials-explore.html", "type": "official"},
            {"title": "Canva Design School", "url": "https://www.canva.com/designschool/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Graphic Design Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=fZe-KWjELVo", "type": "video"},
            {"title": "Photoshop Tutorial — Envato Tuts+", "url": "https://www.youtube.com/watch?v=IyR_uYsRdPs", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Graphic_design"
    },
    "ios development": {
        "docs": [
            {"title": "Apple Developer Documentation", "url": "https://developer.apple.com/documentation/", "type": "official"},
            {"title": "Swift Documentation", "url": "https://docs.swift.org/swift-book/", "type": "official"},
        ],
        "youtube": [
            {"title": "iOS Development — Sean Allen", "url": "https://www.youtube.com/watch?v=CwA1VWP0Ldw", "type": "video"},
            {"title": "SwiftUI Tutorial — Hacking with Swift", "url": "https://www.youtube.com/watch?v=aP-SQXTtWhY", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/IOS"
    },
    "networking": {
        "docs": [
            {"title": "Cisco Networking Academy", "url": "https://www.netacad.com/", "type": "official"},
            {"title": "Computer Networks — GeeksforGeeks", "url": "https://www.geeksforgeeks.org/computer-network-tutorials/", "type": "tutorial"},
        ],
        "youtube": [
            {"title": "Computer Networking Full Course — freeCodeCamp", "url": "https://www.youtube.com/watch?v=qiQR5rTSshw", "type": "video"},
            {"title": "Networking Fundamentals — NetworkChuck", "url": "https://www.youtube.com/watch?v=cNwEVYkx2Kk", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Computer_network"
    },
    "operating systems": {
        "docs": [
            {"title": "Operating Systems — GeeksforGeeks", "url": "https://www.geeksforgeeks.org/operating-systems/", "type": "tutorial"},
            {"title": "Linux Documentation", "url": "https://www.kernel.org/doc/html/latest/", "type": "official"},
        ],
        "youtube": [
            {"title": "Operating Systems — Neso Academy", "url": "https://www.youtube.com/watch?v=vBURTt97EkA", "type": "video"},
            {"title": "OS Full Course — Gate Smashers", "url": "https://www.youtube.com/watch?v=bkSWJJZNgf8", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Operating_system"
    },
    "communication": {
        "docs": [
            {"title": "Coursera Communication Skills", "url": "https://www.coursera.org/courses?query=communication", "type": "tutorial"},
            {"title": "Toastmasters International", "url": "https://www.toastmasters.org/", "type": "official"},
        ],
        "youtube": [
            {"title": "Communication Skills — TED Talks", "url": "https://www.youtube.com/watch?v=eIho2S0ZahI", "type": "video"},
            {"title": "Public Speaking Tips", "url": "https://www.youtube.com/watch?v=JNOXZumCXNM", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Communication"
    },
    "leadership": {
        "docs": [
            {"title": "Harvard Business Review", "url": "https://hbr.org/topic/subject/leadership", "type": "tutorial"},
            {"title": "Scrum Guide", "url": "https://scrumguides.org/", "type": "official"},
        ],
        "youtube": [
            {"title": "Leadership Skills — Simon Sinek", "url": "https://www.youtube.com/watch?v=qp0HIF3SfI4", "type": "video"},
            {"title": "Project Management Full Course — Simplilearn", "url": "https://www.youtube.com/watch?v=uWPIsaYpY7U", "type": "video"},
        ],
        "wikipedia": "https://en.wikipedia.org/wiki/Leadership"
    },
}

# Default resources for unknown skills
DEFAULT_RESOURCES = {
    "docs": [
        {"title": "freeCodeCamp", "url": "https://www.freecodecamp.org/", "type": "tutorial"},
        {"title": "Coursera", "url": "https://www.coursera.org/", "type": "tutorial"},
        {"title": "edX", "url": "https://www.edx.org/", "type": "tutorial"},
    ],
    "youtube": [
        {"title": "freeCodeCamp YouTube", "url": "https://www.youtube.com/@freecodecamp", "type": "channel"},
        {"title": "Traversy Media", "url": "https://www.youtube.com/@TraversyMedia", "type": "channel"},
    ],
    "wikipedia": "https://en.wikipedia.org/"
}


class ResourceFetcher:
    """Fetches curated learning resources for detected skills."""

    def get_resources(self, skill_name):
        """
        Get curated resources for a given skill.

        Args:
            skill_name: Name of the skill (lowercase)

        Returns:
            dict with 'docs', 'youtube', 'wikipedia' resource lists
        """
        skill_key = skill_name.lower().strip()

        # Direct match
        if skill_key in RESOURCE_DATABASE:
            resources = RESOURCE_DATABASE[skill_key]
            return {
                'skill': skill_name,
                'docs': resources.get('docs', []),
                'youtube': resources.get('youtube', []),
                'wikipedia': resources.get('wikipedia', ''),
                'found': True
            }

        # Partial match — try matching against keys
        for db_key in RESOURCE_DATABASE:
            if db_key in skill_key or skill_key in db_key:
                resources = RESOURCE_DATABASE[db_key]
                return {
                    'skill': db_key,
                    'docs': resources.get('docs', []),
                    'youtube': resources.get('youtube', []),
                    'wikipedia': resources.get('wikipedia', ''),
                    'found': True
                }

        # Generate dynamic Wikipedia link
        wiki_search = urllib.parse.quote(skill_name.replace(' ', '_'))
        wiki_url = f"https://en.wikipedia.org/wiki/{wiki_search}"

        # YouTube search link
        yt_search = urllib.parse.quote(f"{skill_name} tutorial")
        yt_url = f"https://www.youtube.com/results?search_query={yt_search}"

        return {
            'skill': skill_name,
            'docs': DEFAULT_RESOURCES['docs'],
            'youtube': [
                {"title": f"Search: {skill_name} tutorials", "url": yt_url, "type": "search"},
                *DEFAULT_RESOURCES['youtube']
            ],
            'wikipedia': wiki_url,
            'found': False
        }

    def get_all_skills(self):
        """Return list of all skills with available resources."""
        return list(RESOURCE_DATABASE.keys())


# Singleton instance
_fetcher = None

def get_fetcher():
    global _fetcher
    if _fetcher is None:
        _fetcher = ResourceFetcher()
    return _fetcher


def get_resources(skill_name):
    """Convenience function for resource fetching."""
    return get_fetcher().get_resources(skill_name)
