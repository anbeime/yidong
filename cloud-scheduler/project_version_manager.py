#!/usr/bin/env python3
"""
项目版本管理模块
支持项目版本控制、增量更新和变更跟踪
"""

import os
import json
import time
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import difflib

@dataclass
class ProjectVersion:
    """项目版本信息"""
    version_id: str
    version_number: str
    description: str
    created_at: str
    author: str
    changes: List[Dict]
    files_snapshot: Dict[str, str]  # 文件路径 -> 文件内容
    metadata: Dict

@dataclass 
class FileChange:
    """文件变更信息"""
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    old_content: Optional[str]
    new_content: Optional[str]
    diff: Optional[str]

class ProjectVersionManager:
    """项目版本管理器"""
    
    def __init__(self, storage_dir: str = "./project_versions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.versions = {}  # project_id -> List[ProjectVersion]
    
    def create_initial_version(self, project_id: str, project_data: Dict) -> ProjectVersion:
        """创建初始版本"""
        version = ProjectVersion(
            version_id=self._generate_version_id(),
            version_number="1.0.0",
            description="初始版本 - AI自动生成",
            created_at=datetime.now().isoformat(),
            author="CloudCoder AI",
            changes=[{
                'type': 'initial_creation',
                'description': '项目初始创建',
                'files_added': len(project_data.get('files', {}))
            }],
            files_snapshot=project_data.get('files', {}),
            metadata={
                'app_type': project_data.get('app_type', 'unknown'),
                'tech_stack': project_data.get('tech_stack', []),
                'requirement': project_data.get('requirement', ''),
                'files_count': len(project_data.get('files', {}))
            }
        )
        
        if project_id not in self.versions:
            self.versions[project_id] = []
        
        self.versions[project_id].append(version)
        self._save_version_to_disk(project_id, version)
        
        return version
    
    def create_incremental_version(self, project_id: str, changes: List[FileChange], 
                                 description: str, author: str = "CloudCoder AI") -> ProjectVersion:
        """创建增量版本"""
        if project_id not in self.versions or not self.versions[project_id]:
            raise ValueError(f"项目 {project_id} 不存在或没有基础版本")
        
        latest_version = self.versions[project_id][-1]
        new_version_number = self._increment_version(latest_version.version_number)
        
        # 应用变更到文件快照
        new_files_snapshot = latest_version.files_snapshot.copy()
        change_summary = []
        
        for change in changes:
            if change.change_type == 'added':
                new_files_snapshot[change.file_path] = change.new_content
                change_summary.append({
                    'type': 'file_added',
                    'file_path': change.file_path,
                    'description': f'新增文件: {change.file_path}'
                })
            elif change.change_type == 'modified':
                new_files_snapshot[change.file_path] = change.new_content
                change_summary.append({
                    'type': 'file_modified',
                    'file_path': change.file_path,
                    'description': f'修改文件: {change.file_path}',
                    'diff_lines': len(change.diff.split('\n')) if change.diff else 0
                })
            elif change.change_type == 'deleted':
                if change.file_path in new_files_snapshot:
                    del new_files_snapshot[change.file_path]
                change_summary.append({
                    'type': 'file_deleted',
                    'file_path': change.file_path,
                    'description': f'删除文件: {change.file_path}'
                })
        
        version = ProjectVersion(
            version_id=self._generate_version_id(),
            version_number=new_version_number,
            description=description,
            created_at=datetime.now().isoformat(),
            author=author,
            changes=change_summary,
            files_snapshot=new_files_snapshot,
            metadata={
                'parent_version': latest_version.version_id,
                'changes_count': len(changes),
                'files_count': len(new_files_snapshot)
            }
        )
        
        self.versions[project_id].append(version)
        self._save_version_to_disk(project_id, version)
        
        return version
    
    def update_project_from_requirement(self, project_id: str, new_requirement: str, 
                                      code_generator) -> ProjectVersion:
        """根据新需求更新项目"""
        if project_id not in self.versions:
            raise ValueError(f"项目 {project_id} 不存在")
        
        latest_version = self.versions[project_id][-1]
        
        # 重新生成项目
        updated_project = code_generator.generate_complete_application(
            new_requirement, 
            latest_version.metadata.get('app_type', 'default')
        )
        
        # 计算文件差异
        changes = self._calculate_file_changes(
            latest_version.files_snapshot,
            updated_project.files
        )
        
        # 创建新版本
        description = f"根据新需求更新: {new_requirement[:100]}..."
        return self.create_incremental_version(project_id, changes, description)
    
    def _calculate_file_changes(self, old_files: Dict[str, str], 
                               new_files: Dict[str, str]) -> List[FileChange]:
        """计算文件变更"""
        changes = []
        
        # 检查新增和修改的文件
        for file_path, new_content in new_files.items():
            if file_path not in old_files:
                # 新增文件
                changes.append(FileChange(
                    file_path=file_path,
                    change_type='added',
                    old_content=None,
                    new_content=new_content,
                    diff=None
                ))
            elif old_files[file_path] != new_content:
                # 修改文件
                diff = '\n'.join(difflib.unified_diff(
                    old_files[file_path].splitlines(keepends=True),
                    new_content.splitlines(keepends=True),
                    fromfile=f'{file_path} (old)',
                    tofile=f'{file_path} (new)'
                ))
                changes.append(FileChange(
                    file_path=file_path,
                    change_type='modified',
                    old_content=old_files[file_path],
                    new_content=new_content,
                    diff=diff
                ))
        
        # 检查删除的文件
        for file_path in old_files.keys():
            if file_path not in new_files:
                changes.append(FileChange(
                    file_path=file_path,
                    change_type='deleted',
                    old_content=old_files[file_path],
                    new_content=None,
                    diff=None
                ))
        
        return changes
    
    def get_project_versions(self, project_id: str) -> List[ProjectVersion]:
        """获取项目所有版本"""
        return self.versions.get(project_id, [])
    
    def get_version_by_id(self, project_id: str, version_id: str) -> Optional[ProjectVersion]:
        """根据版本ID获取特定版本"""
        versions = self.versions.get(project_id, [])
        for version in versions:
            if version.version_id == version_id:
                return version
        return None
    
    def get_latest_version(self, project_id: str) -> Optional[ProjectVersion]:
        """获取最新版本"""
        versions = self.versions.get(project_id, [])
        return versions[-1] if versions else None
    
    def revert_to_version(self, project_id: str, target_version_id: str) -> ProjectVersion:
        """回滚到指定版本"""
        target_version = self.get_version_by_id(project_id, target_version_id)
        if not target_version:
            raise ValueError(f"版本 {target_version_id} 不存在")
        
        latest_version = self.get_latest_version(project_id)
        if not latest_version:
            raise ValueError(f"项目 {project_id} 没有版本历史")
        
        # 计算回滚变更
        changes = self._calculate_file_changes(
            latest_version.files_snapshot,
            target_version.files_snapshot
        )
        
        description = f"回滚到版本 {target_version.version_number}"
        new_version_number = self._increment_version(latest_version.version_number, patch=True)
        
        version = ProjectVersion(
            version_id=self._generate_version_id(),
            version_number=new_version_number,
            description=description,
            created_at=datetime.now().isoformat(),
            author="CloudCoder AI",
            changes=[{
                'type': 'revert',
                'description': description,
                'target_version': target_version_id,
                'changes_count': len(changes)
            }],
            files_snapshot=target_version.files_snapshot.copy(),
            metadata={
                'revert_target': target_version_id,
                'files_count': len(target_version.files_snapshot)
            }
        )
        
        self.versions[project_id].append(version)
        self._save_version_to_disk(project_id, version)
        
        return version
    
    def get_version_diff(self, project_id: str, version1_id: str, version2_id: str) -> Dict:
        """获取两个版本之间的差异"""
        version1 = self.get_version_by_id(project_id, version1_id)
        version2 = self.get_version_by_id(project_id, version2_id)
        
        if not version1 or not version2:
            raise ValueError("指定的版本不存在")
        
        changes = self._calculate_file_changes(version1.files_snapshot, version2.files_snapshot)
        
        return {
            'version1': {
                'id': version1.version_id,
                'number': version1.version_number,
                'created_at': version1.created_at
            },
            'version2': {
                'id': version2.version_id,
                'number': version2.version_number,
                'created_at': version2.created_at
            },
            'changes': [{
                'file_path': change.file_path,
                'change_type': change.change_type,
                'diff': change.diff
            } for change in changes],
            'summary': {
                'added_files': len([c for c in changes if c.change_type == 'added']),
                'modified_files': len([c for c in changes if c.change_type == 'modified']),
                'deleted_files': len([c for c in changes if c.change_type == 'deleted'])
            }
        }
    
    def get_project_history(self, project_id: str) -> Dict:
        """获取项目完整历史"""
        versions = self.get_project_versions(project_id)
        
        history = {
            'project_id': project_id,
            'total_versions': len(versions),
            'latest_version': versions[-1].version_number if versions else None,
            'created_at': versions[0].created_at if versions else None,
            'last_updated': versions[-1].created_at if versions else None,
            'versions': []
        }
        
        for version in versions:
            history['versions'].append({
                'version_id': version.version_id,
                'version_number': version.version_number,
                'description': version.description,
                'created_at': version.created_at,
                'author': version.author,
                'changes_count': len(version.changes),
                'files_count': len(version.files_snapshot),
                'changes_summary': [change.get('description', '') for change in version.changes]
            })
        
        return history
    
    def _generate_version_id(self) -> str:
        """生成版本ID"""
        timestamp = str(int(time.time() * 1000))
        hash_input = f"{timestamp}_{os.urandom(16).hex()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]
    
    def _increment_version(self, current_version: str, major: bool = False, 
                          minor: bool = False, patch: bool = True) -> str:
        """递增版本号"""
        try:
            parts = current_version.split('.')
            major_num = int(parts[0])
            minor_num = int(parts[1]) if len(parts) > 1 else 0
            patch_num = int(parts[2]) if len(parts) > 2 else 0
            
            if major:
                major_num += 1
                minor_num = 0
                patch_num = 0
            elif minor:
                minor_num += 1
                patch_num = 0
            elif patch:
                patch_num += 1
            
            return f"{major_num}.{minor_num}.{patch_num}"
        except:
            # 如果解析失败，直接递增最后一位数字
            return f"{current_version}.1"
    
    def _save_version_to_disk(self, project_id: str, version: ProjectVersion):
        """保存版本到磁盘"""
        project_dir = self.storage_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        version_file = project_dir / f"{version.version_id}.json"
        version_data = asdict(version)
        
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, ensure_ascii=False, indent=2)
    
    def load_project_versions(self, project_id: str):
        """从磁盘加载项目版本"""
        project_dir = self.storage_dir / project_id
        if not project_dir.exists():
            return
        
        versions = []
        for version_file in project_dir.glob('*.json'):
            try:
                with open(version_file, 'r', encoding='utf-8') as f:
                    version_data = json.load(f)
                    version = ProjectVersion(**version_data)
                    versions.append(version)
            except Exception as e:
                print(f"加载版本文件失败 {version_file}: {e}")
        
        # 按创建时间排序
        versions.sort(key=lambda v: v.created_at)
        self.versions[project_id] = versions

