import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Store API key in session storage
const API_KEY_STORAGE_KEY = 'xe_bot_api_key';

const getStoredApiKey = (): string | null => {
  return sessionStorage.getItem(API_KEY_STORAGE_KEY);
};

const setStoredApiKey = (key: string): void => {
  sessionStorage.setItem(API_KEY_STORAGE_KEY, key);
};

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 900000, // 15 minutes for long operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth header if we have an API key
api.interceptors.request.use((config) => {
  const apiKey = getStoredApiKey();
  if (apiKey) {
    config.headers.Authorization = `Bearer ${apiKey}`;
  }
  return config;
});

// Get or create API key
export const ensureApiKey = async (): Promise<string> => {
  let apiKey = getStoredApiKey();
  if (!apiKey) {
    const response = await axios.post(`${API_BASE_URL}/api/keys/create`, {
      name: `frontend_${Date.now()}`,
      email: null
    });
    apiKey = response.data.api_key;
    setStoredApiKey(apiKey!);
  }
  return apiKey!;
};

export interface Paper {
  id: number;
  arxiv_id: string;
  title: string;
  authors: string[];
  abstract?: string;
  status: string;
  created_at?: string;
}

export interface ArxivSearchResult {
  arxiv_id: string;
  title: string;
  authors: string[];
  summary: string;
  published: string;
}

export interface Segment {
  topic: string;
  topic_category: string;
  key_concepts: string[];
  content: string;
}

export interface VideoInfo {
  video_id: string;
  video_url: string;
  download_url: string;
  file_path: string;
  file_size: number;
  relative_path?: string;
  // Enriched fields from database
  paper_id?: number;
  paper_title?: string;
  paper_arxiv_id?: string;
  animation_type?: string;
  status?: string;
  created_at?: string;
  duration_seconds?: number;
  source?: string;
}

export interface ProcessResult {
  status: string;
  paper: Paper;
  segments: Segment[];
  videos: VideoInfo[];
  message: string;
}

// API Functions
export const searchArxiv = async (query: string, maxResults: number = 10): Promise<ArxivSearchResult[]> => {
  const response = await api.get('/search/arxiv', {
    params: { query, max_results: maxResults }
  });
  return response.data.papers || [];
};

export const searchByDomain = async (domain: string, maxResults: number = 10): Promise<ArxivSearchResult[]> => {
  const response = await api.get('/search/domain', {
    params: { domain, max_results: maxResults }
  });
  return response.data.papers || [];
};

export const processPaper = async (
  arxivId: string, 
  render: boolean = true, 
  quality: string = 'medium'
): Promise<ProcessResult> => {
  const response = await api.post('/process', {
    arxiv_id: arxivId,
    render,
    quality
  });
  return response.data;
};

export const getPapers = async (): Promise<Paper[]> => {
  const response = await api.get('/papers');
  return response.data.papers || [];
};

export const getPaper = async (arxivId: string): Promise<Paper> => {
  const response = await api.get(`/papers/${arxivId}`);
  return response.data;
};

export const getVideos = async (): Promise<VideoInfo[]> => {
  try {
    // Try enriched endpoint first
    const response = await api.get('/videos/enriched');
    return response.data.videos || [];
  } catch {
    // Fallback to basic endpoint
    const response = await api.get('/videos');
    return response.data.videos || [];
  }
};

export const getVideoUrl = (path: string): string => {
  return `${API_BASE_URL}/videos/${path}`;
};

export const getDownloadUrl = (path: string): string => {
  return `${API_BASE_URL}/download/${path}`;
};

// Async job API for long-running operations
export interface JobStatus {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  stage?: string;
  stage_detail?: string;
  progress?: number;
  result?: ProcessResult;
  error?: string;
  videos?: Array<{ video_url: string; download_url: string; type: string; topic?: string; segment_index?: number }>;
  paper?: Paper;
  segments?: Segment[];
  segments_count?: number;
}

export const startAsyncProcess = async (arxivId: string): Promise<{ job_id: string }> => {
  // Ensure we have an API key before making the request
  await ensureApiKey();
  
  const response = await api.post('/api/generate', {
    arxiv_id: arxivId,
    render: true,
    quality: 'low'
  }, { timeout: 30000 }); // 30 second timeout for starting job
  return response.data;
};

export const getJobStatus = async (jobId: string): Promise<JobStatus> => {
  const response = await api.get(`/api/jobs/${jobId}`, { timeout: 60000 }); // 60 second timeout
  return response.data;
};

// Poll job status until completion
export const pollJobUntilComplete = async (
  jobId: string,
  onProgress?: (status: JobStatus) => void,
  pollInterval: number = 3000,  // Poll every 3 seconds
  maxAttempts: number = 600     // Max 30 minutes (600 * 3 seconds)
): Promise<JobStatus> => {
  return new Promise((resolve, reject) => {
    let attempts = 0;
    let consecutiveErrors = 0;
    const maxConsecutiveErrors = 10; // Allow more retries on network errors
    
    const poll = async () => {
      try {
        attempts++;
        const status = await getJobStatus(jobId);
        consecutiveErrors = 0; // Reset on success
        onProgress?.(status);
        
        if (status.status === 'completed') {
          resolve(status);
        } else if (status.status === 'failed') {
          reject(new Error(status.error || 'Job failed'));
        } else if (attempts >= maxAttempts) {
          reject(new Error('Job timed out after 30 minutes'));
        } else {
          setTimeout(poll, pollInterval);
        }
      } catch (err) {
        consecutiveErrors++;
        // On network error, retry multiple times before giving up
        if (consecutiveErrors < maxConsecutiveErrors) {
          console.warn(`Poll attempt ${attempts} failed (error ${consecutiveErrors}), retrying...`);
          setTimeout(poll, pollInterval * 2); // Wait longer on error
        } else {
          reject(new Error(`Connection lost after ${maxConsecutiveErrors} retries: ${err instanceof Error ? err.message : 'Unknown error'}`));
        }
      }
    };
    poll();
  });
};

export default api;
