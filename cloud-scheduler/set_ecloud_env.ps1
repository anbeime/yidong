# 设置移动云环境变量的PowerShell脚本

Write-Host "🔧 设置移动云环境变量..." -ForegroundColor Blue

# 设置移动云认证信息
$env:ECLOUD_ACCESS_KEY = "ed7bbd03fad34980834cae597a02cbfc"
$env:ECLOUD_SECRET_KEY = "9ae0582e1e9e4f40ab5c68b744829c61"
$env:ECLOUD_REGION = "cn-north-1"

Write-Host "✅ 移动云环境变量设置完成" -ForegroundColor Green
Write-Host "🔑 认证信息:" -ForegroundColor Yellow
Write-Host "   ECLOUD_ACCESS_KEY: $env:ECLOUD_ACCESS_KEY" -ForegroundColor Yellow
Write-Host "   ECLOUD_SECRET_KEY: $($env:ECLOUD_SECRET_KEY.Substring(0,6))...$($env:ECLOUD_SECRET_KEY.Substring($env:ECLOUD_SECRET_KEY.Length-4))" -ForegroundColor Yellow
Write-Host "   ECLOUD_REGION: $env:ECLOUD_REGION" -ForegroundColor Yellow

# 验证.env文件是否存在
if (Test-Path ".env") {
    Write-Host "✅ .env 配置文件已存在" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env 配置文件不存在，将使用环境变量" -ForegroundColor Yellow
}

Write-Host "🚀 现在可以启动服务了:" -ForegroundColor Blue
Write-Host "   运行 './quick-start.sh start' 启动服务" -ForegroundColor Cyan