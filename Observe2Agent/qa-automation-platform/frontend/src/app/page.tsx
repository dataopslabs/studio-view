'use client'

import React, { useState, useEffect, useCallback, useRef } from 'react'

// ─── Types ───────────────────────────────────────────────
interface HealthStatus {
  status: string
  version: string
  environment: string
}

interface WorkflowStep {
  step_number: number
  title: string
  description: string
  action_type: string
  system: string
  ui_elements: string[]
  expected_output: string
  timestamp: number
  duration: number
}

interface DetectedSystem {
  name: string
  system_type: string
  confidence: number
  version: string
}

interface SOPStep {
  step_number: number
  title: string
  description: string
  system_involved: string
  action_type: string
  expected_output: string
}

interface PipelineState {
  stage: number
  status: 'idle' | 'running' | 'completed' | 'failed'
  videoId: string | null
  analysis: {
    workflow_steps: WorkflowStep[]
    systems_detected: DetectedSystem[]
    data_extraction_patterns: { field: string; confidence: number; example: string }[]
    process_summary: string
    video_duration_seconds: number
    frames_analyzed: number
  } | null
  systems: {
    total_systems_found: number
    detected_systems: DetectedSystem[]
    detected_workflows: string[]
  } | null
  sop: {
    id: string
    title: string
    description: string
    steps: SOPStep[]
    systems_involved: string[]
    success_criteria: string
  } | null
  execution: {
    execution_id: string
    status: string
    passed_steps: number
    total_steps: number
    success_rate: number
    step_results: { step_number: number; title: string; status: string; output: string }[]
  } | null
  validation: {
    id: string
    overall_status: string
    passed_steps: number
    total_steps: number
    success_rate: number
    validation_steps: { step_number: number; title: string; status: string; match_score: number; expected: string; actual: string }[]
    recommendations: string[]
  } | null
}

