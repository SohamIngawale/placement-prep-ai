// ── STATE ───────────────────────────────────────────────────
const state = {
  user: null,
  currentCategory: 'aptitude',
  allQuestions: [],
  filteredQuestions: [],
  activeQuestion: null,
  progress: { completed: [], bookmarks: [] },
  companies: null,
  expandedCategories: {}
};

// ── INIT ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  await checkAuth();
  await loadStats();
  await loadCompanies();
  await loadPOTD();
  showPage('home');
});

// ── MOBILE NAV ──────────────────────────────────────────────
function toggleMobileNav() {
  const links = document.getElementById('navLinks');
  const burger = document.getElementById('navHamburger');
  links.classList.toggle('open');
  burger.classList.toggle('active');
}

// ── AUTH ────────────────────────────────────────────────────
async function checkAuth() {
  try {
    const res = await fetch('/api/me');
    const data = await res.json();
    if (data.logged_in) {
      state.user = data;
      updateNavForUser(data);
      await loadProgress();
    }
  } catch (e) {}
}

function updateNavForUser(user) {
  document.getElementById('navAuth').classList.add('hidden');
  document.getElementById('navUser').classList.remove('hidden');
  const av = document.getElementById('userAvatar');
  av.textContent = (user.username || 'U')[0].toUpperCase();
  
  // Update Hero CTA
  const heroCta = document.getElementById('heroCta');
  if (heroCta) {
    heroCta.innerHTML = `
      <button class="btn-primary large" onclick="showPage('dashboard')">Go to My Dashboard 📊</button>
      <button class="btn-outline large" onclick="showPage('roadmaps')">View Roadmaps</button>
    `;
  }
}

async function submitLogin() {
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;
  const errEl = document.getElementById('loginError');
  errEl.classList.add('hidden');
  if (!username || !password) {
    showFormError('loginError', 'Please fill in all fields'); return;
  }
  try {
    const res = await fetch('/api/login', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (!res.ok) { showFormError('loginError', data.error); return; }
    state.user = data;
    updateNavForUser(data);
    await loadProgress();
    closeModal();
    showToast('Welcome back, ' + data.username + '! 🎉', 'success');
  } catch (e) { showFormError('loginError', 'Connection error. Try again.'); }
}

async function submitRegister() {
  const username = document.getElementById('regUsername').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const password = document.getElementById('regPassword').value;
  showFormError('regError', '');
  if (!username || !email || !password) {
    showFormError('regError', 'Please fill in all fields'); return;
  }
  try {
    const res = await fetch('/api/register', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ username, email, password })
    });
    const data = await res.json();
    if (!res.ok) { showFormError('regError', data.error); return; }
    state.user = data;
    updateNavForUser(data);
    await loadProgress();
    closeModal();
    showToast('Account created! Welcome, ' + data.username + ' 🚀', 'success');
  } catch (e) { showFormError('regError', 'Connection error. Try again.'); }
}

async function logout() {
  await fetch('/api/logout', { method: 'POST' });
  state.user = null;
  state.progress = { completed: [], bookmarks: [] };
  document.getElementById('navAuth').classList.remove('hidden');
  document.getElementById('navUser').classList.add('hidden');
  showPage('home');
  showToast('Logged out successfully');
}

async function loadProgress() {
  if (!state.user) return;
  try {
    const res = await fetch('/api/progress/me');
    state.progress = await res.json();
  } catch (e) {}
}

// ── STATS ───────────────────────────────────────────────────
async function loadStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    const qEl = document.getElementById('statQ');
    const uEl = document.getElementById('statU');
    const cEl = document.getElementById('statC');
    if (qEl) qEl.textContent = data.total_questions + '+';
    if (uEl) uEl.textContent = (data.total_users || 0) + '+';
    if (cEl) cEl.textContent = data.companies;
  } catch (e) {}
}

// ── COMPANIES ────────────────────────────────────────────────
async function loadCompanies() {
  try {
    const res = await fetch('/api/companies');
    state.companies = await res.json();
    renderHomeCompanies();
  } catch (e) {}
}

function renderHomeCompanies() {
  const strip = document.getElementById('homeCompanies');
  if (!strip || !state.companies) return;
  const all = [
    ...(state.companies.product_mncs || []),
    ...(state.companies.startups_unicorns || []),
    ...(state.companies.finance_consulting || []),
    ...(state.companies.service_companies || [])
  ];
  // Show a subset on home page
  const featured = all.slice(0, 12);
  strip.innerHTML = featured.map(c => `
    <div class="company-chip" onclick="filterByCompany('${c.name}')">
      <div class="chip-icon" style="background:${c.color}">${c.logo}</div>
      <div>
        <div class="chip-name">${c.name}</div>
        <div class="chip-cat">${c.difficulty} • ${c.categories.length} categories</div>
      </div>
    </div>
  `).join('');
}

function renderCompanyPage() {
  if (!state.companies) return;
  const grids = {
    mncsGrid: state.companies.product_mncs || [],
    startupsGrid: state.companies.startups_unicorns || [],
    financeGrid: state.companies.finance_consulting || [],
    serviceGrid: state.companies.service_companies || []
  };
  for (const [id, list] of Object.entries(grids)) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = list.map(c => companyCardHTML(c)).join('');
  }
}

function companyCardHTML(c) {
  return `
    <div class="company-card" onclick="filterByCompany('${c.name}')">
      <div class="company-card-header">
        <div class="company-logo" style="background:${c.color}">${c.logo}</div>
        <div>
          <h3>${c.name}</h3>
          <span class="diff-badge diff-${c.difficulty}">${c.difficulty}</span>
        </div>
      </div>
      <div class="company-rounds"><strong>Rounds:</strong> ${c.rounds}</div>
      <div class="company-tags">
        ${c.categories.map(cat => `<span class="tag">${catLabel(cat)}</span>`).join('')}
      </div>
    </div>
  `;
}

function catLabel(cat) {
  return { aptitude: '🧮 Aptitude', dsa: '⚡ DSA', technical: '💻 Technical', hr: '🤝 HR' }[cat] || cat;
}

function filterByCompany(company) {
  showPage('company-details', null, company);
}

// ── COMPANY DETAILS ──────────────────────────────────────────
function renderCompanyDetails(companyName) {
  if (!state.companies) return;
  let companyData = null;
  const groups = ['product_mncs', 'startups_unicorns', 'finance_consulting', 'service_companies'];
  for (const g of groups) {
    if (state.companies[g]) {
      const found = state.companies[g].find(c => c.name === companyName);
      if (found) { companyData = found; break; }
    }
  }
  
  if (!companyData) return;

  const header = document.getElementById('companyDetailsHeader');
  header.innerHTML = `
    <div class="container" style="display:flex; align-items:center; gap: 1.5rem">
      <div class="company-logo" style="background:${companyData.color}; width:80px; height:80px; font-size:2rem">${companyData.logo}</div>
      <div>
        <h1 class="page-title">${companyData.name} Preparation</h1>
        <p class="page-sub">Rounds: ${companyData.rounds} • Difficulty: <span class="diff-badge diff-${companyData.difficulty}">${companyData.difficulty}</span></p>
        ${companyData.ctc ? `<div style="margin-top: 0.5rem; color: var(--primary); font-weight: bold; font-size: 1.1rem">💰 Expected CTC: ${companyData.ctc}</div>` : ''}
        ${companyData.roles ? `<div style="margin-top: 0.2rem; color: var(--text2); font-size: 0.9rem">💼 Target Roles: ${companyData.roles}</div>` : ''}
      </div>
    </div>
  `;

  const tracks = [
    { id: 'aptitude', title: 'Aptitude & Reasoning', icon: '🧮', desc: 'Quants, logical reasoning, and data interpretation.' },
    { id: 'dsa', title: 'Coding / DSA', icon: '⚡', desc: 'Data structures and algorithms problems.' },
    { id: 'technical', title: 'Technical Interview', icon: '💻', desc: 'Core CS subjects like OOP, DBMS, OS, and System Design.' },
    { id: 'hr', title: 'HR Interview', icon: '🤝', desc: 'Behavioral questions and cultural fit.' }
  ];

  const grid = document.getElementById('companyTracksGrid');
  grid.innerHTML = tracks.map(t => {
    // Only highlight categories that this company specifically focuses on, but show all options
    const isCore = companyData.categories.includes(t.id);
    return `
      <div class="company-card" style="cursor:pointer; border: 1px solid ${isCore ? 'var(--primary)' : 'var(--border)'}" onclick="showPage('practice', '${t.id}', '${companyData.name}')">
        <div style="font-size: 2.5rem; margin-bottom: 1rem;">${t.icon}</div>
        <h3 style="margin-bottom: 0.5rem">${t.title}</h3>
        <p style="color:var(--text2); font-size: 0.9rem">${t.desc}</p>
        ${isCore ? '<div style="margin-top: 1rem"><span class="tag">Highly Asked</span></div>' : ''}
      </div>
    `;
  }).join('');

  // Add "Contribute" section
  const contributeHTML = `
    <div style="grid-column: 1 / -1; margin-top: 3rem; text-align: center; padding: 3rem; background: var(--surface2); border-radius: var(--radius); border: 1px dashed var(--border)">
      <div style="font-size: 2.5rem; margin-bottom: 1rem">💡</div>
      <h2 style="margin-bottom: 0.5rem">Know a question asked at ${companyName}?</h2>
      <p style="color:var(--text2); margin-bottom: 1.5rem">Help the community by adding real questions asked in previous drives.</p>
      <button class="btn-primary" onclick="openAddQuestionModal('${companyName}')">Add Previous Question</button>
    </div>
  `;
  grid.innerHTML += contributeHTML;
}

function openAddQuestionModal(companyName) {
  openModal('addQuestion');
  if (companyName) {
    document.getElementById('addQCompany').value = companyName;
  }
}

