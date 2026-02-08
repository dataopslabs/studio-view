"""
ADK (Agent Development Kit) code generation service.
Generates Google ADK agent code from SOP documents for automation execution.
"""

import logging
from typing import Dict, Any, Optional, List
from models.sop import SOPDocument, SOPStep

logger = logging.getLogger(__name__)


class CodeGenerator:
    """
    Generates executable Google ADK agent code from SOP documents.
    Creates Python code for automation that can be executed by the ADK framework.
    """

    def __init__(self):
        """Initialize the code generator."""
        logger.info("Code generator initialized")

    def generate_adk_code(
        self, sop: SOPDocument, target_framework: str = "adk"
    ) -> Dict[str, str]:
        """
        Generate ADK agent code from an SOP document.

        Args:
            sop: SOPDocument to convert to code
            target_framework: Target framework (adk, selenium, playwright)

        Returns:
            Dictionary with file names and generated code
        """
        logger.info(f"Generating {target_framework} code from SOP: {sop.id}")

        if target_framework == "adk":
            return self._generate_adk_agent_code(sop)
        elif target_framework == "selenium":
            return self._generate_selenium_code(sop)
        elif target_framework == "playwright":
            return self._generate_playwright_code(sop)
        else:
            logger.warning(f"Unknown framework: {target_framework}, defaulting to adk")
            return self._generate_adk_agent_code(sop)

    def _generate_adk_agent_code(self, sop: SOPDocument) -> Dict[str, str]:
        """
        Generate Google ADK agent code.

        Args:
            sop: SOPDocument to convert

        Returns:
            Dictionary with generated Python code files
        """
        files = {}

        # Generate main agent file
        files[f"{sop.id}_agent.py"] = self._generate_main_agent(sop)

        # Generate tasks file
        files[f"{sop.id}_tasks.py"] = self._generate_tasks_module(sop)

        # Generate configuration file
        files[f"{sop.id}_config.py"] = self._generate_config_module(sop)

        # Generate orchestration file
        files[f"{sop.id}_orchestration.py"] = self._generate_orchestration(sop)

        return files

    def _generate_main_agent(self, sop: SOPDocument) -> str:
        """
        Generate the main agent Python file.

        Args:
            sop: SOPDocument

        Returns:
            Agent code as string
        """
        code = f'''"""
Auto-generated Google ADK Agent for: {sop.title}
Generated from SOP ID: {sop.id}
"""

import logging
from typing import Optional, Dict, Any
from google.ai.generativelanguage.google_ai_agent import (
    Agent,
    AgentTask,
    AgentConfig,
)

logger = logging.getLogger(__name__)


class {self._to_class_name(sop.title)}Agent(Agent):
    """
    Automated agent for: {sop.title}

    Description: {sop.description}
    Total Steps: {len(sop.steps)}
    Estimated Duration: {sop.execution_time_estimate} minutes
    Systems Involved: {', '.join(sop.systems_involved)}
    """

    def __init__(self):
        """Initialize the agent."""
        super().__init__()
        self.sop_id = "{sop.id}"
        self.logger = logging.getLogger(__name__)
        self.execution_logs = []

    async def execute(self) -> Dict[str, Any]:
        """
        Execute the automated workflow.

        Returns:
            Execution results with status and metrics
        """
        self.logger.info(f"Starting execution of {self.sop_id}")

        try:
            # Execute all workflow steps
            results = {{
                "sop_id": self.sop_id,
                "total_steps": {len(sop.steps)},
                "executed_steps": 0,
                "passed_steps": 0,
                "failed_steps": 0,
                "steps_details": [],
            }}

            for step_num, step_task in enumerate(self.get_step_tasks(), 1):
                try:
                    step_result = await step_task.execute()
                    results["executed_steps"] += 1

                    if step_result.get("success", False):
                        results["passed_steps"] += 1
                    else:
                        results["failed_steps"] += 1

                    results["steps_details"].append({{
                        "step": step_num,
                        "status": "passed" if step_result.get("success") else "failed",
                        "details": step_result,
                    }})

                except Exception as e:
                    self.logger.error(f"Step {{step_num}} failed: {{str(e)}}")
                    results["failed_steps"] += 1
                    results["steps_details"].append({{
                        "step": step_num,
                        "status": "error",
                        "error": str(e),
                    }})

            results["success_rate"] = (
                results["passed_steps"] / results["executed_steps"]
                if results["executed_steps"] > 0
                else 0.0
            )

            self.logger.info(f"Execution completed. Success rate: {{results['success_rate']}}")
            return results

        except Exception as e:
            self.logger.error(f"Agent execution failed: {{str(e)}}")
            return {{
                "sop_id": self.sop_id,
                "success": False,
                "error": str(e),
            }}

    def get_step_tasks(self) -> list:
        """
        Get the list of step tasks to execute.

        Returns:
            List of AgentTask objects for each SOP step
        """
        from . import {self._to_module_name(sop.title)}_tasks as tasks_module

        task_functions = [
{self._generate_step_task_imports(sop.steps)}
        ]
        return task_functions

    async def validate(self) -> bool:
        """
        Validate agent configuration and prerequisites.

        Returns:
            True if validation passes, False otherwise
        """
        self.logger.info("Validating agent configuration")

        # Check system availability
        systems_to_validate = {sop.systems_involved}
        for system in systems_to_validate:
            # System validation logic would go here
            pass

        self.logger.info("Validation completed successfully")
        return True
'''
        return code

    def _generate_tasks_module(self, sop: SOPDocument) -> str:
        """
        Generate the tasks module with individual step implementations.

        Args:
            sop: SOPDocument

        Returns:
            Tasks module code as string
        """
        code = f'''"""
Tasks for: {sop.title}
Each function represents one step in the SOP workflow.
"""

import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class StepExecutionError(Exception):
    """Exception raised when a step fails to execute."""
    pass

'''

        # Generate a task function for each step
        for step in sop.steps:
            code += self._generate_step_function(step)

        return code

    def _generate_step_function(self, step: SOPStep) -> str:
        """
        Generate a function for a single SOP step.

        Args:
            step: SOPStep

        Returns:
            Function code as string
        """
        func_name = self._to_function_name(f"step_{step.step_number}_{step.title}")

        code = f'''
async def {func_name}() -> Dict[str, Any]:
    """
    {step.title}

    Description: {step.description}
    System: {step.system_involved}
    Action: {step.action_type}
    Expected Output: {step.expected_output}
    """
    try:
        logger.info("Executing: {step.title}")

        # Action implementation
        action_result = await execute_{step.action_type}(
            system="{step.system_involved}",
            element_id="{step.element_identifier or 'N/A'}",
        )

        # Validate expected output
        validation_passed = validate_output(
            expected="{step.expected_output}",
            actual=action_result.get("output", ""),
        )

        return {{
            "success": validation_passed,
            "step": {step.step_number},
            "title": "{step.title}",
            "duration": {step.duration or 0},
            "output": action_result,
            "timestamp": {step.timestamp or 0},
        }}

    except Exception as e:
        logger.error(f"Step {step.step_number} failed: {{str(e)}}")
        raise StepExecutionError(f"Step failed: {{str(e)}}")


'''
        return code

    def _generate_config_module(self, sop: SOPDocument) -> str:
        """
        Generate configuration module.

        Args:
            sop: SOPDocument

        Returns:
            Configuration code as string
        """
        code = f'''"""
Configuration for: {sop.title}
Auto-generated configuration module.
"""

# SOP Configuration
SOP_CONFIG = {{
    "id": "{sop.id}",
    "title": "{sop.title}",
    "version": "{sop.version}",
    "execution_timeout": {int((sop.execution_time_estimate or 10) * 60)},  # seconds
    "max_retries": 3,
    "retry_delay": 5,  # seconds
}}

# Systems Configuration
SYSTEMS = {{
{self._generate_systems_config(sop.systems_involved)}
}}

# Execution Parameters
EXECUTION_CONFIG = {{
    "headless": True,
    "capture_screenshots": True,
    "log_level": "INFO",
    "validate_steps": True,
}}

# Validation Rules
VALIDATION_RULES = {{
    "success_threshold": 0.95,
    "allowed_failures": 0,
    "retry_on_failure": True,
}}
'''
        return code

    def _generate_systems_config(self, systems: List[str]) -> str:
        """
        Generate systems configuration section.

        Args:
            systems: List of system names

        Returns:
            Systems config code
        """
        config_code = ""
        for system in systems:
            config_code += f'''    "{system}": {{
        "timeout": 30,
        "polling_interval": 1,
    }},
'''
        return config_code

    def _generate_orchestration(self, sop: SOPDocument) -> str:
        """
        Generate orchestration/coordination code.

        Args:
            sop: SOPDocument

        Returns:
            Orchestration code as string
        """
        code = f'''"""
Orchestration for: {sop.title}
Coordinates execution of all steps and manages dependencies.
"""

import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


async def execute_workflow() -> Dict[str, Any]:
    """
    Execute the complete workflow orchestration.

    Returns:
        Workflow execution results
    """
    logger.info("Starting workflow orchestration")

    workflow_config = {{
        "sop_id": "{sop.id}",
        "steps": {len(sop.steps)},
        "parallel_execution": False,
        "dependencies": {{
{self._generate_dependencies(sop.steps)}
        }},
    }}

    logger.info(f"Workflow config: {{workflow_config}}")

    # Execute steps in order (or in parallel if configured)
    results = {{
        "workflow_id": "{sop.id}",
        "status": "running",
        "step_results": [],
    }}

    # Step execution would happen here

    return results


def create_task_dependency_graph() -> Dict[str, list]:
    """
    Create a dependency graph for step execution.

    Returns:
        Dependency graph as dictionary
    """
    return {{
{self._generate_dependencies(sop.steps)}
    }}
'''
        return code

    def _generate_dependencies(self, steps: List[SOPStep]) -> str:
        """
        Generate step dependencies.

        Args:
            steps: List of SOP steps

        Returns:
            Dependencies code
        """
        deps = ""
        for i, step in enumerate(steps):
            depends_on = [str(j) for j in range(i)] if i > 0 else []
            deps += f'        "step_{step.step_number}": {depends_on},\n'
        return deps

    def _generate_selenium_code(self, sop: SOPDocument) -> Dict[str, str]:
        """
        Generate Selenium WebDriver code.

        Args:
            sop: SOPDocument

        Returns:
            Dictionary with generated code files
        """
        code = f'''"""
Selenium WebDriver automation for: {sop.title}
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logger = logging.getLogger(__name__)


class {self._to_class_name(sop.title)}Automation:
    """Selenium-based automation for {sop.title}"""

    def __init__(self):
        """Initialize WebDriver"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)

    def execute(self):
        """Execute automation"""
        try:
{self._generate_selenium_steps(sop.steps)}
            return {{"success": True}}
        except Exception as e:
            logger.error(f"Automation failed: {{str(e)}}")
            return {{"success": False, "error": str(e)}}
        finally:
            self.driver.quit()

{self._generate_selenium_helper_methods()}
'''
        return {f"{sop.id}_selenium.py": code}

    def _generate_selenium_steps(self, steps: List[SOPStep]) -> str:
        """
        Generate Selenium step code.

        Args:
            steps: List of SOP steps

        Returns:
            Selenium step code
        """
        code = ""
        for step in steps:
            if step.action_type == "click":
                code += f'''            # Step {step.step_number}: {step.title}
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "{step.element_identifier}"))
            )
            element.click()
'''
            elif step.action_type == "input":
                code += f'''            # Step {step.step_number}: {step.title}
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "{step.element_identifier}"))
            )
            element.send_keys("{{input_value}}")
'''
        return code

    def _generate_selenium_helper_methods(self) -> str:
        """Generate helper methods for Selenium."""
        return '''
    def wait_for_element(self, locator, timeout=10):
        """Wait for element to be present"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def take_screenshot(self, filename):
        """Take screenshot"""
        self.driver.save_screenshot(filename)
'''

    def _generate_playwright_code(self, sop: SOPDocument) -> Dict[str, str]:
        """
        Generate Playwright code.

        Args:
            sop: SOPDocument

        Returns:
            Dictionary with generated code files
        """
        code = f'''"""
Playwright automation for: {sop.title}
"""

import asyncio
from playwright.async_api import async_playwright
import logging

logger = logging.getLogger(__name__)


async def run_automation():
    """Execute Playwright automation"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
{self._generate_playwright_steps(sop.steps)}
            return {{"success": True}}
        except Exception as e:
            logger.error(f"Automation failed: {{str(e)}}")
            return {{"success": False, "error": str(e)}}
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run_automation())
'''
        return {f"{sop.id}_playwright.py": code}

    def _generate_playwright_steps(self, steps: List[SOPStep]) -> str:
        """
        Generate Playwright step code.

        Args:
            steps: List of SOP steps

        Returns:
            Playwright step code
        """
        code = ""
        for step in steps:
            if step.action_type == "click":
                code += f'''            # Step {step.step_number}: {step.title}
            await page.click("{step.element_identifier or 'button'}")
            await page.wait_for_timeout(1000)
'''
            elif step.action_type == "input":
                code += f'''            # Step {step.step_number}: {step.title}
            await page.fill("{step.element_identifier}", "{{input_value}}")
'''
        return code

    def _to_class_name(self, text: str) -> str:
        """Convert text to class name."""
        return "".join(word.capitalize() for word in text.split())

    def _to_module_name(self, text: str) -> str:
        """Convert text to module name."""
        return text.lower().replace(" ", "_")

    def _to_function_name(self, text: str) -> str:
        """Convert text to function name."""
        return text.lower().replace(" ", "_").replace("-", "_")