const STAGES = [
  { num: 1, name: 'Upload', icon: '\u2B06' },
  { num: 2, name: 'Analysis', icon: '\uD83D\uDD0D' },
  { num: 3, name: 'Detection', icon: '\uD83D\uDDA5' },
  { num: 4, name: 'SOP Gen', icon: '\uD83D\uDCCB' },
  { num: 5, name: 'ECM Map', icon: '\uD83D\uDD17' },
  { num: 6, name: 'Code Gen', icon: '\uD83D\uDCBB' },
  { num: 7, name: 'Execute', icon: '\u25B6' },
  { num: 8, name: 'Validate', icon: '\u2714' },
]

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'pipeline' | 'results'>('dashboard')
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [healthError, setHealthError] = useState(false)
  const [pipeline, setPipeline] = useState<PipelineState>({
    stage: 0, status: 'idle', videoId: null,
    analysis: null, systems: null, sop: null, execution: null, validation: null,
  })
  const [framework, setFramework] = useState('adk')
  const [dragover, setDragover] = useState(false)
  const [logs, setLogs] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const addLog = useCallback((msg: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`])
  }, [])

  // Health check
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_URL}/health`)
        if (res.ok) {
          const data = await res.json()
          setHealth(data)
          setHealthError(false)
        } else {
          setHealthError(true)
        }
      } catch {
        setHealthError(true)
      }
    }
    checkHealth()
    const interval = setInterval(checkHealth, 15000)
    return () => clearInterval(interval)
  }, [])

  // ─── Simulated Pipeline Run ───
  const runPipeline = useCallback(async (fileName: string) => {
    setPipeline(p => ({ ...p, status: 'running', stage: 1 }))
    setActiveTab('pipeline')
    addLog(`Starting pipeline for: ${fileName}`)

    try {
      // Stage 1: Upload
      addLog('Stage 1: Uploading video...')
      await delay(800)
      const videoId = `video-${randomHex(8)}`
      setPipeline(p => ({ ...p, stage: 1, videoId }))
      addLog(`Video uploaded: ${videoId}`)

      // Stage 2: Analysis
      setPipeline(p => ({ ...p, stage: 2 }))
      addLog('Stage 2: Analyzing video with Gemini AI...')
      await delay(1500)
      const analysis = generateMockAnalysis()
      setPipeline(p => ({ ...p, analysis }))
      addLog(`Analysis complete: ${analysis.workflow_steps.length} steps, ${analysis.systems_detected.length} systems`)

      // Stage 3: System Detection
      setPipeline(p => ({ ...p, stage: 3 }))
      addLog('Stage 3: Detecting enterprise systems...')
      await delay(800)
      const systems = {
        total_systems_found: analysis.systems_detected.length,
        detected_systems: analysis.systems_detected,
        detected_workflows: ['Form Filling', 'System Navigation', 'UI Interaction'],
      }
      setPipeline(p => ({ ...p, systems }))
      addLog(`Detected ${systems.total_systems_found} systems`)

      // Stage 4: SOP Generation
      setPipeline(p => ({ ...p, stage: 4 }))
      addLog('Stage 4: Generating SOP document...')
      await delay(1000)
      const sop = generateMockSOP(videoId, analysis)
      setPipeline(p => ({ ...p, sop }))
      addLog(`SOP generated: ${sop.id}`)

      // Stage 5: ECM Mapping
      setPipeline(p => ({ ...p, stage: 5 }))
      addLog('Stage 5: Mapping to enterprise systems...')
      await delay(700)
      addLog('ECM mapping complete: 100% automation coverage')

      // Stage 6: Code Generation
      setPipeline(p => ({ ...p, stage: 6 }))
      addLog(`Stage 6: Generating ${framework.toUpperCase()} code...`)
      await delay(1000)
      addLog(`Code generated: ${framework === 'adk' ? '3 files' : '1 file'}`)

      // Stage 7: Execution
      setPipeline(p => ({ ...p, stage: 7 }))
      addLog('Stage 7: Executing automation...')
      await delay(1200)
      const execution = generateMockExecution(sop)
      setPipeline(p => ({ ...p, execution }))
      addLog(`Execution ${execution.execution_id}: ${execution.passed_steps}/${execution.total_steps} passed`)

      // Stage 8: Validation
      setPipeline(p => ({ ...p, stage: 8 }))
      addLog('Stage 8: Validating results...')
      await delay(800)
      const validation = generateMockValidation(sop, execution)
      setPipeline(p => ({ ...p, validation, status: 'completed' }))
      addLog(`Validation: ${validation.overall_status.toUpperCase()} - ${(validation.success_rate * 100).toFixed(0)}%`)
      addLog('Pipeline completed successfully!')

    } catch (err) {
      setPipeline(p => ({ ...p, status: 'failed' }))
      addLog(`Pipeline failed: ${err}`)
    }
  }, [framework, addLog])

  const handleFileSelect = useCallback((files: FileList | null) => {
    if (files && files.length > 0) {
      runPipeline(files[0].name)
    }
  }, [runPipeline])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragover(false)
    handleFileSelect(e.dataTransfer.files)
  }, [handleFileSelect])

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
      {/* Header */}
      <header style={{ background: '#1e293b', color: 'white', padding: '16px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 36, height: 36, background: '#2563eb', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: 18 }}>O2</div>
          <div>
            <h1 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>Observe2Agent</h1>
            <p style={{ fontSize: 12, color: '#94a3b8', margin: 0 }}>AI-Powered QA Automation Platform</p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: health ? '#22c55e' : healthError ? '#ef4444' : '#eab308' }} />
            <span style={{ fontSize: 12, color: '#94a3b8' }}>
              {health ? `API v${health.version}` : healthError ? 'API Offline' : 'Connecting...'}
            </span>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav style={{ background: 'white', borderBottom: '1px solid #e5e7eb', padding: '0 32px', display: 'flex', gap: 0 }}>
        {(['dashboard', 'pipeline', 'results'] as const).map(tab => (
          <button
            key={tab}
            className={`nav-tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </nav>

      {/* Content */}
      <main style={{ maxWidth: 1280, margin: '0 auto', padding: '24px 32px' }}>

        {/* ─── Dashboard Tab ─── */}
        {activeTab === 'dashboard' && (
          <div className="fade-in">
            {/* Stats Row */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 24 }}>
              <div className="card stat-card">
                <div className="stat-value" style={{ color: '#2563eb' }}>
                  {pipeline.status === 'completed' ? '1' : '0'}
                </div>
                <div className="stat-label">Pipelines Run</div>
              </div>
              <div className="card stat-card">
                <div className="stat-value" style={{ color: '#16a34a' }}>
                  {pipeline.sop ? pipeline.sop.steps.length : 0}
                </div>
                <div className="stat-label">SOP Steps</div>
              </div>
              <div className="card stat-card">
                <div className="stat-value" style={{ color: '#d97706' }}>
                  {pipeline.systems ? pipeline.systems.total_systems_found : 0}
                </div>
                <div className="stat-label">Systems Detected</div>
              </div>
              <div className="card stat-card">
                <div className="stat-value" style={{ color: pipeline.validation?.overall_status === 'passed' ? '#16a34a' : '#6b7280' }}>
                  {pipeline.validation ? `${(pipeline.validation.success_rate * 100).toFixed(0)}%` : '--'}
                </div>
                <div className="stat-label">Validation Score</div>
              </div>
            </div>

            {/* Upload + Quick Actions */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
              <div className="card">
                <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Upload Business Process Video</h2>
                <div
                  className={`upload-zone ${dragover ? 'dragover' : ''}`}
                  onDragOver={e => { e.preventDefault(); setDragover(true) }}
                  onDragLeave={() => setDragover(false)}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".mp4,.avi,.mov,.mkv,.webm"
                    style={{ display: 'none' }}
                    onChange={e => handleFileSelect(e.target.files)}
                  />
                  <div style={{ fontSize: 48, marginBottom: 12 }}>{'\uD83C\uDFA5'}</div>
                  <p style={{ fontWeight: 600, fontSize: 16, marginBottom: 4 }}>
                    Drop your video here or click to browse
                  </p>
                  <p style={{ color: '#6b7280', fontSize: 13 }}>
                    Supports MP4, AVI, MOV, MKV, WebM (max 500MB)
                  </p>
                </div>

                <div style={{ marginTop: 16, display: 'flex', gap: 12, alignItems: 'center' }}>
                  <label style={{ fontSize: 13, fontWeight: 600, color: '#6b7280' }}>Framework:</label>
                  {['adk', 'selenium', 'playwright'].map(fw => (
                    <button
                      key={fw}
                      className={`btn ${framework === fw ? 'btn-primary' : 'btn-outline'}`}
                      style={{ padding: '6px 14px', fontSize: 13 }}
                      onClick={() => setFramework(fw)}
                    >
                      {fw.toUpperCase()}
                    </button>
                  ))}
                </div>

                <div style={{ marginTop: 16 }}>
                  <button
                    className="btn btn-primary"
                    disabled={pipeline.status === 'running'}
                    onClick={() => runPipeline('demo_sap_purchase_order.mp4')}
                    style={{ width: '100%', justifyContent: 'center', padding: 14 }}
                  >
                    {pipeline.status === 'running' ? (
                      <><div className="spinner" style={{ borderTopColor: 'white' }} /> Running Pipeline...</>
                    ) : (
                      <>{'\u25B6'} Run Demo Pipeline</>
                    )}
                  </button>
                </div>
              </div>

              <div className="card">
                <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Quick Info</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  <InfoItem label="Backend" value={health ? `${health.status} (${health.environment})` : 'Checking...'} ok={!!health} />
                  <InfoItem label="API URL" value={API_URL} ok={true} />
                  <InfoItem label="Framework" value={framework.toUpperCase()} ok={true} />
                  <InfoItem label="Pipeline" value={pipeline.status} ok={pipeline.status !== 'failed'} />
                </div>

                <hr style={{ margin: '16px 0', border: 'none', borderTop: '1px solid #e5e7eb' }} />

                <h4 style={{ fontSize: 13, fontWeight: 600, color: '#6b7280', marginBottom: 8 }}>Pipeline Stages</h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {STAGES.map(s => (
                    <div key={s.num} style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13, padding: '4px 0' }}>
                      <span style={{ width: 20, textAlign: 'center' }}>
                        {pipeline.stage > s.num ? '\u2705' : pipeline.stage === s.num && pipeline.status === 'running' ? '\uD83D\uDD35' : '\u26AA'}
                      </span>
                      <span style={{ color: pipeline.stage >= s.num ? '#1e293b' : '#9ca3af' }}>{s.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ─── Pipeline Tab ─── */}
        {activeTab === 'pipeline' && (
          <div className="fade-in">
            {/* Progress Bar */}
            <div className="card" style={{ marginBottom: 24 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
                <h2 style={{ fontSize: 18, fontWeight: 700 }}>Pipeline Progress</h2>
                <span className={`badge ${pipeline.status === 'completed' ? 'badge-success' : pipeline.status === 'running' ? 'badge-info' : pipeline.status === 'failed' ? 'badge-danger' : 'badge-muted'}`}>
                  {pipeline.status.toUpperCase()}
                </span>
              </div>

              <div className="progress-bar" style={{ marginBottom: 16 }}>
                <div
                  className="progress-fill"
                  style={{
                    width: `${(pipeline.stage / 8) * 100}%`,
                    background: pipeline.status === 'failed' ? '#dc2626' : pipeline.status === 'completed' ? '#16a34a' : '#2563eb',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                {STAGES.map(s => (
                  <div key={s.num} style={{ textAlign: 'center', flex: 1 }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: '50%', margin: '0 auto 4px',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14,
                      background: pipeline.stage > s.num ? '#16a34a' : pipeline.stage === s.num ? '#2563eb' : '#e5e7eb',
                      color: pipeline.stage >= s.num ? 'white' : '#9ca3af',
                    }}>
                      {pipeline.stage > s.num ? '\u2713' : s.num}
                    </div>
                    <div style={{ fontSize: 11, color: pipeline.stage >= s.num ? '#1e293b' : '#9ca3af', fontWeight: pipeline.stage === s.num ? 700 : 400 }}>
                      {s.name}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Analysis Results */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
              {/* Systems Detected */}
              {pipeline.systems && (
                <div className="card fade-in">
                  <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>{'\uD83D\uDDA5'} Detected Systems</h3>
                  {pipeline.systems.detected_systems.map((sys, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12, padding: '8px 0' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600, fontSize: 14 }}>{sys.name}</div>
                        <div style={{ fontSize: 12, color: '#6b7280' }}>{sys.system_type} {sys.version && `\u2022 ${sys.version}`}</div>
                      </div>
                      <div style={{ width: 120 }}>
                        <div className="progress-bar" style={{ height: 6 }}>
                          <div className="progress-fill" style={{
                            width: `${sys.confidence * 100}%`,
                            background: sys.confidence > 0.9 ? '#16a34a' : sys.confidence > 0.7 ? '#d97706' : '#dc2626',
                          }} />
                        </div>
                      </div>
                      <span style={{ fontSize: 13, fontWeight: 600, minWidth: 40, textAlign: 'right' }}>
                        {(sys.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {/* SOP Steps */}
              {pipeline.sop && (
                <div className="card fade-in">
                  <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>{'\uD83D\uDCCB'} SOP: {pipeline.sop.title}</h3>
                  {pipeline.sop.steps.map(step => (
                    <div key={step.step_number} className="step-card">
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span style={{ fontWeight: 600, fontSize: 14 }}>
                          {step.step_number}. {step.title}
                        </span>
                        <span className="badge badge-info" style={{ fontSize: 11 }}>{step.action_type}</span>
                      </div>
                      <p style={{ fontSize: 12, color: '#6b7280', marginBottom: 4 }}>{step.description}</p>
                      <div style={{ fontSize: 11, color: '#2563eb' }}>Expected: {step.expected_output}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Execution + Validation */}
            {(pipeline.execution || pipeline.validation) && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginTop: 24 }}>
                {pipeline.execution && (
                  <div className="card fade-in">
                    <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>{'\u25B6'} Execution Results</h3>
                    <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
                      <div style={{ flex: 1, textAlign: 'center' }}>
                        <div style={{ fontSize: 28, fontWeight: 700, color: '#16a34a' }}>{pipeline.execution.passed_steps}</div>
                        <div style={{ fontSize: 12, color: '#6b7280' }}>Passed</div>
                      </div>
                      <div style={{ flex: 1, textAlign: 'center' }}>
                        <div style={{ fontSize: 28, fontWeight: 700, color: '#dc2626' }}>{pipeline.execution.total_steps - pipeline.execution.passed_steps}</div>
                        <div style={{ fontSize: 12, color: '#6b7280' }}>Failed</div>
                      </div>
                      <div style={{ flex: 1, textAlign: 'center' }}>
                        <div style={{ fontSize: 28, fontWeight: 700, color: '#2563eb' }}>{(pipeline.execution.success_rate * 100).toFixed(0)}%</div>
                        <div style={{ fontSize: 12, color: '#6b7280' }}>Success</div>
                      </div>
                    </div>
                    {pipeline.execution.step_results.map(sr => (
                      <div key={sr.step_number} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '6px 0', fontSize: 13 }}>
                        <span>{sr.status === 'completed' ? '\u2705' : '\u274C'}</span>
                        <span style={{ flex: 1 }}>Step {sr.step_number}: {sr.title}</span>
                      </div>
                    ))}
                  </div>
                )}

                {pipeline.validation && (
                  <div className="card fade-in">
                    <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>{'\u2714'} Validation Report</h3>
                    <div style={{ textAlign: 'center', marginBottom: 16 }}>
                      <div style={{
                        width: 80, height: 80, borderRadius: '50%', margin: '0 auto 8px',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 24, fontWeight: 700, color: 'white',
                        background: pipeline.validation.overall_status === 'passed' ? '#16a34a' : pipeline.validation.overall_status === 'partial' ? '#d97706' : '#dc2626',
                      }}>
                        {(pipeline.validation.success_rate * 100).toFixed(0)}%
                      </div>
                      <span className={`badge ${pipeline.validation.overall_status === 'passed' ? 'badge-success' : pipeline.validation.overall_status === 'partial' ? 'badge-warning' : 'badge-danger'}`}>
                        {pipeline.validation.overall_status.toUpperCase()}
                      </span>
                    </div>
                    {pipeline.validation.validation_steps.map(vs => (
                      <div key={vs.step_number} className={`step-card ${vs.status}`} style={{ padding: '10px 12px', marginBottom: 8 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                          <span style={{ fontWeight: 600 }}>{vs.step_number}. {vs.title}</span>
                          <span style={{ fontWeight: 700, color: vs.status === 'passed' ? '#16a34a' : vs.status === 'partial' ? '#d97706' : '#dc2626' }}>
                            {(vs.match_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                    {pipeline.validation.recommendations.length > 0 && (
                      <div style={{ marginTop: 12, padding: 12, background: '#fffbeb', borderRadius: 8, fontSize: 12 }}>
                        <div style={{ fontWeight: 600, marginBottom: 4, color: '#92400e' }}>Recommendations:</div>
                        {pipeline.validation.recommendations.map((r, i) => (
                          <div key={i} style={{ color: '#78350f' }}>{'\u2022'} {r}</div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Logs */}
            <div className="card" style={{ marginTop: 24 }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>{'\uD83D\uDCDC'} Pipeline Logs</h3>
              <div style={{ background: '#1e293b', borderRadius: 8, padding: 16, maxHeight: 300, overflow: 'auto', fontFamily: 'monospace', fontSize: 12, color: '#94a3b8' }}>
                {logs.length === 0 ? (
                  <div style={{ color: '#475569' }}>No logs yet. Run a pipeline to see output.</div>
                ) : (
                  logs.map((log, i) => (
                    <div key={i} style={{ padding: '2px 0', color: log.includes('failed') || log.includes('Failed') ? '#f87171' : log.includes('complete') || log.includes('passed') || log.includes('success') ? '#4ade80' : '#94a3b8' }}>
                      {log}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* ─── Results Tab ─── */}
        {activeTab === 'results' && (
          <div className="fade-in">
            {pipeline.status !== 'completed' ? (
              <div className="card" style={{ textAlign: 'center', padding: '64px 32px' }}>
                <div style={{ fontSize: 48, marginBottom: 16 }}>{'\uD83D\uDCCA'}</div>
                <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 8 }}>No Results Yet</h2>
                <p style={{ color: '#6b7280', marginBottom: 24 }}>Run a pipeline from the Dashboard to see results here.</p>
                <button className="btn btn-primary" onClick={() => setActiveTab('dashboard')}>Go to Dashboard</button>
              </div>
            ) : (
              <>
                {/* Summary Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 24 }}>
                  <div className="card" style={{ borderLeft: '4px solid #2563eb' }}>
                    <h3 style={{ fontSize: 14, color: '#6b7280', marginBottom: 8 }}>Video Analysis</h3>
                    <div style={{ fontSize: 24, fontWeight: 700 }}>{pipeline.analysis?.workflow_steps.length} Steps</div>
                    <div style={{ fontSize: 13, color: '#6b7280' }}>{pipeline.analysis?.frames_analyzed} frames analyzed</div>
                    <div style={{ fontSize: 13, color: '#6b7280' }}>{pipeline.analysis?.video_duration_seconds}s duration</div>
                  </div>
                  <div className="card" style={{ borderLeft: '4px solid #16a34a' }}>
                    <h3 style={{ fontSize: 14, color: '#6b7280', marginBottom: 8 }}>Execution</h3>
                    <div style={{ fontSize: 24, fontWeight: 700 }}>{pipeline.execution?.passed_steps}/{pipeline.execution?.total_steps} Passed</div>
                    <div style={{ fontSize: 13, color: '#6b7280' }}>Framework: {framework.toUpperCase()}</div>
                    <div style={{ fontSize: 13, color: '#6b7280' }}>ID: {pipeline.execution?.execution_id}</div>
                  </div>
                  <div className="card" style={{ borderLeft: `4px solid ${pipeline.validation?.overall_status === 'passed' ? '#16a34a' : '#d97706'}` }}>
                    <h3 style={{ fontSize: 14, color: '#6b7280', marginBottom: 8 }}>Validation</h3>
                    <div style={{ fontSize: 24, fontWeight: 700 }}>{(pipeline.validation?.success_rate ?? 0) * 100}% Pass Rate</div>
                    <div style={{ fontSize: 13, color: '#6b7280' }}>Status: {pipeline.validation?.overall_status.toUpperCase()}</div>
                    <div style={{ fontSize: 13, color: '#6b7280' }}>ID: {pipeline.validation?.id}</div>
                  </div>
                </div>

                {/* Detailed Table */}
                <div className="card">
                  <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Validation Details</h3>
                  <table className="table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Step</th>
                        <th>Status</th>
                        <th>Match</th>
                        <th>Expected</th>
                        <th>Actual</th>
                      </tr>
                    </thead>
                    <tbody>
                      {pipeline.validation?.validation_steps.map(vs => (
                        <tr key={vs.step_number}>
                          <td style={{ fontWeight: 600 }}>{vs.step_number}</td>
                          <td>{vs.title}</td>
                          <td>
                            <span className={`badge ${vs.status === 'passed' ? 'badge-success' : vs.status === 'partial' ? 'badge-warning' : 'badge-danger'}`}>
                              {vs.status.toUpperCase()}
                            </span>
                          </td>
                          <td style={{ fontWeight: 600 }}>{(vs.match_score * 100).toFixed(0)}%</td>
                          <td style={{ fontSize: 12, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{vs.expected}</td>
                          <td style={{ fontSize: 12, maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{vs.actual}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Data Patterns */}
                {pipeline.analysis?.data_extraction_patterns && (
                  <div className="card" style={{ marginTop: 24 }}>
                    <h3 style={{ fontSize: 18, fontWeight: 700, marginBottom: 16 }}>Extracted Data Patterns</h3>
                    <table className="table">
                      <thead>
                        <tr>
                          <th>Field</th>
                          <th>Confidence</th>
                          <th>Example Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        {pipeline.analysis.data_extraction_patterns.map((p, i) => (
                          <tr key={i}>
                            <td style={{ fontWeight: 600 }}>{p.field}</td>
                            <td>
                              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <div className="progress-bar" style={{ width: 80, height: 6 }}>
                                  <div className="progress-fill" style={{ width: `${p.confidence * 100}%`, background: '#2563eb' }} />
                                </div>
                                {(p.confidence * 100).toFixed(0)}%
                              </div>
                            </td>
                            <td><code style={{ background: '#f3f4f6', padding: '2px 8px', borderRadius: 4, fontSize: 13 }}>{p.example}</code></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer style={{ textAlign: 'center', padding: '24px 32px', color: '#9ca3af', fontSize: 12, borderTop: '1px solid #e5e7eb', marginTop: 48 }}>
        Observe2Agent - AI-Powered QA Automation Platform | Powered by Google Gemini AI
      </footer>
    </div>
  )
}

// ─── Helper Components ───
function InfoItem({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
      <span style={{ color: '#6b7280' }}>{label}</span>
      <span style={{ fontWeight: 600, color: ok ? '#1e293b' : '#dc2626' }}>{value}</span>
    </div>
  )
}

// ─── Helpers ───
function delay(ms: number) { return new Promise(resolve => setTimeout(resolve, ms)) }
function randomHex(len: number) { return Array.from({ length: len }, () => Math.floor(Math.random() * 16).toString(16)).join('') }

function generateMockAnalysis() {
  return {
    workflow_steps: [
      { step_number: 1, title: 'Open SAP ERP System', description: 'User navigates to SAP Fiori Launchpad via browser', action_type: 'navigate', system: 'SAP ERP', ui_elements: ['SAP Fiori Launchpad', 'Browser URL bar'], expected_output: 'SAP dashboard loaded', timestamp: 0, duration: 8.5 },
      { step_number: 2, title: 'Enter Authentication Credentials', description: 'User enters username and password into SAP login form', action_type: 'input', system: 'SAP ERP', ui_elements: ['Username field', 'Password field', 'Sign In button'], expected_output: 'Authentication successful, main menu displayed', timestamp: 8.5, duration: 12.3 },
      { step_number: 3, title: 'Navigate to Purchase Order Module', description: 'User opens Materials Management > Purchase Order > Create (ME21N)', action_type: 'click', system: 'SAP ERP', ui_elements: ['Main Menu', 'Materials Management', 'Create PO button'], expected_output: 'Purchase Order creation form opened', timestamp: 20.8, duration: 6.2 },
      { step_number: 4, title: 'Fill Purchase Order Form', description: 'User enters vendor V-1001, material MAT-5890, quantity 500, delivery date', action_type: 'input', system: 'SAP ERP', ui_elements: ['Vendor field', 'Material field', 'Quantity field'], expected_output: 'PO form populated with all required fields', timestamp: 27.0, duration: 18.7 },
      { step_number: 5, title: 'Submit and Verify Purchase Order', description: 'User clicks Submit, PO number 4500012847 is generated', action_type: 'click', system: 'SAP ERP', ui_elements: ['Submit button', 'Confirmation dialog', 'PO number display'], expected_output: 'PO 4500012847 created, status: Pending Approval', timestamp: 45.7, duration: 10.1 },
    ],
    systems_detected: [
      { name: 'SAP ERP', system_type: 'erp', confidence: 0.96, version: 'S/4HANA 2023' },
      { name: 'Microsoft Outlook', system_type: 'email', confidence: 0.82, version: 'Microsoft 365' },
      { name: 'Chrome Browser', system_type: 'other', confidence: 0.71, version: 'v120' },
    ] as DetectedSystem[],
    data_extraction_patterns: [
      { field: 'PO_Number', confidence: 0.95, example: '4500012847' },
      { field: 'Vendor_ID', confidence: 0.92, example: 'V-1001' },
      { field: 'Material_Code', confidence: 0.90, example: 'MAT-5890' },
      { field: 'Quantity', confidence: 0.88, example: '500' },
      { field: 'Total_Amount', confidence: 0.85, example: '$125,000.00' },
    ],
    process_summary: 'SAP Purchase Order Creation - User logs into SAP S/4HANA, navigates to ME21N, fills vendor/material/quantity details, submits PO, and receives confirmation',
    video_duration_seconds: 55.8,
    frames_analyzed: 167,
  }
}

function generateMockSOP(videoId: string, analysis: ReturnType<typeof generateMockAnalysis>) {
  return {
    id: `sop-${randomHex(8)}`,
    title: 'SAP Purchase Order Creation',
    description: analysis.process_summary,
    steps: analysis.workflow_steps.map(ws => ({
      step_number: ws.step_number,
      title: ws.title,
      description: ws.description,
      system_involved: ws.system,
      action_type: ws.action_type,
      expected_output: ws.expected_output,
    })),
    systems_involved: ['SAP ERP', 'Microsoft Outlook', 'Chrome Browser'],
    success_criteria: 'PO number generated; Status shows Pending Approval; Email confirmation triggered',
  }
}

function generateMockExecution(sop: ReturnType<typeof generateMockSOP>) {
  const stepResults = sop.steps.map(s => ({
    step_number: s.step_number,
    title: s.title,
    status: Math.random() < 0.92 ? 'completed' : 'failed',
    output: Math.random() < 0.92 ? s.expected_output : 'Element not found',
  }))
  const passed = stepResults.filter(s => s.status === 'completed').length
  return {
    execution_id: `exec-${randomHex(8)}`,
    status: passed === stepResults.length ? 'completed' : 'partial',
    passed_steps: passed,
    total_steps: stepResults.length,
    success_rate: passed / stepResults.length,
    step_results: stepResults,
  }
}

function generateMockValidation(
  sop: ReturnType<typeof generateMockSOP>,
  execution: ReturnType<typeof generateMockExecution>
) {
  const validationSteps = sop.steps.map(s => {
    const execStep = execution.step_results.find(e => e.step_number === s.step_number)
    const match = execStep?.status === 'completed' ? 1.0 : 0.16
    return {
      step_number: s.step_number,
      title: s.title,
      status: match >= 0.8 ? 'passed' : match >= 0.5 ? 'partial' : 'failed',
      match_score: match,
      expected: s.expected_output,
      actual: execStep?.output || 'No data',
    }
  })
  const passed = validationSteps.filter(v => v.status === 'passed').length
  const rate = passed / validationSteps.length
  return {
    id: `val-${randomHex(8)}`,
    overall_status: rate >= 0.95 ? 'passed' : rate >= 0.5 ? 'partial' : 'failed',
    passed_steps: passed,
    total_steps: validationSteps.length,
    success_rate: rate,
    validation_steps: validationSteps,
    recommendations: rate < 1 ? ['Review failed steps and add explicit waits for element selectors'] : ['All steps passed. Consider adding edge case tests.'],
  }
}
