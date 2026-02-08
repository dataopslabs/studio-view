/**
 * API client for the QA Automation Platform backend.
 * Provides typed methods for all API endpoints.
 */

import axios, { AxiosInstance, AxiosError } from "axios";
import { VideoUploadResponse, SOPDocument, ValidationReport } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

// Error handler
const handleApiError = (error: AxiosError) => {
  console.error("API Error:", error.response?.data || error.message);
  throw error;
};

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    handleApiError(error);
  }
);

/**
 * Video API endpoints
 */
export const videoAPI = {
  /**
   * Upload a video file for analysis
   */
  uploadVideo: async (file: File): Promise<VideoUploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await apiClient.post<VideoUploadResponse>("/api/videos/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },

  /**
   * Get video processing status
   */
  getVideoStatus: async (videoId: string) => {
    const response = await apiClient.get(`/api/videos/${videoId}/status`);
    return response.data;
  },

  /**
   * Get video analysis results
   */
  getVideoAnalysis: async (videoId: string) => {
    const response = await apiClient.get(`/api/videos/${videoId}/analysis`);
    return response.data;
  },

  /**
   * Delete a video
   */
  deleteVideo: async (videoId: string) => {
    const response = await apiClient.delete(`/api/videos/${videoId}`);
    return response.data;
  },
};

/**
 * SOP API endpoints
 */
export const sopAPI = {
  /**
   * Generate SOP from video analysis
   */
  generateSOP: async (videoId: string, detailLevel: string = "detailed") => {
    const response = await apiClient.post("/api/sops/generate", {
      video_id: videoId,
      include_screenshots: true,
      detail_level: detailLevel,
    });
    return response.data;
  },

  /**
   * Get a specific SOP
   */
  getSOP: async (sopId: string): Promise<SOPDocument> => {
    const response = await apiClient.get(`/api/sops/${sopId}`);
    return response.data;
  },

  /**
   * List all SOPs
   */
  listSOPs: async (skip: number = 0, limit: number = 10) => {
    const response = await apiClient.get("/api/sops/", {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * Update an SOP
   */
  updateSOP: async (sopId: string, sop: Partial<SOPDocument>) => {
    const response = await apiClient.put(`/api/sops/${sopId}`, sop);
    return response.data;
  },

  /**
   * Delete an SOP
   */
  deleteSOP: async (sopId: string) => {
    const response = await apiClient.delete(`/api/sops/${sopId}`);
    return response.data;
  },

  /**
   * Export SOP in different formats
   */
  exportSOP: async (sopId: string, format: "json" | "csv" | "markdown" = "json") => {
    const response = await apiClient.post(`/api/sops/${sopId}/export`, null, {
      params: { format },
    });
    return response.data;
  },
};

/**
 * Execution API endpoints
 */
export const executionAPI = {
  /**
   * Run an SOP execution
   */
  runExecution: async (
    sopId: string,
    framework: string = "adk",
    timeout: number = 300
  ) => {
    const response = await apiClient.post("/api/executions/run", {
      sop_id: sopId,
      framework,
      timeout,
      headless: true,
      environment: "test",
    });
    return response.data;
  },

  /**
   * Get execution status
   */
  getExecutionStatus: async (executionId: string) => {
    const response = await apiClient.get(`/api/executions/${executionId}`);
    return response.data;
  },

  /**
   * Get execution logs
   */
  getExecutionLogs: async (executionId: string) => {
    const response = await apiClient.get(`/api/executions/${executionId}/logs`);
    return response.data;
  },

  /**
   * Cancel an execution
   */
  cancelExecution: async (executionId: string) => {
    const response = await apiClient.post(`/api/executions/${executionId}/cancel`);
    return response.data;
  },

  /**
   * Retry a failed execution
   */
  retryExecution: async (executionId: string) => {
    const response = await apiClient.post(`/api/executions/${executionId}/retry`);
    return response.data;
  },
};

/**
 * Validation API endpoints
 */
export const validationAPI = {
  /**
   * Run validation for a SOP
   */
  validateSOP: async (sopId: string, environment: string = "test") => {
    const response = await apiClient.post("/api/validation/validate", {
      sop_id: sopId,
      environment,
      headless: true,
      capture_screenshots: true,
    });
    return response.data;
  },

  /**
   * Get validation results
   */
  getValidationResult: async (validationId: string): Promise<ValidationReport> => {
    const response = await apiClient.get(`/api/validation/${validationId}`);
    return response.data;
  },

  /**
   * Get validation summary
   */
  getValidationSummary: async (validationId: string) => {
    const response = await apiClient.get(`/api/validation/${validationId}/summary`);
    return response.data;
  },

  /**
   * Get validations for a SOP
   */
  getSOPValidations: async (sopId: string) => {
    const response = await apiClient.get(`/api/validation/sop/${sopId}/validations`);
    return response.data;
  },

  /**
   * Get validation dashboard
   */
  getValidationDashboard: async () => {
    const response = await apiClient.get("/api/validation/dashboard");
    return response.data;
  },

  /**
   * Re-run a validation
   */
  rerunValidation: async (validationId: string) => {
    const response = await apiClient.post(`/api/validation/${validationId}/re-run`);
    return response.data;
  },

  /**
   * Export validation results
   */
  exportValidation: async (
    validationId: string,
    format: "json" | "csv" | "html" = "json"
  ) => {
    const response = await apiClient.post(
      `/api/validation/${validationId}/export`,
      null,
      { params: { format } }
    );
    return response.data;
  },
};

/**
 * Health check
 */
export const healthCheck = async () => {
  try {
    const response = await apiClient.get("/health");
    return response.data;
  } catch (error) {
    console.error("Health check failed:", error);
    return null;
  }
};
