/**
 * SkillMate AI — Resources Page JavaScript
 * Handles: Skill grid rendering, search/filter, skill detail view
 */

// ============================================================
// Skill Database (mirrors backend taxonomy for offline browsing)
// ============================================================
const SKILLS_DATA = {
    "python": { category: "Programming Language", description: "Python is a versatile, high-level programming language known for its simplicity and readability. Used in web development, data science, ML, and automation." },
    "javascript": { category: "Programming Language", description: "JavaScript is the most popular language for web development. It powers interactive websites, server-side apps with Node.js, and mobile apps." },
    "java": { category: "Programming Language", description: "Java is a robust, object-oriented language used for enterprise applications, Android development, and large-scale systems." },
    "c programming": { category: "Programming Language", description: "C is a foundational language that provides low-level memory access. Essential for system programming and embedded systems." },
    "c++": { category: "Programming Language", description: "C++ extends C with object-oriented features. Widely used in game development, system software, and competitive programming." },
    "rust": { category: "Programming Language", description: "Rust focuses on safety, speed, and concurrency. Prevents memory errors at compile time." },
    "go": { category: "Programming Language", description: "Go (Golang) excels at building scalable network services and cloud infrastructure." },
    "web development": { category: "Web Development", description: "Building websites and web applications using HTML, CSS, and JavaScript." },
    "react": { category: "Web Framework", description: "React is a JavaScript library by Facebook for building dynamic UIs with component-based architecture." },
    "html css": { category: "Web Development", description: "HTML provides structure, CSS handles styling. Modern CSS includes Flexbox, Grid, and TailwindCSS." },
    "data science": { category: "Data Science", description: "Combines statistics, programming, and domain expertise to extract insights from data." },
    "machine learning": { category: "Artificial Intelligence", description: "A branch of AI where computers learn patterns from data. Includes supervised, unsupervised, and deep learning." },
    "artificial intelligence": { category: "Artificial Intelligence", description: "Enables machines to simulate human intelligence: NLP, Computer Vision, Robotics, and Generative AI." },
    "database": { category: "Database", description: "Databases store structured data. Includes SQL (PostgreSQL) and NoSQL (MongoDB) systems." },
    "cloud computing": { category: "Cloud Computing", description: "On-demand computing resources via AWS, Azure, and Google Cloud." },
    "devops": { category: "DevOps", description: "Combines development and operations to automate deployment. Docker, Kubernetes, CI/CD." },
    "android development": { category: "Mobile Development", description: "Building mobile apps for Android using Kotlin or Java with Android Studio." },
    "ios development": { category: "Mobile Development", description: "Building apps for Apple devices using Swift and Xcode." },
    "cybersecurity": { category: "Cybersecurity", description: "Protects systems and networks from digital attacks: ethical hacking, encryption, security." },
    "ui ux design": { category: "Design", description: "Creating intuitive, visually appealing user interfaces and experiences with Figma." },
    "graphic design": { category: "Design", description: "Visual content creation using Photoshop, Illustrator, and Canva." },
    "data structures": { category: "Computer Science", description: "Foundation of CS: arrays, linked lists, trees, graphs, and algorithms for sorting/searching." },
    "blockchain": { category: "Blockchain", description: "Decentralized ledger technology for cryptocurrencies, smart contracts, and DApps." },
    "networking": { category: "Networking", description: "How devices communicate: TCP/IP, HTTP, DNS, routing, and the OSI model." },
    "operating systems": { category: "Computer Science", description: "Process management, memory management, file systems, and kernel architecture." },
    "communication": { category: "Soft Skills", description: "Speaking, writing, and presenting ideas effectively for professional success." },
    "leadership": { category: "Soft Skills", description: "Guiding teams, making decisions, project management with Agile and Scrum." },
};

// ============================================================
// DOM Elements
// ============================================================
const searchInput = document.getElementById('searchInput');
const skillsGrid = document.getElementById('skillsGrid');
const skillDetail = document.getElementById('skillDetail');
const btnBackToGrid = document.getElementById('btnBackToGrid');
const detailSkillName = document.getElementById('detailSkillName');
const detailSkillCategory = document.getElementById('detailSkillCategory');
const detailResources = document.getElementById('detailResources');

function escapeHtml(value) {
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#39;');
}

// API Config
const API_BASE = (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.hostname === '' ||
    window.location.protocol === 'file:'
)
    ? 'http://localhost:5000'
    : 'https://skillmate-ai-3s2f.onrender.com';

