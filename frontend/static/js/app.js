// 全局变量
let currentPage = 'dashboard';
let currentUser = null;

// 获取 token
const getToken = () => localStorage.getItem('token');

// 通用请求函数
const request = async (url, options = {}) => {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    const response = await fetch(url, { ...options, headers });
    const data = await response.json();
    if (data.code === 401) {
        localStorage.clear();
        window.location.href = '/login';
        throw new Error('登录已过期');
    }
    if (data.code !== 200) {
        throw new Error(data.msg || '请求失败');
    }
    return data;
};

// ==================== Toast 通知组件 ====================
function showToast(message, type = 'error') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? 'fa-check-circle' : (type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle');
    toast.innerHTML = `<i class="fas ${icon}"></i><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// 显示提示消息（简单alert，可替换为更美观的toast）
const showMsg = (msg, isError = true) => {
    showToast(msg, isError ? 'error' : 'success');
};

// 加载页面内容
const loadPage = async (page) => {
    const container = document.getElementById('pageContent');
    container.innerHTML = '<div class="loading">加载中...</div>';
    try {
        switch (page) {
            case 'dashboard':
                await loadDashboard();
                break;
            case 'user':
                await loadUserList();
                break;
            case 'class':
                await loadClassList();
                break;
            case 'student':
                await loadStudentList();
                break;
            case 'score':
                await loadScoreList();
                break;
            case 'notice':
                await loadNoticeList();
                break;
            case 'profile':
                await loadProfile();
                break;
            default:
                container.innerHTML = '<div class="card">页面不存在</div>';
        }
    } catch (err) {
        container.innerHTML = `<div class="card">加载失败: ${err.message}</div>`;
    }
};

// 仪表盘
const loadDashboard = async () => {
    const html = `
        <div class="card">
            <h3>欢迎使用学生管理系统</h3>
            <p>您可以通过左侧菜单管理用户、班级、学生、成绩和公告。</p>
            <hr>
            <p>当前登录用户: ${currentUser.real_name} (${currentUser.role_type === 1 ? '管理员' : (currentUser.role_type === 2 ? '教师' : '学生')})</p>
        </div>
    `;
    document.getElementById('pageContent').innerHTML = html;
};

// ==================== 用户管理 ====================
let userPage = 1, userPageSize = 10;
const loadUserList = async () => {
    const container = document.getElementById('pageContent');
    if (currentUser.role_type !== 1) {
        container.innerHTML = '<div class="card">权限不足，仅管理员可访问</div>';
        return;
    }
    const data = await request(`/api/user/list?page=${userPage}&page_size=${userPageSize}`);
    const users = data.data.list;
    let html = `
        <div class="card">
            <div class="card-header">
                <h3>用户管理</h3>
                <button class="btn btn-primary" onclick="showAddUser()">+ 新增用户</button>
            </div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr><th>ID</th><th>用户名</th><th>真实姓名</th><th>角色</th><th>电话</th><th>状态</th><th>操作</th></tr>
                    </thead>
                    <tbody>
    `;
    users.forEach(u => {
        const roleText = u.role_type === 1 ? '管理员' : (u.role_type === 2 ? '教师' : '学生');
        const statusText = u.status === 1 ? '正常' : '禁用';
        html += `<tr>
            <td>${u.id}</td><td>${u.username}</td><td>${u.real_name}</td>
            <td>${roleText}</td><td>${u.phone || '-'}</td><td>${statusText}</td>
            <td>
                <button class="btn btn-warning btn-sm" onclick="editUser(${u.id})">编辑</button>
                <button class="btn btn-danger btn-sm" onclick="deleteUser(${u.id})">删除</button>
            </td>
        </tr>`;
    });
    html += `</tbody></table></div><div class="pagination" id="userPagination"></div></div>`;
    container.innerHTML = html;
    renderPagination('userPagination', data.data.total, userPage, userPageSize, (newPage) => {
        userPage = newPage;
        loadUserList();
    });
};

window.showAddUser = () => {
    const modalHtml = `
        <div class="modal" id="userModal">
            <div class="modal-content">
                <div class="modal-header"><span>新增用户</span><span class="close" onclick="closeModal()">&times;</span></div>
                <form id="userForm">
                    <div class="form-group"><label>用户名</label><input id="username" required></div>
                    <div class="form-group"><label>密码</label><input id="password" type="password" required></div>
                    <div class="form-group"><label>真实姓名</label><input id="real_name" required></div>
                    <div class="form-group"><label>角色</label>
                        <select id="role_type"><option value="1">管理员</option><option value="2">教师</option><option value="3">学生</option></select>
                    </div>
                    <div class="form-group"><label>电话</label><input id="phone"></div>
                    <div class="form-group"><label>状态</label>
                        <select id="status"><option value="1">正常</option><option value="0">禁用</option></select>
                    </div>
                    <button type="submit" class="btn btn-primary">提交</button>
                </form>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('userModal');
    modal.classList.add('show');
    document.getElementById('userForm').onsubmit = async (e) => {
        e.preventDefault();
        const data = {
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
            real_name: document.getElementById('real_name').value,
            role_type: parseInt(document.getElementById('role_type').value),
            phone: document.getElementById('phone').value,
            status: parseInt(document.getElementById('status').value)
        };
        try {
            await request('/api/user/add', { method: 'POST', body: JSON.stringify(data) });
            showMsg('添加成功', false);
            closeModal();
            loadUserList();
        } catch (err) {
            showMsg(err.message);
        }
    };
};