async function submitAddQuestion() {
  const company = document.getElementById('addQCompany').value.trim();
  const category = document.getElementById('addQCategory').value;
  const difficulty = document.getElementById('addQDiff').value;
  const question = document.getElementById('addQContent').value.trim();
  const solution = document.getElementById('addQSolution').value.trim();

  if (!company || !question) {
    showToast('Please fill in company and question');
    return;
  }

  try {
    const res = await fetch('/api/admin/add_question', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company, category, difficulty, question, solution })
    });
    const data = await res.json();
    if (data.success) {
      showToast('Question added successfully!');
      closeModal();
      loadStats();
    } else {
      showToast('Error adding question');
    }
  } catch (e) {
    showToast('Failed to add question');
  }
}

// ── PRACTICE ─────────────────────────────────────────────────
async function loadQuestions(category, companyFilter) {
  state.currentCategory = category;
  let url = `/api/questions/${category}`;
  if (companyFilter) url += `?company=${encodeURIComponent(companyFilter)}`;
  try {
    const res = await fetch(url);
    const data = await res.json();
    let qs = data.questions || [];
    
    if (!companyFilter) {
      // Deduplicate questions by question text and combine their company tags
      const grouped = {};
      qs.forEach(q => {
        if (!grouped[q.question]) {
          grouped[q.question] = { ...q, company: [q.company] };
        } else {
          if (q.company && !grouped[q.question].company.includes(q.company)) {
            grouped[q.question].company.push(q.company);
          }
        }
      });
      qs = Object.values(grouped);
    } else {
      // Ensure company is an array for consistency in UI
      qs.forEach(q => { q.company = [q.company]; });
    }

    state.allQuestions = qs;
    state.filteredQuestions = [...state.allQuestions];
    renderSidebar(category, companyFilter);
    // Auto select first
    if (state.filteredQuestions.length > 0) {
      selectQuestion(state.filteredQuestions[0]);
    }
  } catch (e) {
    showToast('Failed to load questions', 'error');
  }
}

function renderSidebar(category, companyFilter) {
  const title = {
    aptitude: '🧮 Aptitude',
    dsa: '⚡ DSA / Coding',
    technical: '💻 Technical',
    hr: '🤝 HR Interview'
  }[category] || 'Questions';

  document.getElementById('sidebarTitle').textContent =
    companyFilter ? `${companyFilter} — ${title}` : title;

  renderQuestionList();
}

function toggleCategoryGroup(catName) {
  state.expandedCategories[catName] = !state.expandedCategories[catName];
  renderQuestionList();
}

function renderQuestionList() {
  const list = document.getElementById('questionList');
  const qs = state.filteredQuestions;
  if (!qs.length) {
    list.innerHTML = '<div style="padding:1rem;color:var(--text2);font-size:0.9rem">No questions found</div>';
    return;
  }
  
  const grouped = {};
  qs.forEach((q, i) => {
    if (!grouped[q.title]) grouped[q.title] = [];
    grouped[q.title].push({ q, index: i });
  });

  // If there's only one group (e.g. from filtering by a single topic), auto-expand it.
  const groupKeys = Object.keys(grouped);
  if (groupKeys.length === 1) {
    state.expandedCategories[groupKeys[0]] = true;
  }

  let html = '';
  for (const [title, groupQs] of Object.entries(grouped)) {
    const isExpanded = !!state.expandedCategories[title];
    const icon = isExpanded ? '▲' : '▼';
    
    // Header for the category
    html += `
      <div style="padding: 1rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; background: var(--surface2); border-bottom: 1px solid var(--border); transition: 0.2s;" onclick="toggleCategoryGroup('${title.replace(/'/g, "\\'")}')" onmouseover="this.style.background='var(--hover)'" onmouseout="this.style.background='var(--surface2)'">
        <span style="font-size: 0.85rem; text-transform: uppercase; color: var(--text); font-weight: bold;">${title} <span style="color:var(--text2); font-weight:normal; font-size:0.75rem">(${groupQs.length})</span></span>
        <span style="color: var(--text2); font-size: 0.7rem;">${icon}</span>
      </div>
    `;
    
    // Questions container (hidden if not expanded)
    if (isExpanded) {
      html += `<div style="background: var(--bg);">`;
      html += groupQs.map(({q, index}) => {
        const done = state.progress.completed.includes(q.id);
        const active = state.activeQuestion && state.activeQuestion.id === q.id;
        const shortTitle = q.question ? q.question.substring(0, 45) + '...' : q.title;
        return `
          <div class="q-item ${done ? 'done' : ''} ${active ? 'active' : ''}" onclick="selectQuestion(allQAt(${index}))">
            <div class="q-item-title" style="font-size: 0.85rem; line-height: 1.4;">${shortTitle}</div>
            <div class="q-item-meta" style="margin-top: 0.5rem;">
              <div class="diff-dot ${q.difficulty}"></div>
              <span class="q-diff">${q.difficulty}</span>
              ${done ? '<span class="done-check">✓ Done</span>' : ''}
            </div>
          </div>
        `;
      }).join('');
      html += `</div>`;
    }
  }
  
  list.innerHTML = html;
}

function allQAt(i) { return state.filteredQuestions[i]; }

function filterQuestions() {
  const diff = document.getElementById('filterDifficulty').value;
  state.filteredQuestions = diff
    ? state.allQuestions.filter(q => q.difficulty === diff)
    : [...state.allQuestions];
  renderQuestionList();
}

function selectQuestion(q) {
  state.activeQuestion = q;
  renderQuestionList();
  renderQuestionPanel(q);
}

function renderQuestionPanel(q) {
  const main = document.getElementById('practiceMain');
  const cat = state.currentCategory;

  let content = '';
  if (cat === 'aptitude') content = renderAptitude(q);
  else if (cat === 'dsa') content = renderDSA(q);
  else if (cat === 'technical') content = renderTechnical(q);
  else if (cat === 'hr') content = renderHR(q);

  const done = state.progress.completed.includes(q.id);
  const bookmarked = (state.progress.bookmarks || []).includes(q.id);
  const companies = Array.isArray(q.company) ? q.company : [q.company];

  if (cat === 'dsa') {
    // DSA gets the full compiler view without q-panel padding
    main.innerHTML = content;
    setTimeout(() => {
      initEditor(q.code_template || "");
    }, 100);
    return;
  }

  main.innerHTML = `
    <div class="q-panel">
      <div class="q-panel-header">
        <h2>${q.title}</h2>
        <div class="q-meta-row">
          <span class="diff-label ${q.difficulty}">${q.difficulty}</span>
          ${companies.map(c => `<span class="company-pill">${c}</span>`).join('')}
        </div>
      </div>
      ${content}
      <div class="action-row">
        ${state.user ? `
          <button class="btn-ghost btn-sm" onclick="toggleComplete('${q.id}')">
            ${done ? '✓ Completed' : '○ Mark Complete'}
          </button>
          <button class="btn-ghost btn-sm" onclick="toggleBookmark('${q.id}')">
            ${bookmarked ? '🔖 Bookmarked' : '📌 Bookmark'}
          </button>
        ` : `<button class="btn-ghost btn-sm" onclick="openModal('login')">Login to track progress</button>`}
      </div>
    </div>
  `;
}

function renderAptitude(q) {
  const letters = ['A', 'B', 'C', 'D'];
  return `
    <div class="q-body">${q.question}</div>
    <div class="options-list" id="optList">
      ${q.options.map((opt, i) => `
        <button class="option-btn" onclick="checkAnswer(${i}, ${q.answer})" id="opt${i}">
          <span class="option-letter">${letters[i]}</span>
          ${opt}
        </button>
      `).join('')}
    </div>
    <div class="explanation-box hidden" id="explBox">
      <strong>💡 Explanation</strong>
      <span>${q.explanation}</span>
    </div>
  `;
}

function checkAnswer(selected, correct) {
  const opts = document.querySelectorAll('.option-btn');
  opts.forEach((btn, i) => {
    btn.disabled = true;
    if (i === correct) btn.classList.add('correct');
    else if (i === selected) btn.classList.add('wrong');
  });
  document.getElementById('explBox').classList.remove('hidden');
  if (selected === correct) {
    showToast('Correct! 🎉', 'success');
    autoMarkComplete();
  } else {
    showToast('Not quite. Review the explanation.', 'error');
  }
}

function renderDSA(q) {
  const languages = [
    { id: 'python', name: 'Python 3', template: q.code_template || "# Type your solution here\n\ndef solve():\n    pass\n" },
    { id: 'javascript', name: 'JavaScript', template: "// Type your solution here\n\nfunction solve() {\n    \n}\n" },
    { id: 'java', name: 'Java', template: "public class Main {\n    public static void main(String[] args) {\n        // Type your solution here\n    }\n}\n" },
    { id: 'cpp', name: 'C++', template: "#include <iostream>\nusing namespace std;\n\nint main() {\n    // Type your solution here\n    return 0;\n}\n" }
  ];

  return `
    <div class="compiler-wrapper">
      <!-- Question Section -->
      <div class="compiler-info">
        <div class="compiler-section-title">Description</div>
        <div class="q-body-compact">${q.question}</div>
        
        ${q.examples ? `
          <div class="compiler-section-title">Examples</div>
          <div class="examples-container">
            ${q.examples.map((ex, i) => `
              <div class="example-item">
                <div class="example-label">Example ${i+1}:</div>
                <div class="example-content">
                  <strong>Input:</strong> ${ex.input}<br>
                  <strong>Output:</strong> ${ex.output}<br>
                  ${ex.explanation ? `<strong>Explanation:</strong> ${ex.explanation}` : ''}
                </div>
              </div>
            `).join('')}
          </div>
        ` : ''}

        ${q.constraints ? `
          <div class="compiler-section-title">Constraints</div>
          <ul class="constraints-list">
            ${q.constraints.map(c => `<li>${c}</li>`).join('')}
          </ul>
        ` : ''}

        <div class="hint-box-compact">
          <strong>💡 Hint:</strong> ${q.hint || 'Think about the optimal data structure.'}
        </div>
      </div>

      <!-- Editor Section -->
      <div class="compiler-editor-container">
        <div class="editor-toolbar">
          <select id="editorLang" onchange="changeLanguage()">
            ${languages.map(l => `<option value="${l.id}">${l.name}</option>`).join('')}
          </select>
          <div class="editor-actions">
            <button class="btn-ghost btn-sm" onclick="resetCode()">Reset</button>
          </div>
        </div>
        
        <div id="editor" class="monaco-editor-instance"></div>

        <div class="editor-footer">
          <div class="output-console" id="outputPanel">
            <div class="console-header">Output</div>
            <div class="console-body" id="consoleBody">▶ Run code to see results...</div>
          </div>
          <div class="compiler-controls">
            <button class="btn-primary" onclick="runCode()" id="runBtn">Run Code</button>
            <button class="btn-ghost" onclick="toggleSolution('${q.id}')">View Solution</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Solution Modal-like overlay -->
    <div class="code-block hidden" id="solBlock">
      <div style="display:flex; justify-content:space-between; margin-bottom:1rem; align-items:center;">
        <strong>Optimal Solution</strong>
        <div style="display:flex; gap:0.5rem">
          <button class="btn-ghost small" onclick="copySolutionText()" id="copySolBtn">Copy</button>
          <button class="btn-ghost small" onclick="toggleSolution()" style="color:var(--accent)">Close</button>
        </div>
      </div>
      <pre><code id="solCodeText">${escapeHtml(q.solution)}</code></pre>
    </div>
  `;
}

