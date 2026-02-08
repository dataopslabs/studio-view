"""
SOP (Standard Operating Procedure) generation service.
Converts video analysis results into structured SOP documents.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4
from models.sop import SOPDocument, SOPStep

logger = logging.getLogger(__name__)


class SOPGenerator:
    """
    Generates structured Standard Operating Procedure documents from video analysis.
    Creates detailed, step-by-step instructions with system information and validation criteria.
    """

    def __init__(self):
        """Initialize the SOP generator."""
        logger.info("SOP generator initialized")

    def generate_sop(
        self,
        video_id: str,
        video_analysis: Dict[str, Any],
        systems_detected: List[str],
        detail_level: str = "detailed",
    ) -> Optional[SOPDocument]:
        """
        Generate an SOP document from video analysis.

        Args:
            video_id: ID of the source video
            video_analysis: Results from video analyzer
            systems_detected: List of detected system names
            detail_level: Level of detail (summary, detailed, expert)

        Returns:
            SOPDocument object or None if generation fails
        """
        logger.info(
            f"Generating SOP from video {video_id} with detail level: {detail_level}"
        )

        if not video_analysis.get("success"):
            logger.error("Cannot generate SOP from failed video analysis")
            return None

        try:
            # Extract workflow steps from analysis
            workflow_steps = video_analysis.get("workflow_steps", [])
            sop_steps = self._create_sop_steps(workflow_steps, detail_level)

            # Generate SOP metadata
            title = self._generate_title(video_analysis)
            description = self._generate_description(video_analysis, detail_level)

            # Create SOP document
            sop = SOPDocument(
                id=f"sop-{uuid4().hex[:8]}",
                title=title,
                description=description,
                version="1.0",
                created_at=datetime.utcnow(),
                video_source_id=video_id,
                systems_involved=systems_detected,
                steps=sop_steps,
                execution_time_estimate=self._calculate_execution_time(sop_steps),
                success_criteria=self._generate_success_criteria(video_analysis),
                preconditions=self._generate_preconditions(systems_detected),
                postconditions=self._generate_postconditions(video_analysis),
                error_handling=self._generate_error_handling(sop_steps),
                notes=self._generate_notes(video_analysis, detail_level),
            )

            logger.info(f"SOP generated successfully: {sop.id}")
            return sop

        except Exception as e:
            logger.error(f"Error generating SOP: {str(e)}")
            return None

    def _create_sop_steps(
        self, workflow_steps: List[Dict[str, Any]], detail_level: str
    ) -> List[SOPStep]:
        """
        Create SOPStep objects from workflow steps.

        Args:
            workflow_steps: Raw workflow steps from analysis
            detail_level: Level of detail for steps

        Returns:
            List of SOPStep objects
        """
        sop_steps = []

        for step in workflow_steps:
            sop_step = SOPStep(
                step_number=step.get("step_number", 0),
                title=step.get("title", "Unknown Step"),
                description=self._enhance_description(
                    step.get("description", ""), detail_level
                ),
                system_involved=step.get("system", "Unknown System"),
                action_type=step.get("action_type", "click"),
                element_identifier=self._generate_element_identifier(step),
                expected_output=self._generate_expected_output(step),
                timestamp=step.get("timestamp"),
                duration=step.get("duration"),
            )
            sop_steps.append(sop_step)

        return sop_steps

    def _enhance_description(self, base_description: str, detail_level: str) -> str:
        """
        Enhance step description based on detail level.

        Args:
            base_description: Original description
            detail_level: Level of detail to add

        Returns:
            Enhanced description
        """
        if detail_level == "summary":
            return base_description[:100] + "..." if len(base_description) > 100 else base_description

        elif detail_level == "expert":
            return (
                f"{base_description}\n\n"
                "Technical Details:\n"
                "- Verify system state before proceeding\n"
                "- Check browser console for errors\n"
                "- Validate network requests if applicable"
            )

        return base_description

    def _generate_element_identifier(self, step: Dict[str, Any]) -> Optional[str]:
        """
        Generate element identifier (XPath, CSS selector, etc.) from step.

        Args:
            step: Workflow step data

        Returns:
            Element identifier string or None
        """
        ui_elements = step.get("ui_elements", [])
        if not ui_elements:
            return None

        # Generate XPath-like identifier from UI elements
        primary_element = ui_elements[0]
        system = step.get("system", "").lower().replace(" ", "_")

        # Create a simplified element identifier
        return f"//div[@class='{system}']//button[contains(text(), '{primary_element}')]"

    def _generate_expected_output(self, step: Dict[str, Any]) -> Optional[str]:
        """
        Generate expected output for a step.

        Args:
            step: Workflow step data

        Returns:
            Expected output description
        """
        action_type = step.get("action_type", "").lower()
        step_title = step.get("title", "")

        if action_type == "click":
            return f"Successfully executed click action on {step_title}"
        elif action_type == "input":
            return f"Data entered successfully in {step_title}"
        elif action_type == "navigate":
            return f"Successfully navigated to {step_title} screen"
        elif action_type == "wait":
            return f"System ready after waiting for {step_title}"

        return f"Step '{step_title}' completed successfully"

    def _generate_title(self, video_analysis: Dict[str, Any]) -> str:
        """
        Generate SOP title from analysis.

        Args:
            video_analysis: Video analysis results

        Returns:
            SOP title
        """
        summary = video_analysis.get("process_summary", "")
        if summary:
            # Extract key process name from summary
            words = summary.split()
            title_words = words[:5] if len(words) >= 5 else words
            return " ".join(title_words)

        return "Business Process Automation"

    def _generate_description(
        self, video_analysis: Dict[str, Any], detail_level: str
    ) -> str:
        """
        Generate SOP description from analysis.

        Args:
            video_analysis: Video analysis results
            detail_level: Level of detail

        Returns:
            SOP description
        """
        base_description = video_analysis.get(
            "process_summary", "Automated business process"
        )

        if detail_level == "detailed":
            systems = video_analysis.get("systems_detected", [])
            system_names = ", ".join(s.get("name") for s in systems)
            duration = video_analysis.get("video_duration", 0)

            return (
                f"{base_description}\n\n"
                f"Systems involved: {system_names}\n"
                f"Total process duration: {duration:.1f} seconds\n"
                f"Estimated manual execution time: {duration / 60:.1f} minutes"
            )

        return base_description

    def _calculate_execution_time(self, steps: List[SOPStep]) -> float:
        """
        Calculate total estimated execution time.

        Args:
            steps: List of SOP steps

        Returns:
            Estimated execution time in minutes
        """
        total_seconds = sum(step.duration or 0 for step in steps)
        return round(total_seconds / 60, 1)

    def _generate_success_criteria(self, video_analysis: Dict[str, Any]) -> str:
        """
        Generate success criteria for the SOP.

        Args:
            video_analysis: Video analysis results

        Returns:
            Success criteria description
        """
        indicators = video_analysis.get("success_indicators", [])

        if indicators:
            return "Process is successful when:\n" + "\n".join(
                f"- {indicator}" for indicator in indicators
            )

        return (
            "Process is successful when:\n"
            "- All steps completed without errors\n"
            "- Expected system state achieved\n"
            "- Confirmation message displayed"
        )

    def _generate_preconditions(self, systems_detected: List[str]) -> str:
        """
        Generate preconditions for executing the SOP.

        Args:
            systems_detected: List of detected systems

        Returns:
            Preconditions description
        """
        preconditions = [
            "User has valid credentials for required systems",
            "Network connectivity is stable",
            "Required browser/application is installed",
        ]

        if "SAP" in str(systems_detected):
            preconditions.append("SAP client is accessible")

        if "Salesforce" in str(systems_detected):
            preconditions.append("Salesforce organization access is available")

        return "\n".join(f"- {pc}" for pc in preconditions)

    def _generate_postconditions(self, video_analysis: Dict[str, Any]) -> str:
        """
        Generate postconditions (expected state after execution).

        Args:
            video_analysis: Video analysis results

        Returns:
            Postconditions description
        """
        return (
            "After successful execution:\n"
            "- Data is persisted in the target system\n"
            "- Relevant approvals/notifications are triggered\n"
            "- Process status is updated in tracking system\n"
            "- Audit logs are created for compliance"
        )

    def _generate_error_handling(self, steps: List[SOPStep]) -> str:
        """
        Generate error handling guidance.

        Args:
            steps: List of SOP steps

        Returns:
            Error handling guidance
        """
        return (
            "If errors occur during execution:\n"
            "1. Check system availability and connectivity\n"
            "2. Verify user permissions and authentication\n"
            "3. Review step prerequisites are met\n"
            "4. Check browser console for JavaScript errors\n"
            "5. Take screenshots and contact support if issue persists"
        )

    def _generate_notes(
        self, video_analysis: Dict[str, Any], detail_level: str
    ) -> str:
        """
        Generate additional notes for the SOP.

        Args:
            video_analysis: Video analysis results
            detail_level: Level of detail

        Returns:
            Notes for the SOP
        """
        notes = [
            f"Generated from video analysis on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
            "Review and validate this SOP in your environment before full deployment",
        ]

        if detail_level == "expert":
            notes.extend(
                [
                    "Consider implementing retry logic for resilience",
                    "Monitor execution logs for performance optimization",
                    "Keep API credentials and sensitive data secure",
                ]
            )

        return "\n".join(f"- {note}" for note in notes)