window.editUser = async (id) => {
    // 先获取用户详情（列表已有信息，但为了简单，直接构造更新表单，需要先查询）
    const data = await request(`/api/user/list?page=1&page_size=100`);
    const user = data.data.list.find(u => u.id === id);
    if (!user) return;
    const modalHtml = `
        <div class="modal" id="userModal">
            <div class="modal-content">
                <div class="modal-header"><span>编辑用户</span><span class="close" onclick="closeModal()">&times;</span></div>
                <form id="userForm">
                    <input type="hidden" id="userId" value="${id}">
                    <div class="form-group"><label>真实姓名</label><input id="real_name" value="${user.real_name}" required></div>
                    <div class="form-group"><label>电话</label><input id="phone" value="${user.phone || ''}"></div>
                    <div class="form-group"><label>新密码</label><input id="password" type="password" placeholder="留空则不修改"></div>
                    ${currentUser.role_type === 1 ? `<div class="form-group"><label>状态</label><select id="status"><option value="1" ${user.status === 1 ? 'selected' : ''}>正常</option><option value="0" ${user.status === 0 ? 'selected' : ''}>禁用</option></select></div>` : ''}
                    <button type="submit" class="btn btn-primary">保存</button>
                </form>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('userModal');
    modal.classList.add('show');
    document.getElementById('userForm').onsubmit = async (e) => {
        e.preventDefault();
        const payload = { id: parseInt(document.getElementById('userId').value), real_name: document.getElementById('real_name').value, phone: document.getElementById('phone').value };
        const pwd = document.getElementById('password').value;
        if (pwd) payload.password = pwd;
        const statusEl = document.getElementById('status');
        if (statusEl) payload.status = parseInt(statusEl.value);
        try {
            await request('/api/user/update', { method: 'PUT', body: JSON.stringify(payload) });
            showMsg('更新成功', false);
            closeModal();
            loadUserList();
        } catch (err) {
            showMsg(err.message);
        }
    };
};

window.deleteUser = async (id) => {
    if (confirm('确定删除该用户吗？')) {
        try {
            await request(`/api/user/delete/${id}`, { method: 'DELETE' });
            showMsg('删除成功', false);
            loadUserList();
        } catch (err) {
            showMsg(err.message);
        }
    }
};

// ==================== 班级管理 ====================
let classList = [];
const loadClassList = async () => {
    const data = await request('/api/class/list');
    classList = data.data;
    let html = `
        <div class="card">
            <div class="card-header">
                <h3>班级管理</h3>
                ${currentUser.role_type === 1 ? '<button class="btn btn-primary" onclick="showAddClass()">+ 新增班级</button>' : ''}
            </div>
            <div class="table-responsive"><table><thead><tr><th>ID</th><th>班级名称</th><th>班级编号</th><th>班主任</th><th>创建时间</th>${currentUser.role_type === 1 ? '<th>操作</th>' : ''}</tr></thead><tbody>`;
    classList.forEach(c => {
        html += `<tr><td>${c.id}</td><td>${c.class_name}</td><td>${c.class_code}</td><td>${c.teacher_name || '-'}</td><td>${c.create_time}</td>`;
        if (currentUser.role_type === 1) {
            html += `<td><button class="btn btn-warning btn-sm" onclick="editClass(${c.id})">编辑</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteClass(${c.id})">删除</button></td>`;
        }
        html += `</tr>`;
    });
    html += `</tbody></table></div></div>`;
    document.getElementById('pageContent').innerHTML = html;
};