function changeLanguage() {
  const lang = document.getElementById('editorLang').value;
  const q = state.activeQuestion;
  let template = "";
  if (lang === 'python') template = q.code_template || "# Python 3\ndef solve():\n    pass";
  else if (lang === 'javascript') template = "// JavaScript\nfunction solve() {\n}";
  else if (lang === 'java') template = "public class Main {\n    public static void main(String[] args) {\n    }\n}";
  else if (lang === 'cpp') template = "#include <iostream>\nusing namespace std;\nint main() {\n    return 0;\n}";
  
  if (editor) {
    const model = editor.getModel();
    monaco.editor.setModelLanguage(model, lang === 'cpp' ? 'cpp' : lang);
    editor.setValue(template);
  }
}

function resetCode() {
  if (confirm("Reset code to template?")) {
    changeLanguage();
  }
}

function toggleSolution(id) {
  const sol = document.getElementById('solBlock');
  const isHidden = sol.classList.toggle('hidden');
  if (!isHidden) { autoMarkComplete(); showToast('Solution revealed', 'success'); }
}

function copySolutionText() {
  const code = document.getElementById('solCodeText').innerText;
  copyToClipboard(code, 'copySolBtn');
}

function copyToClipboard(text, btnId) {
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById(btnId);
    const originalText = btn.textContent;
    btn.textContent = 'Copied! ✅';
    showToast('Copied to clipboard!', 'success');
    setTimeout(() => {
      btn.textContent = originalText;
    }, 2000);
  }).catch(err => {
    showToast('Failed to copy', 'error');
  });
}

function toggleTechAns() {
  const el = document.getElementById('techAns');
  const copyBtn = document.getElementById('copyTechBtn');
  const hidden = el.classList.toggle('hidden');
  if (copyBtn) copyBtn.classList.toggle('hidden', hidden);
  if (!hidden) autoMarkComplete();
}

function toggleHRAns() {
  const el = document.getElementById('hrAns');
  const copyBtn = document.getElementById('copyHRBtn');
  const hidden = el.classList.toggle('hidden');
  if (copyBtn) copyBtn.classList.toggle('hidden', hidden);
  if (!hidden) autoMarkComplete();
}
  const tags = (q.tags || []).map(t => `<span class="tag">${t}</span>`).join('');
  return `
    <div class="q-body">${q.question}</div>
    <div style="margin-bottom:1rem">
      ${tags}
    </div>
    <div style="margin-bottom:1.5rem">
      <label style="display:block;margin-bottom:0.5rem;font-size:0.85rem;color:var(--text2)">Draft your answer:</label>
      <textarea placeholder="Type your answer here to practice..." style="width:100%;min-height:120px;background:var(--bg);color:white;border:1px solid var(--border);border-radius:var(--radius-sm);padding:1rem;font-family:inherit;resize:vertical;"></textarea>
    </div>
    <div style="margin-bottom:0.75rem; display:flex; gap:0.5rem">
      <button class="btn-ghost btn-sm" onclick="toggleTechAns()">💬 View Answer</button>
      <button class="btn-ghost btn-sm hidden" id="copyTechBtn" onclick="copyToClipboard(document.getElementById('techAns').innerText, 'copyTechBtn')">Copy</button>
    </div>
    <div class="sample-ans hidden" id="techAns">${q.solution || q.answer || 'No answer provided.'}</div>
  `;
}

function renderTechnical(q) {
  const tips = (q.tips || []).map(t => `<li>${t}</li>`).join('');
  return `
    <div class="q-body" style="font-size:1.1rem;font-weight:500">"${q.question}"</div>
    <h4 style="margin-bottom:0.75rem;color:var(--accent2)">📌 Tips</h4>
    <ul class="tips-list">${tips}</ul>
    <div style="margin-bottom:1.5rem">
      <label style="display:block;margin-bottom:0.5rem;font-size:0.85rem;color:var(--text2)">Draft your answer:</label>
      <textarea placeholder="How would you answer this?" style="width:100%;min-height:120px;background:var(--bg);color:white;border:1px solid var(--border);border-radius:var(--radius-sm);padding:1rem;font-family:inherit;resize:vertical;"></textarea>
    </div>
    <div style="margin-bottom:0.75rem; display:flex; gap:0.5rem">
      <button class="btn-ghost btn-sm" onclick="toggleHRAns()">💬 Sample Answer</button>
      <button class="btn-ghost btn-sm hidden" id="copyHRBtn" onclick="copyToClipboard(document.getElementById('hrAns').innerText, 'copyHRBtn')">Copy</button>
    </div>
    <div class="sample-ans hidden" id="hrAns">${q.solution || q.sample || 'No sample answer provided.'}</div>
  `;
}

function renderHR(q) {
  if (state.activeQuestion && state.user) {
    toggleComplete(state.activeQuestion.id, true);
  }
}

// ── PROGRESS ─────────────────────────────────────────────────
async function toggleComplete(qid, autoOnly = false) {
  if (!state.user) { openModal('login'); return; }
  if (autoOnly && state.progress.completed.includes(qid)) return;
  try {
    const res = await fetch('/api/progress/complete', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ question_id: qid })
    });
    const data = await res.json();
    state.progress.completed = data.completed;
    renderQuestionList();
    if (state.activeQuestion && state.activeQuestion.id === qid) {
      const panel = document.querySelector('.action-row');
      if (panel) {
        // Re-render action row
        const q = state.activeQuestion;
        renderActionRow(q);
      }
    }
    if (!autoOnly) showToast('Marked as complete ✓', 'success');
  } catch (e) {}
}

async function toggleBookmark(qid) {
  if (!state.user) { openModal('login'); return; }
  try {
    const res = await fetch('/api/progress/bookmark', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ question_id: qid })
    });
    const data = await res.json();
    state.progress.bookmarks = data.bookmarks;
    const msg = data.action === 'added' ? 'Bookmarked! 🔖' : 'Bookmark removed';
    showToast(msg, 'success');
    // Re-render action row
    renderActionRow(state.activeQuestion);
  } catch (e) {}
}

function renderActionRow(q) {
  const ar = document.querySelector('.action-row');
  if (!ar) return;
  const done = state.progress.completed.includes(q.id);
  const bookmarked = (state.progress.bookmarks || []).includes(q.id);
  ar.innerHTML = `
    <button class="btn-ghost btn-sm" onclick="toggleComplete('${q.id}')">
      ${done ? '✓ Completed' : '○ Mark Complete'}
    </button>
    <button class="btn-ghost btn-sm" onclick="toggleBookmark('${q.id}')">
      ${bookmarked ? '🔖 Bookmarked' : '📌 Bookmark'}
    </button>
  `;
}

// ── PROFILE ──────────────────────────────────────────────────
async function loadProfile() {
  if (!state.user) { showPage('home'); openModal('login'); return; }
  await loadProgress();
  const u = state.user;
  document.getElementById('profileAvatar').textContent = (u.username || 'U')[0].toUpperCase();
  document.getElementById('profilePoints').textContent = u.points || 0;
  
  // Load Activity Data
  try {
    const res = await fetch('/api/activity');
    const data = await res.json();
    document.getElementById('profileStreak').textContent = (data.streak || 0) + ' Days';
    document.getElementById('profileMaxStreak').textContent = (data.max_streak || 0) + ' Days';
    renderHeatmap(data.activity || {});
  } catch (e) {}

  document.getElementById('profileName').textContent = u.username;
  document.getElementById('profileEmail').textContent = u.email || '';
  document.getElementById('profileJoined').textContent = 'Joined: ' + (u.joined || '—');
  document.getElementById('statCompleted').textContent = state.progress.completed.length;
  document.getElementById('statBookmarks').textContent = (state.progress.bookmarks || []).length;

  // Best score
  const scores = state.progress.scores || {};
  const best = Object.values(scores).length ? Math.max(...Object.values(scores)) : null;
  document.getElementById('statScore').textContent = best !== null ? best + '%' : '—';

  // Category progress
  const catEl = document.getElementById('categoryProgress');
  const cats = ['aptitude', 'dsa', 'technical', 'hr'];
  const totals = { aptitude: 5, dsa: 5, technical: 5, hr: 4 };
  catEl.innerHTML = cats.map(cat => {
    const done = state.progress.completed.filter(id => id.startsWith(cat.slice(0,3))).length;
    const total = totals[cat];
    const pct = Math.round((done / total) * 100);
    return `
      <div class="prog-row">
        <div class="prog-label">${catLabel(cat).replace(/🧮|⚡|💻|🤝/g,'').trim()}</div>
        <div class="prog-bar-wrap"><div class="prog-bar" style="width:${pct}%"></div></div>
        <div class="prog-count">${done}/${total}</div>
      </div>
    `;
  }).join('');
}

