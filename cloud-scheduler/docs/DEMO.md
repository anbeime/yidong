# 🚀 云智调度 - AI算网资源编排平台演示指南

## 项目概述

本项目是参加移动云开发者大赛的作品，实现了基于AI的智能算网资源统一编排平台。平台能够自动预测资源需求，优化资源分配，降低云计算成本，是移动云算网融合战略的典型应用。

## 🎯 核心功能演示

### 1. 智能资源预测
- **功能**: 基于历史数据使用LSTM和随机森林算法预测未来24小时资源使用情况
- **演示路径**: 总览大屏 → AI智能建议 → 查看详情
- **亮点**: 
  - 集成多种机器学习算法
  - 实时调整预测模型
  - 置信度评估机制

### 2. 自动调度决策
- **功能**: AI分析预测结果，自动生成扩缩容、迁移、优化等调度建议
- **演示路径**: 资源管理 → 选择资源 → 智能扩缩容
- **亮点**:
  - 多维度决策分析
  - 成本效益评估
  - 风险控制机制

### 3. 实时监控大屏
- **功能**: 可视化展示资源使用情况、成本分析、AI调度效果
- **演示路径**: 总览大屏
- **亮点**:
  - 响应式数据大屏
  - 多维度统计分析
  - 实时告警提醒

### 4. 移动云深度集成
- **功能**: 对接移动云ECS、VPC、容器服务等全栈资源
- **演示路径**: 资源管理 → 同步云资源
- **亮点**:
  - 统一资源视图
  - 跨服务协调
  - 原生API集成

## 🎬 演示流程

### 快速启动
```bash
# 1. 克隆项目
git clone <repository-url>
cd cloud-scheduler

# 2. 快速启动（自动安装依赖和初始化数据）
chmod +x quick-start.sh
./quick-start.sh start

# 3. 访问系统
# 前端: http://localhost:3000
# 用户名: admin, 密码: admin123
```

### 演示脚本

#### 第一步：系统概览 (2分钟)
1. **登录系统**: 使用 admin/admin123 登录
2. **总览大屏**: 展示整体资源状况
   - 总资源数: 5个
   - 运行中: 4个
   - 告警资源: 1个（Redis内存使用率95%）
   - 月度成本: ¥992.50
3. **AI建议**: 展示智能优化建议
   - Redis内存优化建议
   - AI计算节点缩容建议
   - 存储类型调整建议

#### 第二步：AI预测演示 (3分钟)
1. **进入监控分析页面**
2. **选择Redis缓存资源**
3. **展示预测结果**:
   - 未来24小时内存使用率趋势
   - AI预测置信度: 87%
   - 建议操作: 增加内存配置
4. **解释算法逻辑**:
   - LSTM时序预测
   - 随机森林回归
   - 集成学习策略

#### 第三步：智能调度 (3分钟)
1. **进入资源管理页面**
2. **选择AI计算节点**
3. **触发智能扩缩容**:
   - AI分析当前负载: CPU 88%, 内存 67%
   - 预测未来6小时负载趋势
   - 生成调度建议: 临时缩容节省成本
4. **展示决策过程**:
   - 多维度分析
   - 成本效益计算
   - 风险评估

#### 第四步：成本优化 (2分钟)
1. **回到总览大屏**
2. **展示成本优化效果**:
   - 本月节省: ¥234.56 (15.2%)
   - AI调度次数: 89次
   - 成功率: 96.6%
3. **实时成本监控**:
   - 按资源类型分析
   - 优化建议统计
   - 趋势对比分析

## 🏆 技术亮点展示

### 1. AI算法创新
```python
# 展示核心预测算法
class LSTMPredictor(nn.Module):
    def __init__(self, input_size=4, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])
```

### 2. 移动云集成
```python
# 展示云API集成
class ECloudAPIClient:
    async def scale_container_service(self, cluster_id, service_name, desired_count):
        data = {
            'Action': 'UpdateService',
            'ClusterId': cluster_id,
            'ServiceName': service_name,
            'DesiredCount': desired_count
        }
        return await self._make_request('PUT', '/api/v1/container/services/scale', data=data)
```

### 3. 实时数据流
```typescript
// 展示前端实时更新
useEffect(() => {
    const fetchData = async () => {
        const response = await api.getResourceMetrics(resourceId);
        setMetrics(response.data);
    };
    
    fetchData();
    const interval = setInterval(fetchData, 30000); // 30秒更新
    return () => clearInterval(interval);
}, [resourceId]);
```

## 📊 评审维度对应

| 评审维度 | 演示重点 | 预期得分 |
|---------|---------|---------|
| 创新价值(15分) | AI+算网融合，LSTM+RF集成预测 | 14分 |
| 商业价值(15分) | 成本节省15.2%，ROI分析 | 13分 |
| 行业前景(10分) | 算网融合趋势，企业数字化需求 | 9分 |
| 移动云应用(15分) | 深度集成ECS、VPC、容器服务 | 14分 |
| 功能完整性(20分) | 端到端完整功能，可运行Demo | 18分 |
| 产品交互性(15分) | 直观大屏，流畅操作体验 | 13分 |
| 算网得分(10分) | 核心算网调度能力 | 10分 |

**预期总分: 91分**

## 🎥 演示视频制作要点

### 时长分配 (总计10分钟)
1. **项目介绍** (1分钟): 背景、目标、架构
2. **功能演示** (6分钟): 核心功能逐一展示
3. **技术亮点** (2分钟): AI算法、云集成
4. **总结展望** (1分钟): 成果、价值、未来

### 录制技巧
- 使用高分辨率屏幕录制
- 准备演示数据和场景
- 配音解说清晰流畅
- 突出AI智能化特色
- 强调移动云集成深度

## 💡 演示准备清单

### 环境准备
- [ ] Docker环境就绪
- [ ] 网络连接稳定
- [ ] 浏览器配置优化
- [ ] 演示数据初始化

### 材料准备
- [ ] PPT演示文稿
- [ ] 技术架构图
- [ ] 成本优化报告
- [ ] 算法流程图

### 话术准备
- [ ] 项目背景介绍
- [ ] 技术亮点说明
- [ ] 功能操作解说
- [ ] 价值总结陈述

## 🔧 故障排除

### 常见问题
1. **服务启动失败**: 检查Docker内存配置，建议8GB以上
2. **AI引擎超时**: 首次启动需要加载模型，等待时间较长
3. **前端加载慢**: 清除浏览器缓存，使用Chrome浏览器
4. **数据库连接失败**: 确保MySQL容器正常启动

### 快速修复
```bash
# 重启服务
./quick-start.sh restart

# 查看日志
./quick-start.sh logs

# 清理重建
./quick-start.sh cleanup
./quick-start.sh start
```

## 📞 联系方式

- **项目负责人**: [你的姓名]
- **邮箱**: [你的邮箱]
- **电话**: [你的电话]
- **技术支持**: 移动云开发者大赛QQ群 958628675

---

**祝演示成功！为移动云算网融合贡献智慧力量！** 🎉