from flask import Flask, request, jsonify, render_template, g
from flask_cors import CORS
from config import Config
from db import db
from auth import verify_password, generate_token, login_required, roles_required, hash_password

app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')
app.config.from_object(Config)
CORS(app, supports_credentials=True)

db.connect()

# ==================== 健康检查 ====================
@app.route('/health')
def health():
    return {'status': 'ok'}

# ==================== 页面路由 ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

# ==================== 认证接口 ====================
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'}), 400

    sql = "SELECT id, username, password, real_name, role_type, status FROM sys_user WHERE username=%s"
    user = db.execute_one(sql, (username,))
    if not user or not verify_password(password, user['password']):
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401
    if user['status'] != 1:
        return jsonify({'code': 403, 'msg': '账号已被禁用'}), 403

    token = generate_token(user['id'], user['username'], user['role_type'])
    return jsonify({
        'code': 200,
        'msg': '登录成功',
        'data': {
            'token': token,
            'user_info': {
                'id': user['id'],
                'username': user['username'],
                'real_name': user['real_name'],
                'role_type': user['role_type']
            }
        }
    })

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    return jsonify({'code': 200, 'msg': '已登出'})

# ==================== 用户管理 ====================
@app.route('/api/user/list', methods=['GET'])
@login_required
@roles_required(1)
def user_list():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    role = request.args.get('role', type=int)
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '')

    conditions = []
    params = []
    if role:
        conditions.append("role_type = %s")
        params.append(role)
    if status is not None:
        conditions.append("status = %s")
        params.append(status)
    if keyword:
        conditions.append("(username LIKE %s OR real_name LIKE %s)")
        params.extend([f'%{keyword}%', f'%{keyword}%'])

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    count_sql = f"SELECT COUNT(*) as total FROM sys_user{where_clause}"
    total = db.execute_one(count_sql, params)['total']

    offset = (page - 1) * page_size
    sql = f"""SELECT id, username, real_name, role_type, phone, status, create_time 
              FROM sys_user{where_clause} ORDER BY id DESC LIMIT %s OFFSET %s"""
    params.extend([page_size, offset])
    users = db.execute_query(sql, params)

    return jsonify({
        'code': 200,
        'data': {
            'list': users,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })

@app.route('/api/user/add', methods=['POST'])
@login_required
@roles_required(1)
def user_add():
    data = request.json
    required = ['username', 'password', 'real_name', 'role_type']
    for field in required:
        if not data.get(field):
            return jsonify({'code': 400, 'msg': f'{field}不能为空'}), 400

    exist = db.execute_one("SELECT id FROM sys_user WHERE username=%s", (data['username'],))
    if exist:
        return jsonify({'code': 400, 'msg': '用户名已存在'}), 400

    pwd_hash = hash_password(data['password'])
    sql = """INSERT INTO sys_user (username, password, real_name, role_type, phone, status)
             VALUES (%s, %s, %s, %s, %s, %s)"""
    new_id = db.execute_insert(sql, (
        data['username'], pwd_hash, data['real_name'], data['role_type'],
        data.get('phone', ''), data.get('status', 1)
    ))
    return jsonify({'code': 200, 'msg': '添加成功', 'data': {'id': new_id}})

@app.route('/api/user/update', methods=['PUT'])
@login_required
def user_update():
    data = request.json
    user_id = data.get('id')
    if not user_id:
        return jsonify({'code': 400, 'msg': '用户ID不能为空'}), 400

    if g.role_type != 1 and g.user_id != user_id:
        return jsonify({'code': 403, 'msg': '无权修改他人信息'}), 403

    fields = []
    params = []
    if 'real_name' in data:
        fields.append("real_name=%s")
        params.append(data['real_name'])
    if 'phone' in data:
        fields.append("phone=%s")
        params.append(data['phone'])
    if 'status' in data and g.role_type == 1:
        fields.append("status=%s")
        params.append(data['status'])
    if 'password' in data and data['password']:
        fields.append("password=%s")
        params.append(hash_password(data['password']))

    if not fields:
        return jsonify({'code': 400, 'msg': '没有要更新的字段'}), 400

    params.append(user_id)
    sql = f"UPDATE sys_user SET {', '.join(fields)} WHERE id=%s"
    db.execute_update(sql, params)
    return jsonify({'code': 200, 'msg': '更新成功'})

@app.route('/api/user/delete/<int:user_id>', methods=['DELETE'])
@login_required
@roles_required(1)
def user_delete(user_id):
    if user_id == g.user_id:
        return jsonify({'code': 400, 'msg': '不能删除当前登录用户'}), 400
    db.execute_update("DELETE FROM sys_user WHERE id=%s", (user_id,))
    return jsonify({'code': 200, 'msg': '删除成功'})

# ==================== 班级管理 ====================
@app.route('/api/class/list', methods=['GET'])
@login_required
def class_list():
    sql = """SELECT c.id, c.class_name, c.class_code, c.teacher_id, c.create_time,
                    u.real_name as teacher_name
             FROM class_info c
             LEFT JOIN sys_user u ON c.teacher_id = u.id
             ORDER BY c.id DESC"""
    classes = db.execute_query(sql)
    return jsonify({'code': 200, 'data': classes})

@app.route('/api/class/add', methods=['POST'])
@login_required
@roles_required(1)
def class_add():
    data = request.json
    if not data.get('class_name') or not data.get('class_code'):
        return jsonify({'code': 400, 'msg': '班级名称和编号不能为空'}), 400
    exist = db.execute_one("SELECT id FROM class_info WHERE class_code=%s", (data['class_code'],))
    if exist:
        return jsonify({'code': 400, 'msg': '班级编号已存在'}), 400

    sql = "INSERT INTO class_info (class_name, class_code, teacher_id) VALUES (%s, %s, %s)"
    new_id = db.execute_insert(sql, (data['class_name'], data['class_code'], data.get('teacher_id')))
    return jsonify({'code': 200, 'msg': '添加成功', 'data': {'id': new_id}})

@app.route('/api/class/update', methods=['PUT'])
@login_required
@roles_required(1)
def class_update():
    data = request.json
    class_id = data.get('id')
    if not class_id:
        return jsonify({'code': 400, 'msg': '班级ID不能为空'}), 400
    fields = []
    params = []
    if 'class_name' in data:
        fields.append("class_name=%s")
        params.append(data['class_name'])
    if 'teacher_id' in data:
        fields.append("teacher_id=%s")
        params.append(data['teacher_id'])
    if not fields:
        return jsonify({'code': 400, 'msg': '没有要更新的字段'}), 400
    params.append(class_id)
    sql = f"UPDATE class_info SET {', '.join(fields)} WHERE id=%s"
    db.execute_update(sql, params)
    return jsonify({'code': 200, 'msg': '更新成功'})

@app.route('/api/class/delete/<int:class_id>', methods=['DELETE'])
@login_required
@roles_required(1)
def class_delete(class_id):
    db.execute_update("DELETE FROM class_info WHERE id=%s", (class_id,))
    return jsonify({'code': 200, 'msg': '删除成功'})

# ==================== 学生管理 ====================
@app.route('/api/student/list', methods=['GET'])
@login_required
def student_list():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    class_id = request.args.get('class_id', type=int)
    keyword = request.args.get('keyword', '')

    conditions = []
    params = []
    if g.role_type == 3:
        stu = db.execute_one("SELECT id FROM student_info WHERE user_id=%s", (g.user_id,))
        if stu:
            conditions.append("s.id = %s")
            params.append(stu['id'])
        else:
            return jsonify({'code': 200, 'data': {'list': [], 'total': 0, 'page': page, 'page_size': page_size}})
    if class_id:
        conditions.append("s.class_id = %s")
        params.append(class_id)
    if keyword:
        conditions.append("(s.name LIKE %s OR s.student_no LIKE %s)")
        params.extend([f'%{keyword}%', f'%{keyword}%'])

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    count_sql = f"SELECT COUNT(*) as total FROM student_info s{where_clause}"
    total = db.execute_one(count_sql, params)['total']

    offset = (page - 1) * page_size
    sql = f"""SELECT s.id, s.student_no, s.name, s.gender, s.age, s.phone, s.class_id,
                     c.class_name, u.username, u.real_name as user_real_name
              FROM student_info s
              LEFT JOIN class_info c ON s.class_id = c.id
              LEFT JOIN sys_user u ON s.user_id = u.id
              {where_clause}
              ORDER BY s.id DESC
              LIMIT %s OFFSET %s"""
    params.extend([page_size, offset])
    students = db.execute_query(sql, params)
    return jsonify({'code': 200, 'data': {'list': students, 'total': total, 'page': page, 'page_size': page_size}})

@app.route('/api/student/add', methods=['POST'])
@login_required
@roles_required(1, 2)
def student_add():
    data = request.json
    if not data.get('student_no') or not data.get('name'):
        return jsonify({'code': 400, 'msg': '学号和姓名不能为空'}), 400
    exist = db.execute_one("SELECT id FROM student_info WHERE student_no=%s", (data['student_no'],))
    if exist:
        return jsonify({'code': 400, 'msg': '学号已存在'}), 400

    default_pwd = '123456'
    pwd_hash = hash_password(default_pwd)
    username = data.get('username') or data['student_no']
    exist_user = db.execute_one("SELECT id FROM sys_user WHERE username=%s", (username,))
    if exist_user:
        return jsonify({'code': 400, 'msg': '用户名已存在'}), 400

    sql_user = """INSERT INTO sys_user (username, password, real_name, role_type, phone, status)
                  VALUES (%s, %s, %s, 3, %s, 1)"""
    user_id = db.execute_insert(sql_user, (username, pwd_hash, data['name'], data.get('phone', '')))

    sql_student = """INSERT INTO student_info (student_no, name, gender, age, phone, class_id, user_id)
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    student_id = db.execute_insert(sql_student, (
        data['student_no'], data['name'], data.get('gender'), data.get('age'),
        data.get('phone'), data.get('class_id'), user_id
    ))
    return jsonify({'code': 200, 'msg': '添加成功', 'data': {'student_id': student_id, 'user_id': user_id}})

@app.route('/api/student/update', methods=['PUT'])
@login_required
def student_update():
    data = request.json
    student_id = data.get('id')
    if not student_id:
        return jsonify({'code': 400, 'msg': '学生ID不能为空'}), 400
    if g.role_type == 3:
        return jsonify({'code': 403, 'msg': '无权限修改学生档案'}), 403

    fields = []
    params = []
    updatable = ['name', 'gender', 'age', 'phone', 'class_id']
    for field in updatable:
        if field in data:
            fields.append(f"{field}=%s")
            params.append(data[field])
    if fields:
        params.append(student_id)
        sql = f"UPDATE student_info SET {', '.join(fields)} WHERE id=%s"
        db.execute_update(sql, params)

    if 'name' in data or 'phone' in data:
        stu = db.execute_one("SELECT user_id FROM student_info WHERE id=%s", (student_id,))
        if stu and stu['user_id']:
            user_fields = []
            user_params = []
            if 'name' in data:
                user_fields.append("real_name=%s")
                user_params.append(data['name'])
            if 'phone' in data:
                user_fields.append("phone=%s")
                user_params.append(data['phone'])
            if user_fields:
                user_params.append(stu['user_id'])
                db.execute_update(f"UPDATE sys_user SET {', '.join(user_fields)} WHERE id=%s", user_params)

    return jsonify({'code': 200, 'msg': '更新成功'})

@app.route('/api/student/delete/<int:student_id>', methods=['DELETE'])
@login_required
@roles_required(1, 2)
def student_delete(student_id):
    db.execute_update("DELETE FROM student_info WHERE id=%s", (student_id,))
    return jsonify({'code': 200, 'msg': '删除成功'})

# ==================== 成绩管理 ====================
@app.route('/api/score/list', methods=['GET'])
@login_required
def score_list():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    student_id = request.args.get('student_id', type=int)
    subject = request.args.get('subject', '')
    semester = request.args.get('semester', '')

    conditions = []
    params = []

    if g.role_type == 3:
        stu = db.execute_one("SELECT id FROM student_info WHERE user_id=%s", (g.user_id,))
        if not stu:
            return jsonify({'code': 200, 'data': {'list': [], 'total': 0}})
        conditions.append("s.student_id = %s")
        params.append(stu['id'])
    else:
        if student_id:
            conditions.append("s.student_id = %s")
            params.append(student_id)

    if subject:
        conditions.append("s.subject LIKE %s")
        params.append(f'%{subject}%')
    if semester:
        conditions.append("s.semester = %s")
        params.append(semester)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    count_sql = f"SELECT COUNT(*) as total FROM student_score s{where_clause}"
    total = db.execute_one(count_sql, params)['total']

    offset = (page - 1) * page_size
    sql = f"""SELECT s.id, s.student_id, s.subject, s.score, s.semester, s.create_time,
                     stu.name as student_name, stu.student_no
              FROM student_score s
              LEFT JOIN student_info stu ON s.student_id = stu.id
              {where_clause}
              ORDER BY s.id DESC
              LIMIT %s OFFSET %s"""
    params.extend([page_size, offset])
    scores = db.execute_query(sql, params)

    return jsonify({
        'code': 200,
        'data': {
            'list': scores,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })

@app.route('/api/score/add', methods=['POST'])
@login_required
@roles_required(1, 2)
def score_add():
    data = request.json
    required = ['student_id', 'subject', 'score', 'semester']
    for field in required:
        if field not in data:
            return jsonify({'code': 400, 'msg': f'{field}不能为空'}), 400

    score = data['score']
    if not isinstance(score, (int, float)) or score < 0 or score > 100:
        return jsonify({'code': 400, 'msg': '分数必须在0-100之间'}), 400

    exist = db.execute_one(
        "SELECT id FROM student_score WHERE student_id=%s AND subject=%s AND semester=%s",
        (data['student_id'], data['subject'], data['semester'])
    )
    if exist:
        return jsonify({'code': 400, 'msg': '该学生此科目本学期成绩已存在，请勿重复录入'}), 400

    sql = """INSERT INTO student_score (student_id, subject, score, semester)
             VALUES (%s, %s, %s, %s)"""
    new_id = db.execute_insert(sql, (
        data['student_id'], data['subject'], data['score'], data['semester']
    ))
    return jsonify({'code': 200, 'msg': '录入成功', 'data': {'id': new_id}})

@app.route('/api/score/update', methods=['PUT'])
@login_required
@roles_required(1, 2)
def score_update():
    data = request.json
    score_id = data.get('id')
    if not score_id:
        return jsonify({'code': 400, 'msg': '成绩ID不能为空'}), 400

    updates = []
    params = []
    if 'score' in data:
        score_val = data['score']
        if not isinstance(score_val, (int, float)) or score_val < 0 or score_val > 100:
            return jsonify({'code': 400, 'msg': '分数必须在0-100之间'}), 400
        updates.append("score=%s")
        params.append(score_val)
    if 'subject' in data:
        updates.append("subject=%s")
        params.append(data['subject'])
    if 'semester' in data:
        updates.append("semester=%s")
        params.append(data['semester'])

    if not updates:
        return jsonify({'code': 400, 'msg': '没有要更新的字段'}), 400

    params.append(score_id)
    sql = f"UPDATE student_score SET {', '.join(updates)} WHERE id=%s"
    db.execute_update(sql, params)
    return jsonify({'code': 200, 'msg': '更新成功'})

@app.route('/api/score/delete/<int:score_id>', methods=['DELETE'])
@login_required
@roles_required(1, 2)
def score_delete(score_id):
    db.execute_update("DELETE FROM student_score WHERE id=%s", (score_id,))
    return jsonify({'code': 200, 'msg': '删除成功'})

# ==================== 公告管理 ====================
@app.route('/api/notice/list', methods=['GET'])
@login_required
def notice_list():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', '')

    conditions = []
    params = []
    if keyword:
        conditions.append("(title LIKE %s OR content LIKE %s)")
        params.extend([f'%{keyword}%', f'%{keyword}%'])

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    count_sql = f"SELECT COUNT(*) as total FROM sys_notice{where_clause}"
    total = db.execute_one(count_sql, params)['total']

    offset = (page - 1) * page_size
    sql = f"""SELECT n.id, n.title, n.content, n.is_top, n.creator_id, n.create_time,
                     u.real_name as creator_name
              FROM sys_notice n
              LEFT JOIN sys_user u ON n.creator_id = u.id
              {where_clause}
              ORDER BY n.is_top DESC, n.create_time DESC
              LIMIT %s OFFSET %s"""
    params.extend([page_size, offset])
    notices = db.execute_query(sql, params)

    return jsonify({
        'code': 200,
        'data': {
            'list': notices,
            'total': total,
            'page': page,
            'page_size': page_size
        }
    })

@app.route('/api/notice/add', methods=['POST'])
@login_required
@roles_required(1, 2)
def notice_add():
    data = request.json
    if not data.get('title') or not data.get('content'):
        return jsonify({'code': 400, 'msg': '标题和内容不能为空'}), 400

    sql = """INSERT INTO sys_notice (title, content, is_top, creator_id)
             VALUES (%s, %s, %s, %s)"""
    new_id = db.execute_insert(sql, (
        data['title'], data['content'], data.get('is_top', 0), g.user_id
    ))
    return jsonify({'code': 200, 'msg': '发布成功', 'data': {'id': new_id}})

@app.route('/api/notice/update', methods=['PUT'])
@login_required
@roles_required(1, 2)
def notice_update():
    data = request.json
    notice_id = data.get('id')
    if not notice_id:
        return jsonify({'code': 400, 'msg': '公告ID不能为空'}), 400

    fields = []
    params = []
    if 'title' in data:
        fields.append("title=%s")
        params.append(data['title'])
    if 'content' in data:
        fields.append("content=%s")
        params.append(data['content'])
    if 'is_top' in data:
        fields.append("is_top=%s")
        params.append(data['is_top'])

    if not fields:
        return jsonify({'code': 400, 'msg': '没有要更新的字段'}), 400

    params.append(notice_id)
    sql = f"UPDATE sys_notice SET {', '.join(fields)} WHERE id=%s"
    db.execute_update(sql, params)
    return jsonify({'code': 200, 'msg': '更新成功'})

@app.route('/api/notice/delete/<int:notice_id>', methods=['DELETE'])
@login_required
@roles_required(1, 2)
def notice_delete(notice_id):
    db.execute_update("DELETE FROM sys_notice WHERE id=%s", (notice_id,))
    return jsonify({'code': 200, 'msg': '删除成功'})

# ==================== 错误处理 ====================
@app.errorhandler(404)
def not_found(error):
    """404 页面处理"""
    return jsonify({'code': 404, 'msg': '请求的资源不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    """500 服务器内部错误处理"""
    return jsonify({'code': 500, 'msg': '服务器内部错误，请稍后再试'}), 500

# ==================== 启动应用 ====================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)