window.showAddClass = () => {
    const modalHtml = `
        <div class="modal" id="classModal"><div class="modal-content"><div class="modal-header"><span>新增班级</span><span class="close" onclick="closeModal()">&times;</span></div>
        <form id="classForm"><div class="form-group"><label>班级名称</label><input id="class_name" required></div>
        <div class="form-group"><label>班级编号</label><input id="class_code" required></div>
        <div class="form-group"><label>班主任ID</label><input id="teacher_id" type="number"></div>
        <button type="submit" class="btn btn-primary">提交</button></form></div></div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('classModal');
    modal.classList.add('show');
    document.getElementById('classForm').onsubmit = async (e) => {
        e.preventDefault();
        const data = {
            class_name: document.getElementById('class_name').value,
            class_code: document.getElementById('class_code').value,
            teacher_id: parseInt(document.getElementById('teacher_id').value) || null
        };
        try {
            await request('/api/class/add', { method: 'POST', body: JSON.stringify(data) });
            showMsg('添加成功', false);
            closeModal();
            loadClassList();
        } catch (err) {
            showMsg(err.message);
        }
    };
};

window.editClass = async (id) => {
    const cls = classList.find(c => c.id === id);
    const modalHtml = `
        <div class="modal" id="classModal"><div class="modal-content"><div class="modal-header"><span>编辑班级</span><span class="close" onclick="closeModal()">&times;</span></div>
        <form id="classForm"><input type="hidden" id="classId" value="${id}">
        <div class="form-group"><label>班级名称</label><input id="class_name" value="${cls.class_name}" required></div>
        <div class="form-group"><label>班主任ID</label><input id="teacher_id" value="${cls.teacher_id || ''}"></div>
        <button type="submit" class="btn btn-primary">保存</button></form></div></div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('classModal');
    modal.classList.add('show');
    document.getElementById('classForm').onsubmit = async (e) => {
        e.preventDefault();
        const data = {
            id: parseInt(document.getElementById('classId').value),
            class_name: document.getElementById('class_name').value,
            teacher_id: parseInt(document.getElementById('teacher_id').value) || null
        };
        try {
            await request('/api/class/update', { method: 'PUT', body: JSON.stringify(data) });
            showMsg('更新成功', false);
            closeModal();
            loadClassList();
        } catch (err) {
            showMsg(err.message);
        }
    };
};

window.deleteClass = async (id) => {
    if (confirm('删除班级会清空该班学生的班级ID，确定吗？')) {
        try {
            await request(`/api/class/delete/${id}`, { method: 'DELETE' });
            showMsg('删除成功', false);
            loadClassList();
        } catch (err) {
            showMsg(err.message);
        }
    }
};

// ==================== 学生管理 ====================
let studentPage = 1;
const loadStudentList = async () => {
    const data = await request(`/api/student/list?page=${studentPage}&page_size=10`);
    const students = data.data.list;
    let html = `
        <div class="card">
            <div class="card-header"><h3>学生管理</h3>
            ${(currentUser.role_type === 1 || currentUser.role_type === 2) ? '<button class="btn btn-primary" onclick="showAddStudent()">+ 新增学生</button>' : ''}
            </div>
            <div class="table-responsive"><table><thead><tr><th>学号</th><th>姓名</th><th>性别</th><th>年龄</th><th>电话</th><th>班级</th><th>操作</th></tr></thead><tbody>`;
    students.forEach(s => {
        const gender = s.gender === 1 ? '男' : (s.gender === 2 ? '女' : '-');
        html += `<tr><td>${s.student_no}</td><td>${s.name}</td><td>${gender}</td><td>${s.age || '-'}</td><td>${s.phone || '-'}</td><td>${s.class_name || '-'}</td>
        <td>${(currentUser.role_type === 1 || currentUser.role_type === 2) ? `<button class="btn btn-warning btn-sm" onclick="editStudent(${s.id})">编辑</button>
        <button class="btn btn-danger btn-sm" onclick="deleteStudent(${s.id})">删除</button>` : (currentUser.role_type === 3 ? '只读' : '')}</td></tr>`;
    });
    html += `</tbody></table></div><div class="pagination" id="studentPagination"></div></div>`;
    document.getElementById('pageContent').innerHTML = html;
    renderPagination('studentPagination', data.data.total, studentPage, 10, (newPage) => {
        studentPage = newPage;
        loadStudentList();
    });
};

