/*
  src/services/videoService.ts
  --------------------------------------
  Servicio para manejar las peticiones del frontend hacia el backend
  relacionadas con la obtención de info del video y la descarga.
*/

import apiClient from "./apiConfig";
import type { VideoFormat } from "../types/VideoFormat";

//  Tipos de datos y payloads

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

export interface DownloadResult {
  blob: Blob;
  serverFilename?: string;
}

export const videoService = {
  /**
   * 1. Obtener información y formatos del video
   */
  async getVideoInfo(url: string): Promise<VideoInfoResponse> {
    const response = await apiClient.post<VideoInfoResponse>("/video/info", {
      url,
    });
    return response.data;
  },

  /**
   * 2. Descargar el formato/calidad elegida como BLOB con seguimiento de progreso
   */
  async downloadVideo(
    payload: DownloadPayload,
    onProgress?: (percentage: number) => void
  ): Promise<DownloadResult> {
    const response = await apiClient.post("/video/download", payload, {
      responseType: "blob",
      onDownloadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });

    // Intentar extraer el nombre real desde Content-Disposition si CORS lo expone
    let serverFilename: string | undefined;
    const disposition = response.headers["content-disposition"];
    if (disposition && disposition.includes("filename=")) {
      const match = disposition.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i);
      if (match?.[1]) {
        serverFilename = decodeURIComponent(match[1]);
      }
    }

    return {
      blob: response.data,
      serverFilename,
    };
  },
};
