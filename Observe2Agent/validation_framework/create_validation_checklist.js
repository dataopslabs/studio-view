const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, WidthType, ShadingType, BorderStyle, HeadingLevel,
        LevelFormat, PageBreak } = require('docx');
const fs = require('fs');

// Border configuration
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

const doc = new Document({
  styles: {
    default: {
      document: {
        run: { font: "Arial", size: 24 }
      }
    },
    paragraphStyles: [
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "000000" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 }
      },
      {
        id: "Heading2",
        name: "Heading 2",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 28, bold: true, font: "Arial", color: "000000" },
        paragraph: { spacing: { before: 180, after: 180 }, outlineLevel: 1 }
      },
      {
        id: "Heading3",
        name: "Heading 3",
        basedOn: "Normal",
        next: "Normal",
        quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "000000" },
        paragraph: { spacing: { before: 120, after: 120 }, outlineLevel: 2 }
      },
    ]
  },
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } }
          }
        ]
      },
      {
        reference: "checkbox",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "☐",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 720, hanging: 360 } } }
          }
        ]
      },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: {
          width: 12240,
          height: 15840
        },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    children: [
      // Title
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        alignment: AlignmentType.CENTER,
        children: [new TextRun("AI QA Automation Platform")]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({
          text: "End-to-End Validation Checklist",
          size: 28,
          bold: true
        })]
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 },
        children: [new TextRun({
          text: "Version 1.0",
          size: 20,
          italics: true
        })]
      }),

      // Overview
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Overview")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun(
          "This document provides a comprehensive checklist for validating the AI QA Automation Platform. " +
          "It covers all critical workflows, integration points, and system components."
        )]
      }),

      // Validation Status Table
      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Validation Status")]
      }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3120, 3120, 3120],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "4472C4", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({
                  children: [new TextRun({ text: "Test Area", bold: true, color: "FFFFFF" })]
                })]
              }),
              new TableCell({
                borders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "4472C4", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({
                  children: [new TextRun({ text: "Status", bold: true, color: "FFFFFF" })]
                })]
              }),
              new TableCell({
                borders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "4472C4", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({
                  children: [new TextRun({ text: "Notes", bold: true, color: "FFFFFF" })]
                })]
              }),
            ]
          }),
          ...["Environment Setup", "SOP Management", "Video Processing", "Execution Orchestration",
              "Validation & Reporting", "Agent Integration"].map(area =>
            new TableRow({
              children: [
                new TableCell({
                  borders,
                  width: { size: 3120, type: WidthType.DXA },
                  margins: { top: 80, bottom: 80, left: 120, right: 120 },
                  children: [new Paragraph({ children: [new TextRun(area)] })]
                }),
                new TableCell({
                  borders,
                  width: { size: 3120, type: WidthType.DXA },
                  margins: { top: 80, bottom: 80, left: 120, right: 120 },
                  children: [new Paragraph({ children: [new TextRun("Pending")] })]
                }),
                new TableCell({
                  borders,
                  width: { size: 3120, type: WidthType.DXA },
                  margins: { top: 80, bottom: 80, left: 120, right: 120 },
                  children: [new Paragraph({ children: [new TextRun("")] })]
                }),
              ]
            })
          )
        ]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 1: Environment Setup
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("1. Environment Setup & Prerequisites")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("1.1 System Requirements")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Docker and Docker Compose installed")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Python 3.9+ installed")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Node.js 18+ and npm installed")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Minimum 8GB RAM available")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Minimum 20GB disk space available")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("1.2 Environment Configuration")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun(".env file created from .env.example")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("ANTHROPIC_API_KEY configured")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("DATABASE_URL configured")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("All required environment variables set")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Environment variables validated")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("1.3 Service Startup")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Backend dependencies installed (pip install -r requirements.txt)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Frontend dependencies installed (npm install)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Database initialized and migrations run")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Backend service starts without errors (http://localhost:8000)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Frontend service starts without errors (http://localhost:3000)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Health check endpoint responds (GET /health)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("API documentation accessible (GET /docs)")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 2: SOP Management
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("2. SOP Creation & Management Workflow")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("2.1 Manual SOP Creation")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Navigate to SOP creation page in UI")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Enter SOP name and description")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Add multiple test steps with actions and expected results")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Select system type (web, mobile, desktop, API)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Save SOP successfully")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Verify SOP appears in SOP list")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("2.2 SOP Generation from Video")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Upload test video file (MP4 format)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Video upload completes successfully")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("AI analysis begins automatically")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("System detects application type correctly")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Test steps extracted with actions")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Expected results generated for each step")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Generated SOP is reviewable and editable")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("SOP saved after review")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("2.3 SOP Management Operations")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("View list of all SOPs")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Search and filter SOPs by name, type, or date")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Open existing SOP for viewing")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Edit SOP steps, description, or system type")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Save updated SOP")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Duplicate existing SOP")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Export SOP to JSON/PDF format")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Delete SOP (with confirmation)")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 3: Video Processing
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("3. Video Processing & Analysis Workflow")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("3.1 Video Upload")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Upload video via drag-and-drop")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Upload video via file picker")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Upload progress indicator displays correctly")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Video format validation (MP4, AVI, MOV accepted)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("File size validation (max size enforced)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Video stored successfully with unique ID")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("3.2 Frame Extraction")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Frame extraction triggered automatically")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Configurable frame rate (1 fps, 0.5 fps, etc.)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Frames extracted at correct intervals")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Frame thumbnails displayed in UI")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Extracted frames stored and accessible")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("3.3 AI Video Analysis")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Video Agent analyzes video content")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Actions detected and timestamped")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("UI elements identified (buttons, inputs, menus)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("User interactions recognized (clicks, typing, navigation)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Confidence scores provided for detections")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Analysis results displayed in structured format")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("3.4 System Detection")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Application type automatically detected")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Web application detection (browser, URL bar visible)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Mobile application detection (device frame, mobile UI)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Desktop application detection (native UI elements)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("API/CLI detection (terminal, code editor visible)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Detection confidence score above threshold (>70%)")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 4: Execution Orchestration
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("4. Test Execution & Orchestration Workflow")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("4.1 Execution Configuration")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Select SOP for execution")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Choose target environment (dev, staging, prod)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Set execution mode (automated, semi-automated, manual)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Configure execution parameters (timeouts, retries)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Validate configuration before starting")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("4.2 Execution Initiation")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Start execution via UI button")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Execution queued successfully")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Unique execution ID generated")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Execution status updates to Running")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Orchestrator agent takes control")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("4.3 Real-time Monitoring")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Execution progress displayed in real-time")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Current step highlighted in UI")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Step status indicators (pending, running, passed, failed)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Execution logs streamed to UI")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Screenshots captured at each step")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Elapsed time displayed and updated")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Ability to pause/resume execution")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("4.4 Orchestrator Agent Coordination")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Orchestrator processes SOP steps sequentially")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Orchestrator invokes appropriate agents per step")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Video Agent called for video-based steps")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Validation Agent called for result verification")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("ECM Agent generates test code if needed")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Agent responses processed correctly")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Error handling and recovery mechanisms work")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("4.5 Execution Completion")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("All steps executed successfully")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Execution status updates to Completed")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Final results summary displayed")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Pass/fail count accurate")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Execution artifacts saved (logs, screenshots)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Notification sent on completion (if configured)")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 5: Validation & Reporting
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("5. Validation & Reporting Workflow")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("5.1 Result Validation")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Validation Agent analyzes execution results")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Expected vs actual results compared")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Text matching with fuzzy logic")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Visual comparison of screenshots")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Similarity scores calculated")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Discrepancies identified and highlighted")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Validation results stored with execution")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("5.2 Baseline Comparison")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Select baseline execution for comparison")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Side-by-side comparison view")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Differences highlighted (added, removed, changed)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Screenshot diff tool shows visual changes")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Performance metrics compared (execution time)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Ability to set new baseline")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("5.3 Report Generation")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Generate report from execution results")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Report includes executive summary")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Report includes detailed step results")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Report includes screenshots and evidence")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Report includes error logs and stack traces")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Report includes validation results")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Report timestamp and metadata included")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("5.4 Report Export")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Export report as JSON format")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Export report as PDF format")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Export report as HTML format")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Exported files downloadable from UI")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Reports accessible via API endpoint")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Email report functionality (if configured)")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 6: Agent Integration
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("6. AI Agent Integration Testing")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("6.1 Video Agent")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Video Agent accessible via API")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Processes video and extracts frames")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Identifies UI elements correctly")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Detects user actions accurately")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Generates test steps from video")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Returns structured JSON response")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Error handling for invalid videos")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("6.2 Validation Agent")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Validation Agent accessible via API")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Compares expected vs actual results")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Calculates similarity scores")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Identifies discrepancies accurately")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Performs visual image comparison")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Handles partial matches intelligently")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Returns detailed validation report")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("6.3 ECM Agent (Enterprise Content Management)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("ECM Agent accessible via API")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Generates test automation code from SOP")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Supports multiple languages (Python, JavaScript)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Supports multiple frameworks (Pytest, Playwright)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Generated code is syntactically valid")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Generated code follows best practices")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Code can be downloaded or copied")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("6.4 Orchestrator Agent")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Orchestrator coordinates all agents")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Routes requests to appropriate agents")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Handles agent responses correctly")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Manages workflow state transitions")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Implements retry logic for failures")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Aggregates results from multiple agents")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Logs all agent interactions")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 7: Performance & Reliability
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("7. Performance & Reliability Testing")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("7.1 Performance Benchmarks")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("API response times under 2 seconds for standard requests")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Video upload completes within reasonable time")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Frame extraction performance acceptable")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("AI analysis completes within timeout")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("UI remains responsive during operations")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Database queries optimized")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("7.2 Concurrent Operations")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Multiple users can create SOPs simultaneously")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Multiple executions can run concurrently")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("No race conditions in execution queue")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Resource contention handled gracefully")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("System remains stable under load")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("7.3 Error Handling & Recovery")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Invalid input validation with clear error messages")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("API returns appropriate HTTP status codes")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Failed executions marked appropriately")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Retry mechanism works for transient failures")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Graceful degradation when services unavailable")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Error logs captured comprehensively")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("System recovers from errors automatically")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("7.4 Data Integrity")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("SOP data remains consistent across operations")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Execution history maintains integrity")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("No data loss during updates")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Relationships between entities preserved")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Audit trail complete and accurate")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Database transactions handled correctly")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 8: Security & Access Control
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("8. Security & Access Control")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("8.1 Authentication")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("User authentication required (if implemented)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Secure password handling")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Session management secure")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Logout functionality works correctly")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("8.2 API Security")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("API key/token validation")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("CORS configured correctly")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Input sanitization prevents injection attacks")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Rate limiting implemented")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("HTTPS enforced in production")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("8.3 Data Protection")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Sensitive data encrypted at rest")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Sensitive data encrypted in transit")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("API keys stored securely (not in code)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("File uploads validated for security")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("No sensitive data in logs")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Section 9: Usability & User Experience
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("9. Usability & User Experience")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("9.1 UI Responsiveness")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("UI loads quickly (< 3 seconds)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Navigation between pages smooth")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Forms submit without lag")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Loading indicators displayed during operations")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("No UI freezing during background tasks")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("9.2 User Feedback")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Success messages displayed clearly")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Error messages helpful and actionable")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Progress indicators accurate")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Confirmation dialogs for destructive actions")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Tooltips and help text available")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("9.3 Accessibility")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Keyboard navigation functional")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Color contrast meets accessibility standards")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        children: [new TextRun("Screen reader compatibility (if required)")]
      }),
      new Paragraph({
        numbering: { reference: "checkbox", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("Responsive design for different screen sizes")]
      }),

      new Paragraph({ children: [new PageBreak()] }),

      // Summary Section
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Validation Summary")]
      }),
      new Paragraph({
        spacing: { after: 120 },
        children: [new TextRun(
          "Complete this section after finishing all validation tasks."
        )]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Overall Results")]
      }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Total Test Items", bold: true })] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("")] })]
              }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Items Passed", bold: true })] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("")] })]
              }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Items Failed", bold: true })] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("")] })]
              }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Items Skipped", bold: true })] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("")] })]
              }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Pass Rate", bold: true })] })]
              }),
              new TableCell({
                borders,
                width: { size: 4680, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("")] })]
              }),
            ]
          }),
        ]
      }),

      new Paragraph({
        spacing: { before: 240, after: 120 },
        children: [new TextRun("")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Critical Issues Found")]
      }),
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun("Document any critical issues that prevent system operation:")]
      }),
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        children: [new TextRun("")]
      }),
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        children: [new TextRun("")]
      }),
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Recommendations")]
      }),
      new Paragraph({
        spacing: { after: 60 },
        children: [new TextRun("Provide recommendations for improvement:")]
      }),
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        children: [new TextRun("")]
      }),
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        children: [new TextRun("")]
      }),
      new Paragraph({
        numbering: { reference: "bullets", level: 0 },
        spacing: { after: 120 },
        children: [new TextRun("")]
      }),

      new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun("Sign-off")]
      }),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3120, 6240],
        rows: [
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Tested By", bold: true })] })]
              }),
              new TableCell({
                borders,
                width: { size: 6240, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("")] })]
              }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Date", bold: true })] })]
              }),
              new TableCell({
                borders,
                width: { size: 6240, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("")] })]
              }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Approved By", bold: true })] })]
              }),
              new TableCell({
                borders,
                width: { size: 6240, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("")] })]
              }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({
                borders,
                width: { size: 3120, type: WidthType.DXA },
                shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun({ text: "Date", bold: true })] })]
              }),
              new TableCell({
                borders,
                width: { size: 6240, type: WidthType.DXA },
                margins: { top: 80, bottom: 80, left: 120, right: 120 },
                children: [new Paragraph({ children: [new TextRun("")] })]
              }),
            ]
          }),
        ]
      }),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("/sessions/modest-sleepy-cori/validation_framework/E2E_Validation_Checklist.docx", buffer);
  console.log("Validation checklist created successfully");
});
