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

      const response = await videoService.downloadVideo({
        url: videoUrl,
        format: format.ext || format.format || "",
        quality: format.quality || "",
      });

      // Descargar el archivo
      const a = document.createElement("a");
      a.href = response.download_url;
      a.download = response.filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch {
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
