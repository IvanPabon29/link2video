/*
  VideoDownloader.tsx
  --------------------------------------------------------
  Componente principal del flujo de descarga:
  1. El usuario ingresa un enlace de YouTube.
  2. Se consulta la API → getVideoInfo().
  3. Se muestra la tarjeta con la información del video.
  4. Se listan los formatos disponibles.
  5. Al seleccionar un formato, se solicita la descarga → downloadVideo().
  6. Se abre el archivo automáticamente.

  Este componente NO guarda historial, ni elimina nada,
  pues el backend eliminará el archivo al finalizar la descarga.
*/

import { useState } from "react";
import { videoService } from "../services/videoService";

import VideoInfoCard from "./VideoInfoCard";
import FormatList from "./FormatList";
import type { VideoFormat } from "../types/VideoFormat";
import "./styles/VideoDownloader.css";


const VideoDownloader = () => {
  // URL ingresada por el usuario
  const [videoUrl, setVideoUrl] = useState("");

  // Información retornada por el backend
  const [videoInfo, setVideoInfo] = useState<{
    title: string;
    thumbnail: string;
    uploader?: string;
    duration: string;
    formats: VideoFormat[];
  } | null>(null);

  // Estado de carga
  const [loading, setLoading] = useState(false);

  // Errores
  const [error, setError] = useState("");

  /**
   * Consulta la API para obtener información del video
   */
  const handleFetchInfo = async () => {
    if (!videoUrl.trim()) {
      setError("Por favor ingresa un enlace válido.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const info = await videoService.getVideoInfo(videoUrl);
      setVideoInfo(info);
    } catch (err) {
      setError("No se pudo obtener la información del video.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Solicita la descarga con el formato seleccionado
   */
  const handleDownload = async (format: VideoFormat) => {
    try {
      setLoading(true);

      // 1. Obtenemos el archivo binario (Blob)
      const blob = await videoService.downloadVideo({
        url: videoUrl,
        format: format.ext || format.format || "mp4", // Asegurar fallback
        quality: format.quality || "720p",
      });

      // 2. Creamos una URL temporal para el Blob
      const url = window.URL.createObjectURL(blob);
      
      // 3. Creamos el link de descarga
      const link = document.createElement("a");
      link.href = url;
      
      // Definimos el nombre del archivo. 
      // Idealmente el backend manda el nombre en headers, pero por simplicidad usamos el título del video.
      const safeTitle = (videoInfo?.title || "video").replace(/[^a-zA-Z0-9]/g, "_");
      const extension = format.ext || format.format || "mp4";
      link.setAttribute("download", `${safeTitle}.${extension}`);
      
      // 4. Ejecutamos click y limpieza
      document.body.appendChild(link);
      link.click();
      
      // Limpieza
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error(err);
      setError("No se pudo iniciar la descarga.");
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="video-downloader-container">
      <h2 className="video-title">Descargar Video / Audio</h2>

      {/* Campo de texto */}
      <input
        type="text"
        className="video-input"
        placeholder="Ingresa el enlace del video Ej: Youtube, Tik Tok, Instagram..."
        value={videoUrl}
        onChange={(e) => setVideoUrl(e.target.value)}
      />

      <button className="video-btn" onClick={handleFetchInfo}>
        {loading ? "Cargando..." : "Obtener Video"}
      </button>

      {/* Error visual */}
      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}

      {/* Mostrar información del video */}
      {videoInfo && (
        <>
          <VideoInfoCard
            thumbnail={videoInfo.thumbnail}
            title={videoInfo.title}
            uploader={videoInfo.uploader ?? ""}
            duration={videoInfo.duration}
          />

          <FormatList
            formats={videoInfo.formats}
            onSelect={handleDownload}
          />
        </>
      )}
    </div>
  );
};

export default VideoDownloader;
