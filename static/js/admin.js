document.addEventListener("DOMContentLoaded", () => {
    checkAuth();
    setupNavigation();
    
    // Default load
    loadDashboard();
    
    // Sidebar toggle
    document.getElementById('sidebarCollapse').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('active');
    });

    document.getElementById('logoutBtn').addEventListener('click', logout);
    document.getElementById('userSearch').addEventListener('input', filterUsers);
});

// -- Globals --
let usersData = [];
let companiesData = {};
let questionsData = [];
let currentConfirmAction = null;

// -- Auth & Init --
async function checkAuth() {
    try {
        const res = await fetch('/api/me');
        const data = await res.json();
        if (!data.logged_in || !data.is_admin) {
            window.location.href = '/';
        } else {
            document.getElementById('adminUsername').textContent = data.username;
        }
    } catch (e) {
        window.location.href = '/';
    }
}

async function logout() {
    await fetch('/api/logout', { method: 'POST' });
    window.location.href = '/';
}

// -- Navigation --
function setupNavigation() {
    const links = document.querySelectorAll('#sidebar ul li a');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active link
            document.querySelectorAll('#sidebar ul li').forEach(li => li.classList.remove('active'));
            link.parentElement.classList.add('active');
            
            // Show target section
            const targetId = link.getAttribute('data-target');
            document.querySelectorAll('.admin-section').forEach(sec => sec.classList.add('d-none'));
            document.getElementById(targetId).classList.remove('d-none');
            
            // Load data based on section
            if (targetId === 'dashboard-section') loadDashboard();
            if (targetId === 'users-section') loadUsers();
            if (targetId === 'companies-section') loadCompanies();
            if (targetId === 'questions-section') loadQuestions();
            if (targetId === 'interviews-section') loadInterviews();
            if (targetId === 'activity-section') loadActivity();
            
            // Mobile sidebar auto-close
            if (window.innerWidth <= 768) {
                document.getElementById('sidebar').classList.remove('active');
            }
        });
    });
}

// -- Dashboard --
async function loadDashboard() {
    try {
        const res = await fetch('/api/admin/dashboard_stats');
        const data = await res.json();
        
        // Cards
        document.getElementById('statsCards').innerHTML = `
            <div class="col-md-3">
                <div class="card bg-glass stat-card">
                    <div class="stat-info">
                        <h3>${data.total_users}</h3>
                        <p>Total Users</p>
                    </div>
                    <div class="icon-box"><i class="fas fa-users"></i></div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-glass stat-card">
                    <div class="stat-info">
                        <h3>${data.total_questions}</h3>
                        <p>Questions</p>
                    </div>
                    <div class="icon-box text-success"><i class="fas fa-code"></i></div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-glass stat-card">
                    <div class="stat-info">
                        <h3>${data.total_interviews}</h3>
                        <p>Interviews</p>
                    </div>
                    <div class="icon-box text-warning"><i class="fas fa-comments"></i></div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-glass stat-card">
                    <div class="stat-info">
                        <h3>${data.total_progress}</h3>
                        <p>Solves</p>
                    </div>
                    <div class="icon-box text-danger"><i class="fas fa-check-circle"></i></div>
                </div>
            </div>
        `;
        
        // Chart
        renderChart(data.chart_data);
        
        // Recent Users
        const tbody = document.getElementById('recentUsersTable').querySelector('tbody');
        tbody.innerHTML = '';
        data.recent_users.forEach(u => {
            tbody.innerHTML += `
                <tr>
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center text-dark fw-bold me-2" style="width: 32px; height: 32px;">
                                ${u.username.charAt(0).toUpperCase()}
                            </div>
                            ${u.username}
                        </div>
                    </td>
                    <td class="text-end text-muted">${u.joined}</td>
                </tr>
            `;
        });
    } catch (e) {
        showToast('Error loading dashboard', 'danger');
    }
}

let growthChartInstance = null;
function renderChart(chartData) {
    const ctx = document.getElementById('growthChart').getContext('2d');
    if (growthChartInstance) growthChartInstance.destroy();
    
    growthChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.map(d => d.date),
            datasets: [{
                label: 'New Users',
                data: chartData.map(d => d.count),
                borderColor: '#58a6ff',
                backgroundColor: 'rgba(88, 166, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#8b949e' } },
                x: { grid: { display: false }, ticks: { color: '#8b949e' } }
            }
        }
    });
}

