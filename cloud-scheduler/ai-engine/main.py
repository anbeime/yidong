import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI调度引擎", version="1.0.0")


class ResourcePrediction(BaseModel):
    """资源预测请求模型"""
    resource_id: int
    historical_data: List[Dict]
    prediction_horizon: int = 24  # 预测时长(小时)


class ScheduleDecision(BaseModel):
    """调度决策响应模型"""
    resource_id: int
    action: str
    confidence: float
    predicted_metrics: Dict
    reasoning: str


class LSTMPredictor(nn.Module):
    """LSTM时序预测模型"""
    
    def __init__(self, input_size=4, hidden_size=64, num_layers=2, output_size=4):
        super(LSTMPredictor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        
        out, _ = self.lstm(x, (h0, c0))
        out = self.dropout(out[:, -1, :])
        out = self.fc(out)
        return out


class AIScheduler:
    """AI智能调度器"""
    
    def __init__(self):
        self.lstm_model = LSTMPredictor()
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        logger.info("AI调度器初始化完成")
    
    def prepare_features(self, data: List[Dict]) -> np.ndarray:
        """准备特征数据"""
        try:
            df = pd.DataFrame(data)
            
            # 提取核心指标
            features = [
                'cpu_usage_percent',
                'memory_usage_percent', 
                'disk_usage_percent',
                'network_in_bytes'
            ]
            
            # 检查必要字段
            for feature in features:
                if feature not in df.columns:
                    df[feature] = 0
            
            # 创建时间特征
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                df['day_of_month'] = df['timestamp'].dt.day
                
                features.extend(['hour', 'day_of_week', 'day_of_month'])
            
            # 创建移动平均特征
            for feature in ['cpu_usage_percent', 'memory_usage_percent']:
                if feature in df.columns:
                    df[f'{feature}_ma3'] = df[feature].rolling(window=3).mean()
                    df[f'{feature}_ma12'] = df[feature].rolling(window=12).mean()
                    features.extend([f'{feature}_ma3', f'{feature}_ma12'])
            
            # 填充缺失值
            df = df.fillna(method='ffill').fillna(0)
            
            return np.array(df[features].values, dtype=float)
            
        except Exception as e:
            logger.error(f"特征准备失败: {e}")
            raise
    
    def predict_resource_usage(self, data: List[Dict], horizon: int = 24) -> Dict:
        """预测资源使用情况"""
        try:
            if len(data) < 24:  # 至少需要24小时的历史数据
                raise ValueError("历史数据不足，至少需要24小时数据")
            
            # 准备特征
            features = self.prepare_features(data)
            
            # 使用LSTM进行预测
            lstm_predictions = self._lstm_predict(features, horizon)
            
            # 使用随机森林进行预测
            rf_predictions = self._rf_predict(features, horizon)
            
            # 集成预测结果
            final_predictions = self._ensemble_predictions(lstm_predictions, rf_predictions)
            
            return {
                "predictions": final_predictions,
                "confidence": self._calculate_confidence(features),
                "model_info": {
                    "lstm_used": True,
                    "rf_used": True,
                    "ensemble": True
                }
            }
            
        except Exception as e:
            logger.error(f"资源使用预测失败: {e}")
            raise
    
    def _lstm_predict(self, features: np.ndarray, horizon: int) -> List[Dict]:
        """LSTM预测"""
        try:
            # 准备序列数据
            sequence_length = 24  # 使用24小时作为序列长度
            if len(features) < sequence_length:
                # 数据不足时使用简单重复
                padded_features = np.tile(features[-1], (sequence_length - len(features), 1))
                features = np.vstack([padded_features, features])
            
            # 标准化
            features_scaled = self.scaler.fit_transform(features)
            
            # 创建序列
            X = []
            for i in range(len(features_scaled) - sequence_length + 1):
                X.append(features_scaled[i:(i + sequence_length)])
            
            if not X:
                # 如果无法创建序列，使用最后的数据
                X = [features_scaled[-sequence_length:]]
            
            X = np.array(X)
            
            # 转换为张量
            X_tensor = torch.FloatTensor(X)
            
            # 预测
            self.lstm_model.eval()
            predictions = []
            
            with torch.no_grad():
                for h in range(horizon):
                    pred = self.lstm_model(X_tensor[-1:])
                    predictions.append(pred.numpy()[0])
                    
                    # 更新输入序列（用预测值）
                    new_input = pred.unsqueeze(0)
                    X_tensor = torch.cat([X_tensor[:, 1:, :], new_input.unsqueeze(1)], dim=1)
            
            # 反标准化预测结果
            predictions = self.scaler.inverse_transform(predictions)
            
            result = []
            base_time = datetime.now()
            for i, pred in enumerate(predictions):
                result.append({
                    "timestamp": base_time + timedelta(hours=i+1),
                    "cpu_usage_percent": max(0, min(100, pred[0])),
                    "memory_usage_percent": max(0, min(100, pred[1])),
                    "disk_usage_percent": max(0, min(100, pred[2])),
                    "network_usage": max(0, pred[3])
                })
            
            return result
            
        except Exception as e:
            logger.error(f"LSTM预测失败: {e}")
            # 返回简单的趋势预测
            return self._fallback_prediction(features, horizon)
    
    def _rf_predict(self, features: np.ndarray, horizon: int) -> List[Dict]:
        """随机森林预测"""
        try:
            if len(features) < 10:
                return self._fallback_prediction(features, horizon)
            
            # 准备训练数据
            X = []
            y = []
            
            # 使用滑动窗口创建训练样本
            window_size = min(12, len(features) // 2)
            
            for i in range(window_size, len(features)):
                # 特征：前window_size小时的数据统计
                window_data = features[i-window_size:i]
                feature_vector = [
                    np.mean(window_data[:, 0]),  # CPU均值
                    np.std(window_data[:, 0]),   # CPU标准差
                    np.mean(window_data[:, 1]),  # 内存均值
                    np.std(window_data[:, 1]),   # 内存标准差
                    np.max(window_data[:, 0]),   # CPU最大值
                    np.max(window_data[:, 1]),   # 内存最大值
                ]
                
                X.append(feature_vector)
                y.append(features[i, :4])  # 目标：下一时刻的指标
            
            if len(X) < 5:
                return self._fallback_prediction(features, horizon)
            
            X = np.array(X)
            y = np.array(y)
            
            # 训练模型
            self.rf_model.fit(X, y)
            
            # 预测
            predictions = []
            current_window = features[-window_size:]
            
            for h in range(horizon):
                # 计算当前窗口特征
                feature_vector = [
                    np.mean(current_window[:, 0]),
                    np.std(current_window[:, 0]),
                    np.mean(current_window[:, 1]),
                    np.std(current_window[:, 1]),
                    np.max(current_window[:, 0]),
                    np.max(current_window[:, 1]),
                ]
                
                # 预测
                pred = self.rf_model.predict([feature_vector])[0]
                predictions.append(pred)
                
                # 更新窗口
                current_window = np.vstack([current_window[1:], pred[:4]])
            
            result = []
            base_time = datetime.now()
            for i, pred in enumerate(predictions):
                result.append({
                    "timestamp": base_time + timedelta(hours=i+1),
                    "cpu_usage_percent": max(0, min(100, pred[0])),
                    "memory_usage_percent": max(0, min(100, pred[1])),
                    "disk_usage_percent": max(0, min(100, pred[2])),
                    "network_usage": max(0, pred[3])
                })
            
            return result
            
        except Exception as e:
            logger.error(f"随机森林预测失败: {e}")
            return self._fallback_prediction(features, horizon)
    
    def _fallback_prediction(self, features: np.ndarray, horizon: int) -> List[Dict]:
        """备用预测方法"""
        if len(features) == 0:
            # 如果没有历史数据，返回默认值
            recent_metrics = {
                "cpu_usage_percent": 20.0,
                "memory_usage_percent": 30.0,
                "disk_usage_percent": 15.0,
                "network_usage": 1000.0
            }
        else:
            # 使用最近数据的平均值
            recent_data = features[-min(24, len(features)):]
            recent_metrics = {
                "cpu_usage_percent": np.mean(recent_data[:, 0]) if recent_data.shape[1] > 0 else 20.0,
                "memory_usage_percent": np.mean(recent_data[:, 1]) if recent_data.shape[1] > 1 else 30.0,
                "disk_usage_percent": np.mean(recent_data[:, 2]) if recent_data.shape[1] > 2 else 15.0,
                "network_usage": np.mean(recent_data[:, 3]) if recent_data.shape[1] > 3 else 1000.0
            }
        
        result = []
        base_time = datetime.now()
        for i in range(horizon):
            # 添加一些随机波动
            noise_factor = 0.1
            result.append({
                "timestamp": base_time + timedelta(hours=i+1),
                "cpu_usage_percent": float(max(0.0, min(100.0, float(recent_metrics["cpu_usage_percent"]) * (1 + float(np.random.normal(0, noise_factor)))))),
                "memory_usage_percent": float(max(0.0, min(100.0, float(recent_metrics["memory_usage_percent"]) * (1 + float(np.random.normal(0, noise_factor)))))),
                "disk_usage_percent": float(max(0.0, min(100.0, float(recent_metrics["disk_usage_percent"]) * (1 + float(np.random.normal(0, noise_factor)))))),
                "network_usage": float(max(0.0, float(recent_metrics["network_usage"]) * (1 + float(np.random.normal(0, noise_factor)))))
            })
        
        return result
    
    def _ensemble_predictions(self, lstm_pred: List[Dict], rf_pred: List[Dict]) -> List[Dict]:
        """集成预测结果"""
        if not lstm_pred or not rf_pred:
            return lstm_pred or rf_pred
        
        result = []
        for i in range(min(len(lstm_pred), len(rf_pred))):
            # 加权平均（LSTM权重0.6，RF权重0.4）
            result.append({
                "timestamp": lstm_pred[i]["timestamp"],
                "cpu_usage_percent": 0.6 * lstm_pred[i]["cpu_usage_percent"] + 0.4 * rf_pred[i]["cpu_usage_percent"],
                "memory_usage_percent": 0.6 * lstm_pred[i]["memory_usage_percent"] + 0.4 * rf_pred[i]["memory_usage_percent"],
                "disk_usage_percent": 0.6 * lstm_pred[i]["disk_usage_percent"] + 0.4 * rf_pred[i]["disk_usage_percent"],
                "network_usage": 0.6 * lstm_pred[i]["network_usage"] + 0.4 * rf_pred[i]["network_usage"]
            })
        
        return result
    
    def _calculate_confidence(self, features: np.ndarray) -> float:
        """计算预测置信度"""
        if len(features) < 24:
            return 0.5  # 数据不足时置信度较低
        
        # 基于数据质量和稳定性计算置信度
        recent_data = features[-24:]
        
        # 计算变异系数
        cv_cpu = np.std(recent_data[:, 0]) / (np.mean(recent_data[:, 0]) + 1e-8)
        cv_memory = np.std(recent_data[:, 1]) / (np.mean(recent_data[:, 1]) + 1e-8)
        
        # 数据越稳定，置信度越高
        stability_score = 1.0 / (1.0 + cv_cpu + cv_memory)
        
        # 数据量评分
        data_score = min(1.0, len(features) / 168.0)  # 一周的数据为满分
        
        # 综合置信度
        confidence = 0.7 * stability_score + 0.3 * data_score
        return float(max(0.1, min(0.95, float(confidence))))
    
    def make_schedule_decision(self, resource_id: int, current_metrics: Dict, predicted_metrics: List[Dict]) -> ScheduleDecision:
        """制定调度决策"""
        try:
            # 分析当前状态
            current_cpu = current_metrics.get('cpu_usage_percent', 0)
            current_memory = current_metrics.get('memory_usage_percent', 0)
            
            # 分析预测趋势
            future_cpu = [m['cpu_usage_percent'] for m in predicted_metrics[:6]]  # 未来6小时
            future_memory = [m['memory_usage_percent'] for m in predicted_metrics[:6]]
            
            avg_future_cpu = np.mean(future_cpu)
            avg_future_memory = np.mean(future_memory)
            max_future_cpu = np.max(future_cpu)
            max_future_memory = np.max(future_memory)
            
            # 决策逻辑
            action = "maintain"
            confidence = 0.8
            reasoning = "资源使用正常，维持当前配置"
            
            # 高负载预警
            if max_future_cpu > 85 or max_future_memory > 85:
                action = "scale_up"
                confidence = 0.9
                reasoning = f"预测未来6小时内CPU或内存使用率将超过85%（CPU:{max_future_cpu:.1f}%, 内存:{max_future_memory:.1f}%），建议扩容"
            
            # 长期高负载
            elif avg_future_cpu > 70 or avg_future_memory > 70:
                action = "scale_up"
                confidence = 0.7
                reasoning = f"预测未来6小时平均负载较高（CPU:{avg_future_cpu:.1f}%, 内存:{avg_future_memory:.1f}%），建议适度扩容"
            
            # 长期低负载
            elif avg_future_cpu < 20 and avg_future_memory < 30 and max_future_cpu < 40:
                action = "scale_down"
                confidence = 0.6
                reasoning = f"预测未来6小时负载较低（CPU:{avg_future_cpu:.1f}%, 内存:{avg_future_memory:.1f}%），可考虑缩容以节省成本"
            
            # 负载波动大
            cpu_std = np.std(future_cpu)
            memory_std = np.std(future_memory)
            if cpu_std > 20 or memory_std > 20:
                action = "optimize"
                confidence = 0.5
                reasoning = f"预测负载波动较大（CPU标准差:{cpu_std:.1f}, 内存标准差:{memory_std:.1f}），建议优化调度策略"
            
            return ScheduleDecision(
                resource_id=resource_id,
                action=action,
                confidence=confidence,
                predicted_metrics={
                    "avg_cpu": avg_future_cpu,
                    "avg_memory": avg_future_memory,
                    "max_cpu": max_future_cpu,
                    "max_memory": max_future_memory
                },
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"调度决策失败: {e}")
            return ScheduleDecision(
                resource_id=resource_id,
                action="maintain",
                confidence=0.1,
                predicted_metrics={},
                reasoning=f"决策分析失败: {str(e)}"
            )


# 全局AI调度器实例
ai_scheduler = AIScheduler()


@app.post("/predict", response_model=Dict)
async def predict_resource_usage(request: ResourcePrediction):
    """预测资源使用情况"""
    try:
        result = ai_scheduler.predict_resource_usage(
            data=request.historical_data,
            horizon=request.prediction_horizon
        )
        return {
            "resource_id": request.resource_id,
            "prediction_horizon": request.prediction_horizon,
            "predictions": result["predictions"],
            "confidence": result["confidence"],
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/schedule", response_model=ScheduleDecision)
async def make_schedule_decision(
    resource_id: int,
    current_metrics: Dict,
    predicted_metrics: List[Dict]
):
    """制定调度决策"""
    try:
        decision = ai_scheduler.make_schedule_decision(
            resource_id=resource_id,
            current_metrics=current_metrics,
            predicted_metrics=predicted_metrics
        )
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "AI调度引擎运行正常",
        "timestamp": datetime.now().isoformat()
    }