window.showAddStudent = async () => {
    // 获取班级列表用于下拉
    const classData = await request('/api/class/list');
    const classes = classData.data;
    const classOptions = classes.map(c => `<option value="${c.id}">${c.class_name}</option>`).join('');
    const modalHtml = `
        <div class="modal" id="studentModal"><div class="modal-content"><div class="modal-header"><span>新增学生</span><span class="close" onclick="closeModal()">&times;</span></div>
        <form id="studentForm"><div class="form-group"><label>学号</label><input id="student_no" required></div>
        <div class="form-group"><label>姓名</label><input id="name" required></div>
        <div class="form-group"><label>性别</label><select id="gender"><option value="1">男</option><option value="2">女</option></select></div>
        <div class="form-group"><label>年龄</label><input id="age" type="number"></div>
        <div class="form-group"><label>电话</label><input id="phone"></div>
        <div class="form-group"><label>班级</label><select id="class_id">${classOptions}</select></div>
        <div class="form-group"><label>用户名（可选，默认学号）</label><input id="username"></div>
        <button type="submit" class="btn btn-primary">提交</button></form></div></div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('studentModal');
    modal.classList.add('show');
    document.getElementById('studentForm').onsubmit = async (e) => {
        e.preventDefault();
        const data = {
            student_no: document.getElementById('student_no').value,
            name: document.getElementById('name').value,
            gender: parseInt(document.getElementById('gender').value),
            age: parseInt(document.getElementById('age').value) || null,
            phone: document.getElementById('phone').value,
            class_id: parseInt(document.getElementById('class_id').value),
            username: document.getElementById('username').value || undefined
        };
        try {
            await request('/api/student/add', { method: 'POST', body: JSON.stringify(data) });
            showMsg('添加成功', false);
            closeModal();
            loadStudentList();
        } catch (err) {
            showMsg(err.message);
        }
    };
};

window.editStudent = async (id) => {
    const data = await request(`/api/student/list?page=1&page_size=100`);
    const student = data.data.list.find(s => s.id === id);
    const classData = await request('/api/class/list');
    const classOptions = classData.data.map(c => `<option value="${c.id}" ${c.id === student.class_id ? 'selected' : ''}>${c.class_name}</option>`).join('');
    const modalHtml = `
        <div class="modal" id="studentModal"><div class="modal-content"><div class="modal-header"><span>编辑学生</span><span class="close" onclick="closeModal()">&times;</span></div>
        <form id="studentForm"><input type="hidden" id="studentId" value="${id}">
        <div class="form-group"><label>姓名</label><input id="name" value="${student.name}" required></div>
        <div class="form-group"><label>性别</label><select id="gender"><option value="1" ${student.gender === 1 ? 'selected' : ''}>男</option><option value="2" ${student.gender === 2 ? 'selected' : ''}>女</option></select></div>
        <div class="form-group"><label>年龄</label><input id="age" value="${student.age || ''}"></div>
        <div class="form-group"><label>电话</label><input id="phone" value="${student.phone || ''}"></div>
        <div class="form-group"><label>班级</label><select id="class_id">${classOptions}</select></div>
        <button type="submit" class="btn btn-primary">保存</button></form></div></div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('studentModal');
    modal.classList.add('show');
    document.getElementById('studentForm').onsubmit = async (e) => {
        e.preventDefault();
        const payload = {
            id: parseInt(document.getElementById('studentId').value),
            name: document.getElementById('name').value,
            gender: parseInt(document.getElementById('gender').value),
            age: parseInt(document.getElementById('age').value) || null,
            phone: document.getElementById('phone').value,
            class_id: parseInt(document.getElementById('class_id').value)
        };
        try {
            await request('/api/student/update', { method: 'PUT', body: JSON.stringify(payload) });
            showMsg('更新成功', false);
            closeModal();
            loadStudentList();
        } catch (err) {
            showMsg(err.message);
        }
    };
};

