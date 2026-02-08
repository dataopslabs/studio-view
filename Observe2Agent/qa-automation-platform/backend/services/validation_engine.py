"""
Validation engine for comparing executed results against expected SOP output.
Validates data extraction, system state changes, and process completion.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from difflib import SequenceMatcher
from datetime import datetime
from uuid import uuid4

from models.validation import (
    ValidationReport,
    ValidationStep,
    ValidationStatus,
    DataValidationResult,
)
from models.sop import SOPDocument

logger = logging.getLogger(__name__)


class ValidationEngine:
    """
    Validates automation execution results against expected outcomes.
    Performs data validation, state verification, and generates validation reports.
    """

    def __init__(self):
        """Initialize the validation engine."""
        self.validation_threshold = 0.95
        logger.info("Validation engine initialized")

    def validate_execution(
        self,
        sop: SOPDocument,
        execution_result: Dict[str, Any],
        captured_data: Optional[Dict[str, Any]] = None,
    ) -> ValidationReport:
        """
        Validate execution results against SOP expectations.

        Args:
            sop: The SOP document that was executed
            execution_result: Results from execution engine
            captured_data: Data captured during execution

        Returns:
            ValidationReport with detailed validation results
        """
        validation_id = f"val-{uuid4().hex[:8]}"
        logger.info(f"Starting validation {validation_id} for SOP {sop.id}")

        try:
            # Validate each step
            step_validations = self._validate_steps(
                sop.steps, execution_result, captured_data
            )

            # Calculate overall metrics
            total_steps = len(step_validations)
            passed_steps = sum(
                1 for s in step_validations if s.status == ValidationStatus.PASSED
            )
            failed_steps = sum(
                1 for s in step_validations if s.status == ValidationStatus.FAILED
            )
            skipped_steps = sum(
                1 for s in step_validations if s.status == ValidationStatus.PENDING
            )

            success_rate = passed_steps / total_steps if total_steps > 0 else 0.0

            # Determine overall status
            if success_rate >= self.validation_threshold:
                overall_status = ValidationStatus.PASSED
            elif success_rate >= 0.5:
                overall_status = ValidationStatus.PARTIAL
            else:
                overall_status = ValidationStatus.FAILED

            # Create validation report
            report = ValidationReport(
                id=validation_id,
                sop_id=sop.id,
                execution_id=execution_result.get("execution_id", "unknown"),
                overall_status=overall_status,
                total_steps=total_steps,
                passed_steps=passed_steps,
                failed_steps=failed_steps,
                skipped_steps=skipped_steps,
                success_rate=round(success_rate, 4),
                validation_steps=step_validations,
                end_time=datetime.utcnow(),
                total_duration=execution_result.get("duration", 0),
                environment=execution_result.get("environment", "test"),
                browser=execution_result.get("browser"),
                os=execution_result.get("os"),
                error_summary=self._generate_error_summary(step_validations),
                recommendations=self._generate_recommendations(step_validations),
            )

            logger.info(f"Validation {validation_id} completed with status: {overall_status}")
            return report

        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return self._create_error_report(validation_id, sop.id, str(e))

    def _validate_steps(
        self,
        sop_steps: List,
        execution_result: Dict[str, Any],
        captured_data: Optional[Dict[str, Any]],
    ) -> List[ValidationStep]:
        """
        Validate each step in the execution.

        Args:
            sop_steps: Steps from the SOP
            execution_result: Execution results
            captured_data: Captured data from execution

        Returns:
            List of ValidationStep results
        """
        validation_steps = []

        exec_steps = execution_result.get("steps_details", [])

        for i, sop_step in enumerate(sop_steps):
            # Find corresponding execution result
            exec_step = next(
                (s for s in exec_steps if s.get("step") == sop_step.step_number),
                None,
            )

            if exec_step is None:
                # Step was not executed
                validation_step = ValidationStep(
                    step_number=sop_step.step_number,
                    title=sop_step.title,
                    status=ValidationStatus.PENDING,
                    expected=sop_step.expected_output or "No expectations defined",
                    actual=None,
                    match_score=0.0,
                    duration=0.0,
                )
            else:
                # Validate the step
                validation_step = self._validate_single_step(
                    sop_step, exec_step, captured_data
                )

            validation_steps.append(validation_step)

        return validation_steps

    def _validate_single_step(
        self,
        sop_step,
        exec_step: Dict[str, Any],
        captured_data: Optional[Dict[str, Any]],
    ) -> ValidationStep:
        """
        Validate a single step.

        Args:
            sop_step: SOP step definition
            exec_step: Execution result for this step
            captured_data: Captured data

        Returns:
            ValidationStep with validation results
        """
        expected_output = sop_step.expected_output or "Step completed successfully"
        actual_output = exec_step.get("details", {}).get("output", "")
        step_status = exec_step.get("status", "error")

        # Calculate match score
        match_score = self._calculate_match_score(expected_output, str(actual_output))

        # Determine validation status
        if step_status == "passed" and match_score >= 0.8:
            validation_status = ValidationStatus.PASSED
        elif step_status == "error":
            validation_status = ValidationStatus.FAILED
        elif match_score >= 0.5:
            validation_status = ValidationStatus.PARTIAL
        else:
            validation_status = ValidationStatus.FAILED

        return ValidationStep(
            step_number=sop_step.step_number,
            title=sop_step.title,
            status=validation_status,
            expected=expected_output,
            actual=str(actual_output)[:200],  # Limit length
            match_score=round(match_score, 4),
            error_message=exec_step.get("error") if step_status == "error" else None,
            duration=exec_step.get("details", {}).get("duration", 0),
            metadata={
                "action_type": sop_step.action_type,
                "system": sop_step.system_involved,
            },
        )

    def validate_data_extraction(
        self,
        expected_fields: Dict[str, Any],
        extracted_data: Dict[str, Any],
    ) -> List[DataValidationResult]:
        """
        Validate extracted data against expected values.

        Args:
            expected_fields: Expected field values
            extracted_data: Actually extracted data

        Returns:
            List of DataValidationResult objects
        """
        logger.info("Validating extracted data")

        results = []

        for field_name, expected_value in expected_fields.items():
            actual_value = extracted_data.get(field_name)

            # Determine data type
            if isinstance(expected_value, (int, float)):
                data_type = "number"
            elif isinstance(expected_value, bool):
                data_type = "boolean"
            elif isinstance(expected_value, list):
                data_type = "array"
            elif isinstance(expected_value, dict):
                data_type = "object"
            else:
                data_type = "string"

            # Validate the field
            is_valid, confidence = self._validate_field(
                expected_value, actual_value, data_type
            )

            error_message = None
            if not is_valid:
                error_message = f"Expected {expected_value}, got {actual_value}"

            result = DataValidationResult(
                field_name=field_name,
                expected_value=expected_value,
                actual_value=actual_value,
                data_type=data_type,
                is_valid=is_valid,
                confidence=round(confidence, 4),
                error_message=error_message,
            )

            results.append(result)

        logger.info(f"Data validation completed: {len(results)} fields validated")
        return results

    def _validate_field(
        self, expected: Any, actual: Any, data_type: str
    ) -> Tuple[bool, float]:
        """
        Validate a single field value.

        Args:
            expected: Expected value
            actual: Actual value
            data_type: Type of data being validated

        Returns:
            Tuple of (is_valid, confidence_score)
        """
        if actual is None:
            return False, 0.0

        if data_type == "string":
            confidence = self._calculate_match_score(str(expected), str(actual))
            return confidence >= 0.8, confidence

        elif data_type == "number":
            try:
                exp_num = float(expected)
                act_num = float(actual)
                # Allow 1% tolerance for numbers
                tolerance = exp_num * 0.01
                is_valid = abs(exp_num - act_num) <= tolerance
                confidence = 1.0 if is_valid else 0.5
                return is_valid, confidence
            except (ValueError, TypeError):
                return False, 0.0

        elif data_type == "boolean":
            is_valid = bool(expected) == bool(actual)
            confidence = 1.0 if is_valid else 0.0
            return is_valid, confidence

        else:
            is_valid = expected == actual
            confidence = 1.0 if is_valid else 0.3
            return is_valid, confidence

    def _calculate_match_score(self, expected: str, actual: str) -> float:
        """
        Calculate string similarity score.

        Args:
            expected: Expected string
            actual: Actual string

        Returns:
            Similarity score 0.0-1.0
        """
        if not expected and not actual:
            return 1.0
        if not expected or not actual:
            return 0.0

        matcher = SequenceMatcher(None, expected.lower(), actual.lower())
        return round(matcher.ratio(), 4)

    def _generate_error_summary(self, validations: List[ValidationStep]) -> str:
        """
        Generate summary of validation errors.

        Args:
            validations: List of validation steps

        Returns:
            Error summary string
        """
        failed_steps = [
            v for v in validations if v.status == ValidationStatus.FAILED
        ]

        if not failed_steps:
            return None

        summary = f"{len(failed_steps)} step(s) failed:\n"
        for step in failed_steps[:5]:  # Limit to first 5
            summary += f"- Step {step.step_number} ({step.title}): {step.error_message or 'Unknown error'}\n"

        return summary

    def _generate_recommendations(self, validations: List[ValidationStep]) -> List[str]:
        """
        Generate recommendations based on validation results.

        Args:
            validations: List of validation steps

        Returns:
            List of recommendations
        """
        recommendations = []

        failed_count = sum(
            1 for v in validations if v.status == ValidationStatus.FAILED
        )
        partial_count = sum(
            1 for v in validations if v.status == ValidationStatus.PARTIAL
        )

        if failed_count > 0:
            recommendations.append(
                f"Review and fix {failed_count} failed step(s) before redeployment"
            )

        if partial_count > 0:
            recommendations.append(
                f"Improve validation logic for {partial_count} partial step(s)"
            )

        # Check for specific error patterns
        for step in validations:
            if step.error_message:
                if "timeout" in step.error_message.lower():
                    recommendations.append("Consider increasing timeouts for slow systems")
                elif "element not found" in step.error_message.lower():
                    recommendations.append("Update element selectors for changed UI")

        return recommendations[:5]  # Limit to 5 recommendations

    def _create_error_report(
        self, validation_id: str, sop_id: str, error_msg: str
    ) -> ValidationReport:
        """
        Create an error validation report.

        Args:
            validation_id: ID of validation
            sop_id: ID of SOP
            error_msg: Error message

        Returns:
            ValidationReport with error status
        """
        return ValidationReport(
            id=validation_id,
            sop_id=sop_id,
            execution_id="unknown",
            overall_status=ValidationStatus.ERROR,
            total_steps=0,
            passed_steps=0,
            failed_steps=0,
            success_rate=0.0,
            error_summary=error_msg,
        )