// -- Users --
async function loadUsers() {
    try {
        const res = await fetch('/api/admin/users');
        usersData = await res.json();
        renderUsersTable(usersData);
    } catch (e) {
        showToast('Error loading users', 'danger');
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = '';
    users.forEach(u => {
        // Mock is_banned if not in API response for backward compat check
        const isBanned = u.is_banned || u.role === 'banned'; 
        const badgeClass = u.role === 'admin' ? 'bg-danger' : (isBanned ? 'bg-secondary' : 'bg-primary');
        
        tbody.innerHTML += `
            <tr>
                <td>#${u.id}</td>
                <td>${u.username}</td>
                <td>${u.email}</td>
                <td>${u.points || 0}</td>
                <td><span class="badge ${badgeClass}">${u.role}</span></td>
                <td>${u.joined}</td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick='openEditUser(${JSON.stringify(u)})'><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-outline-danger ms-1" onclick="confirmDeleteUser(${u.id})"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `;
    });
}

function filterUsers(e) {
    const term = e.target.value.toLowerCase();
    const filtered = usersData.filter(u => 
        u.username.toLowerCase().includes(term) || 
        u.email.toLowerCase().includes(term)
    );
    renderUsersTable(filtered);
}

function openEditUser(user) {
    document.getElementById('editUserId').value = user.id;
    document.getElementById('editUsername').value = user.username;
    document.getElementById('editRole').value = user.role;
    document.getElementById('editPoints').value = user.points || 0;
    // Assuming API sends these, else default false
    document.getElementById('editIsVerified').checked = user.is_verified || false;
    document.getElementById('editIsBanned').checked = user.is_banned || false;
    
    new bootstrap.Modal(document.getElementById('editUserModal')).show();
}

async function saveUser() {
    const id = document.getElementById('editUserId').value;
    const data = {
        role: document.getElementById('editRole').value,
        points: document.getElementById('editPoints').value,
        is_verified: document.getElementById('editIsVerified').checked,
        is_banned: document.getElementById('editIsBanned').checked
    };
    
    try {
        const res = await fetch(\`/api/admin/users/\${id}\`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if (res.ok) {
            showToast('User updated successfully');
            bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
            loadUsers();
        } else {
            showToast('Failed to update user', 'danger');
        }
    } catch (e) {
        showToast('Error', 'danger');
    }
}

function confirmDeleteUser(id) {
    document.getElementById('confirmMessage').textContent = "Are you sure you want to delete this user? This cannot be undone.";
    currentConfirmAction = async () => {
        const res = await fetch(\`/api/admin/users/\${id}\`, { method: 'DELETE' });
        if(res.ok) {
            showToast('User deleted');
            loadUsers();
        }
    };
    new bootstrap.Modal(document.getElementById('confirmModal')).show();
}

// -- Common Confirm Action --
document.getElementById('confirmActionBtn').addEventListener('click', async () => {
    if (currentConfirmAction) {
        await currentConfirmAction();
        currentConfirmAction = null;
        bootstrap.Modal.getInstance(document.getElementById('confirmModal')).hide();
    }
});

// -- Toast Notification --
function showToast(msg, type='success') {
    const toastEl = document.getElementById('liveToast');
    toastEl.className = \`toast align-items-center text-bg-\${type} border-0\`;
    document.getElementById('toastMessage').textContent = msg;
    new bootstrap.Toast(toastEl).show();
}

// -- Companies --
async function loadCompanies() {
    try {
        const res = await fetch('/api/companies');
        companiesData = await res.json();
        renderCompanies();
    } catch (e) {
        showToast('Error loading companies', 'danger');
    }
}

function renderCompanies() {
    const container = document.getElementById('companiesContainer');
    container.innerHTML = '';
    
    Object.keys(companiesData).forEach(category => {
        let title = category.replace('_', ' ').toUpperCase();
        
        let html = \`<div class="col-12 mt-4"><h4>\${title}</h4></div>\`;
        
        companiesData[category].forEach((comp, idx) => {
            html += \`
                <div class="col-md-4">
                    <div class="card bg-glass h-100">
                        <div class="card-body">
                            <div class="d-flex align-items-center mb-3">
                                <div class="rounded d-flex align-items-center justify-content-center text-white fw-bold me-3" style="width: 40px; height: 40px; background-color: \${comp.color}">
                                    \${comp.logo}
                                </div>
                                <h5 class="card-title mb-0">\${comp.name}</h5>
                            </div>
                            <p class="card-text text-muted small mb-2"><i class="fas fa-briefcase"></i> \${comp.roles}</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="badge bg-primary">\${comp.difficulty}</span>
                                <div>
                                    <button class="btn btn-sm btn-outline-info" onclick='openEditCompany("\${category}", \${idx}, \${JSON.stringify(comp)})'><i class="fas fa-edit"></i></button>
                                    <button class="btn btn-sm btn-outline-danger ms-1" onclick="confirmDeleteCompany('\${category}', \${idx})"><i class="fas fa-trash"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            \`;
        });
        container.innerHTML += html;
    });
}

function showCompanyModal() {
    document.getElementById('companyIndex').value = '';
    document.getElementById('companyOldCategory').value = '';
    document.getElementById('compName').value = '';
    document.getElementById('compCat').value = 'product_mncs';
    document.getElementById('compLogo').value = '';
    document.getElementById('compColor').value = '#000000';
    document.getElementById('compDiff').value = 'Medium';
    document.getElementById('compRounds').value = '';
    document.getElementById('compCtc').value = '';
    document.getElementById('compRoles').value = '';
    
    document.getElementById('companyModalTitle').textContent = 'Add Company';
    new bootstrap.Modal(document.getElementById('companyModal')).show();
}

function openEditCompany(cat, idx, comp) {
    document.getElementById('companyIndex').value = idx;
    document.getElementById('companyOldCategory').value = cat;
    
    document.getElementById('compName').value = comp.name;
    document.getElementById('compCat').value = cat;
    document.getElementById('compLogo').value = comp.logo;
    document.getElementById('compColor').value = comp.color;
    document.getElementById('compDiff').value = comp.difficulty;
    document.getElementById('compRounds').value = comp.rounds;
    document.getElementById('compCtc').value = comp.ctc;
    document.getElementById('compRoles').value = comp.roles;
    
    document.getElementById('companyModalTitle').textContent = 'Edit Company';
    new bootstrap.Modal(document.getElementById('companyModal')).show();
}

async function saveCompany() {
    const idx = document.getElementById('companyIndex').value;
    const oldCat = document.getElementById('companyOldCategory').value;
    const newCat = document.getElementById('compCat').value;
    
    const company = {
        name: document.getElementById('compName').value,
        logo: document.getElementById('compLogo').value,
        color: document.getElementById('compColor').value,
        difficulty: document.getElementById('compDiff').value,
        rounds: document.getElementById('compRounds').value,
        ctc: document.getElementById('compCtc').value,
        roles: document.getElementById('compRoles').value,
        categories: [] // Simplification
    };
    
    try {
        let method = 'POST';
        let body = { category: newCat, company: company };
        
        if (idx !== '') {
            // Editing existing
            if (oldCat === newCat) {
                method = 'PUT';
                body.index = parseInt(idx);
            } else {
                // Category changed: delete old, create new
                await fetch('/api/admin/companies', {
                    method: 'DELETE',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ category: oldCat, index: parseInt(idx) })
                });
                method = 'POST';
            }
        }
        
        const res = await fetch('/api/admin/companies', {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        });
        
        if (res.ok) {
            showToast('Company saved');
            bootstrap.Modal.getInstance(document.getElementById('companyModal')).hide();
            loadCompanies();
        }
    } catch (e) {
        showToast('Error saving company', 'danger');
    }
}

function confirmDeleteCompany(cat, idx) {
    document.getElementById('confirmMessage').textContent = "Delete this company?";
    currentConfirmAction = async () => {
        const res = await fetch('/api/admin/companies', {
            method: 'DELETE',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ category: cat, index: idx })
        });
        if(res.ok) {
            showToast('Company deleted');
            loadCompanies();
        }
    };
    new bootstrap.Modal(document.getElementById('confirmModal')).show();
}


// -- Questions --
async function loadQuestions() {
    try {
        // Fetch all questions by category
        const cats = ['technical', 'dsa', 'aptitude', 'hr'];
        questionsData = [];
        for (const cat of cats) {
            const res = await fetch(\`/api/questions/\${cat}\`);
            const data = await res.json();
            questionsData = questionsData.concat(data.questions);
        }
        renderQuestionsTable(questionsData);
    } catch (e) {
        showToast('Error loading questions', 'danger');
    }
}

function renderQuestionsTable(questions) {
    const tbody = document.getElementById('questionsTableBody');
    tbody.innerHTML = '';
    questions.forEach(q => {
        let diffClass = q.difficulty === 'Hard' ? 'danger' : (q.difficulty.includes('Medium') ? 'warning' : 'success');
        tbody.innerHTML += `
            <tr>
                <td>${q.id}</td>
                <td><div style="max-width:250px" class="text-truncate">${q.title || 'Untitled'}</div></td>
                <td>${q.company || '-'}</td>
                <td><span class="badge bg-secondary">${q.category}</span></td>
                <td><span class="badge bg-${diffClass} text-dark">${q.difficulty}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick='openEditQuestion(${JSON.stringify(q)})'><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-outline-danger ms-1" onclick="confirmDeleteQuestion('${q.id}')"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `;
    });
}

function showQuestionModal() {
    document.getElementById('qId').value = '';
    document.getElementById('qTitle').value = '';
    document.getElementById('qCompany').value = '';
    document.getElementById('qCategory').value = 'technical';
    document.getElementById('qDifficulty').value = 'Medium';
    document.getElementById('qText').value = '';
    document.getElementById('qSolution').value = '';
    
    document.getElementById('questionModalTitle').textContent = 'Add Question';
    new bootstrap.Modal(document.getElementById('questionModal')).show();
}

function openEditQuestion(q) {
    document.getElementById('qId').value = q.id;
    document.getElementById('qTitle').value = q.title || '';
    document.getElementById('qCompany').value = q.company || '';
    document.getElementById('qCategory').value = q.category || 'technical';
    document.getElementById('qDifficulty').value = q.difficulty || 'Medium';
    document.getElementById('qText').value = q.question || '';
    document.getElementById('qSolution').value = q.solution || '';
    
    document.getElementById('questionModalTitle').textContent = 'Edit Question';
    new bootstrap.Modal(document.getElementById('questionModal')).show();
}

async function saveQuestion() {
    const id = document.getElementById('qId').value;
    const isNew = id === '';
    
    const url = isNew ? '/api/admin/add_question' : \`/api/admin/questions/\${id}\`;
    const method = isNew ? 'POST' : 'PUT';
    
    const data = {
        title: document.getElementById('qTitle').value,
        company: document.getElementById('qCompany').value,
        category: document.getElementById('qCategory').value,
        difficulty: document.getElementById('qDifficulty').value,
        question: document.getElementById('qText').value,
        solution: document.getElementById('qSolution').value
    };
    
    try {
        const res = await fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (res.ok) {
            showToast('Question saved successfully');
            bootstrap.Modal.getInstance(document.getElementById('questionModal')).hide();
            loadQuestions();
        }
    } catch(e) {
        showToast('Error saving question', 'danger');
    }
}

function confirmDeleteQuestion(id) {
    document.getElementById('confirmMessage').textContent = "Delete this question permanently?";
    currentConfirmAction = async () => {
        const res = await fetch(\`/api/admin/questions/\${id}\`, { method: 'DELETE' });
        if(res.ok) {
            showToast('Question deleted');
            loadQuestions();
        }
    };
    new bootstrap.Modal(document.getElementById('confirmModal')).show();
}

// -- Interviews --
async function loadInterviews() {
    try {
        const res = await fetch('/api/admin/interviews');
        const data = await res.json();
        
        const tbody = document.getElementById('interviewsTableBody');
        tbody.innerHTML = '';
        data.forEach(i => {
            tbody.innerHTML += `
                <tr>
                    <td>${i.date}</td>
                    <td>${i.username}</td>
                    <td>${i.company}</td>
                    <td>${i.role}</td>
                    <td>${i.difficulty}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-danger" onclick="confirmDeleteInterview(${i.id})"><i class="fas fa-trash"></i></button>
                    </td>
                </tr>
            `;
        });
    } catch(e) {}
}

function confirmDeleteInterview(id) {
    document.getElementById('confirmMessage').textContent = "Delete this interview experience?";
    currentConfirmAction = async () => {
        const res = await fetch(\`/api/admin/interviews?id=\${id}\`, { method: 'DELETE' });
        if(res.ok) {
            showToast('Interview deleted');
            loadInterviews();
        }
    };
    new bootstrap.Modal(document.getElementById('confirmModal')).show();
}

// -- Activity --
async function loadActivity() {
    try {
        const res = await fetch('/api/admin/activity');
        const data = await res.json();
        
        const tbody = document.getElementById('activityTableBody');
        tbody.innerHTML = '';
        data.forEach(a => {
            tbody.innerHTML += `
                <tr>
                    <td>${a.date}</td>
                    <td>${a.username}</td>
                    <td><span class="badge bg-success">${a.count}</span></td>
                </tr>
            `;
        });
    } catch(e) {}
}
