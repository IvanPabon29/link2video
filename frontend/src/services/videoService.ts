/*
  videoService.ts
  --------------------------------------
  Servicio para manejar las peticiones del frontend hacia el backend
  relacionadas con la obtención de info del video y la descarga.
*/

import apiClient from "./apiConfig";

//  1. Tipos de datos y payloads

export interface VideoInfoResponse {
  title: string;
  thumbnail: string;
  duration: string;

  formats: Array<{
    format: string;      // mp4, webm, mp3, wav, etc
    quality: string;     // 720p, 1080p, 1440p, 4k, 128kbps, etc
    size?: string;       // "40 MB"
    codec?: string;
    fps?: number;
    type: "audio" | "video";
  }>;
}

export interface DownloadPayload {
  url: string;
  format: string;
  quality: string;
}

export interface DownloadResponse {
  download_url: string;
  filename: string;
}


//  2. Servicio principal 

export const videoService = {

  /**
   * 1. Obtener información y formatos del video
   */
  async getVideoInfo(url: string): Promise<VideoInfoResponse> {
    const response = await apiClient.post<VideoInfoResponse>(
      "/video/info",
      { url }
    );
    return response.data;
  },

  /**
   * 2. Descargar el formato/calidad elegida
   */
  async downloadVideo(payload: DownloadPayload): Promise<DownloadResponse> {
    const response = await apiClient.post<DownloadResponse>(
      "/video/download",
      payload
    );
    return response.data;
  }
  
};
