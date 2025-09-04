#!/usr/bin/env python3
"""
用户认证和项目持久化存储模块
支持用户注册、登录、项目数据持久化等功能
"""

import os
import json
import time
import hashlib
import sqlite3
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import jwt
from pathlib import Path

@dataclass
class User:
    """用户信息"""
    user_id: str
    username: str
    email: str
    password_hash: str
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True
    profile: Optional[Dict] = None

@dataclass
class UserSession:
    """用户会话"""
    session_id: str
    user_id: str
    created_at: str
    expires_at: str
    ip_address: str = ""
    user_agent: str = ""

@dataclass
class ProjectRecord:
    """项目记录"""
    project_id: str
    user_id: str
    name: str
    app_type: str
    requirement: str
    status: str
    created_at: str
    updated_at: str
    metadata: Dict

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "./cloudcoder.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    profile TEXT DEFAULT '{}'
                )
            ''')
            
            # 会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    ip_address TEXT DEFAULT '',
                    user_agent TEXT DEFAULT '',
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # 项目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    app_type TEXT NOT NULL,
                    requirement TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # 项目文件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_content TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (project_id),
                    UNIQUE(project_id, file_path)
                )
            ''')
            
            # 用户活动日志表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    activity_data TEXT DEFAULT '{}',
                    ip_address TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """执行查询"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """执行更新操作"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

