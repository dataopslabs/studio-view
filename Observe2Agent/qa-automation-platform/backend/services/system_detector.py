"""
Enterprise system detection service.
Identifies systems like SAP, Oracle, Salesforce, etc. from video analysis.
"""

import logging
from typing import List, Dict, Any
from models.systems import DetectedSystem, SystemType, SystemsDetectionResult

logger = logging.getLogger(__name__)


class SystemDetector:
    """
    Detects enterprise systems and applications from video analysis.
    Uses pattern matching and UI element recognition to identify systems.
    """

    # Known system signatures and UI patterns
    SYSTEM_SIGNATURES = {
        "SAP": {
            "system_type": SystemType.ERP,
            "patterns": [
                "SAP Logo",
                "Fiori Interface",
                "Transaction Code",
                "SAP Module",
                "SAP Menu",
            ],
            "keywords": ["sap", "fiori", "transaction", "module", "purchase order"],
        },
        "Oracle EBS": {
            "system_type": SystemType.ERP,
            "patterns": [
                "Oracle Logo",
                "EBS Interface",
                "Oracle Menu",
                "Application Menu",
            ],
            "keywords": ["oracle", "ebs", "application", "responsibility"],
        },
        "Salesforce": {
            "system_type": SystemType.CRM,
            "patterns": [
                "Salesforce Logo",
                "Lightning Interface",
                "Salesforce Menu",
            ],
            "keywords": ["salesforce", "lightning", "crm", "opportunity", "account"],
        },
        "Workday": {
            "system_type": SystemType.HCM,
            "patterns": ["Workday Logo", "Workday Interface", "Worker Data"],
            "keywords": ["workday", "hcm", "employee", "worker", "requisition"],
        },
        "Outlook": {
            "system_type": SystemType.EMAIL,
            "patterns": ["Outlook Logo", "Email Interface", "Message Compose"],
            "keywords": ["outlook", "email", "compose", "inbox", "send"],
        },
        "Gmail": {
            "system_type": SystemType.EMAIL,
            "patterns": ["Gmail Logo", "Gmail Interface", "Compose Button"],
            "keywords": ["gmail", "google", "email", "compose"],
        },
        "SharePoint": {
            "system_type": SystemType.COLLABORATION,
            "patterns": [
                "SharePoint Logo",
                "Document Library",
                "List View",
                "SharePoint Menu",
            ],
            "keywords": ["sharepoint", "document library", "list", "collaboration"],
        },
        "ServiceNow": {
            "system_type": SystemType.WORKFLOW,
            "patterns": ["ServiceNow Logo", "Incident Form", "Change Request"],
            "keywords": ["servicenow", "incident", "change", "request"],
        },
    }

    def __init__(self):
        """Initialize the system detector."""
        self.confidence_threshold = 0.7
        logger.info("System detector initialized")

    def detect_systems(
        self, video_analysis: Dict[str, Any], video_id: str
    ) -> SystemsDetectionResult:
        """
        Detect enterprise systems from video analysis results.

        Args:
            video_analysis: Results from video analyzer containing UI elements and actions
            video_id: ID of the analyzed video

        Returns:
            SystemsDetectionResult with detected systems and confidence scores
        """
        logger.info(f"Detecting systems in video {video_id}")

        detected_systems: List[DetectedSystem] = []

        if not video_analysis.get("success"):
            logger.warning("Video analysis failed, returning empty detection result")
            return SystemsDetectionResult(
                video_id=video_id,
                detected_systems=[],
                total_systems_found=0,
                analysis_confidence=0.0,
                processing_time=0.0,
            )

        # Extract systems from analysis
        systems_from_analysis = video_analysis.get("systems_detected", [])
        for system_data in systems_from_analysis:
            detected_systems.append(self._parse_detected_system(system_data))

        # Also analyze workflow steps for additional system indicators
        steps = video_analysis.get("workflow_steps", [])
        for step in steps:
            system_name = step.get("system")
            if system_name and not any(s.name == system_name for s in detected_systems):
                # Add system if not already detected
                detected_system = self._create_system_from_step(system_name, step)
                detected_systems.append(detected_system)

        # Filter by confidence threshold
        filtered_systems = [
            s for s in detected_systems if s.confidence >= self.confidence_threshold
        ]

        # Calculate overall analysis confidence
        overall_confidence = (
            sum(s.confidence for s in filtered_systems) / len(filtered_systems)
            if filtered_systems
            else 0.0
        )

        logger.info(f"Detected {len(filtered_systems)} systems")

        return SystemsDetectionResult(
            video_id=video_id,
            detected_systems=filtered_systems,
            total_systems_found=len(filtered_systems),
            analysis_confidence=overall_confidence,
            processing_time=video_analysis.get("processing_time", 0.0),
            detected_workflows=self._extract_workflows(steps),
            data_patterns=self._extract_data_patterns(video_analysis),
        )

    def _parse_detected_system(self, system_data: Dict[str, Any]) -> DetectedSystem:
        """
        Parse system data from video analysis into DetectedSystem model.

        Args:
            system_data: Raw system data from analysis

        Returns:
            DetectedSystem object
        """
        system_type = self._determine_system_type(system_data.get("system_type", "OTHER"))

        return DetectedSystem(
            name=system_data.get("name", "Unknown System"),
            system_type=system_type,
            confidence=system_data.get("confidence", 0.5),
            url=system_data.get("url"),
            version=system_data.get("version"),
            ui_elements_detected=system_data.get("ui_elements", []),
            authentication_type=system_data.get("auth_type"),
            timestamp=system_data.get("first_detected_at"),
            metadata=system_data.get("metadata", {}),
        )

    def _create_system_from_step(
        self, system_name: str, step: Dict[str, Any]
    ) -> DetectedSystem:
        """
        Create a DetectedSystem from a workflow step.

        Args:
            system_name: Name of the system
            step: Workflow step data

        Returns:
            DetectedSystem object
        """
        system_type = self._determine_system_type(system_name)

        return DetectedSystem(
            name=system_name,
            system_type=system_type,
            confidence=0.85,
            timestamp=step.get("timestamp"),
            ui_elements_detected=step.get("ui_elements", []),
            metadata={
                "source": "workflow_step",
                "step_number": step.get("step_number"),
            },
        )

    def _determine_system_type(self, system_identifier: str) -> SystemType:
        """
        Determine the SystemType based on system identifier.

        Args:
            system_identifier: System name or type identifier

        Returns:
            SystemType enum value
        """
        system_identifier_lower = system_identifier.lower()

        for system_name, config in self.SYSTEM_SIGNATURES.items():
            if system_identifier_lower in system_name.lower():
                return config["system_type"]
            for keyword in config["keywords"]:
                if keyword in system_identifier_lower:
                    return config["system_type"]

        return SystemType.OTHER

    def _extract_workflows(self, steps: List[Dict[str, Any]]) -> List[str]:
        """
        Extract workflow patterns from steps.

        Args:
            steps: List of workflow steps

        Returns:
            List of identified workflow patterns
        """
        workflows = []

        # Check for common workflow patterns
        if steps:
            action_types = [step.get("action_type") for step in steps]

            if "click" in action_types and "input" in action_types:
                workflows.append("Form Filling")

            if "navigate" in action_types:
                workflows.append("System Navigation")

            if any("approval" in str(step).lower() for step in steps):
                workflows.append("Approval Process")

            if any("search" in str(step).lower() for step in steps):
                workflows.append("Data Search")

            if any("download" in str(step).lower() or "export" in str(step).lower() for step in steps):
                workflows.append("Data Export")

        return workflows if workflows else ["General Process"]

    def _extract_data_patterns(self, video_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data handling patterns from analysis.

        Args:
            video_analysis: Full video analysis results

        Returns:
            Dictionary of identified data patterns
        """
        patterns = video_analysis.get("data_extraction_patterns", [])

        return {
            "field_count": len(patterns),
            "fields": [
                {
                    "name": p.get("field_name"),
                    "pattern": p.get("pattern"),
                    "confidence": p.get("confidence"),
                }
                for p in patterns
            ],
            "has_date_fields": any(
                "date" in str(p.get("pattern", "")).lower() for p in patterns
            ),
            "has_currency_fields": any(
                "currency" in str(p.get("pattern", "")).lower() for p in patterns
            ),
            "has_id_fields": any(
                "id" in str(p.get("field_name", "")).lower() for p in patterns
            ),
        }
