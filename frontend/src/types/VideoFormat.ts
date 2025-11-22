/* 
  VideoFormat.ts
  ------------------
  Definición de tipos para formatos de video y audio descargables.

*/
export interface VideoFormat {
  itag?: number;

  // Extensión real enviada por backend
  ext?: string;
  extension?: string;

  // Nombre de formato alternativo
  format?: string;

  // VIDEO
  resolution?: string; 
  height?: number;     
  fps?: number;

  // AUDIO
  audioBitrate?: number;
  bitrate?: number;

  // Ambos
  quality?: string;
  filesize?: number;
  type: "video" | "audio";
}
