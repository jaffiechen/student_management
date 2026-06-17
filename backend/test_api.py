import pytest
import requests
import json

BASE_URL = "http://localhost:5000"
admin_token = None
test_user_id = None
test_class_id = None
test_student_id = None
test_score_id = None
test_notice_id = None

# ==================== 登录测试 ====================
def test_login_success():
    global admin_token
    resp = requests.post(f"{BASE_URL}/api/login", json={
        "username": "admin",
        "password": "123456"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert "token" in data["data"]
    admin_token = data["data"]["token"]

def test_login_wrong_password():
    resp = requests.post(f"{BASE_URL}/api/login", json={
        "username": "admin",
        "password": "wrong"
    })
    assert resp.status_code == 401
    data = resp.json()
    assert data["code"] == 401

def test_login_missing_fields():
    resp = requests.post(f"{BASE_URL}/api/login", json={
        "username": "admin"
    })
    assert resp.status_code == 400
    data = resp.json()
    assert data["code"] == 400

# ==================== 用户管理测试 ====================
def test_user_list():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.get(f"{BASE_URL}/api/user/list?page=1&page_size=10", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    assert "list" in data["data"]

def test_user_add():
    global test_user_id
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.post(f"{BASE_URL}/api/user/add", headers=headers, json={
        "username": "testteacher",
        "password": "123456",
        "real_name": "测试教师",
        "role_type": 2,
        "phone": "13800138000",
        "status": 1
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    test_user_id = data["data"]["id"]

def test_user_update():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.put(f"{BASE_URL}/api/user/update", headers=headers, json={
        "id": test_user_id,
        "real_name": "更新教师名"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200

def test_user_delete():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.delete(f"{BASE_URL}/api/user/delete/{test_user_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200

# ==================== 班级管理测试 ====================
def test_class_list():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.get(f"{BASE_URL}/api/class/list", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200

def test_class_add():
    global test_class_id
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.post(f"{BASE_URL}/api/class/add", headers=headers, json={
        "class_name": "测试班级",
        "class_code": "TEST001",
        "teacher_id": 1
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    test_class_id = data["data"]["id"]

def test_class_update():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.put(f"{BASE_URL}/api/class/update", headers=headers, json={
        "id": test_class_id,
        "class_name": "更新测试班级"
    })
    assert resp.status_code == 200

def test_class_delete():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.delete(f"{BASE_URL}/api/class/delete/{test_class_id}", headers=headers)
    assert resp.status_code == 200

# ==================== 学生管理测试 ====================
def test_student_add():
    global test_student_id
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.post(f"{BASE_URL}/api/student/add", headers=headers, json={
        "student_no": "20249999",
        "name": "测试学生",
        "gender": 1,
        "age": 20,
        "phone": "13912345678",
        "class_id": 1,
        "username": "teststudent"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    test_student_id = data["data"]["student_id"]

def test_student_list():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.get(f"{BASE_URL}/api/student/list?page=1&page_size=10", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200

def test_student_update():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.put(f"{BASE_URL}/api/student/update", headers=headers, json={
        "id": test_student_id,
        "name": "更新测试学生"
    })
    assert resp.status_code == 200

def test_student_delete():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.delete(f"{BASE_URL}/api/student/delete/{test_student_id}", headers=headers)
    assert resp.status_code == 200

# ==================== 成绩管理测试 ====================
def test_score_add():
    global test_score_id
    headers = {"Authorization": f"Bearer {admin_token}"}
    # 需要先确保有学生存在（使用已存在的学生ID 1）
    resp = requests.post(f"{BASE_URL}/api/score/add", headers=headers, json={
        "student_id": 1,
        "subject": "测试科目",
        "score": 90,
        "semester": "2024-2025-1"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    test_score_id = data["data"]["id"]

def test_score_list():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.get(f"{BASE_URL}/api/score/list?page=1&page_size=10", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200

def test_score_update():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.put(f"{BASE_URL}/api/score/update", headers=headers, json={
        "id": test_score_id,
        "score": 95
    })
    assert resp.status_code == 200

def test_score_delete():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.delete(f"{BASE_URL}/api/score/delete/{test_score_id}", headers=headers)
    assert resp.status_code == 200

# ==================== 公告管理测试 ====================
def test_notice_add():
    global test_notice_id
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.post(f"{BASE_URL}/api/notice/add", headers=headers, json={
        "title": "测试公告",
        "content": "这是测试内容",
        "is_top": 1
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200
    test_notice_id = data["data"]["id"]

def test_notice_list():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.get(f"{BASE_URL}/api/notice/list?page=1&page_size=10", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 200

def test_notice_update():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.put(f"{BASE_URL}/api/notice/update", headers=headers, json={
        "id": test_notice_id,
        "title": "更新测试公告"
    })
    assert resp.status_code == 200

def test_notice_delete():
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.delete(f"{BASE_URL}/api/notice/delete/{test_notice_id}", headers=headers)
    assert resp.status_code == 200

# ==================== 权限测试 ====================
def test_unauthorized_access():
    # 没有 token 访问受保护接口
    resp = requests.get(f"{BASE_URL}/api/user/list")
    assert resp.status_code == 401

def test_student_only_self():
    # 需要先获取学生 token
    login_resp = requests.post(f"{BASE_URL}/api/login", json={
        "username": "20240001",
        "password": "123456"
    })
    assert login_resp.status_code == 200
    student_token = login_resp.json()["data"]["token"]
    headers = {"Authorization": f"Bearer {student_token}"}
    resp = requests.get(f"{BASE_URL}/api/student/list", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    # 学生只能看到自己（应该只有一条记录）
    assert len(data["data"]["list"]) <= 1