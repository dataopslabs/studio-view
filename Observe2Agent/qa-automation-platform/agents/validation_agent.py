"""
Validation Agent for automated testing and result validation.
Compares expected vs actual results during automation execution.
"""

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationAgent:
    """
    Agent for validating automation execution results.
    Compares expected outcomes against actual execution results.
    """

    def __init__(self):
        """Initialize the validation agent."""
        self.logger = logging.getLogger(__name__)
        self.validation_threshold = 0.95
        self.logger.info("Validation Agent initialized")

    async def validate_execution(
        self, expected_results: Dict[str, Any], actual_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate execution results against expectations.

        Args:
            expected_results: Expected outcomes from SOP
            actual_results: Actual execution results

        Returns:
            Validation report
        """
        self.logger.info("Starting execution validation")

        validation_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_validations": 0,
            "passed_validations": 0,
            "failed_validations": 0,
            "validation_details": [],
            "overall_status": "unknown",
        }

        # Validate each expected result
        for key, expected_value in expected_results.items():
            actual_value = actual_results.get(key)

            is_valid, confidence = self._compare_values(expected_value, actual_value)

            validation_detail = {
                "field": key,
                "expected": expected_value,
                "actual": actual_value,
                "is_valid": is_valid,
                "confidence": confidence,
            }

            validation_report["validation_details"].append(validation_detail)
            validation_report["total_validations"] += 1

            if is_valid:
                validation_report["passed_validations"] += 1
            else:
                validation_report["failed_validations"] += 1

        # Determine overall status
        if validation_report["total_validations"] > 0:
            success_rate = (
                validation_report["passed_validations"]
                / validation_report["total_validations"]
            )
            validation_report["success_rate"] = success_rate

            if success_rate >= self.validation_threshold:
                validation_report["overall_status"] = "PASSED"
            elif success_rate >= 0.5:
                validation_report["overall_status"] = "PARTIAL"
            else:
                validation_report["overall_status"] = "FAILED"

        self.logger.info(
            f"Validation completed: {validation_report['overall_status']}"
        )
        return validation_report

    async def validate_data_extraction(
        self, extracted_data: Dict[str, Any], validation_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate extracted data against rules.

        Args:
            extracted_data: Data extracted during execution
            validation_rules: Rules for validation

        Returns:
            Data validation results
        """
        self.logger.info("Validating extracted data")

        data_validation = {
            "timestamp": datetime.utcnow().isoformat(),
            "field_validations": [],
            "overall_valid": True,
        }

        for field, rule in validation_rules.items():
            field_value = extracted_data.get(field)

            validation = self._validate_field(field_value, rule)

            data_validation["field_validations"].append(
                {
                    "field": field,
                    "value": field_value,
                    "rule": rule,
                    **validation,
                }
            )

            if not validation["is_valid"]:
                data_validation["overall_valid"] = False

        return data_validation

    async def validate_system_state(
        self, system: str, expected_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate the state of a system after execution.

        Args:
            system: System name
            expected_state: Expected system state

        Returns:
            State validation results
        """
        self.logger.info(f"Validating system state: {system}")

        # Mock system state validation
        state_validation = {
            "system": system,
            "timestamp": datetime.utcnow().isoformat(),
            "expected_state": expected_state,
            "actual_state": {
                "status": "ready",
                "last_update": datetime.utcnow().isoformat(),
            },
            "is_valid": True,
            "details": f"System {system} is in valid state",
        }

        return state_validation

    def _compare_values(
        self, expected: Any, actual: Any
    ) -> Tuple[bool, float]:
        """
        Compare expected vs actual values.

        Args:
            expected: Expected value
            actual: Actual value

        Returns:
            Tuple of (is_valid, confidence_score)
        """
        if actual is None:
            return False, 0.0

        if isinstance(expected, str) and isinstance(actual, str):
            # String comparison with tolerance
            match_ratio = self._string_match_ratio(expected, actual)
            return match_ratio >= 0.8, match_ratio

        elif isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            # Numeric comparison with tolerance
            tolerance = 0.01  # 1% tolerance
            diff = abs(expected - actual) / abs(expected) if expected != 0 else 0
            is_valid = diff <= tolerance
            confidence = 1.0 - diff
            return is_valid, max(0.0, confidence)

        elif isinstance(expected, bool) and isinstance(actual, bool):
            # Boolean comparison
            is_valid = expected == actual
            return is_valid, 1.0 if is_valid else 0.0

        else:
            # Direct equality comparison
            is_valid = expected == actual
            return is_valid, 1.0 if is_valid else 0.3

    def _validate_field(
        self, value: Any, rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a field against a rule.

        Args:
            value: Field value to validate
            rule: Validation rule

        Returns:
            Validation result
        """
        result = {
            "is_valid": True,
            "error": None,
            "confidence": 1.0,
        }

        if rule.get("required") and value is None:
            result["is_valid"] = False
            result["error"] = "Required field is missing"
            result["confidence"] = 0.0
            return result

        if rule.get("type") == "string" and value is not None:
            if not isinstance(value, str):
                result["is_valid"] = False
                result["error"] = f"Expected string, got {type(value).__name__}"
                result["confidence"] = 0.0

        elif rule.get("type") == "number" and value is not None:
            if not isinstance(value, (int, float)):
                result["is_valid"] = False
                result["error"] = f"Expected number, got {type(value).__name__}"
                result["confidence"] = 0.0

        if rule.get("pattern") and value is not None:
            import re

            if not re.match(rule["pattern"], str(value)):
                result["is_valid"] = False
                result["error"] = f"Value does not match pattern {rule['pattern']}"
                result["confidence"] = 0.5

        if rule.get("min_length") and value is not None:
            if len(str(value)) < rule["min_length"]:
                result["is_valid"] = False
                result["error"] = f"Value too short, minimum {rule['min_length']}"
                result["confidence"] = 0.5

        return result

    def _string_match_ratio(self, s1: str, s2: str) -> float:
        """
        Calculate string similarity ratio.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score 0.0-1.0
        """
        from difflib import SequenceMatcher

        if not s1 or not s2:
            return 0.0

        matcher = SequenceMatcher(None, s1.lower(), s2.lower())
        return matcher.ratio()


async def validate_execution_task(
    expected_results: Dict[str, Any], actual_results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Task to validate execution results.

    Args:
        expected_results: Expected outcomes
        actual_results: Actual results

    Returns:
        Validation report
    """
    agent = ValidationAgent()
    return await agent.validate_execution(expected_results, actual_results)
