
#!/usr/bin/env python3
"""
RAG Benchmark System for Confluence Documentation
Creates comprehensive test cases and evaluation metrics for RAG system performance
"""

import json
import time
import logging
import statistics
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """Single test case with expected answer and metadata"""
    query: str
    expected_answer: str
    ground_truth_location: str
    difficulty: str  # EASY, MEDIUM, HARD
    importance: str  # LOW, MEDIUM, HIGH, CRITICAL
    requires_reasoning: Optional[str] = None
    why_hard: Optional[str] = None
    category: Optional[str] = None

@dataclass
class EvaluationResult:
    """Result of evaluating a single test case"""
    query: str
    expected_answer: str
    actual_answer: str
    is_correct: bool
    confidence_score: float
    response_time: float
    difficulty: str
    category: str
    evaluation_notes: Optional[str] = None

@dataclass
class BenchmarkReport:
    """Complete benchmark evaluation report"""
    total_cases: int
    correct_answers: int
    overall_accuracy: float
    accuracy_by_difficulty: Dict[str, float]
    accuracy_by_category: Dict[str, float]
    avg_response_time: float
    response_time_by_difficulty: Dict[str, float]
    critical_misses: List[str]
    evaluation_timestamp: str
    system_name: str

class ConfluenceBenchmark:
    """
    Benchmark system for evaluating RAG performance on Confluence documentation
    """

    def __init__(self):
        self.test_cases = self._create_test_cases()
        self.results: List[EvaluationResult] = []

    def _create_test_cases(self) -> List[TestCase]:
        """Create stratified test cases based on actual Confluence content"""

        test_cases = [
            # ============= EASY CASES - Simple factual lookup =============
            TestCase(
                query="What Kafka topic does the Order-Processor Service consume from?",
                expected_answer="new-orders",
                ground_truth_location="Order-Processor Service - Overview section",
                difficulty="EASY",
                importance="MEDIUM",
                category="Configuration"
            ),
            TestCase(
                query="How many replicas does the Order-Processor Service have in production?",
                expected_answer="3 replicas",
                ground_truth_location="Order-Processor Service - Overview section",
                difficulty="EASY",
                importance="MEDIUM",
                category="Architecture"
            ),
            TestCase(
                query="What programming language is the User-Profile Service written in?",
                expected_answer="Java 17",
                ground_truth_location="User-Profile Service - Tech Stack section",
                difficulty="EASY",
                importance="LOW",
                category="Technology"
            ),
            TestCase(
                query="What framework does the Notification-Dispatcher Service use?",
                expected_answer="Spring Boot 2.7.x",
                ground_truth_location="Notification-Dispatcher Service - Overview section",
                difficulty="EASY",
                importance="LOW",
                category="Technology"
            ),
            TestCase(
                query="How many retry attempts does Order-Processor have for standard errors?",
                expected_answer="3 retry attempts with 3-second backoff",
                ground_truth_location="Order-Processor Service - Error Handling section",
                difficulty="EASY",
                importance="MEDIUM",
                category="Error Handling"
            ),

            # ============= MEDIUM CASES - Requires context understanding =============
            TestCase(
                query="What happens when the Payment Gateway has repeated 5xx errors?",
                expected_answer="Kafka listener stops and orders are written to local H2 database file",
                ground_truth_location="Order-Processor Service - Error Handling section, paragraph 2",
                difficulty="MEDIUM",
                importance="HIGH",
                category="Error Handling",
                requires_reasoning="Must connect '5xx errors' with 'PAYMENT_HALT state' and understand the fallback mechanism"
            ),
            TestCase(
                query="Why was the Email Template Throttling project abandoned?",
                expected_answer="In-memory ConcurrentHashMap approach doesn't work in multi-replica deployment",
                ground_truth_location="Notification-Dispatcher Service - Project Backlog section",
                difficulty="MEDIUM",
                importance="MEDIUM",
                category="Architecture",
                requires_reasoning="Must understand the connection between implementation approach and deployment constraints"
            ),
            TestCase(
                query="What triggers the GDPR forget-me functionality?",
                expected_answer="DELETE /api/v2/users/{userId}/forget endpoint, currently in development",
                ground_truth_location="User-Profile Service - Current Development section",
                difficulty="MEDIUM",
                importance="HIGH",
                category="Compliance",
                requires_reasoning="Must understand GDPR context and current development status"
            ),
            TestCase(
                query="What's the difference between soft delete and GDPR forget-me for users?",
                expected_answer="Soft delete sets is_active=false but keeps PII; GDPR forget-me scrubs all PII asynchronously",
                ground_truth_location="User-Profile Service - API Endpoints and Current Development sections",
                difficulty="MEDIUM",
                importance="HIGH",
                category="Compliance",
                requires_reasoning="Must compare two different deletion approaches across different sections"
            ),
            TestCase(
                query="What monitoring issue exists with the Notification-Dispatcher Service?",
                expected_answer="Kafka consumer lag spikes during high traffic and SendGrid rate limit issues",
                ground_truth_location="Notification-Dispatcher Service - Known Production Issues section",
                difficulty="MEDIUM",
                importance="HIGH",
                category="Operations"
            ),

            # ============= HARD CASES - Buried info, multi-hop reasoning =============
            TestCase(
                query="What are the data loss risks in the Order-Processor Service?",
                expected_answer="Pod restart during PAYMENT_HALT state causes permanent order loss from local H2 file",
                ground_truth_location="Order-Processor Service - Error Handling section, buried in dense paragraph",
                difficulty="HARD",
                importance="CRITICAL",
                category="Risk Management",
                why_hard="Critical info buried mid-paragraph, requires understanding system state transitions",
                requires_reasoning="Must connect payment errors -> PAYMENT_HALT -> H2 file -> pod restart -> data loss"
            ),
            TestCase(
                query="Which parts of the Order-Processor system have no test coverage?",
                expected_answer="LegacyPaymentFallback class - the deprecated payment fallback mechanism",
                ground_truth_location="Order-Processor Service - Error Handling section, end of paragraph 2",
                difficulty="HARD",
                importance="CRITICAL",
                category="Code Quality",
                why_hard="Mentioned casually at end of complex paragraph with no formatting emphasis",
                requires_reasoning="Must find and understand significance of 'no test coverage' mention"
            ),
            TestCase(
                query="What deprecated systems are still running in production?",
                expected_answer="LegacyPaymentFallback class handles payment errors but is marked @Deprecated yet still active",
                ground_truth_location="Order-Processor Service - Error Handling section",
                difficulty="HARD",
                importance="HIGH",
                category="Technical Debt",
                why_hard="Requires connecting '@Deprecated' annotation with 'still active' across complex paragraph",
                requires_reasoning="Must understand code annotation vs runtime status contradiction"
            ),
            TestCase(
                query="What configuration security issue exists in Order-Processor?",
                expected_answer="Redis connection string is hardcoded in RedisConfig.java line 47, needs externalization",
                ground_truth_location="Order-Processor Service - Configuration section, warning note",
                difficulty="HARD",
                importance="HIGH",
                category="Security",
                why_hard="Security issue mentioned as side note in configuration section",
                requires_reasoning="Must recognize hardcoded credentials as security vulnerability"
            ),
            TestCase(
                query="Who left the company and what knowledge was lost?",
                expected_answer="Original developer of LegacyPaymentFallback is no longer with team, and previous tech lead Mark Johnson left Feb 2023",
                ground_truth_location="Order-Processor Service - multiple sections",
                difficulty="HARD",
                importance="HIGH",
                category="Knowledge Management",
                why_hard="Information scattered across document, requires connecting people with system components",
                requires_reasoning="Must connect personnel changes with knowledge gaps and system risks"
            ),
            TestCase(
                query="What's the cost analysis result for the batching optimization?",
                expected_answer="Savings would be only ~$200/month, so product team deprioritized the feature",
                ground_truth_location="Notification-Dispatcher Service - Investigation section",
                difficulty="HARD",
                importance="MEDIUM",
                category="Business Analysis",
                why_hard="Cost information buried in technical investigation section",
                requires_reasoning="Must connect technical complexity with business value assessment"
            ),
            TestCase(
                query="What blocks the Spring Boot 3.x upgrade for Notification-Dispatcher?",
                expected_answer="Blocked by Java 17→21 upgrade waiting for infrastructure team to update Docker base images",
                ground_truth_location="Notification-Dispatcher Service - Project Backlog, Spring Boot 3.x item",
                difficulty="HARD",
                importance="MEDIUM",
                category="Dependencies",
                why_hard="Dependency chain buried in project planning section",
                requires_reasoning="Must trace dependency chain: Spring Boot upgrade → Java upgrade → Infrastructure team → Docker images"
            )
        ]

        logger.info(f"Created {len(test_cases)} test cases:")
        difficulty_counts = {}
        for case in test_cases:
            difficulty_counts[case.difficulty] = difficulty_counts.get(case.difficulty, 0) + 1

        for difficulty, count in difficulty_counts.items():
            logger.info(f"  {difficulty}: {count} cases")

        return test_cases

    def evaluate_answer(self, expected: str, actual: str, test_case: TestCase) -> Tuple[bool, float, str]:
        """
        Evaluate if the actual answer matches the expected answer
        Returns: (is_correct, confidence_score, evaluation_notes)
        """
        # Simple keyword-based evaluation (in production, you'd use LLM-as-judge)
        expected_lower = expected.lower()
        actual_lower = actual.lower()

        # Extract key terms from expected answer
        key_terms = []
        if "3 retry" in expected_lower or "3-second" in expected_lower:
            key_terms.extend(["3", "retry", "second"])
        if "new-orders" in expected_lower:
            key_terms.append("new-orders")
        if "payment_halt" in expected_lower or "kafka listener stops" in expected_lower:
            key_terms.extend(["payment", "halt", "listener", "stop"])
        if "h2" in expected_lower and "file" in expected_lower:
            key_terms.extend(["h2", "file", "local"])
        if "pod restart" in expected_lower:
            key_terms.extend(["pod", "restart"])
        if "permanent" in expected_lower and "loss" in expected_lower:
            key_terms.extend(["permanent", "loss"])
        if "legacypaymentfallback" in expected_lower:
            key_terms.extend(["legacy", "payment", "fallback"])
        if "test coverage" in expected_lower:
            key_terms.extend(["test", "coverage"])
        if "deprecated" in expected_lower:
            key_terms.append("deprecated")
        if "hardcoded" in expected_lower:
            key_terms.extend(["hardcoded", "redis"])
        if "java 17" in expected_lower:
            key_terms.extend(["java", "17"])
        if "spring boot" in expected_lower:
            key_terms.extend(["spring", "boot"])

        # Simple matching logic
        if not key_terms:
            # Extract simple key terms from expected answer
            words = expected_lower.split()
            key_terms = [word for word in words if len(word) > 3 and word not in ['that', 'with', 'from', 'this']]

        matches = sum(1 for term in key_terms if term in actual_lower)
        confidence_score = matches / len(key_terms) if key_terms else 0

        # Consider it correct if confidence > 0.6 for EASY/MEDIUM, > 0.5 for HARD
        threshold = 0.6 if test_case.difficulty != "HARD" else 0.5
        is_correct = confidence_score >= threshold

        evaluation_notes = f"Key terms found: {matches}/{len(key_terms)} (confidence: {confidence_score:.2f})"

        return is_correct, confidence_score, evaluation_notes

    def evaluate_rag_system(self, rag_system, system_name: str = "Unknown") -> BenchmarkReport:
        """
        Evaluate a RAG system against all test cases
        """
        logger.info(f"Starting evaluation of {system_name} with {len(self.test_cases)} test cases...")

        results = []
        start_time = time.time()

        for i, test_case in enumerate(self.test_cases, 1):
            logger.info(f"Evaluating case {i}/{len(self.test_cases)}: {test_case.difficulty} - {test_case.query[:50]}...")

            # Time the query
            query_start = time.time()
            try:
                if hasattr(rag_system, 'ask'):
                    response = rag_system.ask(test_case.query)
                    actual_answer = response.get('answer', '') if isinstance(response, dict) else str(response)
                elif hasattr(rag_system, 'query'):
                    actual_answer = str(rag_system.query(test_case.query))
                else:
                    raise ValueError("RAG system must have 'ask' or 'query' method")

                query_time = time.time() - query_start

                # Evaluate the answer
                is_correct, confidence_score, evaluation_notes = self.evaluate_answer(
                    test_case.expected_answer,
                    actual_answer,
                    test_case
                )

                result = EvaluationResult(
                    query=test_case.query,
                    expected_answer=test_case.expected_answer,
                    actual_answer=actual_answer,
                    is_correct=is_correct,
                    confidence_score=confidence_score,
                    response_time=query_time,
                    difficulty=test_case.difficulty,
                    category=test_case.category or "Unknown",
                    evaluation_notes=evaluation_notes
                )

                results.append(result)

                # Log result
                status = "✓" if is_correct else "✗"
                logger.info(f"  {status} {test_case.difficulty} | Confidence: {confidence_score:.2f} | Time: {query_time:.2f}s")
                if not is_correct and test_case.importance == "CRITICAL":
                    logger.warning(f"  CRITICAL MISS: {test_case.query}")

            except Exception as e:
                logger.error(f"  ERROR evaluating case {i}: {e}")
                result = EvaluationResult(
                    query=test_case.query,
                    expected_answer=test_case.expected_answer,
                    actual_answer=f"ERROR: {str(e)}",
                    is_correct=False,
                    confidence_score=0.0,
                    response_time=0.0,
                    difficulty=test_case.difficulty,
                    category=test_case.category or "Unknown",
                    evaluation_notes=f"System error: {str(e)}"
                )
                results.append(result)

        total_time = time.time() - start_time
        logger.info(f"Evaluation completed in {total_time:.2f}s")

        # Generate report
        return self._generate_report(results, system_name)

    def _generate_report(self, results: List[EvaluationResult], system_name: str) -> BenchmarkReport:
        """Generate comprehensive benchmark report"""

        total_cases = len(results)
        correct_answers = sum(1 for r in results if r.is_correct)
        overall_accuracy = correct_answers / total_cases if total_cases > 0 else 0

        # Accuracy by difficulty
        accuracy_by_difficulty = {}
        for difficulty in ["EASY", "MEDIUM", "HARD"]:
            difficulty_results = [r for r in results if r.difficulty == difficulty]
            if difficulty_results:
                correct = sum(1 for r in difficulty_results if r.is_correct)
                accuracy_by_difficulty[difficulty] = correct / len(difficulty_results)
            else:
                accuracy_by_difficulty[difficulty] = 0.0

        # Accuracy by category
        accuracy_by_category = {}
        categories = set(r.category for r in results)
        for category in categories:
            category_results = [r for r in results if r.category == category]
            if category_results:
                correct = sum(1 for r in category_results if r.is_correct)
                accuracy_by_category[category] = correct / len(category_results)

        # Response time metrics
        response_times = [r.response_time for r in results if r.response_time > 0]
        avg_response_time = statistics.mean(response_times) if response_times else 0

        response_time_by_difficulty = {}
        for difficulty in ["EASY", "MEDIUM", "HARD"]:
            difficulty_times = [r.response_time for r in results
                             if r.difficulty == difficulty and r.response_time > 0]
            response_time_by_difficulty[difficulty] = statistics.mean(difficulty_times) if difficulty_times else 0

        # Critical misses
        critical_test_cases = [tc for tc in self.test_cases if tc.importance == "CRITICAL"]
        critical_misses = []
        for tc in critical_test_cases:
            result = next((r for r in results if r.query == tc.query), None)
            if result and not result.is_correct:
                critical_misses.append(tc.query)

        return BenchmarkReport(
            total_cases=total_cases,
            correct_answers=correct_answers,
            overall_accuracy=overall_accuracy,
            accuracy_by_difficulty=accuracy_by_difficulty,
            accuracy_by_category=accuracy_by_category,
            avg_response_time=avg_response_time,
            response_time_by_difficulty=response_time_by_difficulty,
            critical_misses=critical_misses,
            evaluation_timestamp=datetime.now().isoformat(),
            system_name=system_name
        )

    def print_report(self, report: BenchmarkReport):
        """Print a formatted benchmark report"""

        print("\n" + "="*80)
        print(f"RAG SYSTEM BENCHMARK REPORT - {report.system_name}")
        print("="*80)
        print(f"Evaluation Date: {report.evaluation_timestamp}")
        print(f"Total Test Cases: {report.total_cases}")
        print()

        print("📊 OVERALL PERFORMANCE")
        print("-" * 40)
        print(f"Accuracy: {report.overall_accuracy:.1%} ({report.correct_answers}/{report.total_cases})")
        print(f"Average Response Time: {report.avg_response_time:.2f}s")
        print()

        print("📈 ACCURACY BY DIFFICULTY")
        print("-" * 40)
        for difficulty in ["EASY", "MEDIUM", "HARD"]:
            accuracy = report.accuracy_by_difficulty.get(difficulty, 0)
            status = "✓" if accuracy > 0.8 else "⚠" if accuracy > 0.5 else "✗"
            print(f"{status} {difficulty:6}: {accuracy:.1%}")
        print()

        print("⏱️ RESPONSE TIME BY DIFFICULTY")
        print("-" * 40)
        for difficulty in ["EASY", "MEDIUM", "HARD"]:
            time_val = report.response_time_by_difficulty.get(difficulty, 0)
            print(f"  {difficulty:6}: {time_val:.2f}s")
        print()

        print("🎯 ACCURACY BY CATEGORY")
        print("-" * 40)
        sorted_categories = sorted(report.accuracy_by_category.items(), key=lambda x: x[1], reverse=True)
        for category, accuracy in sorted_categories:
            status = "✓" if accuracy > 0.8 else "⚠" if accuracy > 0.5 else "✗"
            print(f"{status} {category:20}: {accuracy:.1%}")
        print()

        if report.critical_misses:
            print("🚨 CRITICAL MISSES")
            print("-" * 40)
            for miss in report.critical_misses:
                print(f"✗ {miss}")
            print()
        else:
            print("✅ NO CRITICAL MISSES")
            print()

        print("💡 RESUME BULLETS")
        print("-" * 40)
        improvement_vs_baseline = "N/A"  # Would need baseline comparison
        print(f"• Achieved {report.overall_accuracy:.1%} accuracy on {report.total_cases}-query documentation benchmark")
        print(f"• Excelled at complex queries: {report.accuracy_by_difficulty.get('HARD', 0):.1%} accuracy on hard cases")
        print(f"• Average response time: {report.avg_response_time:.2f}s")
        if not report.critical_misses:
            print(f"• 100% accuracy on critical risk detection queries")
        print()

    def save_detailed_results(self, results: List[EvaluationResult], filepath: str):
        """Save detailed results to JSON file"""

        data = {
            "evaluation_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_cases": len(results),
                "framework_version": "1.0"
            },
            "results": [asdict(result) for result in results],
            "test_cases": [asdict(tc) for tc in self.test_cases]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Detailed results saved to {filepath}")

# Example usage and testing
def demo_benchmark():
    """Demo the benchmark system with a mock RAG system"""

    class MockRAGSystem:
        """Mock RAG system for testing"""
        def ask(self, query: str) -> dict:
            # Simulate different performance based on query complexity
            if "java" in query.lower():
                return {"answer": "Java 17"}
            elif "kafka topic" in query.lower():
                return {"answer": "new-orders topic"}
            elif "retry" in query.lower():
                return {"answer": "3 retry attempts with backoff"}
            elif "data loss" in query.lower():
                return {"answer": "Pod restart can cause data loss from local H2 file"}
            else:
                return {"answer": "I don't have information about that"}

    # Run benchmark
    benchmark = ConfluenceBenchmark()
    mock_system = MockRAGSystem()

    report = benchmark.evaluate_rag_system(mock_system, "Mock RAG System")
    benchmark.print_report(report)

if __name__ == "__main__":
    demo_benchmark()