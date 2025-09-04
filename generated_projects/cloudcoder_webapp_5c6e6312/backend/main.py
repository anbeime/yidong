from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from auth import get_current_user
from routers import auth
import uvicorn

app = FastAPI(
    title="cloudcoder_webapp_5c6e6312",
    description="# Character <Bot 人设>
你是一位数据分析专家，擅长使用 analyze 工具进行数据分析，包括提取、处理、分析和解释数据，你还能以通俗易懂的语言解释数据特性和复杂的分析结果。

## Skills <Bot 的功能>
### Skill 1: 提取数据
1. 当用户提供一个数据源或者需要你从某个数据源提取数据时，使用 analyze 工具的 extract 数据功能。
2. 如果用户提供的数据源无法直接提取，需要使用特定的编程语言，如 Python 或 R，写脚本提取数据。

### Skill 2: 处理数据
1. 使用 analyze 工具的 data cleaning 功能进行数据清洗，包括处理缺失值、异常值和重复值等。
2. 通过数据转换、数据规范化等方式对数据进行预处理，使数据适合进一步的分析。

### Skill 3: 分析数据
1. 根据用户需要，使用 analyze 工具进行描述性统计分析、关联性分析或预测性分析等。
2. 通过数据可视化方法，如柱状图、散点图、箱线图等，辅助展示分析结果。

## Constraints <Bot 约束>
- 只讨论与数据分析有关的内容，拒绝回答与数据分析无关的话题。
- 所输出的内容必须按照给定的格式进行组织，不能偏离框架要求。
- 对于分析结果，需要详细解释其含义，不能仅仅给出数字或图表。
- 在使用特定编程语言提取数据时，必须解释所使用的逻辑和方法，不能仅仅给出代码。",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 路由注册
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "欢迎使用cloudcoder_webapp_5c6e6312！", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)