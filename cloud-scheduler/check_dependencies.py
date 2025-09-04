#!/usr/bin/env python3
"""
CloudCoder依赖检查脚本
验证所有必要的Python包是否已正确安装
"""

import sys
from importlib import import_module

def check_package(package_name, alias=None):
    """检查单个包是否可以导入"""
    try:
        if alias:
            module = import_module(package_name)
            print(f"✅ {package_name} (as {alias}) - 导入成功")
        else:
            import_module(package_name)
            print(f"✅ {package_name} - 导入成功")
        return True
    except ImportError as e:
        print(f"❌ {package_name} - 导入失败: {e}")
        return False

def main():
    """主检查函数"""
    print("🔍 CloudCoder依赖包检查")
    print("=" * 50)
    
    # 核心依赖包列表
    packages = [
        # Web框架
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        
        # AI/ML核心库
        ("torch", "PyTorch"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("sklearn", "Scikit-learn"),
        ("scipy", "SciPy"),
        
        # 数据处理和可视化
        ("matplotlib", "Matplotlib"),
        ("seaborn", "Seaborn"),
        ("joblib", "Joblib"),
        
        # 异步处理
        ("aiohttp", "AioHTTP"),
        ("aiofiles", "AioFiles"),
        
        # HTTP客户端
        ("requests", "Requests"),
        ("httpx", "HTTPX"),
        
        # 工具库
        ("dotenv", "Python-dotenv"),
        ("jinja2", "Jinja2"),
        
        # 日期时间
        ("dateutil", "Python-dateutil"),
        ("pytz", "PyTZ"),
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package, description in packages:
        if check_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 检查结果: {success_count}/{total_count} 包导入成功")
    
    if success_count == total_count:
        print("🎉 所有依赖包都已正确安装！")
        
        # 测试关键功能
        print("\n🧪 功能测试:")
        test_torch()
        test_fastapi()
        test_pandas()
        
    else:
        print("⚠️  部分依赖包缺失，请运行以下命令安装:")
        print("pip install -r requirements.txt")
    
    return success_count == total_count

def test_torch():
    """测试PyTorch功能"""
    try:
        import torch
        import torch.nn as nn
        
        # 创建简单的神经网络
        model = nn.Linear(10, 1)
        x = torch.randn(1, 10)
        y = model(x)
        
        print("✅ PyTorch神经网络测试 - 成功")
    except Exception as e:
        print(f"❌ PyTorch测试失败: {e}")

def test_fastapi():
    """测试FastAPI功能"""
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
        
        app = FastAPI()
        
        class TestModel(BaseModel):
            name: str
            value: int
        
        @app.get("/test")
        def test_endpoint():
            return {"message": "FastAPI测试成功"}
        
        print("✅ FastAPI应用创建测试 - 成功")
    except Exception as e:
        print(f"❌ FastAPI测试失败: {e}")

def test_pandas():
    """测试Pandas功能"""
    try:
        import pandas as pd
        import numpy as np
        
        # 创建测试数据
        df = pd.DataFrame({
            'A': np.random.randn(10),
            'B': np.random.randn(10)
        })
        
        # 基本操作
        result = df.describe()
        
        print("✅ Pandas数据处理测试 - 成功")
    except Exception as e:
        print(f"❌ Pandas测试失败: {e}")

if __name__ == "__main__":
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print()
    
    success = main()
    
    if success:
        print("\n🚀 CloudCoder开发环境已准备就绪！")
        sys.exit(0)
    else:
        print("\n💡 请先安装缺失的依赖包")
        sys.exit(1)