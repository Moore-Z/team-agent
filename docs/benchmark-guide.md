# RAG System Benchmark Guide

## 🎯 Overview

This comprehensive benchmark system evaluates your RAG system performance on real Confluence documentation with **17 stratified test cases** across three difficulty levels. It provides quantifiable metrics you can use on your resume and for system optimization.

## 📊 What Gets Measured

### Core Metrics
- **Overall Accuracy**: Percentage of correct answers across all test cases
- **Accuracy by Difficulty**: Performance on EASY/MEDIUM/HARD questions
- **Accuracy by Category**: Performance across different types of information (Configuration, Security, Risk Management, etc.)
- **Response Time**: Average time to answer queries
- **Critical Miss Rate**: Failed detection of high-importance information

### Test Case Distribution
- **EASY (5 cases)**: Simple factual lookups - any RAG should get these
- **MEDIUM (5 cases)**: Context understanding across sentences
- **HARD (7 cases)**: Buried information requiring multi-hop reasoning

### Information Categories
- Configuration & Architecture
- Error Handling & Operations
- Security & Compliance
- Risk Management & Technical Debt
- Business Analysis & Dependencies

## 🚀 Quick Start

### 1. Run Complete Benchmark
```bash
cd /home/zhumoore/projects/team-agent
python backend/core/rag/run_benchmark.py full
```

This will:
- Evaluate your advanced QA Agent
- Evaluate a baseline system for comparison
- Generate detailed reports with resume-ready metrics

### 2. Quick Test (Subset)
```bash
python backend/core/rag/run_benchmark.py quick
```

Runs first 8 test cases for faster feedback during development.

### 3. Interactive Testing
```bash
python backend/core/rag/run_benchmark.py interactive
```

Test specific queries interactively to debug issues.

## 📈 Example Results

### Sample Output
```
📊 OVERALL PERFORMANCE
Accuracy: 92.3% (12/13)
Average Response Time: 2.34s

📈 ACCURACY BY DIFFICULTY
✓ EASY  : 100.0%
✓ MEDIUM: 100.0%
✓ HARD  : 85.7%

🎯 ACCURACY BY CATEGORY
✓ Risk Management     : 100.0%
✓ Error Handling      : 100.0%
✓ Security           : 100.0%
⚠ Dependencies       : 50.0%

✅ NO CRITICAL MISSES
```

### Resume Bullets Generated
```
• Engineered advanced RAG system achieving 92% accuracy vs. 36% baseline
  (+156% improvement) on 17-query documentation benchmark

• Excelled at complex reasoning: 86% accuracy on hard queries vs. 14% baseline
  (+514% improvement on buried information retrieval)

• Achieved 100% critical risk detection vs. 4 misses in baseline system

• System validated on stratified difficulty benchmark with real-world documentation
```

## 🔍 Test Case Examples

### EASY - Simple Factual Lookup
**Query**: "What Kafka topic does the Order-Processor Service consume from?"
**Expected**: "new-orders"
**Why Easy**: Direct fact stated in overview section

### MEDIUM - Context Understanding
**Query**: "What happens when the Payment Gateway has repeated 5xx errors?"
**Expected**: "Kafka listener stops and orders are written to local H2 database file"
**Why Medium**: Requires connecting 5xx errors → PAYMENT_HALT state → fallback mechanism

### HARD - Buried Information + Multi-hop Reasoning
**Query**: "What are the data loss risks in the Order-Processor Service?"
**Expected**: "Pod restart during PAYMENT_HALT state causes permanent order loss from local H2 file"
**Why Hard**: Critical information buried mid-paragraph, requires understanding state transitions

## 📋 Benchmark Test Cases

### Configuration & Architecture (3 cases)
- Kafka topic identification (EASY)
- Service replica count (EASY)
- Technology stack details (EASY)

### Error Handling & Operations (3 cases)
- Retry mechanism details (EASY)
- Payment gateway error handling (MEDIUM)
- Monitoring issues (MEDIUM)

### Security & Compliance (2 cases)
- GDPR functionality (MEDIUM)
- Configuration security issues (HARD)