// ── PAGE ROUTER ───────────────────────────────────────────────
function showPage(page, category, company) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById('page-' + page);
  if (target) target.classList.add('active');

  if (page === 'practice') {
    loadQuestions(category || 'aptitude', company);
  }

  if (page === 'companies') {
    renderCompanyPage();
  }
  
  if (page === 'company-details') {
    renderCompanyDetails(company);
  }
  
  if (page === 'leaderboard') loadLeaderboard();
  
  if (page === 'mock-tests') initMockTestSetup();
  
  if (page === 'profile') loadProfile();

  if (page === 'dashboard') loadDashboard();

  if (page === 'interviews') loadInterviews();
  
  if (page === 'resume-builder') loadResume();

  if (page === 'ai-interviewer') initAIInterviewer();
  
  if (page === 'roadmaps') resetRoadmap();
  
  window.scrollTo(0, 0);
}

// ── MODAL ────────────────────────────────────────────────────
function openModal(type) {
  document.getElementById('modalOverlay').classList.remove('hidden');
  // Hide all forms
  ['formLogin', 'formRegister', 'formInterview', 'formAddQuestion', 'formForgotPassword', 'formResetPassword'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  });
  
  // Convert kebab-case to camelCase for ID (e.g., forgot-password -> ForgotPassword)
  const camelType = type.split('-').map(part => part.charAt(0).toUpperCase() + part.slice(1)).join('');
  const formId = `form${camelType}`;
  const formEl = document.getElementById(formId);
  if (formEl) formEl.classList.remove('hidden');
  
  // Clear errors
  ['loginError','regError', 'forgotError', 'resetError'].forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.classList.add('hidden'); el.textContent = ''; }
  });
}

async function submitForgotPassword() {
  const email = document.getElementById('forgotEmail').value.trim();
  if (!email) { showFormError('forgotError', 'Please enter your email'); return; }
  
  try {
    const res = await fetch('/api/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    const data = await res.json();
    if (!res.ok) { showFormError('forgotError', data.error); return; }
    
    showToast(data.message, 'success');
    // Store username for the reset step
    state.tempResetUsername = data.username;
    // Switch to reset form
    openModal('reset-password');
  } catch (e) { showFormError('forgotError', 'Connection error'); }
}

async function submitResetPassword() {
  const otp = document.getElementById('resetOtp').value.trim();
  const password = document.getElementById('resetPassword').value;
  const username = state.tempResetUsername;
  
  if (!otp || !password) { showFormError('resetError', 'Please fill in all fields'); return; }
  
  try {
    const res = await fetch('/api/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, otp, password })
    });
    const data = await res.json();
    if (!res.ok) { showFormError('resetError', data.error); return; }
    
    showToast('Password updated! You can now login.', 'success');
    openModal('login');
  } catch (e) { showFormError('resetError', 'Connection error'); }
}

async function runCode() {
  if (!editor) return;
  const code = editor.getValue();
  const lang = document.getElementById('editorLang').value;
  const consoleBody = document.getElementById('consoleBody');
  const runBtn = document.getElementById('runBtn');

  consoleBody.innerHTML = '<span style="color:var(--text2)">Compiling & Running... ⏳</span>';
  runBtn.disabled = true;
  runBtn.textContent = 'Running...';

  try {
    const res = await fetch('/api/run-code', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, language: lang })
    });
    
    const data = await res.json();
    if (data.run) {
      const output = data.run.stdout || data.run.stderr || data.run.output || 'No output.';
      consoleBody.innerHTML = escapeHtml(output);
      consoleBody.style.color = data.run.code !== 0 ? '#EF4444' : '#00ff88';
      
      if (data.run.code === 0) {
        showToast('Execution successful!', 'success');
        autoMarkComplete();
      } else {
        showToast('Execution failed with errors.', 'error');
      }
    } else {
      consoleBody.textContent = data.error || 'Execution failed.';
      consoleBody.style.color = '#EF4444';
    }
  } catch (e) {
    consoleBody.textContent = 'Error connecting to execution server.';
    consoleBody.style.color = '#EF4444';
  } finally {
    runBtn.disabled = false;
    runBtn.textContent = 'Run Code';
  }
}

let editor;

function initEditor(code = "") {
  require.config({ paths: { vs: 'https://unpkg.com/monaco-editor@latest/min/vs' }});

  require(['vs/editor/editor.main'], function () {
    if (editor) {
      editor.dispose();
    }
    editor = monaco.editor.create(document.getElementById('editor'), {
      value: code,
      language: 'python',
      theme: 'vs-dark',
      automaticLayout: true,
      fontSize: 14
    });
  });
}

function closeModal() {
  document.getElementById('modalOverlay').classList.add('hidden');
}

function showFormError(elId, msg) {
  const el = document.getElementById(elId);
  if (!el) return;
  if (msg) { el.textContent = msg; el.classList.remove('hidden'); }
  else el.classList.add('hidden');
}

// ── TOAST ────────────────────────────────────────────────────
let toastTimer;
function showToast(msg, type = '') {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.className = 'toast ' + type;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.add('hidden'), 3000);
}