window.deleteStudent = async (id) => {
    if (confirm('删除学生将同时删除其登录账号，确定吗？')) {
        try {
            await request(`/api/student/delete/${id}`, { method: 'DELETE' });
            showMsg('删除成功', false);
            loadStudentList();
        } catch (err) {
            showMsg(err.message);
        }
    }
};

// ==================== 成绩管理 ====================
let scorePage = 1;
const loadScoreList = async () => {
    const data = await request(`/api/score/list?page=${scorePage}&page_size=10`);
    const scores = data.data.list;
    let html = `
        <div class="card">
            <div class="card-header"><h3>成绩管理</h3>
            ${(currentUser.role_type === 1 || currentUser.role_type === 2) ? '<button class="btn btn-primary" onclick="showAddScore()">+ 录入成绩</button>' : ''}
            </div>
            <div class="table-responsive"><table><thead><tr><th>学生姓名</th><th>学号</th><th>科目</th><th>分数</th><th>学期</th><th>录入时间</th>${(currentUser.role_type !== 3) ? '<th>操作</th>' : ''}</tr></thead><tbody>`;
    scores.forEach(s => {
        html += `<tr><td>${s.student_name}</td><td>${s.student_no}</td><td>${s.subject}</td><td>${s.score}</td><td>${s.semester}</td><td>${s.create_time}</td>`;
        if (currentUser.role_type !== 3) {
            html += `<td><button class="btn btn-warning btn-sm" onclick="editScore(${s.id})">编辑</button>
            <button class="btn btn-danger btn-sm" onclick="deleteScore(${s.id})">删除</button></td>`;
        }
        html += `</tr>`;
    });
    html += `</tbody></table></div><div class="pagination" id="scorePagination"></div></div>`;
    document.getElementById('pageContent').innerHTML = html;
    renderPagination('scorePagination', data.data.total, scorePage, 10, (newPage) => {
        scorePage = newPage;
        loadScoreList();
    });
};

window.showAddScore = async () => {
    // 获取学生列表
    const stuData = await request(`/api/student/list?page=1&page_size=100`);
    const students = stuData.data.list;
    const studentOptions = students.map(s => `<option value="${s.id}">${s.name} (${s.student_no})</option>`).join('');
    const modalHtml = `
        <div class="modal" id="scoreModal"><div class="modal-content"><div class="modal-header"><span>录入成绩</span><span class="close" onclick="closeModal()">&times;</span></div>
        <form id="scoreForm"><div class="form-group"><label>学生</label><select id="student_id">${studentOptions}</select></div>
        <div class="form-group"><label>科目</label><input id="subject" required></div>
        <div class="form-group"><label>分数</label><input id="score" type="number" step="0.1" min="0" max="100" required></div>
        <div class="form-group"><label>学期</label><input id="semester" placeholder="例如 2024-2025-1" required></div>
        <button type="submit" class="btn btn-primary">提交</button></form></div></div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('scoreModal');
    modal.classList.add('show');
    document.getElementById('scoreForm').onsubmit = async (e) => {
        e.preventDefault();
        const data = {
            student_id: parseInt(document.getElementById('student_id').value),
            subject: document.getElementById('subject').value,
            score: parseFloat(document.getElementById('score').value),
            semester: document.getElementById('semester').value
        };
        try {
            await request('/api/score/add', { method: 'POST', body: JSON.stringify(data) });
            showMsg('录入成功', false);
            closeModal();
            loadScoreList();
        } catch (err) {
            showMsg(err.message);
        }
    };
};

window.editScore = async (id) => {
    const data = await request(`/api/score/list?page=1&page_size=100`);
    const score = data.data.list.find(s => s.id === id);
    const modalHtml = `
        <div class="modal" id="scoreModal"><div class="modal-content"><div class="modal-header"><span>编辑成绩</span><span class="close" onclick="closeModal()">&times;</span></div>
        <form id="scoreForm"><input type="hidden" id="scoreId" value="${id}">
        <div class="form-group"><label>科目</label><input id="subject" value="${score.subject}" required></div>
        <div class="form-group"><label>分数</label><input id="score" type="number" step="0.1" min="0" max="100" value="${score.score}" required></div>
        <div class="form-group"><label>学期</label><input id="semester" value="${score.semester}" required></div>
        <button type="submit" class="btn btn-primary">保存</button></form></div></div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('scoreModal');
    modal.classList.add('show');
    document.getElementById('scoreForm').onsubmit = async (e) => {
        e.preventDefault();
        const payload = {
            id: parseInt(document.getElementById('scoreId').value),
            subject: document.getElementById('subject').value,
            score: parseFloat(document.getElementById('score').value),
            semester: document.getElementById('semester').value
        };
        try {
            await request('/api/score/update', { method: 'PUT', body: JSON.stringify(payload) });
            showMsg('更新成功', false);
            closeModal();
            loadScoreList();
        } catch (err) {
            showMsg(err.message);
        }
    };
};

