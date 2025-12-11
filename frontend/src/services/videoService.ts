/*
  videoService.ts
  --------------------------------------
  Servicio para manejar las peticiones del frontend hacia el backend
  relacionadas con la obtención de info del video y la descarga.
*/

import apiClient from "./apiConfig";
import type { VideoFormat } from "../types/VideoFormat";

//  1. Tipos de datos y payloads

export interface VideoInfoResponse {
  title: string;
  thumbnail: string;
  duration: string;
  uploader: string;
  platform: string;
  formats: VideoFormat[];
}

export interface DownloadPayload {
  url: string;
  format: string;
  quality: string;
}


// 2. Servicio de video
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
   * 2. Descargar el formato/calidad elegida como BLOB (Archivo binario)
   */
  async downloadVideo(payload: DownloadPayload): Promise<Blob> {
    const response = await apiClient.post(
      "/video/download",
      payload,
      {
        responseType: 'blob', // IMPORTANTE: Esto evita que Axios corrompa el archivo
      }
    );
    return response.data; // Retorna el objeto Blob
  }
  
};