#!/usr/bin/env python3
"""
Validation Report Generator
Creates comprehensive HTML and JSON reports from validation results
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E2E Validation Report - AI QA Automation Platform</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #4472C4;
        }}

        h1 {{
            color: #2c3e50;
            font-size: 32px;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #7f8c8d;
            font-size: 18px;
        }}

        .timestamp {{
            color: #95a5a6;
            font-size: 14px;
            margin-top: 10px;
        }}

        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .summary-card {{
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .summary-card.passed {{
            background: #d4edda;
            border-left: 4px solid #28a745;
        }}

        .summary-card.failed {{
            background: #f8d7da;
            border-left: 4px solid #dc3545;
        }}

        .summary-card.skipped {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
        }}

        .summary-card.total {{
            background: #d1ecf1;
            border-left: 4px solid #17a2b8;
        }}

        .summary-card h3 {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .summary-card .value {{
            font-size: 36px;
            font-weight: bold;
            color: #2c3e50;
        }}

        .section {{
            margin: 40px 0;
        }}

        .section-title {{
            font-size: 24px;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}

        .test-suite {{
            background: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #6c757d;
        }}

        .test-suite.passed {{
            border-left-color: #28a745;
            background: #f0f8f4;
        }}

        .test-suite.failed {{
            border-left-color: #dc3545;
            background: #fef5f5;
        }}

        .test-suite.skipped {{
            border-left-color: #ffc107;
            background: #fffbf0;
        }}

        .test-suite-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .test-suite-name {{
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
        }}

        .test-suite-status {{
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .test-suite-status.passed {{
            background: #28a745;
            color: white;
        }}

        .test-suite-status.failed {{
            background: #dc3545;
            color: white;
        }}

        .test-suite-status.skipped {{
            background: #ffc107;
            color: #333;
        }}

        .test-suite-status.error {{
            background: #6c757d;
            color: white;
        }}

        .test-suite-details {{
            margin-top: 10px;
            font-size: 14px;
            color: #666;
        }}

        .error-message {{
            background: #fff5f5;
            border: 1px solid #feb2b2;
            padding: 15px;
            margin-top: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: #c53030;
        }}

        .recommendation {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}

        .recommendation-title {{
            font-weight: 600;
            color: #1976d2;
            margin-bottom: 5px;
        }}

        .chart {{
            margin: 30px 0;
            text-align: center;
        }}

        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #ecf0f1;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 14px;
            transition: width 0.3s ease;
        }}

        footer {{
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
            text-align: center;
            color: #95a5a6;
            font-size: 14px;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin: 0 4px;
        }}

        .badge.success {{
            background: #d4edda;
            color: #155724;
        }}

        .badge.danger {{
            background: #f8d7da;
            color: #721c24;
        }}

        .badge.warning {{
            background: #fff3cd;
            color: #856404;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}

        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>End-to-End Validation Report</h1>
            <div class="subtitle">AI QA Automation Platform</div>
            <div class="timestamp">Generated: {timestamp}</div>
        </header>

        <section class="section">
            <h2 class="section-title">Executive Summary</h2>

            <div class="summary-grid">
                <div class="summary-card total">
                    <h3>Total Suites</h3>
                    <div class="value">{total_suites}</div>
                </div>
                <div class="summary-card passed">
                    <h3>Passed</h3>
                    <div class="value">{passed_suites}</div>
                </div>
                <div class="summary-card failed">
                    <h3>Failed</h3>
                    <div class="value">{failed_suites}</div>
                </div>
                <div class="summary-card skipped">
                    <h3>Skipped</h3>
                    <div class="value">{skipped_suites}</div>
                </div>
            </div>

            <div class="progress-bar">
                <div class="progress-fill" style="width: {pass_rate}%">
                    Pass Rate: {pass_rate}%
                </div>
            </div>

            {status_message}
        </section>

        <section class="section">
            <h2 class="section-title">Test Suites</h2>
            {test_suites_html}
        </section>

        {recommendations_section}

        <footer>
            <p>AI QA Automation Platform - Validation Framework v1.0</p>
            <p>Report generated automatically from validation results</p>
        </footer>
    </div>
</body>
</html>
"""


