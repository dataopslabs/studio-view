#!/usr/bin/env python3
"""
End-to-End Simulation Test for AI-Powered QA Automation Platform
================================================================

This script simulates the complete pipeline WITHOUT requiring FastAPI or external APIs.
It exercises every stage of the platform using mock data:

    Video Upload → Video Analysis → System Detection → SOP Generation
    → ECM Mapping → Code Generation → Execution → Validation

Each stage is tested independently and then wired together for a full E2E run.
"""

import os
import sys
import json
import uuid
import time
import asyncio
import tempfile
import textwrap
import traceback
from datetime import datetime
from difflib import SequenceMatcher
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from enum import Enum

# ============================================================
# ANSI Colors for beautiful terminal output
# ============================================================
class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def banner(text):
    width = 70
    print(f"\n{C.BOLD}{C.BLUE}{'='*width}")
    print(f"  {text}")
    print(f"{'='*width}{C.END}\n")

def stage_header(num, title):
    print(f"\n{C.BOLD}{C.CYAN}{'─'*60}")
    print(f"  Stage {num}: {title}")
    print(f"{'─'*60}{C.END}")

def success(msg):
    print(f"  {C.GREEN}✓{C.END} {msg}")

def fail(msg):
    print(f"  {C.RED}✗{C.END} {msg}")

def info(msg):
    print(f"  {C.DIM}→{C.END} {msg}")

def warn(msg):
    print(f"  {C.YELLOW}⚠{C.END} {msg}")

# ============================================================
# Data Models (standalone, no pydantic needed)
# ============================================================
class SystemType(str, Enum):
    ERP = "erp"
    CRM = "crm"
    EMAIL = "email"
    DOCUMENT_MANAGEMENT = "document_management"
    WORKFLOW = "workflow"
    OTHER = "other"

class ValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"
    PENDING = "pending"
    RUNNING = "running"

@dataclass
class WorkflowStep:
    step_number: int
    title: str
    description: str
    timestamp: float
    duration: float
    action_type: str
    system: str
    ui_elements: List[str]
    expected_output: Optional[str] = None

@dataclass
class DetectedSystem:
    name: str
    system_type: SystemType
    confidence: float
    version: str = ""
    ui_elements: List[str] = field(default_factory=list)
    authentication_type: str = "SSO"

@dataclass
class SOPStep:
    step_number: int
    title: str
    description: str
    system_involved: str
    action_type: str
    element_identifier: str = ""
    expected_output: str = ""
    timestamp: float = 0.0
    duration: float = 0.0

@dataclass
class SOPDocument:
    id: str
    title: str
    description: str
    video_source_id: str
    systems_involved: List[str]
    steps: List[SOPStep]
    version: str = "1.0"
    created_at: str = ""
    success_criteria: str = ""
    preconditions: str = ""
    error_handling: str = ""

@dataclass
class ValidationStep:
    step_number: int
    title: str
    status: ValidationStatus
    expected: str
    actual: str
    match_score: float
    duration: float = 0.0

@dataclass
class ValidationReport:
    id: str
    sop_id: str
    execution_id: str
    overall_status: ValidationStatus
    total_steps: int
    passed_steps: int
    failed_steps: int
    success_rate: float
    validation_steps: List[ValidationStep]
    start_time: str = ""
    end_time: str = ""
    total_duration: float = 0.0
    recommendations: List[str] = field(default_factory=list)


