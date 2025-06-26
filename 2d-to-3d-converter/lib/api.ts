const API_BASE_URL = typeof window !== 'undefined' 
  ? (window as any).__NEXT_DATA__?.props?.apiUrl || 'http://localhost:8000'
  : 'http://localhost:8000';

export interface ConversionOptions {
  model_type: 'mesh' | 'point_cloud' | 'textured';
  quality: 'low' | 'medium' | 'high';
}

export interface ConversionResponse {
  success: boolean;
  model_path: string;
  file_name: string;
  file_size: number;
  model_type: string;
  quality: string;
}

export interface ModelInfo {
  type: string;
  vertices?: number;
  faces?: number;
  points?: number;
  file_size: number;
  bounds?: number[][];
}

class API {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  async healthCheck(): Promise<{ status: string; services: any }> {
    return this.request<{ status: string; services: any }>('/health');
  }

  async convertImage(
    file: File,
    options: ConversionOptions = { model_type: 'mesh', quality: 'medium' }
  ): Promise<ConversionResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_type', options.model_type);
    formData.append('quality', options.quality);

    const url = `${this.baseURL}/convert`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Image conversion failed:', error);
      throw error;
    }
  }

  async downloadModel(filename: string): Promise<Blob> {
    const url = `${this.baseURL}/download/${filename}`;
    
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.blob();
    } catch (error) {
      console.error('Model download failed:', error);
      throw error;
    }
  }

  async getModelInfo(filename: string): Promise<ModelInfo> {
    return this.request<ModelInfo>(`/model-info/${filename}`);
  }

  // Helper method to convert base64 image to File
  async base64ToFile(base64Data: string, filename: string = 'image.jpg'): Promise<File> {
    // Remove data URL prefix if present
    const base64 = base64Data.replace(/^data:image\/[a-z]+;base64,/, '');
    
    // Convert base64 to blob
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'image/jpeg' });
    
    return new File([blob], filename, { type: 'image/jpeg' });
  }
}

export const api = new API();
export default api; 