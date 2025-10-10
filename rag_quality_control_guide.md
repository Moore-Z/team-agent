# RAG 系统质量控制指南

## 问题背景

RAG (Retrieval-Augmented Generation) 系统中，检索质量直接影响 LLM 回答质量。当 RAG 查不到相关数据时，LLM 可能会生成不准确的回答。

## RAG 检索失败的常见情况

### 1. 检索失败的原因

```python
# 示例：用户问题与知识库不匹配
user_query = "如何重启服务器"
# 但知识库中只有：
knowledge_base = [
    "服务器维护流程...",      # 语义相似但不完全匹配
    "系统监控指标...",        # 完全不相关
]
# 结果：没有高质量匹配，距离分数都很高（相似度低）
```

### 2. 检测检索质量

```python
def search_with_quality_check(self, query: str, threshold: float = 0.7):
    results = self.collection.query(
        query_texts=[query],
        n_results=5
    )

    # 检查最佳匹配的相似度
    if results['distances'] and results['distances'][0]:
        best_distance = results['distances'][0][0]

        if best_distance > threshold:  # 距离太大，相似度太低
            return {
                'found_relevant': False,
                'confidence': 'low',
                'results': []
            }

    return {
        'found_relevant': True,
        'confidence': 'high',
        'results': self.format_results(results)
    }
```

## 防止 LLM 乱回答的策略

### 1. 系统提示词约束

```python
def create_rag_prompt(query: str, context: List[str]):
    if not context:
        # 没有找到相关内容时的处理
        return f"""
用户问题：{query}

重要：你的知识库中没有找到相关信息来回答这个问题。
请诚实地告诉用户你无法基于现有知识库回答这个问题，并建议他们：
1. 检查问题描述是否准确
2. 联系相关团队成员
3. 查阅其他文档资源

不要编造或猜测答案。
"""

    return f"""
基于以下知识库内容回答问题：

知识库内容：
{chr(10).join(context)}

用户问题：{query}

要求：
1. 只基于提供的知识库内容回答
2. 如果知识库内容不足以完整回答，明确说明
3. 不要添加知识库中没有的信息
"""
```

### 2. 置信度评估

```python
class RAGWithConfidence:
    def answer_query(self, query: str):
        # 1. 检索相关文档
        search_result = self.search_with_quality_check(query)

        if not search_result['found_relevant']:
            return {
                'answer': "抱歉，我在知识库中没有找到与您问题相关的信息。建议您联系团队成员或查阅其他资源。",
                'confidence': 'no_context',
                'sources': []
            }

        # 2. 生成答案
        context = [doc['content'] for doc in search_result['results']]
        prompt = self.create_rag_prompt(query, context)

        # 3. 要求LLM评估自己的置信度
        enhanced_prompt = prompt + "\n\n请在回答后评估你的置信度（高/中/低）并说明原因。"

        answer = self.llm.generate(enhanced_prompt)

        return {
            'answer': answer,
            'confidence': search_result['confidence'],
            'sources': [doc['metadata'] for doc in search_result['results']]
        }
```

### 3. 多轮验证

```python
def verify_answer_quality(self, query: str, answer: str, sources: List[str]):
    verification_prompt = f"""
原始问题：{query}
生成的答案：{answer}
使用的源文档：{sources}

请评估这个答案是否：
1. 完全基于提供的源文档
2. 准确回答了用户问题
3. 没有添加额外信息

返回：VALID（有效）或 INVALID（无效），并说明原因。
"""

    verification = self.llm.generate(verification_prompt)
    return 'VALID' in verification.upper()
```

### 4. 用户反馈机制

```python
def generate_response_with_feedback(self, query: str):
    result = self.answer_query(query)

    response = f"""
{result['answer']}

---
📊 **回答质量信息：**
- 置信度：{result['confidence']}
- 参考来源：{len(result['sources'])} 个文档
- 如果这个回答不准确，请告诉我们以改进知识库

💡 **改进建议：**
- 如果没有找到相关信息，请尝试换个方式描述问题
- 可以联系 @team-experts 获取人工帮助
"""
    return response
```

## 实际部署建议

### 1. 设置严格的相似度阈值

```python
# 在 vector_store.py 中添加
SIMILARITY_THRESHOLD = 0.7  # 根据实际测试调整
MIN_RESULTS_FOR_ANSWER = 2   # 至少需要2个相关文档
```

### 2. 监控和告警

```python
def log_low_confidence_queries(self, query: str, confidence: str):
    if confidence in ['low', 'no_context']:
        logger.warning(f"Low confidence query: {query}")
        # 发送告警，提醒团队更新知识库
```

### 3. 渐进式改进

- 收集用户反馈
- 分析失败案例
- 持续优化检索算法和提示词

## 核心原则

**宁可说"不知道"，也不要胡编乱造。**

---

*本文档保存于：/home/zhumoore/projects/team-agent/rag_quality_control_guide.md*