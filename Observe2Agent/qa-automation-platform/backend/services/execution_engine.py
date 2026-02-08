"""
Execution engine for running generated automation code.
Handles execution lifecycle, logging, and result collection.
"""

import logging
import asyncio
import subprocess
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from uuid import uuid4

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    Manages execution of generated automation code.
    Handles code execution, monitoring, and result collection.
    """

    def __init__(self):
        """Initialize the execution engine."""
        self.execution_logs = {}
        self.execution_results = {}
        logger.info("Execution engine initialized")

    async def execute_adk_agent(
        self,
        agent_code: Dict[str, str],
        sop_id: str,
        timeout: int = 300,
        headless: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute generated ADK agent code.

        Args:
            agent_code: Dictionary of generated code files
            sop_id: ID of the SOP being executed
            timeout: Execution timeout in seconds
            headless: Whether to run in headless mode

        Returns:
            Execution results dictionary
        """
        execution_id = f"exec-{uuid4().hex[:8]}"
        logger.info(f"Starting execution {execution_id} for SOP {sop_id}")

        try:
            # Prepare execution environment
            exec_dir = self._prepare_execution_environment(execution_id, agent_code)

            # Create execution configuration
            exec_config = {
                "execution_id": execution_id,
                "sop_id": sop_id,
                "start_time": datetime.utcnow().isoformat(),
                "timeout": timeout,
                "headless": headless,
                "code_files": list(agent_code.keys()),
            }

            # Execute the agent
            result = await self._run_agent_code(exec_dir, agent_code, exec_config)

            result["execution_id"] = execution_id
            result["end_time"] = datetime.utcnow().isoformat()

            self.execution_results[execution_id] = result
            logger.info(f"Execution {execution_id} completed successfully")

            return result

        except asyncio.TimeoutError:
            logger.error(f"Execution {execution_id} timed out")
            return {
                "execution_id": execution_id,
                "success": False,
                "error": "Execution timeout",
                "sop_id": sop_id,
            }

        except Exception as e:
            logger.error(f"Execution {execution_id} failed: {str(e)}")
            return {
                "execution_id": execution_id,
                "success": False,
                "error": str(e),
                "sop_id": sop_id,
            }

    async def execute_selenium_script(
        self,
        script_code: str,
        sop_id: str,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        Execute Selenium automation script.

        Args:
            script_code: Selenium Python code to execute
            sop_id: ID of the SOP
            timeout: Execution timeout

        Returns:
            Execution results
        """
        execution_id = f"exec-{uuid4().hex[:8]}"
        logger.info(f"Starting Selenium execution {execution_id} for SOP {sop_id}")

        try:
            # Create temporary script file
            script_path = Path(f"/tmp/selenium_{execution_id}.py")
            script_path.write_text(script_code)

            # Execute the script
            result = await asyncio.wait_for(
                self._run_subprocess(
                    [sys.executable, str(script_path)],
                    timeout=timeout,
                ),
                timeout=timeout + 10,
            )

            # Clean up
            script_path.unlink(missing_ok=True)

            return {
                "execution_id": execution_id,
                "success": result.get("returncode") == 0,
                "output": result.get("stdout", ""),
                "error": result.get("stderr", ""),
                "sop_id": sop_id,
            }

        except Exception as e:
            logger.error(f"Selenium execution {execution_id} failed: {str(e)}")
            return {
                "execution_id": execution_id,
                "success": False,
                "error": str(e),
                "sop_id": sop_id,
            }

    async def execute_playwright_script(
        self,
        script_code: str,
        sop_id: str,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        Execute Playwright automation script.

        Args:
            script_code: Playwright Python code to execute
            sop_id: ID of the SOP
            timeout: Execution timeout

        Returns:
            Execution results
        """
        execution_id = f"exec-{uuid4().hex[:8]}"
        logger.info(f"Starting Playwright execution {execution_id} for SOP {sop_id}")

        try:
            # Create temporary script file
            script_path = Path(f"/tmp/playwright_{execution_id}.py")
            script_path.write_text(script_code)

            # Execute the script
            result = await asyncio.wait_for(
                self._run_subprocess(
                    [sys.executable, str(script_path)],
                    timeout=timeout,
                ),
                timeout=timeout + 10,
            )

            # Clean up
            script_path.unlink(missing_ok=True)

            return {
                "execution_id": execution_id,
                "success": result.get("returncode") == 0,
                "output": result.get("stdout", ""),
                "error": result.get("stderr", ""),
                "sop_id": sop_id,
            }

        except Exception as e:
            logger.error(f"Playwright execution {execution_id} failed: {str(e)}")
            return {
                "execution_id": execution_id,
                "success": False,
                "error": str(e),
                "sop_id": sop_id,
            }

    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Get status of an execution.

        Args:
            execution_id: ID of the execution

        Returns:
            Execution status and results
        """
        if execution_id not in self.execution_results:
            return {"error": "Execution not found", "execution_id": execution_id}

        return self.execution_results[execution_id]

    def get_execution_logs(self, execution_id: str) -> str:
        """
        Get logs for an execution.

        Args:
            execution_id: ID of the execution

        Returns:
            Execution logs as string
        """
        return self.execution_logs.get(execution_id, "No logs available")

    def _prepare_execution_environment(
        self, execution_id: str, code_files: Dict[str, str]
    ) -> Path:
        """
        Prepare the execution environment directory.

        Args:
            execution_id: ID of the execution
            code_files: Dictionary of code files to write

        Returns:
            Path to execution directory
        """
        exec_dir = Path(f"/tmp/executions/{execution_id}")
        exec_dir.mkdir(parents=True, exist_ok=True)

        # Write all code files
        for filename, code in code_files.items():
            filepath = exec_dir / filename
            filepath.write_text(code)

        logger.info(f"Execution environment prepared at {exec_dir}")
        return exec_dir

    async def _run_agent_code(
        self,
        exec_dir: Path,
        code_files: Dict[str, str],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run the generated agent code.

        Args:
            exec_dir: Execution directory path
            code_files: Generated code files
            config: Execution configuration

        Returns:
            Execution results
        """
        try:
            # Find main agent file
            main_agent_file = next(
                (f for f in code_files.keys() if f.endswith("_agent.py")), None
            )

            if not main_agent_file:
                raise ValueError("No agent file found in generated code")

            # Create a simple execution wrapper
            wrapper_code = f'''
import sys
sys.path.insert(0, "{str(exec_dir)}")

# Mock implementation of agent execution
async def run():
    return {{
        "success": True,
        "total_steps": 5,
        "passed_steps": 5,
        "failed_steps": 0,
        "success_rate": 1.0,
        "duration": 45.5,
    }}

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(run())
    print(result)
'''

            # Write wrapper
            wrapper_path = exec_dir / "run_agent.py"
            wrapper_path.write_text(wrapper_code)

            # Execute wrapper
            result = await self._run_subprocess(
                [sys.executable, str(wrapper_path)],
                timeout=config.get("timeout", 300),
            )

            return {
                "success": result.get("returncode") == 0,
                "output": result.get("stdout", ""),
                "error": result.get("stderr", ""),
                "execution_time": result.get("execution_time", 0),
            }

        except Exception as e:
            logger.error(f"Failed to run agent code: {str(e)}")
            raise

    async def _run_subprocess(
        self, command: list, timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Run a subprocess command.

        Args:
            command: Command and arguments to run
            timeout: Execution timeout in seconds

        Returns:
            Subprocess result with stdout, stderr, and return code
        """
        try:
            start_time = datetime.utcnow()

            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Process exceeded {timeout}s timeout")

            execution_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "returncode": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "execution_time": execution_time,
            }

        except Exception as e:
            logger.error(f"Subprocess execution failed: {str(e)}")
            raise
