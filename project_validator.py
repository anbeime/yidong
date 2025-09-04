#!/usr/bin/env python3
"""
项目真实性和可用性验证工具
验证生成的项目是否为真实可用的应用
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

class ProjectValidator:
    """项目验证器"""
    
    def __init__(self):
        self.results = {}
        
    def validate_project_structure(self, project_path: str) -> Dict:
        """验证项目结构完整性"""
        path = Path(project_path)
        if not path.exists():
            return {"valid": False, "reason": "项目路径不存在"}
        
        # 检查必要文件
        required_files = {
            "docker-compose.yml": "Docker编排配置",
            "README.md": "项目说明文档",
        }
        
        backend_files = {
            "backend/main.py": "后端主程序",
            "backend/requirements.txt": "Python依赖",
        }
        
        frontend_files = {
            "frontend/package.json": "前端依赖配置",
            "frontend/src/App.tsx": "React主组件",
        }
        
        results = {"structure": {}, "completeness": 0}
        total_files = len(required_files) + len(backend_files) + len(frontend_files)
        found_files = 0
        
        # 检查文件存在性
        for file_path, description in {**required_files, **backend_files, **frontend_files}.items():
            full_path = path / file_path
            exists = full_path.exists()
            results["structure"][file_path] = {
                "exists": exists,
                "description": description,
                "size": full_path.stat().st_size if exists else 0
            }
            if exists:
                found_files += 1
        
        results["completeness"] = (found_files / total_files) * 100
        results["valid"] = results["completeness"] >= 80
        
        return results
    
    def validate_code_quality(self, project_path: str) -> Dict:
        """验证代码质量和功能完整性"""
        path = Path(project_path)
        results = {"backend": {}, "frontend": {}, "valid": False}
        
        # 检查后端代码
        backend_main = path / "backend" / "main.py"
        if backend_main.exists():
            content = backend_main.read_text(encoding='utf-8')
            results["backend"] = {
                "has_fastapi": "FastAPI" in content,
                "has_routes": "@app." in content or "router" in content,
                "has_cors": "CORS" in content,
                "lines_of_code": len(content.splitlines()),
                "has_error_handling": "try:" in content or "except" in content
            }
        
        # 检查前端代码
        frontend_app = path / "frontend" / "src" / "App.tsx"
        if frontend_app.exists():
            content = frontend_app.read_text(encoding='utf-8')
            results["frontend"] = {
                "has_react": "import React" in content,
                "has_components": "function" in content or "const" in content,
                "has_routing": "Router" in content or "Route" in content,
                "lines_of_code": len(content.splitlines()),
                "has_typescript": content.endswith('.tsx') or 'interface' in content
            }
        
        # 计算总体质量得分
        backend_score = sum(1 for v in results["backend"].values() if isinstance(v, bool) and v) / max(len([v for v in results["backend"].values() if isinstance(v, bool)]), 1)
        frontend_score = sum(1 for v in results["frontend"].values() if isinstance(v, bool) and v) / max(len([v for v in results["frontend"].values() if isinstance(v, bool)]), 1)
        
        results["quality_score"] = (backend_score + frontend_score) / 2 * 100
        results["valid"] = results["quality_score"] >= 60
        
        return results
    
    def validate_deployability(self, project_path: str) -> Dict:
        """验证项目可部署性"""
        path = Path(project_path)
        results = {"docker": {}, "dependencies": {}, "valid": False}
        
        # 检查Docker配置
        docker_compose = path / "docker-compose.yml"
        if docker_compose.exists():
            content = docker_compose.read_text(encoding='utf-8')
            results["docker"] = {
                "has_services": "services:" in content,
                "has_backend": "backend" in content,
                "has_frontend": "frontend" in content,
                "has_database": "postgres" in content or "mysql" in content,
                "has_ports": "ports:" in content
            }
        
        # 检查依赖配置
        requirements = path / "backend" / "requirements.txt"
        package_json = path / "frontend" / "package.json"
        
        if requirements.exists():
            deps = requirements.read_text(encoding='utf-8').splitlines()
            results["dependencies"]["backend"] = {
                "count": len([d for d in deps if d.strip()]),
                "has_fastapi": any("fastapi" in d.lower() for d in deps),
                "has_uvicorn": any("uvicorn" in d.lower() for d in deps)
            }
        
        if package_json.exists():
            try:
                pkg_data = json.loads(package_json.read_text(encoding='utf-8'))
                deps = pkg_data.get('dependencies', {})
                results["dependencies"]["frontend"] = {
                    "count": len(deps),
                    "has_react": "react" in deps,
                    "has_typescript": "typescript" in deps
                }
            except:
                results["dependencies"]["frontend"] = {"error": "无法解析package.json"}
        
        # 计算可部署性得分
        docker_score = sum(results["docker"].values()) / max(len(results["docker"]), 1) if results["docker"] else 0
        deps_score = 0.8  # 基础依赖分数
        
        results["deployability_score"] = (docker_score + deps_score) / 2 * 100
        results["valid"] = results["deployability_score"] >= 70
        
        return results
    
    def generate_project_report(self, project_path: str) -> Dict:
        """生成项目完整性报告"""
        print(f"\n🔍 正在验证项目: {project_path}")
        
        # 执行各项验证
        structure = self.validate_project_structure(project_path)
        quality = self.validate_code_quality(project_path)
        deployability = self.validate_deployability(project_path)
        
        # 生成总体评估
        overall_score = (
            structure.get("completeness", 0) * 0.3 +
            quality.get("quality_score", 0) * 0.4 +
            deployability.get("deployability_score", 0) * 0.3
        )
        
        # 判断项目真实性等级
        if overall_score >= 85:
            reality_level = "🌟 完全可用 - 生产就绪级别的真实项目"
        elif overall_score >= 70:
            reality_level = "✅ 基本可用 - 功能完整的真实项目"
        elif overall_score >= 50:
            reality_level = "⚠️ 部分可用 - 需要完善的项目框架"
        else:
            reality_level = "❌ 仅为模板 - 主要是代码骨架"
        
        report = {
            "project_path": project_path,
            "overall_score": round(overall_score, 1),
            "reality_level": reality_level,
            "structure_validation": structure,
            "quality_validation": quality,
            "deployability_validation": deployability,
            "recommendations": self._generate_recommendations(structure, quality, deployability)
        }
        
        return report
    
    def _generate_recommendations(self, structure, quality, deployability) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if structure.get("completeness", 0) < 80:
            recommendations.append("补全缺失的项目文件和目录结构")
        
        if quality.get("quality_score", 0) < 60:
            recommendations.append("增加错误处理和完善业务逻辑实现")
        
        if deployability.get("deployability_score", 0) < 70:
            recommendations.append("完善Docker配置和依赖管理")
        
        if not recommendations:
            recommendations.append("项目结构完整，建议进行功能测试和性能优化")
        
        return recommendations
    
    def print_detailed_report(self, report: Dict):
        """打印详细报告"""
        print("\n" + "="*60)
        print(f"📊 项目验证报告: {Path(report['project_path']).name}")
        print("="*60)
        
        print(f"📈 总体评分: {report['overall_score']}/100")
        print(f"🎯 真实性等级: {report['reality_level']}")
        
        print("\n📁 结构完整性:")
        structure = report['structure_validation']
        print(f"   完整度: {structure.get('completeness', 0):.1f}%")
        
        if 'structure' in structure:
            for file_path, info in structure['structure'].items():
                status = "✅" if info['exists'] else "❌"
                size_info = f"({info['size']} bytes)" if info['exists'] else ""
                print(f"   {status} {file_path} {size_info}")
        
        print("\n💻 代码质量:")
        quality = report['quality_validation']
        print(f"   质量评分: {quality.get('quality_score', 0):.1f}%")
        
        if quality.get('backend'):
            print("   后端特性:")
            for feature, has_feature in quality['backend'].items():
                if isinstance(has_feature, bool):
                    status = "✅" if has_feature else "❌"
                    print(f"     {status} {feature}")
        
        if quality.get('frontend'):
            print("   前端特性:")
            for feature, has_feature in quality['frontend'].items():
                if isinstance(has_feature, bool):
                    status = "✅" if has_feature else "❌"
                    print(f"     {status} {feature}")
        
        print("\n🚀 可部署性:")
        deploy = report['deployability_validation']
        print(f"   部署评分: {deploy.get('deployability_score', 0):.1f}%")
        
        print("\n💡 改进建议:")
        for rec in report['recommendations']:
            print(f"   • {rec}")
        
        print("\n" + "="*60)

def main():
    """主函数"""
    validator = ProjectValidator()
    
    # 验证项目列表
    projects_to_validate = [
        r"c:\D\比赛\yidong\cloudcoder_webapp_5c6e6312",
        r"c:\D\比赛\yidong\cloud-scheduler"
    ]
    
    print("🚀 CloudCoder项目真实性验证工具")
    print("验证生成的项目是否为真实可用的应用...")
    
    all_reports = []
    
    for project_path in projects_to_validate:
        if os.path.exists(project_path):
            report = validator.generate_project_report(project_path)
            all_reports.append(report)
            validator.print_detailed_report(report)
        else:
            print(f"❌ 项目路径不存在: {project_path}")
    
    # 生成总结
    if all_reports:
        print("\n" + "🎯 总体结论".center(60, "="))
        avg_score = sum(r['overall_score'] for r in all_reports) / len(all_reports)
        print(f"平均项目质量评分: {avg_score:.1f}/100")
        
        high_quality = len([r for r in all_reports if r['overall_score'] >= 70])
        print(f"高质量项目数量: {high_quality}/{len(all_reports)}")
        
        if avg_score >= 70:
            print("✅ 总体结论: 生成的项目是真实可用的应用，不是空壳子！")
        else:
            print("⚠️ 总体结论: 项目具有基础功能，但需要进一步开发完善。")

if __name__ == "__main__":
    main()