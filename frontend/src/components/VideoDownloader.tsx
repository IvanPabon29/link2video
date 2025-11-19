/* =======================================================
   Componente: VideoDownloader.tsx
   Descripción:
   - Permite al usuario pegar un enlace
   - Obtiene la información del video desde el backend
   - Muestra formatos disponibles
   - Permite descargar el formato elegido
   ======================================================= */

import { useState } from "react";
import { videoService } from "../services/videoService"; 
import "./styles/VideoDownloader.css"; // 

function VideoDownloader() {
  /* ----------------------------------------
     Estados
     ---------------------------------------- */
  const [url, setUrl] = useState("");
  const [loadingInfo, setLoadingInfo] = useState(false);
  const [loadingDownload, setLoadingDownload] = useState(false);

  const [videoInfo, setVideoInfo] = useState<any>(null);
  const [error, setError] = useState("");

  /* 1. Obtener información del video */
  const handleGetInfo = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!url.trim()) {
      setError("Por favor ingresa un enlace válido.");
      return;
    }

    try {
      setError("");
      setLoadingInfo(true);

      const info = await videoService.getVideoInfo(url);
      setVideoInfo(info);

    } catch (err) {
      setError("No se pudo obtener la información del video.");
      console.error(err);
    } finally {
      setLoadingInfo(false);
    }
  };

  /* 2. Descargar formato seleccionado */
  const handleDownload = async (format: string, quality: string) => {
    try {
      setLoadingDownload(true);
      setError("");

      const response = await videoService.downloadVideo({
        url,
        format,
        quality
      });

      // Iniciar descarga automática
      window.open(response.download_url, "_blank");

    } catch (err) {
      setError("Error al procesar la descarga.");
      console.error(err);
    } finally {
      setLoadingDownload(false);
    }
  };

  return (
    <div className="video-downloader container mt-5">

      {/* ===== FORMULARIO ===== */}
      <form onSubmit={handleGetInfo} className="mb-4 text-center">
        <h2 className="mb-3">Descargar Video</h2>

        <input
          type="url"
          className="form-control form-control-lg mb-3"
          placeholder="Pega aquí el enlace..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
        />

        <button
          type="submit"
          className="btn btn-primary btn-lg"
          disabled={loadingInfo}
        >
          {loadingInfo ? "Procesando..." : "Obtener Información"}
        </button>

        {error && <p className="text-danger mt-3">{error}</p>}
      </form>

      {/* ===== MOSTRAR INFO DEL VIDEO ===== */}
      {videoInfo && (
        <div className="video-info card p-3 shadow-sm">

          <div className="row">
            <div className="col-md-4 text-center">
              <img
                src={videoInfo.thumbnail}
                alt="Thumbnail"
                className="img-fluid rounded"
              />
            </div>

            <div className="col-md-8">
              <h4>{videoInfo.title}</h4>
              <p className="text-muted">Duración: {videoInfo.duration}</p>
            </div>
          </div>

          <hr />

          {/* ===== FORMATOS ===== */}
          <h5 className="mt-3">Formatos disponibles</h5>

          <div className="row">
            {videoInfo.formats.map((item: any, idx: number) => (
              <div key={idx} className="col-md-4 mt-3">

                <button
                  className="btn btn-outline-success w-100"
                  disabled={loadingDownload}
                  onClick={() => handleDownload(item.format, item.quality)}
                >
                  {item.type === "video" ? "📹" : "🎵"}  
                  {item.format.toUpperCase()} — {item.quality}
                  {item.size ? ` (${item.size})` : ""}
                </button>

              </div>
            ))}
          </div>

          {loadingDownload && (
            <p className="text-center mt-3 text-primary">
              Preparando descarga...
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default VideoDownloader;