// ── UTILS ────────────────────────────────────────────────────
function escapeHtml(text) {
  return (text || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// ── LEADERBOARD ──────────────────────────────────────────────
async function loadLeaderboard() {
  try {
    const res = await fetch('/api/leaderboard');
    const data = await res.json();
    const tbody = document.getElementById('leaderboardBody');
    if (!tbody) return;
    
    tbody.innerHTML = data.leaderboard.map((u, i) => `
      <tr style="border-bottom: 1px solid var(--border);">
        <td style="padding: 1rem;">
          ${i === 0 ? '🥇 1st' : i === 1 ? '🥈 2nd' : i === 2 ? '🥉 3rd' : `${i + 1}th`}
        </td>
        <td style="padding: 1rem; font-weight: bold; color: ${u.username === state.user?.username ? 'var(--primary)' : 'inherit'}">
          ${u.username} ${u.username === state.user?.username ? '(You)' : ''}
        </td>
        <td style="padding: 1rem; text-align: right; color: var(--primary); font-family: monospace; font-size: 1.1rem;">
          ${u.points} pts
        </td>
      </tr>
    `).join('');
  } catch (e) {
    console.error('Failed to load leaderboard', e);
  }
}

// ── MOCK TESTS ───────────────────────────────────────────────
let mockState = {
  questions: [],
  answers: {},
  timer: null,
  timeLeft: 1800 // 30 mins
};

function initMockTestSetup() {
  document.getElementById('mockSetupView').classList.remove('hidden');
  document.getElementById('mockActiveView').classList.add('hidden');
  document.getElementById('mockResultView').classList.add('hidden');
  
  // Populate companies dropdown
  const select = document.getElementById('mockCompany');
  if (select && state.companies) {
    const allGroups = [
      ...(state.companies.product_mncs || []),
      ...(state.companies.startups_unicorns || []),
      ...(state.companies.finance_consulting || []),
      ...(state.companies.service_companies || [])
    ];
    // Create unique sorted list
    const unique = [...new Set(allGroups.map(c => c.name))].sort();
    select.innerHTML = '<option value="">Any Company</option>' + 
      unique.map(name => `<option value="${name}">${name}</option>`).join('');
  }
}

async function startMockTest() {
  const category = document.getElementById('mockCategory').value;
  const company = document.getElementById('mockCompany').value;
  
  // Fetch questions for this mock
  let url = `/api/questions/${category}`;
  if (company) url += `?company=${encodeURIComponent(company)}`;
  
  try {
    const res = await fetch(url);
    const data = await res.json();
    let qs = data.questions || [];
    
    if (qs.length === 0) {
      showToast('No questions found for this combination.', 'error');
      return;
    }
    
    // Shuffle and pick 10
    qs = qs.sort(() => 0.5 - Math.random()).slice(0, 10);
    mockState.questions = qs;
    mockState.answers = {};
    mockState.timeLeft = 1800;
    
    document.getElementById('mockSetupView').classList.add('hidden');
    document.getElementById('mockActiveView').classList.remove('hidden');
    
    renderMockQuestions();
    startMockTimer();
  } catch (e) {
    showToast('Failed to start test.', 'error');
  }
}

function renderMockQuestions() {
  const container = document.getElementById('mockQuestionsContainer');
  container.innerHTML = mockState.questions.map((q, i) => {
    let inputHtml = '';
    
    if (q.options) {
      // Multiple choice (Aptitude)
      inputHtml = `<div class="options-list">` + 
        q.options.map((opt, optIdx) => `
          <div class="option-item" onclick="selectMockOption(${i}, ${optIdx})" id="mockOpt_${i}_${optIdx}">
            <span class="option-letter">${String.fromCharCode(65 + optIdx)}</span>
            <span class="option-text">${opt}</span>
          </div>
        `).join('') + `</div>`;
    } else {
      // Text area for DSA/Technical/HR
      inputHtml = `<textarea id="mockAns_${i}" placeholder="Type your answer or code here..." style="width: 100%; height: 150px; background: var(--bg); color: white; border: 1px solid var(--border); border-radius: 8px; padding: 1rem; font-family: monospace; resize: vertical;"></textarea>`;
    }
    
    return `
      <div style="background: var(--surface); padding: 2rem; border-radius: 12px; margin-bottom: 2rem; border: 1px solid var(--border);">
        <h4 style="color: var(--text2); margin-bottom: 1rem;">Question ${i + 1} of ${mockState.questions.length}</h4>
        <div style="font-size: 1.1rem; margin-bottom: 1.5rem; line-height: 1.6;">${q.question}</div>
        ${inputHtml}
      </div>
    `;
  }).join('');
}

function selectMockOption(qIndex, optIndex) {
  mockState.answers[qIndex] = optIndex;
  // Update UI
  const qInfo = mockState.questions[qIndex];
  if (qInfo.options) {
    for (let i = 0; i < qInfo.options.length; i++) {
      const el = document.getElementById(`mockOpt_${qIndex}_${i}`);
      if (el) {
        el.style.border = i === optIndex ? '1px solid var(--primary)' : '1px solid var(--border)';
        el.style.background = i === optIndex ? 'rgba(102, 126, 234, 0.1)' : 'var(--surface2)';
      }
    }
  }
}

function startMockTimer() {
  clearInterval(mockState.timer);
  const display = document.getElementById('mockTimer');
  
  mockState.timer = setInterval(() => {
    mockState.timeLeft--;
    const m = Math.floor(mockState.timeLeft / 60).toString().padStart(2, '0');
    const s = (mockState.timeLeft % 60).toString().padStart(2, '0');
    display.textContent = `${m}:${s}`;
    
    if (mockState.timeLeft <= 60) {
      display.style.color = '#EF4444'; // Red when <= 1 min
    }
    
    if (mockState.timeLeft <= 0) {
      clearInterval(mockState.timer);
      submitMockTest();
    }
  }, 1000);
}

function submitMockTest() {
  clearInterval(mockState.timer);
  document.getElementById('mockActiveView').classList.add('hidden');
  document.getElementById('mockResultView').classList.remove('hidden');
  
  // Calculate score (Only exact match for MCQs, +1 for filled text areas)
  let score = 0;
  
  mockState.questions.forEach((q, i) => {
    if (q.options) {
      if (mockState.answers[i] === q.answer) score++;
    } else {
      const textEl = document.getElementById(`mockAns_${i}`);
      if (textEl && textEl.value.trim().length > 10) score++; // Basic validation
    }
  });
  
  document.getElementById('mockScoreDisplay').textContent = `${score} / ${mockState.questions.length}`;
  
  // Bonus Points
  const bonus = score * 5;
  document.getElementById('mockBonusPoints').textContent = bonus;
  
  // Save bonus to DB via a dummy progress completion
  if (bonus > 0 && state.user && mockState.questions.length > 0) {
    // Just mark the first question of the test as complete to trigger points
    // (A dedicated submit endpoint is better, but this reuses existing logic)
    fetch('/api/progress/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ qid: mockState.questions[0].id })
    });
  }
}

function resetMockTest() {
  initMockTestSetup();
}

// ── PROBLEM OF THE DAY ───────────────────────────────────────
let currentPOTD = null;

async function loadPOTD() {
  try {
    const res = await fetch('/api/potd');
    const data = await res.json();
    if (data && data.id) {
      currentPOTD = data;
      document.getElementById('potdTitle').textContent = `${data.title} (${data.company || 'Multiple'})`;
      document.getElementById('potdBanner').classList.remove('hidden');
    }
  } catch (e) {
    console.error("Failed to load POTD", e);
  }
}

function goToPOTD() {
  if (!currentPOTD) return;
  showPage('practice', currentPOTD.category, currentPOTD.company);
  setTimeout(() => {
    selectQuestion(currentPOTD);
  }, 500);
}

// ── AI REVIEW ────────────────────────────────────────────────
let aiMode = 'resume';

function setAiMode(mode) {
  aiMode = mode;
  document.getElementById('btnAiResume').className = mode === 'resume' ? 'btn-primary' : 'btn-ghost';
  document.getElementById('btnAiAnswer').className = mode === 'answer' ? 'btn-primary' : 'btn-ghost';
  document.getElementById('aiInputLabel').textContent = mode === 'resume' ? 'Paste your resume text here:' : 'Paste your behavioral interview answer here (STAR method):';
  document.getElementById('aiInputText').placeholder = mode === 'resume' ? 'E.g. I am a software engineer with experience in...' : 'E.g. During my time at XYZ, I was tasked with...';
  document.getElementById('aiResultArea').classList.add('hidden');
  const fileContainer = document.getElementById('aiFileContainer');
  if (fileContainer) fileContainer.style.display = mode === 'resume' ? 'block' : 'none';
}

async function submitAiReview() {
  const text = document.getElementById('aiInputText').value;
  const fileInput = document.getElementById('aiFileInput');
  const file = fileInput ? fileInput.files[0] : null;

  if ((!text || text.length < 10) && !file) {
    showToast('Please enter text or upload a file to analyze.', 'error');
    return;
  }
  
  const btn = document.querySelector('#page-ai-review button.full');
  const originalText = btn.textContent;
  btn.textContent = 'Analyzing... ⏳';
  btn.disabled = true;
  
  try {
    const formData = new FormData();
    formData.append('text', text);
    formData.append('type', aiMode);
    if (file) {
      formData.append('file', file);
    }

    const res = await fetch('/api/ai-review', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    
    document.getElementById('aiResultArea').classList.remove('hidden');
    document.getElementById('aiScoreDisplay').textContent = `${data.score}/100`;
    
    // Color score
    const scoreColor = data.score >= 80 ? '#10b981' : data.score >= 50 ? '#f59e0b' : '#ef4444';
    document.getElementById('aiScoreDisplay').style.color = scoreColor;
    
    document.getElementById('aiFeedbackDisplay').innerHTML = `<ul>${data.feedback.split('. ').filter(Boolean).map(f => `<li>${f}</li>`).join('')}</ul>`;
    
  } catch (e) {
    showToast('Failed to analyze text.', 'error');
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

// ── INTERVIEW EXPERIENCES ────────────────────────────────────
async function loadInterviews() {
  const list = document.getElementById('interviewsList');
  list.innerHTML = '<div style="text-align:center; padding:3rem; color:var(--text2)">Loading experiences...</div>';
  try {
    const res = await fetch('/api/interviews');
    const data = await res.json();
    if (!data.experiences.length) {
      list.innerHTML = '<div style="text-align:center; padding:3rem; color:var(--text2)">No stories shared yet. Be the first!</div>';
      return;
    }
    list.innerHTML = data.experiences.map(e => `
      <div style="background:var(--surface2); border:1px solid var(--border); border-radius:12px; padding:2rem; transition:0.3s;" onmouseover="this.style.borderColor='var(--primary)'" onmouseout="this.style.borderColor='var(--border)'">
        <div style="display:flex; justify-content:space-between; margin-bottom:1rem; align-items:flex-start">
          <div>
            <h3 style="margin-bottom:0.25rem">${e.company} <span style="font-size:0.9rem; font-weight:normal; color:var(--text2)">- ${e.role}</span></h3>
            <div style="display:flex; gap:0.75rem; align-items:center">
              <span class="diff-badge diff-${e.difficulty}" style="font-size:0.7rem">${e.difficulty}</span>
              <span style="font-size:0.8rem; color:var(--text2)">By ${e.username} • ${e.date}</span>
            </div>
          </div>
        </div>
        <div style="color:var(--text2); line-height:1.7; white-space:pre-wrap;">${e.content}</div>
      </div>
    `).join('');
  } catch (e) {
    list.innerHTML = '<div style="text-align:center; padding:3rem; color:var(--danger)">Failed to load.</div>';
  }
}

async function submitInterview() {
  const company = document.getElementById('intCompany').value;
  const role = document.getElementById('intRole').value;
  const content = document.getElementById('intContent').value;
  const difficulty = document.getElementById('intDiff').value;

  if (!company || !content) { showToast('Please fill all required fields.', 'error'); return; }

  try {
    const res = await fetch('/api/interviews', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ company, role, content, difficulty })
    });
    if (res.ok) {
      showToast('Experience shared! Thank you.', 'success');
      closeModal();
      loadInterviews();
    }
  } catch (e) {}
}

// ── HEATMAP ──────────────────────────────────────────────────
function renderHeatmap(activityData) {
  const grid = document.getElementById('heatmapGrid');
  if (!grid) return;
  grid.innerHTML = '';
  
  const today = new Date();
  const yearAgo = new Date();
  yearAgo.setDate(today.getDate() - 365);
  
  // Fill 53 weeks (approx 365 days)
  for (let i = 0; i < 371; i++) { // 53 * 7
    const d = new Date(yearAgo);
    d.setDate(yearAgo.getDate() + i);
    if (d > today) break;
    
    const dateStr = d.toISOString().split('T')[0];
    const count = activityData[dateStr] || 0;
    
    const level = count === 0 ? 0 : count < 2 ? 1 : count < 5 ? 2 : count < 10 ? 3 : 4;
    const colors = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353'];
    
    const day = document.createElement('div');
    day.style.width = '12px';
    day.style.height = '12px';
    day.style.background = colors[level];
    day.style.borderRadius = '2px';
    day.title = `${dateStr}: ${count} activities`;
    grid.appendChild(day);
  }
}

// ── RESUME BUILDER LOGIC ──────────────────────────────────────
let resumeState = {
  edu: [],
  exp: [],
  proj: []
};

function addResumeItem(type) {
  const id = Date.now();
  const item = { id };
  resumeState[type].push(item);
  renderResumeFormList(type);
  updateResumePreview();
}

function removeResumeItem(type, id) {
  resumeState[type] = resumeState[type].filter(item => item.id !== id);
  renderResumeFormList(type);
  updateResumePreview();
}

function renderResumeFormList(type) {
  const container = document.getElementById(`res${type.charAt(0).toUpperCase() + type.slice(1)}List`);
  if(!container) return;
  container.innerHTML = resumeState[type].map(item => {
    if (type === 'edu') {
      return `
        <div class="resume-item-edit">
          <span class="remove-btn" onclick="removeResumeItem('edu', ${item.id})">Remove</span>
          <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 1.25rem;">
            <div class="form-group"><label>Institution</label><input type="text" placeholder="e.g. IIT Bombay" oninput="updateItemData('edu', ${item.id}, 'inst', this.value)" value="${item.inst || ''}"></div>
            <div class="form-group"><label>Degree</label><input type="text" placeholder="e.g. B.Tech CS" oninput="updateItemData('edu', ${item.id}, 'deg', this.value)" value="${item.deg || ''}"></div>
          </div>
          <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-top:0.5rem">
            <div class="form-group"><label>Graduation Year</label><input type="text" placeholder="e.g. 2024" oninput="updateItemData('edu', ${item.id}, 'year', this.value)" value="${item.year || ''}"></div>
            <div class="form-group"><label>Score (CGPA/%)</label><input type="text" placeholder="e.g. 9.2 or 85%" oninput="updateItemData('edu', ${item.id}, 'score', this.value)" value="${item.score || ''}"></div>
          </div>
        </div>
      `;
    } else if (type === 'exp') {
      return `
        <div class="resume-item-edit">
          <span class="remove-btn" onclick="removeResumeItem('exp', ${item.id})">Remove</span>
          <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 1.25rem;">
            <div class="form-group"><label>Company Name</label><input type="text" placeholder="e.g. Google" oninput="updateItemData('exp', ${item.id}, 'comp', this.value)" value="${item.comp || ''}"></div>
            <div class="form-group"><label>Job Title</label><input type="text" placeholder="e.g. Software Engineer" oninput="updateItemData('exp', ${item.id}, 'role', this.value)" value="${item.role || ''}"></div>
          </div>
          <div class="form-group" style="margin-top:0.5rem">
            <label>Duration</label>
            <input type="text" placeholder="e.g. Jan 2023 - Present" oninput="updateItemData('exp', ${item.id}, 'dur', this.value)" value="${item.dur || ''}">
          </div>
          <div class="form-group" style="margin-top:0.5rem">
            <label>Description</label>
            <textarea placeholder="Describe your achievements and responsibilities..." style="height:120px" oninput="updateItemData('exp', ${item.id}, 'desc', this.value)">${item.desc || ''}</textarea>
          </div>
        </div>
      `;
    } else {
      return `
        <div class="resume-item-edit">
          <span class="remove-btn" onclick="removeResumeItem('proj', ${item.id})">Remove</span>
          <div class="form-group">
            <label>Project Name</label>
            <input type="text" placeholder="e.g. E-commerce Platform" oninput="updateItemData('proj', ${item.id}, 'name', this.value)" value="${item.name || ''}">
          </div>
          <div class="form-group" style="margin-top:0.5rem">
            <label>Tech Stack</label>
            <input type="text" placeholder="e.g. React, Node.js, MongoDB" oninput="updateItemData('proj', ${item.id}, 'tech', this.value)" value="${item.tech || ''}">
          </div>
          <div class="form-group" style="margin-top:0.5rem">
            <label>Project Description</label>
            <textarea placeholder="Key results and features..." style="height:100px" oninput="updateItemData('proj', ${item.id}, 'desc', this.value)">${item.desc || ''}</textarea>
          </div>
        </div>
      `;
    }
  }).join('');
}

function updateItemData(type, id, field, val) {
  const item = resumeState[type].find(i => i.id === id);
  if (item) item[field] = val;
  updateResumePreview();
}

function updateResumePreview() {
  const paper = document.getElementById('resumePaper');
  if(!paper) return;
  const data = {
    name: document.getElementById('resName').value,
    title: document.getElementById('resTitle').value,
    email: document.getElementById('resEmail').value,
    phone: document.getElementById('resPhone').value,
    links: document.getElementById('resLinks').value,
    loc: document.getElementById('resLocation').value,
    summary: document.getElementById('resSummary').value,
    skills: document.getElementById('resSkills').value,
    ...resumeState
  };

  paper.innerHTML = `
    <div class="res-header">
      <h1>${data.name || 'YOUR NAME'}</h1>
      <div style="font-weight:700; color:var(--accent); margin-bottom:5pt">${data.title || 'Professional Title'}</div>
      <div class="res-contact">
        ${data.email ? `<span>${data.email}</span>` : ''}
        ${data.phone ? `<span>${data.phone}</span>` : ''}
        ${data.links ? `<span>${data.links}</span>` : ''}
        ${data.loc ? `<span>${data.loc}</span>` : ''}
      </div>
    </div>

    ${data.summary ? `
      <h2>Professional Summary</h2>
      <div class="res-summary">${data.summary}</div>
    ` : ''}

    ${data.exp.length ? `
      <h2>Professional Experience</h2>
      ${data.exp.map(e => `
        <div class="res-item">
          <div class="res-item-head">
            <span>${e.comp || 'Company'}</span>
            <span>${e.dur || ''}</span>
          </div>
          <div class="res-item-sub">
            <span>${e.role || 'Job Role'}</span>
          </div>
          <div class="res-item-desc">${e.desc || ''}</div>
        </div>
      `).join('')}
    ` : ''}

    ${data.edu.length ? `
      <h2>Education</h2>
      ${data.edu.map(e => `
        <div class="res-item">
          <div class="res-item-head">
            <span>${e.inst || 'Institution'}</span>
            <span>${e.year || ''}</span>
          </div>
          <div class="res-item-sub">
            <span>${e.deg || 'Degree'}</span>
            <span>${e.score || ''}</span>
          </div>
        </div>
      `).join('')}
    ` : ''}

    ${data.proj.length ? `
      <h2>Key Projects</h2>
      ${data.proj.map(p => `
        <div class="res-item">
          <div class="res-item-head">
            <span>${p.name || 'Project Name'}</span>
          </div>
          <div class="res-item-sub">
            <span>Tech: ${p.tech || ''}</span>
          </div>
          <div class="res-item-desc">${p.desc || ''}</div>
        </div>
      `).join('')}
    ` : ''}

    ${data.skills ? `
      <h2>Skills & Expertise</h2>
      <div class="res-summary">${data.skills}</div>
    ` : ''}
  `;
}

async function saveResume() {
  if (!state.user) { openModal('login'); return; }
  const data = {
    name: document.getElementById('resName').value,
    title: document.getElementById('resTitle').value,
    email: document.getElementById('resEmail').value,
    phone: document.getElementById('resPhone').value,
    links: document.getElementById('resLinks').value,
    loc: document.getElementById('resLocation').value,
    summary: document.getElementById('resSummary').value,
    skills: document.getElementById('resSkills').value,
    ...resumeState
  };
  try {
    const res = await fetch('/api/resume', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (res.ok) showToast('Resume draft saved! 💾', 'success');
  } catch (e) { showToast('Failed to save draft', 'error'); }
}

async function loadResume() {
  if (!state.user) return;
  try {
    const res = await fetch('/api/resume');
    if(!res.ok) return;
    const data = await res.json();
    if (data && data.name !== undefined) {
      document.getElementById('resName').value = data.name || '';
      document.getElementById('resTitle').value = data.title || '';
      document.getElementById('resEmail').value = data.email || '';
      document.getElementById('resPhone').value = data.phone || '';
      document.getElementById('resLinks').value = data.links || '';
      document.getElementById('resLocation').value = data.loc || '';
      document.getElementById('resSummary').value = data.summary || '';
      document.getElementById('resSkills').value = data.skills || '';
      resumeState.edu = data.edu || [];
      resumeState.exp = data.exp || [];
      resumeState.proj = data.proj || [];
      renderResumeFormList('edu');
      renderResumeFormList('exp');
      renderResumeFormList('proj');
    }
    updateResumePreview();
  } catch (e) {}
}

function printResume() {
  window.print();
}
// ── THEME TOGGLE ──────────────────────────────────────────────
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute('data-theme');
  const next = current === 'light' ? '' : 'light';
  if (next) {
    html.setAttribute('data-theme', 'light');
  } else {
    html.removeAttribute('data-theme');
  }
  const btn = document.getElementById('themeToggle');
  btn.textContent = next === 'light' ? '☀️' : '🌙';
  localStorage.setItem('theme', next || 'dark');
}

(function() {
  const saved = localStorage.getItem('theme');
  if (saved === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
    const btn = document.getElementById('themeToggle');
    if (btn) btn.textContent = '☀️';
  }
})();

// ── PERSONALIZED DASHBOARD ────────────────────────────────────
async function loadDashboard() {
  if (!state.user) { showPage('home'); openModal('login'); return; }
  await loadProgress();
  const completed = state.progress.completed || [];
  document.getElementById('dashCompleted').textContent = completed.length;
  document.getElementById('dashPoints').textContent = state.user.points || 0;
  try {
    const res = await fetch('/api/activity');
    const data = await res.json();
    document.getElementById('dashStreak').textContent = data.streak || 0;
  } catch(e) {}
  try {
    const res = await fetch('/api/leaderboard');
    const data = await res.json();
    const lb = data.leaderboard || [];
    const idx = lb.findIndex(u => u.username === state.user.username);
    document.getElementById('dashRank').textContent = idx >= 0 ? '#' + (idx + 1) : '—';
  } catch(e) {}
  const goalsEl = document.getElementById('dashGoals');
  const dsaDone = completed.filter(id => id.startsWith('dsa')).length;
  const aptDone = completed.filter(id => id.startsWith('apt')).length;
  const techDone = completed.filter(id => id.startsWith('tech')).length;
  goalsEl.innerHTML = `
    <div class="dash-goal-item"><span>${dsaDone > 0 ? '✅' : '⬜'}</span> Solve 1 DSA problem</div>
    <div class="dash-goal-item"><span>${aptDone >= 3 ? '✅' : '⬜'}</span> Practice 3 aptitude questions</div>
    <div class="dash-goal-item"><span>${techDone > 0 ? '✅' : '⬜'}</span> Review 1 technical concept</div>
  `;
  const cats = [
    { key: 'apt', label: 'Aptitude', color: 'var(--accent)' },
    { key: 'dsa', label: 'DSA', color: 'var(--accent2)' },
    { key: 'tech', label: 'Technical', color: 'var(--accent3)' },
    { key: 'hr', label: 'HR', color: 'var(--hard)' }
  ];
  const weakEl = document.getElementById('dashWeakAreas');
  weakEl.innerHTML = '<p style="color:var(--text2); font-size:0.9rem; margin-bottom:0.5rem">Based on your practice history:</p>';
  cats.forEach(cat => {
    const done = completed.filter(id => id.startsWith(cat.key)).length;
    const total = Math.max(done + 5, 10);
    const pct = Math.round((done / total) * 100);
    weakEl.innerHTML += `<div class="focus-bar"><div class="focus-bar-label">${cat.label}</div><div class="focus-bar-track"><div class="focus-bar-fill" style="width:${pct}%; background:${cat.color}"></div></div><div class="focus-bar-pct">${pct}%</div></div>`;
  });
  const recoEl = document.getElementById('dashRecommendations');
  const weakestCat = cats.reduce((min, cat) => {
    const done = completed.filter(id => id.startsWith(cat.key)).length;
    return done < (min.done === undefined ? Infinity : min.done) ? { ...cat, done } : min;
  }, { done: Infinity });
  const suggestions = [
    { title: 'Practice ' + weakestCat.label, desc: 'You have done ' + (weakestCat.done || 0) + ' — try more!', cat: weakestCat.key === 'apt' ? 'aptitude' : weakestCat.key === 'tech' ? 'technical' : weakestCat.key },
    { title: 'Take a Mock Test', desc: 'Test yourself under time pressure', page: 'mock-tests' },
    { title: 'Build Your Resume', desc: 'Create an ATS-friendly resume', page: 'resume-builder' },
    { title: 'AI Mock Interview', desc: 'Practice with our AI interviewer', page: 'ai-interviewer' }
  ];
  recoEl.innerHTML = suggestions.map(s => `<div class="dash-reco-card" onclick="${s.cat ? "showPage('practice','" + s.cat + "')" : "showPage('" + s.page + "')"}"><h4>${s.title}</h4><p>${s.desc}</p></div>`).join('');
  const cpEl = document.getElementById('dashCategoryProgress');
  cpEl.innerHTML = cats.map(cat => {
    const done = completed.filter(id => id.startsWith(cat.key)).length;
    const total = Math.max(done + 5, 10);
    const pct = Math.round((done / total) * 100);
    return `<div class="prog-row"><div class="prog-label">${cat.label}</div><div class="prog-bar-wrap"><div class="prog-bar" style="width:${pct}%"></div></div><div class="prog-count">${done}/${total}</div></div>`;
  }).join('');

  // Add Heatmap to Dashboard too
  try {
    const res = await fetch('/api/activity');
    const data = await res.json();
    renderHeatmap(data.activity || {});
  } catch(e) {}
}

// ── AI MOCK INTERVIEWER ───────────────────────────────────────
const interviewQuestionBank = {
  technical: {
    easy: ["What is the difference between a stack and a queue?","Explain what an API is in simple terms.","What is the difference between HTTP and HTTPS?","What is the purpose of an operating system?","Explain the concept of Object-Oriented Programming."],
    medium: ["Explain the difference between process and thread.","What are ACID properties in databases?","How does indexing work in databases?","What is the difference between TCP and UDP?","Explain the concept of virtual memory."],
    hard: ["Design a caching system. What eviction policies would you consider?","Explain CAP theorem and its implications for distributed systems.","How would you handle a database deadlock in production?","Explain the trade-offs between SQL and NoSQL databases.","Describe the internal workings of a garbage collector."]
  },
  hr: {
    easy: ["Tell me about yourself.","Why do you want to work here?","What are your strengths?","Where do you see yourself in 5 years?","Why should we hire you?"],
    medium: ["Describe a time you faced a difficult challenge.","Tell me about a time you disagreed with a team member.","What is your biggest weakness?","Describe a situation where you showed leadership.","How do you handle pressure and tight deadlines?"],
    hard: ["Tell me about a time you failed. What did you learn?","How would you convince a resistant stakeholder?","Describe an ethical dilemma you faced.","How would you handle a manager asking you to do something you disagree with?","What would you do if your team was heading in the wrong direction?"]
  },
  dsa: {
    easy: ["How would you reverse a string?","What data structure for balanced parentheses?","How would you find the max in an array?","Explain how a hash map works internally.","What is the time complexity of binary search?"],
    medium: ["How would you detect a cycle in a linked list?","Explain your approach to merge two sorted arrays.","How to find the longest common subsequence?","Describe finding the kth largest element.","How would you implement a LRU cache?"],
    hard: ["How would you solve the N-Queens problem?","Explain word break using DP.","Shortest path with negative edges?","Approach to the traveling salesman problem?","How would you implement a Trie?"]
  },
  'system-design': {
    easy: ["How would you design a URL shortener?","Walk me through designing a chat app.","How would you design a product page?","Design a simple blog platform.","How would you design a notification system?"],
    medium: ["How would you design Twitter's feed?","Design a ride-sharing service like Uber.","Design a video streaming platform.","Design a search autocomplete system.","How would you design a rate limiter?"],
    hard: ["Design Google Docs for real-time collaboration.","Design a distributed message queue.","How would you design a global CDN?","Design a recommendation engine for Netflix.","Design a system handling millions of concurrent transactions."]
  }
};

let aiIntState = { type: '', difficulty: '', company: '', questions: [], currentQ: 0, answers: [], scores: [] };

function initAIInterviewer() {
  document.getElementById('interviewSetup').classList.remove('hidden');
  document.getElementById('interviewChat').classList.add('hidden');
  document.getElementById('interviewResult').classList.add('hidden');
}

async function startAIInterview() {
  const type = document.getElementById('aiIntType').value;
  const diff = document.getElementById('aiIntDiff').value;
  const company = document.getElementById('aiIntCompany').value;
  
  let questions = [];
  
  // Try to fetch real previous year questions for this company
  if (company) {
    try {
      const res = await fetch(`/api/questions/${type}?company=${encodeURIComponent(company)}`);
      const data = await res.json();
      if (data.questions && data.questions.length > 0) {
        // Shuffle and take up to 5 real questions
        questions = data.questions
          .sort(() => Math.random() - 0.5)
          .slice(0, 5)
          .map(q => q.question);
      }
    } catch (e) {
      console.error("Error fetching company questions:", e);
    }
  }

  // Fallback to hardcoded bank if no company questions found
  if (questions.length === 0) {
    const bank = interviewQuestionBank[type] && interviewQuestionBank[type][diff] ? interviewQuestionBank[type][diff] : interviewQuestionBank.technical.medium;
    questions = [...bank].sort(() => Math.random() - 0.5).slice(0, 5);
  }

  aiIntState = { type, difficulty: diff, company, questions, currentQ: 0, answers: [], scores: [] };
  
  document.getElementById('interviewSetup').classList.add('hidden');
  document.getElementById('interviewChat').classList.remove('hidden');
  document.getElementById('interviewResult').classList.add('hidden');
  
  const typeLabels = { technical: '💻 Technical', hr: '🤝 HR / Behavioral', dsa: '⚡ DSA', 'system-design': '🏗️ System Design' };
  document.getElementById('aiIntTitle').textContent = (typeLabels[type] || type) + ' Interview' + (company ? ' — ' + company : '');
  document.getElementById('chatContainer').innerHTML = '';
  
  addChatMsg('ai', `Welcome! Since you mentioned ${company || 'your target company'}, I've prepared a set of ${company ? 'real questions asked previously at ' + company : 'standard interview questions'}. Let's begin!`);
  setTimeout(() => askNextQ(), 800);
}

function askNextQ() {
  if (aiIntState.currentQ >= aiIntState.questions.length) { endAIInterview(); return; }
  const q = aiIntState.questions[aiIntState.currentQ];
  document.getElementById('aiIntSubtitle').textContent = 'Question ' + (aiIntState.currentQ + 1) + ' of ' + aiIntState.questions.length;
  addChatMsg('ai', q);
  document.getElementById('chatInput').value = '';
  document.getElementById('chatInput').focus();
}

function addChatMsg(type, text) {
  const container = document.getElementById('chatContainer');
  const senderMap = { ai: '🤖 Interviewer', user: '👤 You', feedback: '📊 Feedback' };
  const div = document.createElement('div');
  div.className = 'chat-msg ' + type;
  div.innerHTML = '<div class="chat-sender">' + senderMap[type] + '</div><div>' + text + '</div>';
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

async function sendChatAnswer() {
  const input = document.getElementById('chatInput');
  const answer = input.value.trim();
  if (!answer) return;
  addChatMsg('user', answer);
  aiIntState.answers.push(answer);
  input.value = '';
  
  const btn = document.getElementById('chatSendBtn');
  btn.disabled = true;
  btn.textContent = 'Thinking...';

  try {
    const question = aiIntState.questions[aiIntState.currentQ];
    const messages = [{ role: 'user', content: `Question: "${question}"\n\nMy Answer: "${answer}"\n\nEvaluate my answer out of 10 and provide brief feedback.` }];
    const systemPrompt = `You are a professional ${aiIntState.type} interviewer. Evaluate the candidate's answer based on correctness, depth, and communication. Return your response EXACTLY in this JSON format, with no other text: {"score": 8, "feedback": "Your feedback here..."}`;

    const res = await fetch('/api/ai_chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, system_prompt: systemPrompt })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    
    let replyText = data.reply;
    const jsonMatch = replyText.match(/\{[\s\S]*\}/);
    if (jsonMatch) replyText = jsonMatch[0];
    const parsed = JSON.parse(replyText);
    
    const score = parsed.score || 5;
    aiIntState.scores.push(score);
    addChatMsg('feedback', `<strong>Score: ${score}/10</strong><br>${parsed.feedback}`);
    
  } catch (err) {
    console.error("AI Evaluation error:", err);
    const score = scoreAnswer(answer, aiIntState.type);
    aiIntState.scores.push(score);
    let fb = '';
    if (score >= 8) fb = '🌟 <strong>Excellent!</strong> Very thorough answer. ';
    else if (score >= 6) fb = '👍 <strong>Good answer!</strong> ';
    else if (score >= 4) fb = '⚠️ <strong>Decent attempt.</strong> ';
    else fb = '❌ <strong>Needs improvement.</strong> ';
    fb += '<br><em>Score: ' + score + '/10</em><br><small>(Fallback local evaluation used)</small>';
    addChatMsg('feedback', fb);
  }

  btn.disabled = false;
  btn.textContent = 'Send →';

  aiIntState.currentQ++;
  setTimeout(() => {
    if (aiIntState.currentQ < aiIntState.questions.length) { askNextQ(); }
    else {
      addChatMsg('ai', 'That concludes our interview! Let me prepare your scorecard...');
      setTimeout(() => endAIInterview(), 1500);
    }
  }, 1200);
}

function scoreAnswer(answer, type) {
  let score = 5;
  const words = answer.split(/\s+/).length;
  if (words > 100) score += 2;
  else if (words > 50) score += 1;
  else if (words < 15) score -= 2;
  if (answer.indexOf('example') !== -1 || answer.indexOf('for instance') !== -1) score += 1;
  if (answer.indexOf('because') !== -1 || answer.indexOf('therefore') !== -1) score += 1;
  const techKw = ['algorithm','complexity','data structure','database','API','cache','memory','thread','process','scalab','optim','hash','tree','stack','queue'];
  const hrKw = ['team','communic','leader','challenge','learn','grow','achieve','collaborat','manage','priorit','deadline','feedback'];
  const kws = type === 'hr' ? hrKw : techKw;
  const hits = kws.filter(k => answer.toLowerCase().indexOf(k) !== -1).length;
  score += Math.min(hits, 3);
  return Math.min(10, Math.max(1, score));
}

function endAIInterview() {
  document.getElementById('interviewChat').classList.add('hidden');
  document.getElementById('interviewResult').classList.remove('hidden');
  const scores = aiIntState.scores;
  const avg = scores.length > 0 ? (scores.reduce((a,b) => a + b, 0) / scores.length).toFixed(1) : 0;
  const best = scores.length > 0 ? Math.max(...scores) : 0;
  const worst = scores.length > 0 ? Math.min(...scores) : 0;
  let grade = '🏆 Outstanding';
  if (avg < 8) grade = '✅ Good';
  if (avg < 6) grade = '⚠️ Average';
  if (avg < 4) grade = '❌ Needs Practice';
  document.getElementById('interviewScorecard').innerHTML = '<div style="font-size:3rem; font-weight:800; color:var(--accent); margin-bottom:0.5rem; font-family:var(--font-display)">' + avg + '/10</div><div style="font-size:1.1rem; margin-bottom:2rem">' + grade + '</div><div class="scorecard-grid"><div class="scorecard-item"><div class="sc-label">Questions Answered</div><div class="sc-value">' + scores.length + '/5</div></div><div class="scorecard-item"><div class="sc-label">Average Score</div><div class="sc-value" style="color:var(--accent)">' + avg + '</div></div><div class="scorecard-item"><div class="sc-label">Best Answer</div><div class="sc-value" style="color:var(--accent2)">' + best + '/10</div></div><div class="scorecard-item"><div class="sc-label">Weakest Answer</div><div class="sc-value" style="color:var(--hard)">' + worst + '/10</div></div></div>';
}

function resetAIInterview() {
  aiIntState = { type: '', difficulty: '', company: '', questions: [], currentQ: 0, answers: [], scores: [] };
  initAIInterviewer();
}

// ── ROADMAPS ──────────────────────────────────────────────────
async function generateAIRoadmap() {
  const company = document.getElementById('roadmapCompany').value.trim();
  const role = document.getElementById('roadmapRole').value.trim();
  const skills = document.getElementById('roadmapSkills').value.trim();
  const duration = document.getElementById('roadmapDuration').value;

  if (!company || !role) {
    showToast('Please specify target company and role.', 'error');
    return;
  }

  const btn = document.getElementById('btnGenRoadmap');
  const originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = 'Generating with AI... ✨';

  try {
    const res = await fetch('/api/generate-roadmap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company, role, skills, duration })
    });
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    renderRoadmap(data);
  } catch (err) {
    showToast('Failed to generate roadmap. Using fallback...', 'error');
    loadStaticRoadmap(company.toLowerCase().includes('google') ? 'google' : (company.toLowerCase().includes('amazon') ? 'amazon' : 'tcs'));
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
  }
}

function loadStaticRoadmap(type) {
  const roadmaps = {
    google: {
      title: "Google SDE Roadmap",
      description: "A high-intensity path focused on advanced algorithms and system design.",
      phases: [
        { name: "Phase 1: DSA Foundations", days: "Day 1-15", tasks: ["Arrays & Strings (Sliding Window)", "Linked Lists & Stacks", "Trees & Graphs (BFS/DFS)"], resources: ["LeetCode Top 100", "Striver's SDE Sheet"] },
        { name: "Phase 2: Advanced Topics", days: "Day 16-30", tasks: ["Dynamic Programming (1D/2D)", "Graphs (Shortest Path, MST)", "Tries & Segment Trees"], resources: ["Google Recurring Patterns", "CP Algorithms"] },
        { name: "Phase 3: System Design & Core CS", days: "Day 31-45", tasks: ["Load Balancers, Caching, DB Sharding", "OS Fundamentals (Semaphores, Memory)", "LPU (Low Level Design)"], resources: ["Grokking the System Design", "Design Gurus"] }
      ],
      tips: ["Focus on time complexity optimization", "Practice clear communication during coding", "Understand the 'Googliness' principles"]
    },
    amazon: {
      title: "Amazon SDE-1 Roadmap",
      description: "Focused on core DSA and the famous Leadership Principles.",
      phases: [
        { name: "Phase 1: Core Problem Solving", days: "Day 1-20", tasks: ["Sorting & Searching", "Heaps & Priority Queues", "Binary Trees (Traversal, View)"], resources: ["Amazon Tagged LeetCode", "GFG Must Do"] },
        { name: "Phase 2: Leadership Principles", days: "Day 21-30", tasks: ["Study 16 LPs", "Prepare STAR stories for each LP", "Mock Behavioral Interviews"], resources: ["Amazon LP Official Guide", "Dan Croitor's YouTube"] },
        { name: "Phase 3: Scale & Design", days: "Day 31-40", tasks: ["Basic System Design Concepts", "Database Normalization", "Concurrency & Multi-threading"], resources: ["High Scalability Blog", "System Design Interview by Alex Xu"] }
      ],
      tips: ["LPs are as important as coding", "Know your projects inside out", "Focus on code quality and edge cases"]
    },
    tcs: {
      title: "TCS Digital/Ninja Roadmap",
      description: "A balanced path covering Aptitude, Core CS, and Basic Coding.",
      phases: [
        { name: "Phase 1: Aptitude & Reasoning", days: "Day 1-10", tasks: ["Quantitative Aptitude (P&L, Time/Work)", "Logical Reasoning", "Verbal Ability"], resources: ["IndiaBix", "R.S. Aggarwal"] },
        { name: "Phase 2: Technical Foundations", days: "Day 11-20", tasks: ["DBMS (SQL Queries, Joins)", "Operating Systems (Scheduling)", "Networking Basics"], resources: ["Knowledge Gate", "GFG Technical Notes"] },
        { name: "Phase 3: Programming", days: "Day 21-30", tasks: ["String Manipulation", "Array operations", "Basic Data Structures"], resources: ["TCS NQT Previous Papers", "Hackerrank Basic"] }
      ],
      tips: ["Speed in Aptitude is key", "Practice basic SQL queries", "Stay confident in HR rounds"]
    }
  };

  const data = roadmaps[type] || roadmaps['tcs'];
  renderRoadmap(data);
}

function renderRoadmap(data) {
  const placeholder = document.getElementById('roadmapPlaceholder');
  const display = document.getElementById('roadmapDisplay');
  
  placeholder.classList.add('hidden');
  display.classList.remove('hidden');

  display.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:2rem">
      <div>
        <h2 style="font-family:var(--font-display); font-size:2rem; margin-bottom:0.5rem">${data.title}</h2>
        <p style="color:var(--text2)">${data.description}</p>
      </div>
      <button class="btn-ghost" onclick="resetRoadmap()">← Back to All</button>
    </div>

    <div class="roadmap-content">
      ${data.phases.map((p, i) => `
        <div class="roadmap-phase">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem">
            <h3>${p.name}</h3>
            <span class="tag" style="background:var(--bg3)">${p.days}</span>
          </div>
          <ul class="roadmap-tasks">
            ${p.tasks.map(t => `<li>${t}</li>`).join('')}
          </ul>
          <div style="margin-top:1rem; padding:1rem; background:rgba(124,106,247,0.05); border-radius:8px; border:1px dashed var(--border)">
            <strong style="font-size:0.8rem; color:var(--accent); text-transform:uppercase">Recommended Resources:</strong>
            <p style="font-size:0.85rem; color:var(--text2); margin-top:0.3rem">${p.resources.join(', ')}</p>
          </div>
        </div>
      `).join('')}
    </div>

    <div style="margin-top:3rem; padding:2rem; background:var(--surface2); border:1px solid var(--border); border-radius:var(--radius)">
      <h3 style="margin-bottom:1rem">💡 Expert Tips</h3>
      <ul style="list-style:disc; padding-left:1.5rem; color:var(--text2)">
        ${data.tips.map(tip => `<li style="margin-bottom:0.5rem">${tip}</li>`).join('')}
      </ul>
    </div>
  `;
}

function resetRoadmap() {
  document.getElementById('roadmapPlaceholder').classList.remove('hidden');
  document.getElementById('roadmapDisplay').classList.add('hidden');
}

