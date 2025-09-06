@echo off
echo 🔧 设置移动云环境变量...

REM 设置移动云认证信息
set ECLOUD_ACCESS_KEY=ed7bbd03fad34980834cae597a02cbfc
set ECLOUD_SECRET_KEY=9ae0582e1e9e4f40ab5c68b744829c61
set ECLOUD_REGION=cn-north-1

echo ✅ 移动云环境变量设置完成
echo 🔑 认证信息:
echo    ECLOUD_ACCESS_KEY: %ECLOUD_ACCESS_KEY%
echo    ECLOUD_SECRET_KEY: %ECLOUD_SECRET_KEY:~0,6%...%ECLOUD_SECRET_KEY:~-4%
echo    ECLOUD_REGION: %ECLOUD_REGION%

REM 验证.env文件是否存在
if exist ".env" (
    echo ✅ .env 配置文件已存在
) else (
    echo ⚠️  .env 配置文件不存在，将使用环境变量
)

echo 🚀 现在可以启动服务了:
echo    运行 quick-start.sh start 启动服务

REM 保持命令行窗口打开
cmd /k