class UserAuthManager:
    """用户认证管理器"""
    
    def __init__(self, db_manager: DatabaseManager, secret_key: str = "cloudcoder_secret_key"):
        self.db = db_manager
        self.secret_key = secret_key
        self.session_expire_hours = 24 * 7  # 7天
    
    def register_user(self, username: str, email: str, password: str) -> Dict:
        """用户注册"""
        try:
            # 检查用户名和邮箱是否已存在
            existing_users = self.db.execute_query(
                "SELECT user_id FROM users WHERE username = ? OR email = ?",
                (username, email)
            )
            
            if existing_users:
                return {
                    'success': False,
                    'error': '用户名或邮箱已存在'
                }
            
            # 创建新用户
            user_id = str(uuid.uuid4())
            password_hash = self._hash_password(password)
            created_at = datetime.now().isoformat()
            
            self.db.execute_update(
                '''INSERT INTO users (user_id, username, email, password_hash, created_at)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, username, email, password_hash, created_at)
            )
            
            # 记录活动日志
            self._log_user_activity(user_id, 'user_registered', {
                'username': username,
                'email': email
            })
            
            return {
                'success': True,
                'user_id': user_id,
                'message': '注册成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'注册失败: {str(e)}'
            }
    
    def login_user(self, username: str, password: str, ip_address: str = "", user_agent: str = "") -> Dict:
        """用户登录"""
        try:
            # 查找用户
            users = self.db.execute_query(
                "SELECT * FROM users WHERE username = ? OR email = ?",
                (username, username)
            )
            
            if not users:
                return {
                    'success': False,
                    'error': '用户不存在'
                }
            
            user = users[0]
            
            # 验证密码
            if not self._verify_password(password, user['password_hash']):
                return {
                    'success': False,
                    'error': '密码错误'
                }
            
            # 检查用户状态
            if not user['is_active']:
                return {
                    'success': False,
                    'error': '账户已被禁用'
                }
            
            # 创建会话
            session = self._create_session(user['user_id'], ip_address, user_agent)
            
            # 更新最后登录时间
            self.db.execute_update(
                "UPDATE users SET last_login = ? WHERE user_id = ?",
                (datetime.now().isoformat(), user['user_id'])
            )
            
            # 记录活动日志
            self._log_user_activity(user['user_id'], 'user_logged_in', {
                'ip_address': ip_address,
                'user_agent': user_agent
            }, ip_address)
            
            return {
                'success': True,
                'user': {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'email': user['email']
                },
                'session': {
                    'session_id': session.session_id,
                    'expires_at': session.expires_at
                },
                'token': self._generate_jwt_token(user['user_id'], session.session_id)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'登录失败: {str(e)}'
            }
    
    def verify_session(self, session_id: str) -> Optional[Dict]:
        """验证会话"""
        try:
            sessions = self.db.execute_query(
                '''SELECT s.*, u.username, u.email, u.is_active
                   FROM user_sessions s
                   JOIN users u ON s.user_id = u.user_id
                   WHERE s.session_id = ?''',
                (session_id,)
            )
            
            if not sessions:
                return None
            
            session = sessions[0]
            
            # 检查会话是否过期
            expires_at = datetime.fromisoformat(session['expires_at'])
            if datetime.now() > expires_at:
                # 删除过期会话
                self.db.execute_update(
                    "DELETE FROM user_sessions WHERE session_id = ?",
                    (session_id,)
                )
                return None
            
            # 检查用户状态
            if not session['is_active']:
                return None
            
            return {
                'user_id': session['user_id'],
                'username': session['username'],
                'email': session['email'],
                'session_id': session['session_id']
            }
            
        except Exception as e:
            print(f"会话验证失败: {e}")
            return None
    
    def logout_user(self, session_id: str) -> bool:
        """用户登出"""
        try:
            # 获取会话信息用于日志
            sessions = self.db.execute_query(
                "SELECT user_id FROM user_sessions WHERE session_id = ?",
                (session_id,)
            )
            
            # 删除会话
            deleted = self.db.execute_update(
                "DELETE FROM user_sessions WHERE session_id = ?",
                (session_id,)
            )
            
            # 记录活动日志
            if sessions:
                self._log_user_activity(sessions[0]['user_id'], 'user_logged_out', {
                    'session_id': session_id
                })
            
            return deleted > 0
            
        except Exception as e:
            print(f"登出失败: {e}")
            return False
    
    def _create_session(self, user_id: str, ip_address: str, user_agent: str) -> UserSession:
        """创建用户会话"""
        session_id = str(uuid.uuid4())
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=self.session_expire_hours)
        
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            created_at=created_at.isoformat(),
            expires_at=expires_at.isoformat(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 保存到数据库
        self.db.execute_update(
            '''INSERT INTO user_sessions (session_id, user_id, created_at, expires_at, ip_address, user_agent)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (session.session_id, session.user_id, session.created_at, session.expires_at, 
             session.ip_address, session.user_agent)
        )
        
        return session
    
    def _generate_jwt_token(self, user_id: str, session_id: str) -> str:
        """生成JWT令牌"""
        payload = {
            'user_id': user_id,
            'session_id': session_id,
            'exp': datetime.now() + timedelta(hours=self.session_expire_hours),
            'iat': datetime.now()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """验证JWT令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return self.verify_session(payload['session_id'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        salt = os.urandom(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + ':' + pwdhash.hex()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        try:
            salt_hex, pwdhash_hex = password_hash.split(':')
            salt = bytes.fromhex(salt_hex)
            pwdhash = bytes.fromhex(pwdhash_hex)
            
            new_pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return pwdhash == new_pwdhash
        except:
            return False
    
    def _log_user_activity(self, user_id: str, activity_type: str, activity_data: Dict, ip_address: str = ""):
        """记录用户活动日志"""
        try:
            self.db.execute_update(
                '''INSERT INTO user_activity_logs (user_id, activity_type, activity_data, ip_address, created_at)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, activity_type, json.dumps(activity_data), ip_address, datetime.now().isoformat())
            )
        except Exception as e:
            print(f"记录活动日志失败: {e}")

class ProjectStorageManager:
    """项目存储管理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def save_project(self, user_id: str, project_data: Dict) -> Dict:
        """保存项目"""
        try:
            project_id = project_data.get('project_id', str(uuid.uuid4()))
            created_at = datetime.now().isoformat()
            
            # 保存项目基本信息
            self.db.execute_update(
                '''INSERT OR REPLACE INTO projects 
                   (project_id, user_id, name, app_type, requirement, status, created_at, updated_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    project_id,
                    user_id,
                    project_data.get('name', 'Untitled Project'),
                    project_data.get('app_type', 'unknown'),
                    project_data.get('requirement', ''),
                    'active',
                    created_at,
                    created_at,
                    json.dumps(project_data.get('metadata', {}))
                )
            )
            
            # 保存项目文件
            if 'files' in project_data:
                for file_path, file_content in project_data['files'].items():
                    file_hash = hashlib.md5(file_content.encode('utf-8')).hexdigest()
                    
                    self.db.execute_update(
                        '''INSERT OR REPLACE INTO project_files 
                           (project_id, file_path, file_content, file_hash, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (project_id, file_path, file_content, file_hash, created_at, created_at)
                    )
            
            return {
                'success': True,
                'project_id': project_id,
                'message': '项目保存成功'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'项目保存失败: {str(e)}'
            }
    
    def get_user_projects(self, user_id: str) -> List[Dict]:
        """获取用户的所有项目"""
        try:
            projects = self.db.execute_query(
                '''SELECT project_id, name, app_type, requirement, status, created_at, updated_at,
                          (SELECT COUNT(*) FROM project_files WHERE project_id = p.project_id) as files_count
                   FROM projects p
                   WHERE user_id = ? AND status != 'deleted'
                   ORDER BY updated_at DESC''',
                (user_id,)
            )
            
            return projects
            
        except Exception as e:
            print(f"获取用户项目失败: {e}")
            return []
    
    def get_project_detail(self, project_id: str, user_id: str) -> Optional[Dict]:
        """获取项目详情"""
        try:
            # 获取项目基本信息
            projects = self.db.execute_query(
                "SELECT * FROM projects WHERE project_id = ? AND user_id = ?",
                (project_id, user_id)
            )
            
            if not projects:
                return None
            
            project = projects[0]
            
            # 获取项目文件
            files = self.db.execute_query(
                "SELECT file_path, file_content FROM project_files WHERE project_id = ?",
                (project_id,)
            )
            
            project['files'] = {file['file_path']: file['file_content'] for file in files}
            project['metadata'] = json.loads(project.get('metadata', '{}'))
            
            return project
            
        except Exception as e:
            print(f"获取项目详情失败: {e}")
            return None
    
    def delete_project(self, project_id: str, user_id: str) -> bool:
        """删除项目（软删除）"""
        try:
            deleted = self.db.execute_update(
                "UPDATE projects SET status = 'deleted', updated_at = ? WHERE project_id = ? AND user_id = ?",
                (datetime.now().isoformat(), project_id, user_id)
            )
            
            return deleted > 0
            
        except Exception as e:
            print(f"删除项目失败: {e}")
            return False
    
    def update_project(self, project_id: str, user_id: str, updates: Dict) -> bool:
        """更新项目"""
        try:
            # 构建更新语句
            update_fields = []
            params = []
            
            for field in ['name', 'app_type', 'requirement']:
                if field in updates:
                    update_fields.append(f"{field} = ?")
                    params.append(updates[field])
            
            if 'metadata' in updates:
                update_fields.append("metadata = ?")
                params.append(json.dumps(updates['metadata']))
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.extend([project_id, user_id])
            
            updated = self.db.execute_update(
                f"UPDATE projects SET {', '.join(update_fields)} WHERE project_id = ? AND user_id = ?",
                tuple(params)
            )
            
            # 更新文件（如果提供）
            if 'files' in updates:
                # 删除旧文件
                self.db.execute_update(
                    "DELETE FROM project_files WHERE project_id = ?",
                    (project_id,)
                )
                
                # 添加新文件
                created_at = datetime.now().isoformat()
                for file_path, file_content in updates['files'].items():
                    file_hash = hashlib.md5(file_content.encode('utf-8')).hexdigest()
                    
                    self.db.execute_update(
                        '''INSERT INTO project_files 
                           (project_id, file_path, file_content, file_hash, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (project_id, file_path, file_content, file_hash, created_at, created_at)
                    )
            
            return updated > 0
            
        except Exception as e:
            print(f"更新项目失败: {e}")
            return False

# 使用示例
if __name__ == "__main__":
    # 初始化数据库和管理器
    db_manager = DatabaseManager()
    auth_manager = UserAuthManager(db_manager)
    storage_manager = ProjectStorageManager(db_manager)
    
    # 测试用户注册
    register_result = auth_manager.register_user("testuser", "test@example.com", "password123")
    print("注册结果:", register_result)
    
    # 测试用户登录
    if register_result['success']:
        login_result = auth_manager.login_user("testuser", "password123")
        print("登录结果:", login_result)
        
        if login_result['success']:
            user_id = login_result['user']['user_id']
            session_id = login_result['session']['session_id']
            
            # 测试项目保存
            project_data = {
                'name': '测试项目',
                'app_type': 'ecommerce',
                'requirement': '电商网站',
                'files': {
                    'main.py': 'print("Hello World")',
                    'README.md': '# 测试项目'
                },
                'metadata': {'version': '1.0.0'}
            }
            
            save_result = storage_manager.save_project(user_id, project_data)
            print("项目保存结果:", save_result)
            
            # 测试获取用户项目
            projects = storage_manager.get_user_projects(user_id)
            print("用户项目:", projects)