def generate_html_report(results: Dict[str, Any], output_file: Path):
    """Generate HTML report from validation results"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary = results.get("summary", {})

    total_suites = summary.get("total_suites", 0)
    passed_suites = summary.get("passed", 0)
    failed_suites = summary.get("failed", 0)
    skipped_suites = summary.get("skipped", 0)

    pass_rate = 0 if total_suites == 0 else int((passed_suites / total_suites) * 100)

    # Generate status message
    if failed_suites == 0 and passed_suites > 0:
        status_message = """
        <div class="recommendation">
            <div class="recommendation-title">✅ All Validations Passed!</div>
            <p>All test suites completed successfully. The system is functioning as expected.</p>
        </div>
        """
    elif failed_suites > 0:
        status_message = f"""
        <div class="recommendation">
            <div class="recommendation-title">⚠️ Validation Issues Detected</div>
            <p>{failed_suites} test suite(s) failed. Please review the details below and address the issues.</p>
        </div>
        """
    else:
        status_message = ""

    # Generate test suites HTML
    test_suites_html = ""
    for suite in results.get("test_suites", []):
        suite_name = suite.get("suite_name", "Unknown")
        suite_status = suite.get("status", "unknown")
        suite_error = suite.get("error", "")
        suite_reason = suite.get("reason", "")

        details = ""
        if suite_error:
            details = f'<div class="error-message">Error: {suite_error}</div>'
        elif suite_reason:
            details = f'<div class="test-suite-details">Reason: {suite_reason}</div>'

        test_suites_html += f"""
        <div class="test-suite {suite_status}">
            <div class="test-suite-header">
                <div class="test-suite-name">{suite_name}</div>
                <div class="test-suite-status {suite_status}">{suite_status}</div>
            </div>
            {details}
        </div>
        """

    # Generate recommendations
    recommendations_html = ""
    if failed_suites > 0:
        recommendations_html = """
        <section class="section">
            <h2 class="section-title">Recommendations</h2>
            <div class="recommendation">
                <div class="recommendation-title">Next Steps</div>
                <ol style="margin-left: 20px; margin-top: 10px;">
                    <li>Review failed test suite details above</li>
                    <li>Check service logs for additional error information</li>
                    <li>Verify all prerequisites and environment configuration</li>
                    <li>Re-run failed tests after addressing issues</li>
                    <li>Consult the validation framework README for troubleshooting</li>
                </ol>
            </div>
        </section>
        """

    # Fill template
    html_content = HTML_TEMPLATE.format(
        timestamp=timestamp,
        total_suites=total_suites,
        passed_suites=passed_suites,
        failed_suites=failed_suites,
        skipped_suites=skipped_suites,
        pass_rate=pass_rate,
        status_message=status_message,
        test_suites_html=test_suites_html,
        recommendations_section=recommendations_html
    )

    # Write to file
    with open(output_file, 'w') as f:
        f.write(html_content)

    return output_file


def generate_json_report(results: Dict[str, Any], output_file: Path):
    """Generate enhanced JSON report with additional metadata"""

    enhanced_results = {
        **results,
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
            "framework_version": "1.0.0",
            "platform": "AI QA Automation Platform"
        }
    }

    with open(output_file, 'w') as f:
        json.dump(enhanced_results, f, indent=2)

    return output_file


def main():
    """Main entry point"""

    # Check if results file exists
    results_file = Path("validation_results.json")

    if not results_file.exists():
        print("❌ No validation results found.")
        print("   Run 'python run_validation.py' first to generate results.")
        sys.exit(1)

    # Load results
    with open(results_file) as f:
        results = json.load(f)

    # Generate reports
    print("Generating validation reports...")

    html_report = generate_html_report(results, Path("validation_report.html"))
    print(f"✓ HTML report generated: {html_report.absolute()}")

    json_report = generate_json_report(results, Path("validation_report_enhanced.json"))
    print(f"✓ Enhanced JSON report generated: {json_report.absolute()}")

    # Print summary
    summary = results.get("summary", {})
    print("\n📊 Summary:")
    print(f"   Total Suites: {summary.get('total_suites', 0)}")
    print(f"   Passed: {summary.get('passed', 0)}")
    print(f"   Failed: {summary.get('failed', 0)}")
    print(f"   Skipped: {summary.get('skipped', 0)}")

    if summary.get('failed', 0) > 0:
        print("\n⚠️  Some test suites failed. Review the HTML report for details.")
        sys.exit(1)
    else:
        print("\n✅ All test suites passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