# 使用示例
if __name__ == "__main__":
    # 初始化版本管理器
    version_manager = ProjectVersionManager()
    
    # 模拟项目数据
    project_data = {
        'app_type': 'ecommerce',
        'tech_stack': ['React', 'FastAPI', 'MySQL'],
        'requirement': '电商平台',
        'files': {
            'frontend/src/App.tsx': '// React App',
            'backend/main.py': '# FastAPI App',
            'README.md': '# Project README'
        }
    }
    
    # 创建初始版本
    project_id = 'demo_project'
    initial_version = version_manager.create_initial_version(project_id, project_data)
    print(f"创建初始版本: {initial_version.version_number}")
    
    # 模拟文件变更
    changes = [
        FileChange(
            file_path='frontend/src/components/Header.tsx',
            change_type='added',
            old_content=None,
            new_content='// Header Component',
            diff=None
        ),
        FileChange(
            file_path='README.md',
            change_type='modified',
            old_content='# Project README',
            new_content='# Project README\n\nUpdated documentation',
            diff='+ Updated documentation'
        )
    ]
    
    # 创建增量版本
    new_version = version_manager.create_incremental_version(
        project_id, changes, "添加Header组件并更新文档"
    )
    print(f"创建增量版本: {new_version.version_number}")
    
    # 获取项目历史
    history = version_manager.get_project_history(project_id)
    print(f"项目历史: {json.dumps(history, ensure_ascii=False, indent=2)}")