### Risk Management (4 cases)
- Data loss scenarios (HARD) 🚨 CRITICAL
- Untested code identification (HARD) 🚨 CRITICAL
- Deprecated systems in production (HARD)
- Knowledge management risks (HARD)

### Business Analysis & Dependencies (2 cases)
- Cost analysis results (HARD)
- Upgrade blockers (HARD)

## 🛠️ Customizing the Benchmark

### Adding New Test Cases

Edit `backend/core/rag/benchmark_system.py`:

```python
TestCase(
    query="Your question here",
    expected_answer="Expected response",
    ground_truth_location="Document section where answer is found",
    difficulty="EASY|MEDIUM|HARD",
    importance="LOW|MEDIUM|HIGH|CRITICAL",
    category="Your Category",
    requires_reasoning="Why this requires reasoning" # Optional
),
```

### Modifying Evaluation Logic

The `evaluate_answer()` method uses keyword matching. For production use, consider:
- LLM-as-judge evaluation
- Semantic similarity scoring
- Human evaluation for ground truth

### Testing Different RAG Systems

The benchmark works with any system that has:
- `.ask(query)` method returning `{"answer": "..."}`, OR
- `.query(query)` method returning answer string

## 📊 Understanding Your Results

### What Good Scores Look Like
- **EASY**: Should be 100% - these are basic facts
- **MEDIUM**: 80%+ indicates good context understanding
- **HARD**: 70%+ indicates excellent buried information retrieval

### Red Flags
- **Critical Misses**: Any missed CRITICAL importance items
- **Poor HARD Performance**: <50% suggests issues with complex reasoning
- **Slow Response**: >5s average may indicate inefficient retrieval

### Improvement Strategies by Performance Pattern

**High EASY, Low MEDIUM/HARD**: Improve context understanding
- Better chunking strategies
- Query expansion
- Reranking mechanisms

**Good Overall but Critical Misses**: Focus on information coverage
- Ensure complete document indexing
- Test with comprehensive queries
- Add query reformulation

**Fast but Inaccurate**: Improve relevance scoring
- Better embedding models
- Metadata enrichment
- Hybrid search approaches

## 🎯 Using Results for Resume/Portfolio

### Strong Results (>85% overall)
```
"Engineered hierarchical RAG system achieving 89% accuracy on complex
documentation queries vs. 34% baseline, with particular excellence at
identifying buried critical risks (92% vs. 8% on hard cases)"
```

### Moderate Results (60-85% overall)
```
"Developed RAG system with 73% accuracy on technical documentation
benchmark, demonstrating 2x improvement over baseline semantic search
on complex reasoning tasks"
```

### Focus on Specific Strengths
```
"Achieved 100% accuracy on critical system risk detection through
advanced document preprocessing and semantic reranking, validated
on 17-query benchmark with real enterprise documentation"
```

## 🔧 Technical Implementation

### Files Structure
```
backend/core/rag/
├── benchmark_system.py     # Core benchmark framework
├── run_benchmark.py        # CLI runner and comparisons
└── json_to_vector.py      # Data preparation

docs/
└── benchmark-guide.md     # This guide
```

### Dependencies
- Your existing QA Agent system
- ChromaDB vector store with your data
- Python 3.8+ with dataclasses support

### Data Requirements
The benchmark uses the actual Confluence data from:
`/home/zhumoore/projects/team-agent/data/jason/Software_dev_confluence_data.json`

This data must be loaded into your vector database using the `json_to_vector.py` script.

## 📝 Next Steps

1. **Run Initial Benchmark**: `python backend/core/rag/run_benchmark.py full`
2. **Identify Weak Areas**: Review category and difficulty breakdowns
3. **Iterate and Improve**: Modify your RAG system based on findings
4. **Re-benchmark**: Track improvements quantitatively
5. **Document Results**: Use metrics for resume and technical discussions

## 🤝 Contributing

To add more test cases:
1. Analyze your documentation for good examples
2. Create cases with clear expected answers
3. Ensure stratified difficulty distribution
4. Test with both systems to validate difficulty levels

Remember: The goal is defensible, reproducible metrics that demonstrate your RAG system's real-world performance on complex enterprise documentation.