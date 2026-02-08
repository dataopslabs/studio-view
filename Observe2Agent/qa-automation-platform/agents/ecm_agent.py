"""
ECM (Enterprise Content Management) Mapping Agent.
Maps business processes to enterprise systems and creates integration configuration.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class ECMAgent:
    """
    Agent for mapping business processes to enterprise systems.
    Creates ECM configurations and system integration mappings.
    """

    def __init__(self):
        """Initialize the ECM agent."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("ECM Agent initialized")

    async def map_process_to_systems(
        self, workflow_steps: List[Dict[str, Any]], detected_systems: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Map workflow steps to detected enterprise systems.

        Args:
            workflow_steps: List of workflow steps from video analysis
            detected_systems: List of detected systems

        Returns:
            Mapping configuration
        """
        self.logger.info("Mapping process to enterprise systems")

        mapping = {
            "process_system_mapping": [],
            "system_interactions": [],
            "data_flow": [],
            "integration_config": {},
        }

        # Map each step to systems
        for step in workflow_steps:
            step_system = step.get("system", "Unknown")

            system_mapping = {
                "step_number": step["step_number"],
                "step_title": step["title"],
                "system_involved": step_system,
                "action_type": step["action_type"],
                "data_involved": self._extract_step_data(step),
            }

            mapping["process_system_mapping"].append(system_mapping)

        # Identify system interactions
        mapping["system_interactions"] = self._identify_interactions(
            workflow_steps, detected_systems
        )

        # Create integration configuration
        for system in detected_systems:
            mapping["integration_config"][system["name"]] = {
                "api_endpoint": f"https://api.{system['name'].lower()}.com",
                "authentication": "oauth2",
                "retry_policy": {"max_retries": 3, "backoff_factor": 1.0},
                "timeout": 30,
            }

        self.logger.info("System mapping completed")
        return mapping

    def _extract_step_data(self, step: Dict[str, Any]) -> List[str]:
        """
        Extract data elements from a step.

        Args:
            step: Workflow step

        Returns:
            List of data elements
        """
        data_elements = []

        # Mock data extraction based on action type
        if step["action_type"] == "input":
            data_elements = [
                "vendor_name",
                "amount",
                "po_number",
            ]
        elif step["action_type"] == "click":
            data_elements = ["confirmation", "status_update"]

        return data_elements

    def _identify_interactions(
        self, steps: List[Dict[str, Any]], systems: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify interactions between systems.

        Args:
            steps: Workflow steps
            systems: Detected systems

        Returns:
            List of system interactions
        """
        interactions = []

        systems_used = set(step.get("system") for step in steps)

        for i, system1 in enumerate(list(systems_used)):
            for system2 in list(systems_used)[i + 1 :]:
                interactions.append(
                    {
                        "source_system": system1,
                        "target_system": system2,
                        "interaction_type": "data_transfer",
                        "bidirectional": True,
                    }
                )

        return interactions

    async def validate_ecm_mapping(
        self, mapping: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate ECM mapping configuration.

        Args:
            mapping: ECM mapping configuration

        Returns:
            Validation results
        """
        self.logger.info("Validating ECM mapping")

        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
        }

        # Check for missing system configurations
        if not mapping.get("integration_config"):
            validation_result["errors"].append("No system integrations configured")
            validation_result["is_valid"] = False

        # Check for orphaned steps
        mapped_steps = {m["step_number"] for m in mapping.get("process_system_mapping", [])}
        total_steps = max(mapped_steps) if mapped_steps else 0

        for i in range(1, total_steps + 1):
            if i not in mapped_steps:
                validation_result["warnings"].append(f"Step {i} is not mapped to any system")

        self.logger.info(f"Validation completed: {'VALID' if validation_result['is_valid'] else 'INVALID'}")
        return validation_result


async def map_process_task(
    workflow_steps: List[Dict[str, Any]], detected_systems: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Task to map a process to enterprise systems.

    Args:
        workflow_steps: List of workflow steps
        detected_systems: List of detected systems

    Returns:
        Mapping configuration
    """
    agent = ECMAgent()
    return await agent.map_process_to_systems(workflow_steps, detected_systems)
