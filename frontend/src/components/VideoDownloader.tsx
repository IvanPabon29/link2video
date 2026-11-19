/*
  src/components/VideoDownloader.tsx
  --------------------------------------------------------
  Componente principal del flujo de descarga con manejo de errores
  del backend, descarga mediante Blob e indicador de progreso.
*/

import { useState } from "react";
import { videoService } from "../services/videoService";
import { extractApiErrorMessage } from "../utils/errorHandler";

import VideoInfoCard from "./VideoInfoCard";
import FormatList from "./FormatList";
import type { VideoFormat } from "../types/VideoFormat";
import "./styles/VideoDownloader.css";

const VideoDownloader = () => {
  const [videoUrl, setVideoUrl] = useState("");
  const [videoInfo, setVideoInfo] = useState<{
    title: string;
    thumbnail: string;
    uploader?: string;
    duration: string;
    formats: VideoFormat[];
  } | null>(null);

  // Estados de carga separados
  const [isFetchingInfo, setIsFetchingInfo] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState<number>(0);

  // Mensajes de error
  const [error, setError] = useState("");

  /**
   * 1. Consulta la API para obtener información del video
   */
  const handleFetchInfo = async () => {
    if (!videoUrl.trim()) {
      setError("Por favor ingresa un enlace válido.");
      return;
    }

    setError("");
    setVideoInfo(null);
    setIsFetchingInfo(true);

    try {
      const info = await videoService.getVideoInfo(videoUrl.trim());
      setVideoInfo(info);
    } catch (err) {
      const message = await extractApiErrorMessage(
        err,
        "No se pudo obtener la información del video."
      );
      setError(message);
    } finally {
      setIsFetchingInfo(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !isFetchingInfo) {
      handleFetchInfo();
    }
  };

  /**
   * 2. Solicita la descarga con el formato seleccionado y gestiona el Blob
   */
  const handleDownload = async (format: VideoFormat) => {
    if (isDownloading) return;

    setError("");
    setIsDownloading(true);
    setDownloadProgress(0);

    try {
      const selectedExt = format.extension || format.ext || format.format || "mp4";
      const selectedQuality = format.quality || "720p";

      const { blob, serverFilename } = await videoService.downloadVideo(
        {
          url: videoUrl.trim(),
          format: selectedExt,
          quality: selectedQuality,
        },
        (percent) => setDownloadProgress(percent)
      );

      // Verificación extra: evitar descargar un archivo vacío o corrupto
      if (!blob || blob.size === 0) {
        throw new Error("El archivo recibido está vacío.");
      }

      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;

      // Usar el nombre del servidor si existe, o limpiar el título manteniendo legibilidad
      const cleanTitle = (videoInfo?.title || "video")
        .replace(/[\\/:"*?<>|]+/g, "_")
        .trim()
        .slice(0, 100);

      link.setAttribute(
        "download",
        serverFilename || `${cleanTitle}.${selectedExt}`
      );

      document.body.appendChild(link);
      link.click();

      // Limpieza de memoria en el navegador
      link.remove();
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      const message = await extractApiErrorMessage(
        err,
        "No se pudo completar la descarga del archivo."
      );
      setError(message);
    } finally {
      setIsDownloading(false);
      setDownloadProgress(0);
    }
  };

  return (
    <div className="video-downloader-container">
      <h2 className="video-title">Descargar Video / Audio</h2>

      {/* Campo de texto */}
      <input
        type="text"
        className="video-input"
        placeholder="Ingresa el enlace del video Ej: YouTube, TikTok, Instagram..."
        value={videoUrl}
        onChange={(e) => setVideoUrl(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isFetchingInfo || isDownloading}
      />

      <button
        className="video-btn"
        onClick={handleFetchInfo}
        disabled={isFetchingInfo || isDownloading}
      >
        {isFetchingInfo ? "Analizando enlace..." : "Obtener Video"}
      </button>

      {/* Mensaje de error amigable */}
      {error && (
        <div
          style={{
            color: "#b91c1c",
            backgroundColor: "#fee2e2",
            padding: "0.75rem 1rem",
            borderRadius: "8px",
            marginTop: "1rem",
            border: "1px solid #f87171",
          }}
        >
          {error}
        </div>
      )}

      {/* Indicador de progreso durante la conversión y descarga */}
      {isDownloading && (
        <div style={{ marginTop: "1.25rem" }}>
          <p style={{ marginBottom: "0.5rem", fontWeight: 500 }}>
            {downloadProgress === 0
              ? "Procesando y convirtiendo video (esto puede tardar unos segundos)..."
              : `Descargando archivo a tu dispositivo: ${downloadProgress}%`}
          </p>
          <div
            style={{
              width: "100%",
              height: "10px",
              backgroundColor: "#e5e7eb",
              borderRadius: "999px",
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${downloadProgress === 0 ? 100 : downloadProgress}%`,
                height: "100%",
                backgroundColor: downloadProgress === 0 ? "#f59e0b" : "#10b981",
                transition: "width 0.3s ease",
                opacity: downloadProgress === 0 ? 0.7 : 1,
              }}
            />
          </div>
        </div>
      )}

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