window.deleteScore = async (id) => {
    if (confirm('确定删除该成绩吗？')) {
        try {
            await request(`/api/score/delete/${id}`, { method: 'DELETE' });
            showMsg('删除成功', false);
            loadScoreList();
        } catch (err) {
            showMsg(err.message);
        }
    }
};

// ==================== 公告管理 ====================
let noticePage = 1;
const loadNoticeList = async () => {
    const data = await request(`/api/notice/list?page=${noticePage}&page_size=10`);
    const notices = data.data.list;
    let html = `
        <div class="card">
            <div class="card-header"><h3>公告管理</h3>
            ${(currentUser.role_type === 1 || currentUser.role_type === 2) ? '<button class="btn btn-primary" onclick="showAddNotice()">+ 发布公告</button>' : ''}
            </div>
            <div class="table-responsive"><table><thead><tr><th>标题</th><th>内容</th><th>置顶</th><th>发布人</th><th>发布时间</th>${(currentUser.role_type !== 3) ? '<th>操作</th>' : ''}</tr></thead><tbody>`;
    notices.forEach(n => {
        html += `<tr><td>${n.title}</td><td>${n.content.substring(0, 50)}${n.content.length > 50 ? '...' : ''}</td><td>${n.is_top ? '是' : '否'}</td><td>${n.creator_name}</td><td>${n.create_time}</td>`;
        if (currentUser.role_type !== 3) {
            html += `<td><button class="btn btn-warning btn-sm" onclick="editNotice(${n.id})">编辑</button>
            <button class="btn btn-danger btn-sm" onclick="deleteNotice(${n.id})">删除</button></td>`;
        }
        html += `</tr>`;
    });
    html += `</tbody></table></div><div class="pagination" id="noticePagination"></div></div>`;
    document.getElementById('pageContent').innerHTML = html;
    renderPagination('noticePagination', data.data.total, noticePage, 10, (newPage) => {
        noticePage = newPage;
        loadNoticeList();
    });
};

window.showAddNotice = () => {
    const modalHtml = `
        <div class="modal" id="noticeModal"><div class="modal-content"><div class="modal-header"><span>发布公告</span><span class="close" onclick="closeModal()">&times;</span></div>
        <form id="noticeForm"><div class="form-group"><label>标题</label><input id="title" required></div>
        <div class="form-group"><label>内容</label><textarea id="content" rows="4" required></textarea></div>
        <div class="form-group"><label><input type="checkbox" id="is_top"> 置顶</label></div>
        <button type="submit" class="btn btn-primary">发布</button></form></div></div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('noticeModal');
    modal.classList.add('show');
    document.getElementById('noticeForm').onsubmit = async (e) => {
        e.preventDefault();
        const data = {
            title: document.getElementById('title').value,
            content: document.getElementById('content').value,
            is_top: document.getElementById('is_top').checked ? 1 : 0
        };
        try {
            await request('/api/notice/add', { method: 'POST', body: JSON.stringify(data) });
            showMsg('发布成功', false);
            closeModal();
            loadNoticeList();
        } catch (err) {
            showMsg(err.message);
        }
    };
};

window.editNotice = async (id) => {
    const data = await request(`/api/notice/list?page=1&page_size=100`);
    const notice = data.data.list.find(n => n.id === id);
    const modalHtml = `
        <div class="modal" id="noticeModal"><div class="modal-content"><div class="modal-header"><span>编辑公告</span><span class="close" onclick="closeModal()">&times;</span></div>
        <form id="noticeForm"><input type="hidden" id="noticeId" value="${id}">
        <div class="form-group"><label>标题</label><input id="title" value="${notice.title}" required></div>
        <div class="form-group"><label>内容</label><textarea id="content" rows="4" required>${notice.content}</textarea></div>
        <div class="form-group"><label><input type="checkbox" id="is_top" ${notice.is_top ? 'checked' : ''}> 置顶</label></div>
        <button type="submit" class="btn btn-primary">保存</button></form></div></div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('noticeModal');
    modal.classList.add('show');
    document.getElementById('noticeForm').onsubmit = async (e) => {
        e.preventDefault();
        const payload = {
            id: parseInt(document.getElementById('noticeId').value),
            title: document.getElementById('title').value,
            content: document.getElementById('content').value,
            is_top: document.getElementById('is_top').checked ? 1 : 0
        };
        try {
            await request('/api/notice/update', { method: 'PUT', body: JSON.stringify(payload) });
            showMsg('更新成功', false);
            closeModal();
            loadNoticeList();
        } catch (err) {
            showMsg(err.message);
        }
    };
};

