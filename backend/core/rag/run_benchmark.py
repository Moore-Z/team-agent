#!/usr/bin/env python3
"""
Benchmark Runner for RAG Systems
Run comprehensive benchmarks against your RAG system and baselines
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.core.rag.benchmark_system import ConfluenceBenchmark, BenchmarkReport
from backend.core.agents.qa_agent import QAAgent
from backend.core.rag.vector_store import VectorStore
import logging
import time
import json
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaselineRAGSystem:
    """
    Simple baseline RAG system using basic semantic search
    For comparison purposes
    """

    def __init__(self, vector_db_path: str = "./data/chroma_db"):
        self.vector_store = VectorStore(persist_directory=vector_db_path)
        self.vector_store.create_or_get_collection("team_knowledge")

    def ask(self, query: str) -> Dict:
        """Simple search - return top result"""
        try:
            results = self.vector_store.search(query, n_results=1)
            if results:
                answer = results[0]['content'][:500] + "..." if len(results[0]['content']) > 500 else results[0]['content']
                return {"answer": answer}
            else:
                return {"answer": "No relevant information found."}
        except Exception as e:
            return {"answer": f"Error: {str(e)}"}

def run_comprehensive_benchmark():
    """Run benchmark against both advanced and baseline systems"""

    logger.info("🚀 Starting Comprehensive RAG Benchmark")
    logger.info("=" * 60)

    # Initialize benchmark
    benchmark = ConfluenceBenchmark()

    # Initialize systems
    logger.info("Initializing RAG systems...")

    try:
        # Advanced system (your QA agent)
        advanced_system = QAAgent(
            chroma_db_path="./data/chroma_db",
            ollama_model="llama2:latest"
        )
        logger.info("✅ Advanced QA Agent initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Advanced QA Agent: {e}")
        advanced_system = None

    try:
        # Baseline system
        baseline_system = BaselineRAGSystem("./data/chroma_db")
        logger.info("✅ Baseline RAG system initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Baseline system: {e}")
        baseline_system = None

    reports = []

    # Evaluate Advanced System
    if advanced_system:
        logger.info("\n🔥 Evaluating Advanced QA Agent...")
        advanced_report = benchmark.evaluate_rag_system(advanced_system, "Advanced QA Agent")
        reports.append(("Advanced", advanced_report))

        # Save detailed results
        results_file = f"./data/benchmark_results_advanced_{int(time.time())}.json"
        benchmark.save_detailed_results(
            [result for result in benchmark.results if result],
            results_file
        )
        logger.info(f"📄 Detailed results saved to {results_file}")

    # Evaluate Baseline System
    if baseline_system:
        logger.info("\n⚖️ Evaluating Baseline System...")
        baseline_report = benchmark.evaluate_rag_system(baseline_system, "Baseline Vector Search")
        reports.append(("Baseline", baseline_report))

        # Save detailed results
        results_file = f"./data/benchmark_results_baseline_{int(time.time())}.json"
        benchmark.save_detailed_results(
            [result for result in benchmark.results if result],
            results_file
        )
        logger.info(f"📄 Detailed results saved to {results_file}")

    # Print individual reports
    for system_name, report in reports:
        logger.info(f"\n📊 {system_name} System Report")
        logger.info("-" * 50)
        benchmark.print_report(report)

    # Generate comparison report
    if len(reports) == 2:
        logger.info("\n🏆 SYSTEM COMPARISON")
        logger.info("=" * 60)
        generate_comparison_report(reports)

    logger.info("\n🎉 Benchmark completed!")
    return reports

def generate_comparison_report(reports: List[tuple]):
    """Generate side-by-side comparison report"""

    if len(reports) != 2:
        return

    advanced_name, advanced_report = reports[0]
    baseline_name, baseline_report = reports[1]

    print(f"\n{'Metric':<25} | {'Advanced':<15} | {'Baseline':<15} | {'Improvement':<15}")
    print("-" * 75)

    # Overall accuracy
    adv_acc = advanced_report.overall_accuracy
    base_acc = baseline_report.overall_accuracy
    improvement = ((adv_acc - base_acc) / base_acc * 100) if base_acc > 0 else 0
    print(f"{'Overall Accuracy':<25} | {f'{adv_acc:.1%}':<15} | {f'{base_acc:.1%}':<15} | {improvement:+.1f}%")

    # By difficulty
    for difficulty in ["EASY", "MEDIUM", "HARD"]:
        adv_diff = advanced_report.accuracy_by_difficulty.get(difficulty, 0)
        base_diff = baseline_report.accuracy_by_difficulty.get(difficulty, 0)
        improvement = ((adv_diff - base_diff) / base_diff * 100) if base_diff > 0 else 0
        print(f"{f'{difficulty} Queries':<25} | {f'{adv_diff:.1%}':<15} | {f'{base_diff:.1%}':<15} | {improvement:+.1f}%")

    # Response time
    adv_time = advanced_report.avg_response_time
    base_time = baseline_report.avg_response_time
    time_change = ((adv_time - base_time) / base_time * 100) if base_time > 0 else 0
    print(f"{'Avg Response Time':<25} | {adv_time:.2f}s{'':<9} | {base_time:.2f}s{'':<9} | {time_change:+.0f}%")

    # Critical misses
    adv_critical = len(advanced_report.critical_misses)
    base_critical = len(baseline_report.critical_misses)
    print(f"{'Critical Misses':<25} | {adv_critical:<15} | {base_critical:<15} | {base_critical - adv_critical:+}")

    print("\n💼 RESUME BULLETS FOR YOUR ACHIEVEMENT")
    print("-" * 50)

    overall_improvement = ((adv_acc - base_acc) / base_acc * 100) if base_acc > 0 else 0
    hard_adv = advanced_report.accuracy_by_difficulty.get("HARD", 0)
    hard_base = baseline_report.accuracy_by_difficulty.get("HARD", 0)
    hard_improvement = ((hard_adv - hard_base) / hard_base * 100) if hard_base > 0 else 0

    print(f"• Engineered advanced RAG system achieving {adv_acc:.1%} accuracy vs. {base_acc:.1%} baseline")
    print(f"  (+{overall_improvement:.0f}% improvement) on {advanced_report.total_cases}-query documentation benchmark")
    print(f"• Excelled at complex reasoning: {hard_adv:.1%} accuracy on hard queries vs. {hard_base:.1%} baseline")
    print(f"  (+{hard_improvement:.0f}% improvement on buried information retrieval)")

    if adv_critical == 0 and base_critical > 0:
        print(f"• Achieved 100% critical risk detection vs. {base_critical} misses in baseline system")

    print(f"• System validated on stratified difficulty benchmark with real-world documentation")

def quick_benchmark():
    """Run a quick benchmark with just a few test cases"""

    logger.info("🏃‍♂️ Running Quick Benchmark (subset of test cases)")

    benchmark = ConfluenceBenchmark()

    # Use only first 8 test cases for quick evaluation
    benchmark.test_cases = benchmark.test_cases[:8]

    try:
        qa_agent = QAAgent(chroma_db_path="./data/chroma_db", ollama_model="qwen3:4b")
        report = benchmark.evaluate_rag_system(qa_agent, "QA Agent (Quick Test)")
        benchmark.print_report(report)
    except Exception as e:
        logger.error(f"Quick benchmark failed: {e}")

def test_specific_query():
    """Test a specific query interactively"""

    logger.info("🎯 Interactive Query Testing")

    try:
        qa_agent = QAAgent(chroma_db_path="./data/chroma_db", ollama_model="qwen3:4b")

        while True:
            query = input("\nEnter your test query (or 'quit' to exit): ").strip()
            if query.lower() in ['quit', 'exit', '']:
                break

            start_time = time.time()
            result = qa_agent.ask(query)
            response_time = time.time() - start_time

            print(f"\n📝 Query: {query}")
            print(f"⏱️ Response Time: {response_time:.2f}s")
            print(f"🤖 Answer: {result.get('answer', 'No answer')}")
            print("-" * 50)

    except Exception as e:
        logger.error(f"Interactive testing failed: {e}")

def main():
    """Main CLI interface"""

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run_benchmark.py full       # Run complete benchmark with comparison")
        print("  python run_benchmark.py quick      # Run quick subset benchmark")
        print("  python run_benchmark.py interactive # Interactive query testing")
        return

    command = sys.argv[1].lower()

    if command == "full":
        run_comprehensive_benchmark()
    elif command == "quick":
        quick_benchmark()
    elif command == "interactive":
        test_specific_query()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()