# ============================================================
# Stage 1: Video Upload Simulation
# ============================================================
class VideoUploader:
    """Simulates video upload and file management."""

    def __init__(self, upload_dir: str = "/tmp/qa-automation-uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    def upload(self, video_filename: str) -> Dict[str, Any]:
        """Simulate uploading a business process video."""
        video_id = f"video-{uuid.uuid4().hex[:8]}"

        # Create a mock video file
        filepath = os.path.join(self.upload_dir, f"{video_id}_{video_filename}")
        with open(filepath, 'wb') as f:
            f.write(b'\x00' * 1024 * 100)  # 100KB mock video

        file_size = os.path.getsize(filepath)

        return {
            "success": True,
            "video_id": video_id,
            "filename": video_filename,
            "filepath": filepath,
            "size_bytes": file_size,
            "upload_time": datetime.now().isoformat(),
            "status": "uploaded"
        }


# ============================================================
# Stage 2: Video Analysis (Gemini Simulation)
# ============================================================
class VideoAnalyzer:
    """Simulates Gemini multimodal video analysis."""

    def analyze(self, video_id: str, video_path: str) -> Dict[str, Any]:
        """Simulate AI analysis of a business process video."""

        # Simulate processing time
        time.sleep(0.3)

        workflow_steps = [
            WorkflowStep(
                step_number=1,
                title="Open SAP ERP System",
                description="User navigates to SAP Fiori Launchpad and opens the ERP module via browser",
                timestamp=0.0, duration=8.5,
                action_type="navigate",
                system="SAP ERP",
                ui_elements=["SAP Fiori Launchpad", "Browser URL bar", "Login tile"],
                expected_output="SAP dashboard loaded"
            ),
            WorkflowStep(
                step_number=2,
                title="Enter Authentication Credentials",
                description="User enters username and password into the SAP login form and clicks Sign In",
                timestamp=8.5, duration=12.3,
                action_type="input",
                system="SAP ERP",
                ui_elements=["Username field", "Password field", "Sign In button", "SSO option"],
                expected_output="Authentication successful, main menu displayed"
            ),
            WorkflowStep(
                step_number=3,
                title="Navigate to Purchase Order Module",
                description="User clicks on Materials Management menu, selects Purchase Order → Create, opens transaction ME21N",
                timestamp=20.8, duration=6.2,
                action_type="click",
                system="SAP ERP",
                ui_elements=["Main Menu", "Materials Management", "Purchase Order", "Create PO button"],
                expected_output="Purchase Order creation form opened"
            ),
            WorkflowStep(
                step_number=4,
                title="Fill Purchase Order Form",
                description="User enters vendor details (V-1001), material (MAT-5890), quantity (500), delivery date, and cost center",
                timestamp=27.0, duration=18.7,
                action_type="input",
                system="SAP ERP",
                ui_elements=["Vendor field", "Material field", "Quantity field", "Delivery Date picker", "Cost Center dropdown", "Unit Price field"],
                expected_output="PO form populated with all required fields"
            ),
            WorkflowStep(
                step_number=5,
                title="Submit and Verify Purchase Order",
                description="User clicks Submit, confirms the dialog, PO number 4500012847 is generated, confirmation email is triggered",
                timestamp=45.7, duration=10.1,
                action_type="click",
                system="SAP ERP",
                ui_elements=["Submit button", "Confirmation dialog", "OK button", "PO number display"],
                expected_output="PO 4500012847 created, status: Pending Approval"
            ),
        ]

        systems_detected = [
            {
                "name": "SAP ERP",
                "system_type": "erp",
                "confidence": 0.96,
                "version": "S/4HANA 2023",
                "ui_elements": ["SAP Fiori Launchpad", "Transaction Code ME21N", "SAP Menu Bar"],
                "first_detected_at": 0.0
            },
            {
                "name": "Microsoft Outlook",
                "system_type": "email",
                "confidence": 0.82,
                "version": "Microsoft 365",
                "ui_elements": ["Outlook notification", "Email toast popup"],
                "first_detected_at": 50.2
            },
            {
                "name": "Chrome Browser",
                "system_type": "other",
                "confidence": 0.71,
                "version": "v120",
                "ui_elements": ["Browser tab", "URL bar", "Bookmarks bar"],
                "first_detected_at": 0.0
            }
        ]

        data_patterns = [
            {"field": "PO_Number", "pattern": r"PO-\d{10}", "confidence": 0.95, "example": "4500012847"},
            {"field": "Vendor_ID", "pattern": r"V-\d{4}", "confidence": 0.92, "example": "V-1001"},
            {"field": "Material_Code", "pattern": r"MAT-\d{4}", "confidence": 0.90, "example": "MAT-5890"},
            {"field": "Quantity", "pattern": r"\d+", "confidence": 0.88, "example": "500"},
            {"field": "Total_Amount", "pattern": r"\$[\d,]+\.\d{2}", "confidence": 0.85, "example": "$125,000.00"}
        ]

        return {
            "success": True,
            "video_id": video_id,
            "video_path": video_path,
            "video_duration_seconds": 55.8,
            "frames_analyzed": 167,
            "workflow_steps": [
                {
                    "step_number": s.step_number,
                    "title": s.title,
                    "description": s.description,
                    "timestamp": s.timestamp,
                    "duration": s.duration,
                    "action_type": s.action_type,
                    "system": s.system,
                    "ui_elements": s.ui_elements,
                    "expected_output": s.expected_output
                }
                for s in workflow_steps
            ],
            "systems_detected": systems_detected,
            "data_extraction_patterns": data_patterns,
            "process_summary": "SAP Purchase Order Creation - User logs into SAP S/4HANA, navigates to ME21N, fills vendor/material/quantity details, submits PO, and receives confirmation email",
            "estimated_execution_time_minutes": 3.5,
            "success_indicators": [
                "PO number 4500012847 generated",
                "Status shows Pending Approval",
                "Email confirmation triggered"
            ],
            "analysis_timestamp": datetime.now().isoformat(),
            "model_used": "gemini-3-pro-vision (simulated)"
        }


# ============================================================
# Stage 3: System Detection
# ============================================================
class SystemDetector:
    """Detects enterprise systems from video analysis results."""

    SYSTEM_SIGNATURES = {
        "SAP": {"type": SystemType.ERP, "patterns": ["SAP", "Fiori", "Transaction Code", "SAP Module"]},
        "Oracle": {"type": SystemType.ERP, "patterns": ["Oracle", "EBS", "Oracle Menu"]},
        "Salesforce": {"type": SystemType.CRM, "patterns": ["Salesforce", "Lightning", "SFDC"]},
        "Outlook": {"type": SystemType.EMAIL, "patterns": ["Outlook", "Email", "Message"]},
        "Gmail": {"type": SystemType.EMAIL, "patterns": ["Gmail", "Compose"]},
        "SharePoint": {"type": SystemType.DOCUMENT_MANAGEMENT, "patterns": ["SharePoint", "Document Library"]},
    }

    def detect(self, video_analysis: Dict, video_id: str, confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """Detect and classify enterprise systems from analysis."""

        raw_systems = video_analysis.get("systems_detected", [])
        detected = []

        for sys_data in raw_systems:
            confidence = sys_data.get("confidence", 0)
            if confidence < confidence_threshold:
                continue

            name = sys_data["name"]
            sys_type = self._determine_type(name)

            detected.append(DetectedSystem(
                name=name,
                system_type=sys_type,
                confidence=confidence,
                version=sys_data.get("version", ""),
                ui_elements=sys_data.get("ui_elements", []),
                authentication_type="SSO"
            ))

        # Detect workflows
        workflows = self._detect_workflows(video_analysis.get("workflow_steps", []))

        return {
            "video_id": video_id,
            "total_systems_found": len(detected),
            "detected_systems": [
                {
                    "name": s.name,
                    "system_type": s.system_type.value,
                    "confidence": s.confidence,
                    "version": s.version,
                    "ui_elements": s.ui_elements,
                    "authentication_type": s.authentication_type
                }
                for s in detected
            ],
            "analysis_confidence": sum(s.confidence for s in detected) / max(len(detected), 1),
            "detected_workflows": workflows,
            "processing_time_seconds": 0.15
        }

    def _determine_type(self, name: str) -> SystemType:
        name_lower = name.lower()
        for sig_name, sig_data in self.SYSTEM_SIGNATURES.items():
            if sig_name.lower() in name_lower:
                return sig_data["type"]
        return SystemType.OTHER

    def _detect_workflows(self, steps: List[Dict]) -> List[str]:
        workflows = set()
        for step in steps:
            action = step.get("action_type", "")
            if action == "input":
                workflows.add("Form Filling")
            elif action == "navigate":
                workflows.add("System Navigation")
            elif action == "click":
                workflows.add("UI Interaction")
        return sorted(workflows)


# ============================================================
# Stage 4: SOP Generation
# ============================================================
class SOPGenerator:
    """Generates Standard Operating Procedures from analysis."""

    def generate(self, video_id: str, analysis: Dict, systems: Dict,
                 detail_level: str = "detailed") -> SOPDocument:
        """Generate an SOP from video analysis and detected systems."""

        sop_id = f"sop-{uuid.uuid4().hex[:8]}"

        # Create SOP steps from workflow
        steps = []
        for ws in analysis.get("workflow_steps", []):
            step = SOPStep(
                step_number=ws["step_number"],
                title=ws["title"],
                description=ws["description"],
                system_involved=ws.get("system", "Unknown"),
                action_type=ws.get("action_type", "manual"),
                element_identifier=", ".join(ws.get("ui_elements", [])),
                expected_output=ws.get("expected_output", ""),
                timestamp=ws.get("timestamp", 0),
                duration=ws.get("duration", 0)
            )

            if detail_level == "expert":
                step.description += f" [System: {step.system_involved}, Duration: {step.duration}s]"

            steps.append(step)

        # Build system list
        system_names = [s["name"] for s in systems.get("detected_systems", [])]

        summary = analysis.get("process_summary", "Business Process Automation")
        title = " ".join(summary.split()[:6]) + "..."

        sop = SOPDocument(
            id=sop_id,
            title=title,
            description=summary,
            video_source_id=video_id,
            systems_involved=system_names,
            steps=steps,
            created_at=datetime.now().isoformat(),
            success_criteria="; ".join(analysis.get("success_indicators", [])),
            preconditions="Valid user credentials; Network connectivity; System availability; Browser installed",
            error_handling="Retry on timeout; Flag low-confidence steps; Rollback on DB error"
        )

        return sop


# ============================================================
# Stage 5: ECM Mapping
# ============================================================
class ECMMapper:
    """Maps SOP steps to Enterprise Content Management systems."""

    def map_process(self, sop: SOPDocument, detected_systems: Dict) -> Dict[str, Any]:
        """Create ECM mapping from SOP and detected systems."""

        process_mapping = []
        for step in sop.steps:
            mapping = {
                "step_number": step.step_number,
                "step_title": step.title,
                "system_involved": step.system_involved,
                "action_type": step.action_type,
                "data_involved": self._extract_data_fields(step.description),
                "automatable": True,
                "complexity": self._assess_complexity(step)
            }
            process_mapping.append(mapping)

        # Detect system interactions
        interactions = self._detect_interactions(sop.steps)

        # Generate integration config
        integration_config = {}
        for sys in detected_systems.get("detected_systems", []):
            name = sys["name"]
            integration_config[name] = {
                "api_endpoint": f"https://api.enterprise.com/{name.lower().replace(' ', '-')}/v2",
                "authentication": "OAuth2 + SSO",
                "retry_policy": {"max_retries": 3, "backoff_factor": 1.5},
                "timeout_seconds": 30,
                "rate_limit": "100 req/min"
            }

        return {
            "sop_id": sop.id,
            "process_system_mapping": process_mapping,
            "system_interactions": interactions,
            "integration_config": integration_config,
            "total_automatable_steps": sum(1 for m in process_mapping if m["automatable"]),
            "automation_coverage": 1.0
        }

    def _extract_data_fields(self, description: str) -> List[str]:
        fields = []
        keywords = ["vendor", "material", "quantity", "date", "cost", "PO", "order",
                     "username", "password", "number", "email", "price"]
        desc_lower = description.lower()
        for kw in keywords:
            if kw.lower() in desc_lower:
                fields.append(kw.capitalize())
        return fields if fields else ["General"]

    def _assess_complexity(self, step: SOPStep) -> str:
        if step.action_type == "navigate":
            return "low"
        elif step.action_type == "input":
            return "medium" if step.duration < 15 else "high"
        else:
            return "low"

    def _detect_interactions(self, steps: List[SOPStep]) -> List[Dict]:
        systems_used = list({s.system_involved for s in steps})
        interactions = []
        for i, src in enumerate(systems_used):
            for tgt in systems_used[i+1:]:
                interactions.append({
                    "source_system": src,
                    "target_system": tgt,
                    "interaction_type": "data_transfer",
                    "bidirectional": False
                })
        return interactions


# ============================================================
# Stage 6: Code Generation (ADK / Selenium / Playwright)
# ============================================================
class CodeGenerator:
    """Generates automation code from SOP."""

    def generate(self, sop: SOPDocument, framework: str = "adk") -> Dict[str, str]:
        """Generate automation code files for the given framework."""

        if framework == "adk":
            return self._generate_adk(sop)
        elif framework == "selenium":
            return self._generate_selenium(sop)
        elif framework == "playwright":
            return self._generate_playwright(sop)
        else:
            raise ValueError(f"Unknown framework: {framework}")

    def _generate_adk(self, sop: SOPDocument) -> Dict[str, str]:
        safe_id = sop.id.replace("-", "_")
        class_name = "".join(w.capitalize() for w in sop.title.split()[:3]) + "Agent"

        # Agent file
        agent_code = textwrap.dedent(f'''\
            """Auto-generated ADK Agent: {sop.title}"""
            import asyncio
            from typing import Dict, Any
            from datetime import datetime

            class {class_name}:
                """Agent for: {sop.description[:80]}"""

                def __init__(self, config: Dict[str, Any] = None):
                    self.config = config or {{}}
                    self.sop_id = "{sop.id}"
                    self.execution_log = []

                async def execute(self) -> Dict[str, Any]:
                    """Execute the full automation workflow."""
                    start = datetime.now()
                    results = {{"steps": [], "status": "running"}}

                    try:
        ''')

        for step in sop.steps:
            agent_code += f'                results["steps"].append(await self.step_{step.step_number}())\n'

        agent_code += textwrap.dedent(f'''\
                        results["status"] = "completed"
                    except Exception as e:
                        results["status"] = "failed"
                        results["error"] = str(e)

                    results["duration"] = (datetime.now() - start).total_seconds()
                    return results
        ''')

        # Task methods
        for step in sop.steps:
            safe_title = step.title.lower().replace(" ", "_")[:30]
            agent_code += textwrap.dedent(f'''
                async def step_{step.step_number}(self) -> Dict[str, Any]:
                    """Step {step.step_number}: {step.title}"""
                    self.execution_log.append(f"Executing: {step.title}")
                    await asyncio.sleep(0.1)  # Simulate action
                    return {{
                        "step": {step.step_number},
                        "title": "{step.title}",
                        "status": "completed",
                        "action": "{step.action_type}",
                        "system": "{step.system_involved}",
                        "output": "{step.expected_output}"
                    }}
            ''')

        # Config file
        config_code = textwrap.dedent(f'''\
            """Configuration for {sop.title}"""

            SOP_CONFIG = {{
                "sop_id": "{sop.id}",
                "title": "{sop.title}",
                "version": "{sop.version}",
                "systems": {json.dumps(sop.systems_involved)},
                "total_steps": {len(sop.steps)},
                "success_criteria": "{sop.success_criteria[:100]}"
            }}

            EXECUTION_CONFIG = {{
                "timeout_seconds": 300,
                "retry_count": 3,
                "headless": True,
                "screenshot_on_error": True,
                "log_level": "INFO"
            }}

            VALIDATION_RULES = {{
                "match_threshold": 0.95,
                "strict_mode": False,
                "validate_screenshots": True
            }}
        ''')

        # Orchestration file
        orchestration_code = textwrap.dedent(f'''\
            """Orchestration for {sop.title}"""
            import asyncio
            from {safe_id}_agent import {class_name}

            async def execute_workflow(config=None):
                agent = {class_name}(config)
                result = await agent.execute()
                return result

            if __name__ == "__main__":
                result = asyncio.run(execute_workflow())
                print(f"Execution result: {{result['status']}}")
                for step in result.get("steps", []):
                    print(f"  Step {{step['step']}}: {{step['title']}} → {{step['status']}}")
        ''')

        return {
            f"{safe_id}_agent.py": agent_code,
            f"{safe_id}_config.py": config_code,
            f"{safe_id}_orchestration.py": orchestration_code,
            "_metadata": {
                "framework": "adk",
                "total_files": 3,
                "class_name": class_name,
                "total_lines": sum(c.count('\n') for c in [agent_code, config_code, orchestration_code])
            }
        }

    def _generate_selenium(self, sop: SOPDocument) -> Dict[str, str]:
        safe_id = sop.id.replace("-", "_")
        code = textwrap.dedent(f'''\
            """Selenium automation: {sop.title}"""
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time

            def run_automation():
                options = webdriver.ChromeOptions()
                options.add_argument("--headless")
                driver = webdriver.Chrome(options=options)

                try:
        ''')
        for step in sop.steps:
            code += f'        # Step {step.step_number}: {step.title}\n'
            code += f'        print("Executing: {step.title}")\n'
            if step.action_type == "navigate":
                code += f'        driver.get("https://example.com")\n'
            elif step.action_type == "input":
                code += f'        # driver.find_element(By.ID, "field").send_keys("value")\n'
            else:
                code += f'        # driver.find_element(By.ID, "button").click()\n'
            code += f'        time.sleep(1)\n\n'

        code += textwrap.dedent('''\
                    return {"status": "completed"}
                except Exception as e:
                    return {"status": "failed", "error": str(e)}
                finally:
                    driver.quit()

            if __name__ == "__main__":
                result = run_automation()
                print(f"Result: {result['status']}")
        ''')

        return {
            f"{safe_id}_selenium.py": code,
            "_metadata": {"framework": "selenium", "total_files": 1}
        }

    def _generate_playwright(self, sop: SOPDocument) -> Dict[str, str]:
        safe_id = sop.id.replace("-", "_")
        code = textwrap.dedent(f'''\
            """Playwright automation: {sop.title}"""
            import asyncio
            from playwright.async_api import async_playwright

            async def run_automation():
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()

                    try:
        ''')
        for step in sop.steps:
            code += f'            # Step {step.step_number}: {step.title}\n'
            code += f'            print("Executing: {step.title}")\n'
            if step.action_type == "navigate":
                code += f'            await page.goto("https://example.com")\n'
            elif step.action_type == "input":
                code += f'            # await page.fill("#field", "value")\n'
            else:
                code += f'            # await page.click("#button")\n'
            code += f'            await page.wait_for_timeout(1000)\n\n'

        code += textwrap.dedent('''\
                        return {"status": "completed"}
                    except Exception as e:
                        return {"status": "failed", "error": str(e)}
                    finally:
                        await browser.close()

            if __name__ == "__main__":
                result = asyncio.run(run_automation())
                print(f"Result: {result['status']}")
        ''')

        return {
            f"{safe_id}_playwright.py": code,
            "_metadata": {"framework": "playwright", "total_files": 1}
        }


# ============================================================
# Stage 7: Execution Engine (Simulated)
# ============================================================
class ExecutionEngine:
    """Simulates execution of generated automation code."""

    def execute(self, sop: SOPDocument, generated_code: Dict[str, str],
                framework: str = "adk") -> Dict[str, Any]:
        """Execute the generated code (simulation mode)."""

        execution_id = f"exec-{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        # Write code files to temp directory
        exec_dir = tempfile.mkdtemp(prefix=f"qa_exec_{execution_id}_")
        files_written = []
        for filename, content in generated_code.items():
            if filename.startswith("_"):
                continue
            filepath = os.path.join(exec_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
            files_written.append(filepath)

        # Simulate step-by-step execution
        step_results = []
        for step in sop.steps:
            step_start = time.time()
            time.sleep(0.05)  # Simulate execution time

            # 95% chance of success per step for realistic simulation
            import random
            step_success = random.random() < 0.95

            step_results.append({
                "step_number": step.step_number,
                "title": step.title,
                "status": "completed" if step_success else "failed",
                "action_type": step.action_type,
                "system": step.system_involved,
                "output": step.expected_output if step_success else "Element not found",
                "duration_seconds": time.time() - step_start,
                "screenshot": f"screenshot_step_{step.step_number}.png"
            })

        total_duration = time.time() - start_time
        passed = sum(1 for s in step_results if s["status"] == "completed")
        total = len(step_results)

        return {
            "execution_id": execution_id,
            "sop_id": sop.id,
            "framework": framework,
            "status": "completed" if passed == total else "partial",
            "start_time": datetime.fromtimestamp(start_time).isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_duration_seconds": total_duration,
            "step_results": step_results,
            "total_steps": total,
            "passed_steps": passed,
            "failed_steps": total - passed,
            "success_rate": passed / max(total, 1),
            "execution_directory": exec_dir,
            "files_written": files_written,
            "logs": [
                f"[{datetime.now().isoformat()}] Starting execution: {sop.id}",
                f"[{datetime.now().isoformat()}] Framework: {framework}",
                *[f"[{datetime.now().isoformat()}] Step {s['step_number']}: {s['title']} → {s['status']}" for s in step_results],
                f"[{datetime.now().isoformat()}] Execution complete: {passed}/{total} steps passed"
            ]
        }


# ============================================================
# Stage 8: Validation Engine
# ============================================================
class ValidationEngine:
    """Validates execution results against SOP expectations."""

    def __init__(self, match_threshold: float = 0.8):
        self.match_threshold = match_threshold

    def validate(self, sop: SOPDocument, execution_result: Dict) -> ValidationReport:
        """Validate execution results against SOP."""

        validation_id = f"val-{uuid.uuid4().hex[:8]}"
        start_time = time.time()

        validation_steps = []
        step_results = execution_result.get("step_results", [])

        for sop_step in sop.steps:
            # Find matching execution step
            exec_step = next(
                (s for s in step_results if s["step_number"] == sop_step.step_number),
                None
            )

            if exec_step is None:
                validation_steps.append(ValidationStep(
                    step_number=sop_step.step_number,
                    title=sop_step.title,
                    status=ValidationStatus.FAILED,
                    expected=sop_step.expected_output,
                    actual="No execution data",
                    match_score=0.0
                ))
                continue

            # Compare expected vs actual output
            expected = sop_step.expected_output
            actual = exec_step.get("output", "")

            match_score = self._calculate_match(expected, actual)
            exec_passed = exec_step.get("status") == "completed"

            if exec_passed and match_score >= self.match_threshold:
                status = ValidationStatus.PASSED
            elif exec_passed and match_score >= 0.5:
                status = ValidationStatus.PARTIAL
            else:
                status = ValidationStatus.FAILED

            validation_steps.append(ValidationStep(
                step_number=sop_step.step_number,
                title=sop_step.title,
                status=status,
                expected=expected,
                actual=actual,
                match_score=match_score,
                duration=exec_step.get("duration_seconds", 0)
            ))

        # Calculate totals
        passed = sum(1 for v in validation_steps if v.status == ValidationStatus.PASSED)
        failed = sum(1 for v in validation_steps if v.status == ValidationStatus.FAILED)
        total = len(validation_steps)
        success_rate = passed / max(total, 1)

        # Determine overall status
        if success_rate >= 0.95:
            overall = ValidationStatus.PASSED
        elif success_rate >= 0.5:
            overall = ValidationStatus.PARTIAL
        else:
            overall = ValidationStatus.FAILED

        # Generate recommendations
        recommendations = []
        for vs in validation_steps:
            if vs.status == ValidationStatus.FAILED:
                recommendations.append(f"Step {vs.step_number} ({vs.title}): Review element selectors and add explicit waits")
            elif vs.status == ValidationStatus.PARTIAL:
                recommendations.append(f"Step {vs.step_number} ({vs.title}): Output partially matched ({vs.match_score:.0%}) — verify expected values")

        if not recommendations:
            recommendations.append("All steps passed validation. Consider adding edge case tests.")

        total_duration = time.time() - start_time

        return ValidationReport(
            id=validation_id,
            sop_id=sop.id,
            execution_id=execution_result["execution_id"],
            overall_status=overall,
            total_steps=total,
            passed_steps=passed,
            failed_steps=failed,
            success_rate=success_rate,
            validation_steps=validation_steps,
            start_time=datetime.fromtimestamp(start_time).isoformat(),
            end_time=datetime.now().isoformat(),
            total_duration=total_duration,
            recommendations=recommendations
        )

    def _calculate_match(self, expected: str, actual: str) -> float:
        if not expected and not actual:
            return 1.0
        if not expected or not actual:
            return 0.0
        return SequenceMatcher(None, expected.lower(), actual.lower()).ratio()


# ============================================================
# Pipeline Orchestrator
# ============================================================
class PipelineOrchestrator:
    """Orchestrates the complete E2E pipeline."""

    def __init__(self):
        self.uploader = VideoUploader()
        self.analyzer = VideoAnalyzer()
        self.detector = SystemDetector()
        self.sop_gen = SOPGenerator()
        self.ecm_mapper = ECMMapper()
        self.code_gen = CodeGenerator()
        self.executor = ExecutionEngine()
        self.validator = ValidationEngine()

        self.results = {}

    def run(self, video_filename: str = "sap_po_creation.mp4",
            framework: str = "adk", detail_level: str = "detailed") -> Dict[str, Any]:
        """Run the complete E2E pipeline."""

        pipeline_start = time.time()
        pipeline_id = f"pipeline-{uuid.uuid4().hex[:8]}"

        banner(f"E2E Pipeline Simulation: {pipeline_id}")
        print(f"  Video: {video_filename}")
        print(f"  Framework: {framework}")
        print(f"  Detail Level: {detail_level}")

        # ── Stage 1: Upload ──
        stage_header(1, "Video Upload")
        try:
            upload = self.uploader.upload(video_filename)
            self.results["upload"] = upload
            success(f"Video uploaded: {upload['video_id']}")
            info(f"File size: {upload['size_bytes']:,} bytes")
            info(f"Stored at: {upload['filepath']}")
        except Exception as e:
            fail(f"Upload failed: {e}")
            return self._build_result(pipeline_id, pipeline_start, "failed", str(e))

        # ── Stage 2: Analysis ──
        stage_header(2, "Video Analysis (Gemini Simulation)")
        try:
            t0 = time.time()
            analysis = self.analyzer.analyze(upload["video_id"], upload["filepath"])
            self.results["analysis"] = analysis
            success(f"Analysis complete in {time.time()-t0:.2f}s")
            info(f"Video duration: {analysis['video_duration_seconds']}s")
            info(f"Frames analyzed: {analysis['frames_analyzed']}")
            info(f"Workflow steps found: {len(analysis['workflow_steps'])}")
            info(f"Systems detected: {len(analysis['systems_detected'])}")
            info(f"Data patterns: {len(analysis['data_extraction_patterns'])}")

            print(f"\n  {C.DIM}Workflow Steps:{C.END}")
            for step in analysis["workflow_steps"]:
                print(f"    {step['step_number']}. {step['title']} [{step['action_type']}] → {step['system']}")

        except Exception as e:
            fail(f"Analysis failed: {e}")
            traceback.print_exc()
            return self._build_result(pipeline_id, pipeline_start, "failed", str(e))

        # ── Stage 3: System Detection ──
        stage_header(3, "System Detection & Classification")
        try:
            systems = self.detector.detect(analysis, upload["video_id"])
            self.results["systems"] = systems
            success(f"Detected {systems['total_systems_found']} systems (threshold: 0.7)")

            for sys in systems["detected_systems"]:
                conf_bar = "█" * int(sys["confidence"] * 20) + "░" * (20 - int(sys["confidence"] * 20))
                print(f"    {C.CYAN}{sys['name']:<25}{C.END} [{conf_bar}] {sys['confidence']:.0%}  ({sys['system_type']})")

            info(f"Detected workflows: {', '.join(systems['detected_workflows'])}")

        except Exception as e:
            fail(f"System detection failed: {e}")
            traceback.print_exc()
            return self._build_result(pipeline_id, pipeline_start, "failed", str(e))

        # ── Stage 4: SOP Generation ──
        stage_header(4, "SOP Generation")
        try:
            sop = self.sop_gen.generate(
                upload["video_id"], analysis, systems, detail_level
            )
            self.results["sop"] = sop
            success(f"SOP generated: {sop.id}")
            info(f"Title: {sop.title}")
            info(f"Steps: {len(sop.steps)}")
            info(f"Systems: {', '.join(sop.systems_involved)}")
            info(f"Success criteria: {sop.success_criteria[:80]}...")

            print(f"\n  {C.DIM}SOP Steps:{C.END}")
            for step in sop.steps:
                print(f"    {step.step_number}. [{step.action_type:>8}] {step.title}")
                print(f"       → Expected: {step.expected_output}")

        except Exception as e:
            fail(f"SOP generation failed: {e}")
            traceback.print_exc()
            return self._build_result(pipeline_id, pipeline_start, "failed", str(e))

        # ── Stage 5: ECM Mapping ──
        stage_header(5, "ECM Mapping")
        try:
            ecm = self.ecm_mapper.map_process(sop, systems)
            self.results["ecm"] = ecm
            success(f"ECM mapping complete for {sop.id}")
            info(f"Automatable steps: {ecm['total_automatable_steps']}/{len(sop.steps)}")
            info(f"Automation coverage: {ecm['automation_coverage']:.0%}")

            if ecm["system_interactions"]:
                info(f"System interactions:")
                for ix in ecm["system_interactions"]:
                    print(f"      {ix['source_system']} → {ix['target_system']} ({ix['interaction_type']})")

            info(f"Integration configs: {', '.join(ecm['integration_config'].keys())}")

        except Exception as e:
            fail(f"ECM mapping failed: {e}")
            traceback.print_exc()
            return self._build_result(pipeline_id, pipeline_start, "failed", str(e))

        # ── Stage 6: Code Generation ──
        stage_header(6, f"Code Generation ({framework.upper()})")
        try:
            code = self.code_gen.generate(sop, framework)
            self.results["code"] = code

            metadata = code.get("_metadata", {})
            success(f"Generated {metadata.get('total_files', '?')} code files ({framework})")
            info(f"Total lines: ~{metadata.get('total_lines', '?')}")

            for filename, content in code.items():
                if filename.startswith("_"):
                    continue
                lines = content.count('\n')
                print(f"    📄 {filename} ({lines} lines)")

            if framework == "adk":
                info(f"Agent class: {metadata.get('class_name', '?')}")

        except Exception as e:
            fail(f"Code generation failed: {e}")
            traceback.print_exc()
            return self._build_result(pipeline_id, pipeline_start, "failed", str(e))

        # ── Stage 7: Execution ──
        stage_header(7, "Execution Engine (Simulated)")
        try:
            execution = self.executor.execute(sop, code, framework)
            self.results["execution"] = execution

            status_color = C.GREEN if execution["status"] == "completed" else C.YELLOW
            success(f"Execution {execution['execution_id']}: {status_color}{execution['status']}{C.END}")
            info(f"Duration: {execution['total_duration_seconds']:.2f}s")
            info(f"Steps: {execution['passed_steps']}/{execution['total_steps']} passed ({execution['success_rate']:.0%})")
            info(f"Files written to: {execution['execution_directory']}")

            print(f"\n  {C.DIM}Step Results:{C.END}")
            for sr in execution["step_results"]:
                icon = f"{C.GREEN}✓{C.END}" if sr["status"] == "completed" else f"{C.RED}✗{C.END}"
                print(f"    {icon} Step {sr['step_number']}: {sr['title']} → {sr['output'][:50]}")

        except Exception as e:
            fail(f"Execution failed: {e}")
            traceback.print_exc()
            return self._build_result(pipeline_id, pipeline_start, "failed", str(e))

        # ── Stage 8: Validation ──
        stage_header(8, "Validation Engine")
        try:
            report = self.validator.validate(sop, execution)
            self.results["validation"] = report

            status_color = {
                ValidationStatus.PASSED: C.GREEN,
                ValidationStatus.PARTIAL: C.YELLOW,
                ValidationStatus.FAILED: C.RED
            }.get(report.overall_status, C.END)

            success(f"Validation {report.id}: {status_color}{report.overall_status.value.upper()}{C.END}")
            info(f"Success rate: {report.success_rate:.0%} ({report.passed_steps}/{report.total_steps} steps)")
            info(f"Duration: {report.total_duration:.3f}s")

            print(f"\n  {C.DIM}Validation Details:{C.END}")
            for vs in report.validation_steps:
                if vs.status == ValidationStatus.PASSED:
                    icon = f"{C.GREEN}✓{C.END}"
                elif vs.status == ValidationStatus.PARTIAL:
                    icon = f"{C.YELLOW}~{C.END}"
                else:
                    icon = f"{C.RED}✗{C.END}"

                print(f"    {icon} Step {vs.step_number}: {vs.title}")
                print(f"      Match: {vs.match_score:.0%}  |  Expected: {vs.expected[:40]}  |  Actual: {vs.actual[:40]}")

            if report.recommendations:
                print(f"\n  {C.DIM}Recommendations:{C.END}")
                for rec in report.recommendations:
                    print(f"    → {rec}")

        except Exception as e:
            fail(f"Validation failed: {e}")
            traceback.print_exc()
            return self._build_result(pipeline_id, pipeline_start, "failed", str(e))

        # ── Summary ──
        total_duration = time.time() - pipeline_start
        return self._build_result(pipeline_id, pipeline_start, "success", total_duration=total_duration)

    def _build_result(self, pipeline_id, start_time, status, error=None, total_duration=None):
        if total_duration is None:
            total_duration = time.time() - start_time

        result = {
            "pipeline_id": pipeline_id,
            "status": status,
            "total_duration_seconds": total_duration,
            "stages_completed": len(self.results),
            "stages": {k: "ok" for k in self.results},
        }

        if error:
            result["error"] = error

        # Print summary
        banner("Pipeline Summary")

        stages = [
            ("Upload", "upload"),
            ("Analysis", "analysis"),
            ("Detection", "systems"),
            ("SOP Generation", "sop"),
            ("ECM Mapping", "ecm"),
            ("Code Generation", "code"),
            ("Execution", "execution"),
            ("Validation", "validation")
        ]

        for label, key in stages:
            if key in self.results:
                print(f"  {C.GREEN}✓{C.END} {label}")
            else:
                print(f"  {C.RED}✗{C.END} {label}")

        print(f"\n  Status: {C.GREEN if status == 'success' else C.RED}{status.upper()}{C.END}")
        print(f"  Total Duration: {total_duration:.2f}s")
        print(f"  Pipeline ID: {pipeline_id}")

        if "validation" in self.results:
            report = self.results["validation"]
            print(f"\n  {C.BOLD}Final Validation:{C.END}")
            print(f"    Overall: {report.overall_status.value.upper()}")
            print(f"    Success Rate: {report.success_rate:.0%}")
            print(f"    Passed: {report.passed_steps}/{report.total_steps}")

        return result


# ============================================================
# Multi-Framework Test
# ============================================================
def run_multi_framework_test():
    """Run the pipeline with all three frameworks and compare."""

    banner("Multi-Framework Comparison Test")

    frameworks = ["adk", "selenium", "playwright"]
    results = {}

    for fw in frameworks:
        print(f"\n{C.BOLD}━━━ Testing {fw.upper()} Framework ━━━{C.END}")
        orchestrator = PipelineOrchestrator()
        result = orchestrator.run(
            video_filename=f"sap_po_creation_{fw}.mp4",
            framework=fw,
            detail_level="detailed"
        )
        results[fw] = {
            "status": result["status"],
            "duration": result["total_duration_seconds"],
            "stages_completed": result["stages_completed"],
            "validation": orchestrator.results.get("validation")
        }

    # Comparison table
    banner("Framework Comparison Results")

    print(f"  {'Framework':<15} {'Status':<12} {'Duration':<12} {'Stages':<10} {'Validation':<15} {'Success Rate'}")
    print(f"  {'─'*15} {'─'*12} {'─'*12} {'─'*10} {'─'*15} {'─'*12}")

    for fw, res in results.items():
        val = res.get("validation")
        val_status = val.overall_status.value if val else "N/A"
        val_rate = f"{val.success_rate:.0%}" if val else "N/A"

        status_color = C.GREEN if res["status"] == "success" else C.RED
        print(f"  {fw.upper():<15} {status_color}{res['status']:<12}{C.END} {res['duration']:<12.2f} {res['stages_completed']:<10} {val_status:<15} {val_rate}")

    return results


# ============================================================
# Data Export Test
# ============================================================
def run_export_test(orchestrator: PipelineOrchestrator, output_dir: str):
    """Export all pipeline artifacts to files."""

    banner("Exporting Pipeline Artifacts")
    os.makedirs(output_dir, exist_ok=True)

    # Export analysis results
    if "analysis" in orchestrator.results:
        path = os.path.join(output_dir, "1_video_analysis.json")
        with open(path, 'w') as f:
            json.dump(orchestrator.results["analysis"], f, indent=2, default=str)
        success(f"Video analysis → {path}")

    # Export system detection
    if "systems" in orchestrator.results:
        path = os.path.join(output_dir, "2_systems_detected.json")
        with open(path, 'w') as f:
            json.dump(orchestrator.results["systems"], f, indent=2, default=str)
        success(f"Systems detected → {path}")

    # Export SOP
    if "sop" in orchestrator.results:
        sop = orchestrator.results["sop"]
        sop_dict = {
            "id": sop.id, "title": sop.title, "description": sop.description,
            "version": sop.version, "video_source_id": sop.video_source_id,
            "systems_involved": sop.systems_involved,
            "steps": [
                {"step_number": s.step_number, "title": s.title, "description": s.description,
                 "system_involved": s.system_involved, "action_type": s.action_type,
                 "element_identifier": s.element_identifier, "expected_output": s.expected_output,
                 "timestamp": s.timestamp, "duration": s.duration}
                for s in sop.steps
            ],
            "success_criteria": sop.success_criteria,
            "preconditions": sop.preconditions,
            "error_handling": sop.error_handling,
            "created_at": sop.created_at
        }
        path = os.path.join(output_dir, "3_sop_document.json")
        with open(path, 'w') as f:
            json.dump(sop_dict, f, indent=2, default=str)
        success(f"SOP document → {path}")

        # Also export as markdown
        md_path = os.path.join(output_dir, "3_sop_document.md")
        with open(md_path, 'w') as f:
            f.write(f"# {sop.title}\n\n")
            f.write(f"**ID:** {sop.id}  \n")
            f.write(f"**Version:** {sop.version}  \n")
            f.write(f"**Systems:** {', '.join(sop.systems_involved)}  \n\n")
            f.write(f"## Description\n{sop.description}\n\n")
            f.write(f"## Preconditions\n{sop.preconditions}\n\n")
            f.write(f"## Steps\n\n")
            f.write(f"| # | Action | Title | System | Expected Output |\n")
            f.write(f"|---|--------|-------|--------|----------------|\n")
            for s in sop.steps:
                f.write(f"| {s.step_number} | {s.action_type} | {s.title} | {s.system_involved} | {s.expected_output} |\n")
            f.write(f"\n## Success Criteria\n{sop.success_criteria}\n")
            f.write(f"\n## Error Handling\n{sop.error_handling}\n")
        success(f"SOP markdown → {md_path}")

    # Export ECM mapping
    if "ecm" in orchestrator.results:
        path = os.path.join(output_dir, "4_ecm_mapping.json")
        with open(path, 'w') as f:
            json.dump(orchestrator.results["ecm"], f, indent=2, default=str)
        success(f"ECM mapping → {path}")

    # Export generated code
    if "code" in orchestrator.results:
        code_dir = os.path.join(output_dir, "5_generated_code")
        os.makedirs(code_dir, exist_ok=True)
        for filename, content in orchestrator.results["code"].items():
            if filename.startswith("_"):
                continue
            path = os.path.join(code_dir, filename)
            with open(path, 'w') as f:
                f.write(content)
            success(f"Code file → {path}")

    # Export execution results
    if "execution" in orchestrator.results:
        path = os.path.join(output_dir, "6_execution_results.json")
        with open(path, 'w') as f:
            json.dump(orchestrator.results["execution"], f, indent=2, default=str)
        success(f"Execution results → {path}")

    # Export validation report
    if "validation" in orchestrator.results:
        report = orchestrator.results["validation"]
        val_dict = {
            "id": report.id, "sop_id": report.sop_id, "execution_id": report.execution_id,
            "overall_status": report.overall_status.value,
            "total_steps": report.total_steps, "passed_steps": report.passed_steps,
            "failed_steps": report.failed_steps, "success_rate": report.success_rate,
            "validation_steps": [
                {"step_number": v.step_number, "title": v.title, "status": v.status.value,
                 "expected": v.expected, "actual": v.actual, "match_score": v.match_score}
                for v in report.validation_steps
            ],
            "total_duration": report.total_duration,
            "recommendations": report.recommendations
        }
        path = os.path.join(output_dir, "7_validation_report.json")
        with open(path, 'w') as f:
            json.dump(val_dict, f, indent=2, default=str)
        success(f"Validation report → {path}")

    file_count = sum(1 for _, _, files in os.walk(output_dir) for f in files)
    info(f"Total exported files: {file_count}")
    info(f"Output directory: {output_dir}")


# ============================================================
# Unit Tests for Individual Components
# ============================================================
def run_unit_tests():
    """Run unit tests for each pipeline component."""

    banner("Unit Tests")

    tests_passed = 0
    tests_failed = 0

    def assert_test(name, condition, detail=""):
        nonlocal tests_passed, tests_failed
        if condition:
            success(f"[PASS] {name}")
            tests_passed += 1
        else:
            fail(f"[FAIL] {name} — {detail}")
            tests_failed += 1

    # Test 1: Video Upload
    print(f"\n  {C.BOLD}VideoUploader Tests{C.END}")
    uploader = VideoUploader()
    result = uploader.upload("test_video.mp4")
    assert_test("Upload returns success", result["success"])
    assert_test("Video ID generated", result["video_id"].startswith("video-"))
    assert_test("File created on disk", os.path.exists(result["filepath"]))
    assert_test("File has correct size", result["size_bytes"] == 102400)

    # Test 2: Video Analysis
    print(f"\n  {C.BOLD}VideoAnalyzer Tests{C.END}")
    analyzer = VideoAnalyzer()
    analysis = analyzer.analyze("test-id", result["filepath"])
    assert_test("Analysis returns success", analysis["success"])
    assert_test("Has workflow steps", len(analysis["workflow_steps"]) == 5)
    assert_test("Has systems detected", len(analysis["systems_detected"]) >= 2)
    assert_test("Has data patterns", len(analysis["data_extraction_patterns"]) >= 3)
    assert_test("Steps are sequential", all(
        analysis["workflow_steps"][i]["step_number"] == i+1
        for i in range(len(analysis["workflow_steps"]))
    ))
    assert_test("All steps have expected_output", all(
        s.get("expected_output") for s in analysis["workflow_steps"]
    ))

    # Test 3: System Detection
    print(f"\n  {C.BOLD}SystemDetector Tests{C.END}")
    detector = SystemDetector()
    systems = detector.detect(analysis, "test-id")
    assert_test("Systems found", systems["total_systems_found"] >= 2)
    assert_test("Confidence threshold applied", all(
        s["confidence"] >= 0.7 for s in systems["detected_systems"]
    ))
    assert_test("SAP detected as ERP", any(
        s["name"] == "SAP ERP" and s["system_type"] == "erp"
        for s in systems["detected_systems"]
    ))
    assert_test("Workflows detected", len(systems["detected_workflows"]) > 0)

    # Test 4: SOP Generation
    print(f"\n  {C.BOLD}SOPGenerator Tests{C.END}")
    sop_gen = SOPGenerator()
    sop = sop_gen.generate("test-id", analysis, systems, "detailed")
    assert_test("SOP ID generated", sop.id.startswith("sop-"))
    assert_test("SOP has title", len(sop.title) > 0)
    assert_test("SOP has steps", len(sop.steps) == 5)
    assert_test("Steps have action types", all(s.action_type for s in sop.steps))
    assert_test("Steps have expected outputs", all(s.expected_output for s in sop.steps))
    assert_test("SOP has success criteria", len(sop.success_criteria) > 0)
    assert_test("SOP has preconditions", len(sop.preconditions) > 0)

    # Test 5: ECM Mapping
    print(f"\n  {C.BOLD}ECMMapper Tests{C.END}")
    ecm = ECMMapper()
    mapping = ecm.map_process(sop, systems)
    assert_test("Has process mapping", len(mapping["process_system_mapping"]) == 5)
    assert_test("All steps automatable", mapping["total_automatable_steps"] == 5)
    assert_test("Has integration config", len(mapping["integration_config"]) > 0)
    assert_test("Complexity assessed", all(
        m["complexity"] in ("low", "medium", "high")
        for m in mapping["process_system_mapping"]
    ))

    # Test 6: Code Generation
    print(f"\n  {C.BOLD}CodeGenerator Tests{C.END}")
    codegen = CodeGenerator()

    # ADK
    adk_code = codegen.generate(sop, "adk")
    assert_test("ADK generates 3 files", adk_code["_metadata"]["total_files"] == 3)
    assert_test("ADK agent file exists", any("_agent.py" in k for k in adk_code))
    assert_test("ADK config file exists", any("_config.py" in k for k in adk_code))
    assert_test("ADK has class definition", "class " in list(v for k,v in adk_code.items() if "_agent.py" in k)[0])

    # Selenium
    sel_code = codegen.generate(sop, "selenium")
    assert_test("Selenium generates code", sel_code["_metadata"]["total_files"] == 1)
    assert_test("Selenium imports webdriver", "selenium" in list(sel_code.values())[0])

    # Playwright
    pw_code = codegen.generate(sop, "playwright")
    assert_test("Playwright generates code", pw_code["_metadata"]["total_files"] == 1)
    assert_test("Playwright uses async", "async" in list(pw_code.values())[0])

    # Test 7: Execution
    print(f"\n  {C.BOLD}ExecutionEngine Tests{C.END}")
    engine = ExecutionEngine()
    exec_result = engine.execute(sop, adk_code, "adk")
    assert_test("Execution ID generated", exec_result["execution_id"].startswith("exec-"))
    assert_test("Has step results", len(exec_result["step_results"]) == 5)
    assert_test("Has execution logs", len(exec_result["logs"]) > 0)
    assert_test("Duration is positive", exec_result["total_duration_seconds"] > 0)
    assert_test("Files written to disk", len(exec_result["files_written"]) > 0)
    assert_test("Success rate calculated", 0 <= exec_result["success_rate"] <= 1)

    # Test 8: Validation
    print(f"\n  {C.BOLD}ValidationEngine Tests{C.END}")
    validator = ValidationEngine()
    report = validator.validate(sop, exec_result)
    assert_test("Validation ID generated", report.id.startswith("val-"))
    assert_test("Has validation steps", len(report.validation_steps) == 5)
    assert_test("Total steps correct", report.total_steps == 5)
    assert_test("Passed + Failed = Total", report.passed_steps + report.failed_steps == report.total_steps)
    assert_test("Success rate in range", 0 <= report.success_rate <= 1)
    assert_test("Has recommendations", len(report.recommendations) > 0)
    assert_test("Duration tracked", report.total_duration > 0)

    # Test 9: Match Calculation
    print(f"\n  {C.BOLD}Match Calculation Tests{C.END}")
    v = ValidationEngine()
    assert_test("Exact match = 1.0", v._calculate_match("hello", "hello") == 1.0)
    assert_test("Empty match = 1.0", v._calculate_match("", "") == 1.0)
    assert_test("Partial match > 0.5", v._calculate_match("PO created", "PO created successfully") > 0.5)
    assert_test("No match < 0.3", v._calculate_match("hello", "xyz") < 0.3)
    assert_test("Case insensitive", v._calculate_match("Hello", "hello") == 1.0)

    # Summary
    total = tests_passed + tests_failed
    print(f"\n  {C.BOLD}{'─'*50}{C.END}")
    print(f"  Tests: {C.GREEN}{tests_passed} passed{C.END}, {C.RED if tests_failed else C.DIM}{tests_failed} failed{C.END}, {total} total")

    if tests_failed == 0:
        print(f"\n  {C.GREEN}{C.BOLD}ALL TESTS PASSED ✓{C.END}")
    else:
        print(f"\n  {C.YELLOW}{C.BOLD}SOME TESTS FAILED{C.END}")

    return tests_passed, tests_failed


# ============================================================
# Main Entry Point
# ============================================================
if __name__ == "__main__":
    import random
    random.seed(42)  # Reproducible results

    OUTPUT_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "test_output"
    )

    banner("AI-Powered QA Automation Platform")
    print(f"  {C.DIM}End-to-End Simulation Test Suite{C.END}")
    print(f"  {C.DIM}Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.END}")

    # ── Part 1: Unit Tests ──
    passed, failed = run_unit_tests()

    # ── Part 2: E2E Pipeline (ADK) ──
    orchestrator = PipelineOrchestrator()
    pipeline_result = orchestrator.run(
        video_filename="sap_purchase_order_demo.mp4",
        framework="adk",
        detail_level="detailed"
    )

    # ── Part 3: Export Artifacts ──
    run_export_test(orchestrator, OUTPUT_DIR)

    # ── Part 4: Multi-Framework Test ──
    fw_results = run_multi_framework_test()

    # ── Final Summary ──
    banner("FINAL TEST RESULTS")
    print(f"  {C.BOLD}Unit Tests:{C.END}          {C.GREEN}{passed} passed{C.END}, {C.RED if failed else C.DIM}{failed} failed{C.END}")
    print(f"  {C.BOLD}E2E Pipeline:{C.END}        {C.GREEN if pipeline_result['status'] == 'success' else C.RED}{pipeline_result['status'].upper()}{C.END} ({pipeline_result['total_duration_seconds']:.2f}s)")
    print(f"  {C.BOLD}Data Export:{C.END}          {C.GREEN}Complete{C.END} → {OUTPUT_DIR}")
    print(f"  {C.BOLD}Multi-Framework:{C.END}      ", end="")
    for fw, res in fw_results.items():
        color = C.GREEN if res["status"] == "success" else C.RED
        print(f"{fw.upper()}: {color}{res['status']}{C.END}  ", end="")
    print()

    total_ok = (
        failed == 0 and
        pipeline_result["status"] == "success" and
        all(r["status"] == "success" for r in fw_results.values())
    )

    if total_ok:
        print(f"\n  {C.GREEN}{C.BOLD}{'='*50}")
        print(f"  ALL TESTS PASSED — PLATFORM READY ✓")
        print(f"  {'='*50}{C.END}")
    else:
        print(f"\n  {C.YELLOW}{C.BOLD}SOME TESTS HAD ISSUES — REVIEW ABOVE{C.END}")

    print()