// ============================================================
// Render Skills Grid
// ============================================================
function renderSkillsGrid(filter = '') {
    const filteredSkills = Object.entries(SKILLS_DATA).filter(([name, data]) => {
        const searchTerm = filter.toLowerCase();
        return name.includes(searchTerm) ||
               data.category.toLowerCase().includes(searchTerm) ||
               data.description.toLowerCase().includes(searchTerm);
    });

    if (filteredSkills.length === 0) {
        skillsGrid.innerHTML = `
            <div class="skills-empty">
                <p class="skills-empty-title">No skills found</p>
                <p class="skills-empty-subtitle">Try a different search term</p>
            </div>`;
        return;
    }

    skillsGrid.innerHTML = filteredSkills.map(([name, data]) => `
        <div class="glass-card skill-resource-card" data-skill="${escapeHtml(name)}" role="button" tabindex="0">
            <span class="category-tag">${escapeHtml(data.category)}</span>
            <h3>${escapeHtml(name)}</h3>
            <p>${escapeHtml(data.description)}</p>
        </div>
    `).join('');
}

// ============================================================
// Show Skill Detail
// ============================================================
async function showSkillDetail(skillName) {
    skillsGrid.style.display = 'none';
    document.querySelector('.search-bar').style.display = 'none';
    skillDetail.style.display = 'block';

    detailSkillName.textContent = skillName;
    detailSkillCategory.textContent = SKILLS_DATA[skillName]?.category || '';

    // Show loading
    detailResources.innerHTML = `
        <div class="resource-loading">
            <div class="spinner resource-loading-spinner"></div>
            Loading resources...
        </div>`;

    try {
        const response = await fetch(`${API_BASE}/api/resources/${encodeURIComponent(skillName)}`);
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        renderDetailResources(data);
    } catch (err) {
        // Fallback: show generic resources
        detailResources.innerHTML = `
            <p class="resource-fallback">
                Could not load resources from server. 
                <a href="https://www.google.com/search?q=${encodeURIComponent(skillName + ' tutorial')}" 
                   target="_blank" class="resource-fallback-link">
                    Search on Google →
                </a>
            </p>`;
    }
}

function renderDetailResources(resources) {
    let html = '';

    // Docs
    if (resources.docs && resources.docs.length > 0) {
        html += `<div class="resource-type resource-type-first">
            <div class="resource-type-label">📄 Documentation</div>
            <div class="resource-links">`;
        resources.docs.forEach(doc => {
            html += `<a href="${doc.url}" target="_blank" rel="noopener" class="resource-link">
                <div class="r-icon docs">📄</div>
                <span class="r-title">${doc.title}</span>
                <span class="r-type">${doc.type || 'docs'}</span>
            </a>`;
        });
        html += `</div></div>`;
    }

    // YouTube
    if (resources.youtube && resources.youtube.length > 0) {
        html += `<div class="resource-type">
            <div class="resource-type-label">▶ YouTube Tutorials</div>
            <div class="resource-links">`;
        resources.youtube.forEach(vid => {
            html += `<a href="${vid.url}" target="_blank" rel="noopener" class="resource-link">
                <div class="r-icon youtube">▶</div>
                <span class="r-title">${vid.title}</span>
                <span class="r-type">${vid.type || 'video'}</span>
            </a>`;
        });
        html += `</div></div>`;
    }

    // Wikipedia
    if (resources.wikipedia) {
        html += `<div class="resource-type">
            <div class="resource-type-label">🌐 Wikipedia</div>
            <div class="resource-links">
                <a href="${resources.wikipedia}" target="_blank" rel="noopener" class="resource-link">
                    <div class="r-icon wiki">W</div>
                    <span class="r-title">Wikipedia Article</span>
                    <span class="r-type">reference</span>
                </a>
            </div>
        </div>`;
    }

    detailResources.innerHTML = html || '<p class="resources-empty-state">No resources available.</p>';
}

// ============================================================
// Back to Grid
// ============================================================
btnBackToGrid.addEventListener('click', () => {
    skillDetail.style.display = 'none';
    skillsGrid.style.display = '';
    document.querySelector('.search-bar').style.display = '';
});

skillsGrid.addEventListener('click', (event) => {
    const card = event.target.closest('.skill-resource-card');
    if (!card) return;
    const skill = card.dataset.skill;
    if (skill && SKILLS_DATA[skill]) {
        showSkillDetail(skill);
    }
});

skillsGrid.addEventListener('keydown', (event) => {
    const card = event.target.closest('.skill-resource-card');
    if (!card) return;
    if (event.key !== 'Enter' && event.key !== ' ') return;
    event.preventDefault();
    const skill = card.dataset.skill;
    if (skill && SKILLS_DATA[skill]) {
        showSkillDetail(skill);
    }
});

// ============================================================
// Search
// ============================================================
let searchTimeout;
searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        renderSkillsGrid(searchInput.value);
    }, 200);
});

// ============================================================
// Initialize
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    renderSkillsGrid();
});
