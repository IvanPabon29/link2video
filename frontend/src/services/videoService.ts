/*
  videoService.ts
  --------------------------------------
  Servicio para manejar las peticiones relacionadas con videos
  hacia el backend.
*/

import apiClient from "./apiConfig";

// Tipos para la solicitud
export interface VideoDownloadPayload {
  url: string;
  format?: string;
  quality?: string;
}

// Tipo para cada video en el backend
export interface VideoData {
  id: string;
  title: string;
  filename: string;
  format: string;
  quality: string;
  platform: string;
  download_url: string;
  created_at: string;
}

// Servicio principal con todas las funciones del frontend
export const videoService = {
  /**
   * 1 Descargar/procesar un video
   */
  async downloadVideo(payload: VideoDownloadPayload): Promise<VideoData> {
    try {
      const response = await apiClient.post<VideoData>(
        "/video/download",
        payload
      );
      return response.data;
    } catch (error: any) {
      console.error("Error en downloadVideo:", error);
      throw error.response?.data || error;
    }
  },

  /**
   * 2 Obtener todos los videos guardados
   */
  async getVideos(): Promise<VideoData[]> {
    try {
      const response = await apiClient.get<VideoData[]>("/video");
      return response.data;
    } catch (error: any) {
      console.error("Error en getVideos:", error);
      throw error.response?.data || error;
    }
  },

  /**
   * 3 Eliminar un video por ID
   */
  async deleteVideo(id: string): Promise<{ message: string }> {
    try {
      const response = await apiClient.delete<{ message: string }>(
        `/video/${id}`
      );
      return response.data;
    } catch (error: any) {
      console.error("Error en deleteVideo:", error);
      throw error.response?.data || error;
    }
  },
};
