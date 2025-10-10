<!-- source venv/bin/activate -->

# 项目结构
team-knowledge-agent/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI主应用
│   │   ├── config.py            # 配置管理
│   │   └── dependencies.py      # 依赖注入
│   ├── core/
│   │   ├── rag/
│   │   │   ├── embeddings.py    # 嵌入生成
│   │   │   ├── vector_store.py  # 向量存储
│   │   │   └── retriever.py     # 检索逻辑
│   │   └── llm/
│   │       ├── base.py          # LLM基类
│   │       └── providers.py     # OpenAI/Claude/Local
│   ├── connectors/
│   │   ├── base.py              # 连接器基类
│   │   ├── confluence.py        # Confluence集成
│   │   └── slack.py            # Slack集成
│   └── tests/
├── cli/                          # CLI客户端
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md

Development Note
Week1 
