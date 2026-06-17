import jwt
import hashlib
import datetime
from functools import wraps
from flask import request, jsonify, g
from config import Config
from db import db

SECRET_KEY = Config.SECRET_KEY
SALT = "student2024"  # 固定盐值，生产环境建议每个用户不同

def hash_password(password):
    """对密码进行SHA256加盐哈希"""
    return hashlib.sha256((password + SALT).encode()).hexdigest()

def verify_password(input_pwd, stored_hash):
    """验证密码"""
    return hash_password(input_pwd) == stored_hash

def generate_token(user_id, username, role_type):
    """生成JWT Token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role_type': role_type,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """解析Token，返回payload或None"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def login_required(f):
    """验证Token的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'code': 401, 'msg': '缺少或无效的Token'}), 401
        token = token[7:]  # 去掉 "Bearer " 前缀
        payload = decode_token(token)
        if not payload:
            return jsonify({'code': 401, 'msg': 'Token无效或已过期'}), 401
        g.user_id = payload['user_id']
        g.username = payload['username']
        g.role_type = payload['role_type']
        return f(*args, **kwargs)
    return decorated

def roles_required(*allowed_roles):
    """角色权限控制装饰器，必须搭配 @login_required 使用"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if g.role_type not in allowed_roles:
                return jsonify({'code': 403, 'msg': '权verify_password限不足'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator