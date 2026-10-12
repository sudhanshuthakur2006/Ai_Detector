import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes for model inference & humanization
});

export const api = {
  checkHealth: async () => {
    const res = await apiClient.get('/api/health');
    return res.data;
  },

  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  detectText: async (text) => {
    const res = await apiClient.post('/api/detect', { text });
    return res.data;
  },

  humanizeDocument: async ({ sessionId, text, apiKey }) => {
    const headers = {};
    if (apiKey) {
      headers['X-Gemini-Api-Key'] = apiKey;
    }
    const res = await apiClient.post(
      '/api/humanize',
      { session_id: sessionId, text, api_key: apiKey },
      { headers }
    );
    return res.data;
  },

  getDownloadUrl: (sessionId) => {
    return `${API_BASE_URL}/api/download/${sessionId}`;
  },
};