window.deleteNotice = async (id) => {
    if (confirm('确定删除该公告吗？')) {
        try {
            await request(`/api/notice/delete/${id}`, { method: 'DELETE' });
            showMsg('删除成功', false);
            loadNoticeList();
        } catch (err) {
            showMsg(err.message);
        }
    }
};

// ==================== 个人资料 ====================
const loadProfile = () => {
    const html = `
        <div class="card">
            <h3>个人资料</h3>
            <p><strong>用户名:</strong> ${currentUser.username}</p>
            <p><strong>真实姓名:</strong> ${currentUser.real_name}</p>
            <p><strong>角色:</strong> ${currentUser.role_type === 1 ? '管理员' : (currentUser.role_type === 2 ? '教师' : '学生')}</p>
            <p><strong>ID:</strong> ${currentUser.id}</p>
            <hr>
            <button class="btn btn-primary" onclick="showChangePassword()">修改密码</button>
        </div>
    `;
    document.getElementById('pageContent').innerHTML = html;
};

window.showChangePassword = () => {
    const modalHtml = `
        <div class="modal" id="pwdModal"><div class="modal-content"><div class="modal-header"><span>修改密码</span><span class="close" onclick="closeModal()">&times;</span></div>
        <form id="pwdForm"><div class="form-group"><label>新密码</label><input type="password" id="newPwd" required></div>
        <button type="submit" class="btn btn-primary">确认修改</button></form></div></div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = document.getElementById('pwdModal');
    modal.classList.add('show');
    document.getElementById('pwdForm').onsubmit = async (e) => {
        e.preventDefault();
        const newPwd = document.getElementById('newPwd').value;
        try {
            await request('/api/user/update', { method: 'PUT', body: JSON.stringify({ id: currentUser.id, password: newPwd }) });
            showMsg('密码修改成功，请重新登录', false);
            setTimeout(() => {
                localStorage.clear();
                window.location.href = '/login';
            }, 1500);
        } catch (err) {
            showMsg(err.message);
        }
    };
};

// ==================== 公共函数 ====================
const closeModal = () => {
    const modal = document.querySelector('.modal');
    if (modal) modal.remove();
};

const renderPagination = (containerId, total, currentPage, pageSize, onPageChange) => {
    const totalPages = Math.ceil(total / pageSize);
    if (totalPages <= 1) return;
    let html = '';
    for (let i = 1; i <= totalPages; i++) {
        html += `<button class="${i === currentPage ? 'active' : ''}" data-page="${i}">${i}</button>`;
    }
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = html;
        container.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', () => onPageChange(parseInt(btn.dataset.page)));
        });
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    const userInfo = localStorage.getItem('userInfo');
    if (!userInfo) {
        window.location.href = '/login';
        return;
    }
    currentUser = JSON.parse(userInfo);
    document.getElementById('userRealName').innerText = currentUser.real_name;
    const roleText = currentUser.role_type === 1 ? '管理员' : (currentUser.role_type === 2 ? '教师' : '学生');
    document.getElementById('userRole').innerText = roleText;

    // 根据角色隐藏不可见菜单
    if (currentUser.role_type === 3) {
        const userMenu = document.querySelector('[data-page="user"]');
        if (userMenu) userMenu.style.display = 'none';
    }

    // 菜单点击
    document.querySelectorAll('.nav-menu li[data-page]').forEach(li => {
        li.addEventListener('click', () => {
            const page = li.dataset.page;
            currentPage = page;
            document.querySelectorAll('.nav-menu li').forEach(l => l.classList.remove('active'));
            li.classList.add('active');
            loadPage(page);
        });
    });

    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = '/login';
    });

    loadPage('dashboard');
});