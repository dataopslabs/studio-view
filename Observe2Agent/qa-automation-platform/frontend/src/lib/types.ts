export interface VideoUploadResponse {
  success: boolean;
  video_id: string;
  filename: string;
  size_bytes: number;
  status: string;
}

export interface SOPStep {
  step_number: number;
  title: string;
  description: string;
  system_involved: string;
  action_type: string;
  element_identifier: string;
  expected_output: string;
  timestamp: number;
  duration: number;
}

export interface SOPDocument {
  id: string;
  title: string;
  description: string;
  video_source_id: string;
  systems_involved: string[];
  steps: SOPStep[];
  version: string;
  created_at: string;
  success_criteria: string;
  preconditions: string;
  error_handling: string;
}

export interface ValidationStep {
  step_number: number;
  title: string;
  status: string;
  expected: string;
  actual: string;
  match_score: number;
  duration: number;
}

export interface ValidationReport {
  id: string;
  sop_id: string;
  execution_id: string;
  overall_status: string;
  total_steps: number;
  passed_steps: number;
  failed_steps: number;
  success_rate: number;
  validation_steps: ValidationStep[];
  total_duration: number;
  recommendations: string[];
}
