import asyncio
import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import httpx
import openai
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"

@dataclass
class TestCase:
    """Represents a single test case with query and expected answer"""
    id: str
    query: str
    ground_truth: str
    description: Optional[str] = None

@dataclass
class TestRunResult:
    """Results from running a single test case"""
    test_case: TestCase
    agent_response: str
    evaluation_result: TestResult
    evaluation_reasoning: str
    execution_time: float
    error_message: Optional[str] = None

class AgentConfig(BaseModel):
    """Configuration for an SQL agent endpoint"""
    name: str
    base_url: str
    endpoint: str
    headers: Dict[str, str] = {}
    timeout: int = 30

class SQLAgentTester:
    """Main test framework for SQL agents"""
    
    def __init__(self, evaluator_client: openai.OpenAI, agent_config: AgentConfig):
        self.evaluator_client = evaluator_client
        self.agent_config = agent_config
        self.test_cases: List[TestCase] = []
        
    def add_test_case(self, test_case: TestCase):
        """Add a test case to the test suite"""
        self.test_cases.append(test_case)
        
    def load_test_cases_from_json(self, file_path: str):
        """Load test cases from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            for item in data.get('test_cases', []):
                test_case = TestCase(
                    id=item['id'],
                    query=item['query'],
                    ground_truth=item['ground_truth'],
                    description=item.get('description')
                )
                self.add_test_case(test_case)
                
            logger.info(f"Loaded {len(self.test_cases)} test cases from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading test cases: {e}")
            raise
    
    async def query_agent(self, query: str, context: str = "northwind") -> str:
        """Query the configured SQL agent"""
        url = f"{self.agent_config.base_url.rstrip('/')}/{self.agent_config.endpoint.lstrip('/')}"
        
        payload = {"query": query}

        params = {"context": context}
        
        async with httpx.AsyncClient(timeout=self.agent_config.timeout) as client:
            try:
                response = await client.post(
                    url,
                    json=payload,
                    params=params,
                    headers=self.agent_config.headers
                )
                response.raise_for_status()

                result = response.json()
                
                # Assuming the agent returns JSON with a 'result' or 'answer' field
                if "response" in result:
                    agent_response = result["response"]
                    if isinstance(agent_response, dict) and "output" in agent_response:
                        return str(agent_response["output"])
                    else:
                        return str(agent_response)
                
                
                # Try common response field names
                for field in ['result', 'answer', 'response', 'summary']:
                    if field in result:
                        return str(result[field])
                
                # If no standard field found, return the whole response as string
                return str(result)
                
            except httpx.TimeoutException:
                raise Exception(f"Timeout querying agent at {url}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"HTTP error {e.response.status_code}: {e.response.text}")
            except Exception as e:
                raise Exception(f"Error querying agent: {e}")
    
    def evaluate_consistency(self, agent_answer: str, ground_truth: str) -> tuple[TestResult, str]:
        """Use LLM to evaluate if agent answer is consistent with ground truth"""
        
        evaluation_prompt = f"""
            You are an expert evaluator for SQL query results. Your task is to determine if two answers are semantically consistent with each other.

            Ground Truth Answer: {ground_truth}

            Agent Answer: {agent_answer}

            Instructions:
            1. Compare the semantic meaning of both answers
            2. Consider that answers may be phrased differently but convey the same information
            3. Look for factual consistency rather than exact word matching
            4. Consider numerical values, dates, and specific facts carefully
            5. Minor formatting differences should not affect consistency

            Respond with a JSON object containing:
            - "consistent": true/false
            - "reasoning": "Detailed explanation of your evaluation"

            Example response:
            {{
                "consistent": true,
                "reasoning": "Both answers indicate the same total sales figure of $1.2M for Q3, though phrased differently."
            }}
        """

        try:
            response = self.evaluator_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert evaluator that determines semantic consistency between answers."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            evaluation = json.loads(content)
            
            result = TestResult.PASS if evaluation["consistent"] else TestResult.FAIL
            reasoning = evaluation["reasoning"]
            
            return result, reasoning
            
        except json.JSONDecodeError:
            logger.error("Failed to parse evaluator response as JSON")
            return TestResult.ERROR, "Failed to parse evaluation response"
        except Exception as e:
            logger.error(f"Error in evaluation: {e}")
            return TestResult.ERROR, f"Evaluation error: {e}"
    
    async def run_single_test(self, test_case: TestCase) -> TestRunResult:
        """Run a single test case"""
        import time
        start_time = time.time()
        
        try:
            # Query the agent
            logger.info(f"Running test case: {test_case.id}")
            agent_response = await self.query_agent(test_case.query)
            
            # Evaluate consistency
            eval_result, reasoning = self.evaluate_consistency(agent_response, test_case.ground_truth)
            
            execution_time = time.time() - start_time
            
            return TestRunResult(
                test_case=test_case,
                agent_response=agent_response,
                evaluation_result=eval_result,
                evaluation_reasoning=reasoning,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error running test case {test_case.id}: {e}")
            
            return TestRunResult(
                test_case=test_case,
                agent_response="",
                evaluation_result=TestResult.ERROR,
                evaluation_reasoning=f"Test execution error: {e}",
                execution_time=execution_time,
                error_message=str(e)
            )
    
    async def run_all_tests(self) -> List[TestRunResult]:
        """Run all test cases"""
        logger.info(f"Starting test run with {len(self.test_cases)} test cases")
        
        results = []
        for test_case in self.test_cases:
            result = await self.run_single_test(test_case)
            results.append(result)
            
            # Log result
            status = "✓" if result.evaluation_result == TestResult.PASS else "✗"
            logger.info(f"{status} {test_case.id}: {result.evaluation_result.value}")
            
        return results
    
    def generate_report(self, results: List[TestRunResult]) -> str:
        """Generate a comprehensive test report"""
        total_tests = len(results)
        passed = sum(1 for r in results if r.evaluation_result == TestResult.PASS)
        failed = sum(1 for r in results if r.evaluation_result == TestResult.FAIL)
        errors = sum(1 for r in results if r.evaluation_result == TestResult.ERROR)
        
        avg_time = sum(r.execution_time for r in results) / total_tests if results else 0
        
        report = f"""
            SQL Agent Test Report
            =====================
            Agent: {self.agent_config.name}
            Endpoint: {self.agent_config.base_url}/{self.agent_config.endpoint}

            Summary:
            - Total Tests: {total_tests}
            - Passed: {passed} ({passed/total_tests*100:.1f}%)
            - Failed: {failed} ({failed/total_tests*100:.1f}%)
            - Errors: {errors} ({errors/total_tests*100:.1f}%)
            - Average Execution Time: {avg_time:.2f}s

            Detailed Results:
            """
                    
        for result in results:
            status_symbol = {
                TestResult.PASS: "✓",
                TestResult.FAIL: "✗",
                TestResult.ERROR: "⚠"
            }[result.evaluation_result]
                        
            report += f"""
                {status_symbol} {result.test_case.id} ({result.execution_time:.2f}s)
                Query: {result.test_case.query}
                Ground Truth: {result.test_case.ground_truth}
                Agent Response: {result.agent_response}
                Evaluation: {result.evaluation_reasoning}
            """
            
        if result.error_message:
            report += f"  Error: {result.error_message}\n"
                
        return report
    
    # Example usage and configuration
async def main():
    """Example of how to use the test framework"""
    
    # Configure the evaluator (OpenAI client)
    evaluator_client = openai.OpenAI(api_key="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")
    
    # Configure the agent to test
    agent_config = AgentConfig(
        name="Langchain Zero-Shot SQL Agent",
        base_url="http://localhost:9000",
        endpoint="/agent/ask",
        headers={"Content-Type": "application/json"},
        timeout=300
    )

    # agent_config = AgentConfig(
    #     name="Langchain Few-Shot SQL Agent",
    #     base_url="http://localhost:8000",
    #     endpoint="/agent/ask",
    #     headers={"Content-Type": "application/json"},
    #     timeout=300
    # )

    # agent_config = AgentConfig(
    #     name="MCP-Toolbox SQL Agent",
    #     base_url="http://localhost:8001",
    #     endpoint="/query",
    #     headers={"Content-Type": "application/json"},
    #     timeout=300
    # )
    
    # Initialize tester
    tester = SQLAgentTester(evaluator_client, agent_config)
    
    # Or load from JSON file
    tester.load_test_cases_from_json("test_cases.json")
    
    # Run all tests
    results = await tester.run_all_tests()
    
    # Generate and print report
    report = tester.generate_report(results)
    print(report)
    
    # Save report to file
    with open("test_report_zero_shot.txt", "w") as f:
        f.write(report)

if __name__ == "__main__":
    asyncio.run(main())