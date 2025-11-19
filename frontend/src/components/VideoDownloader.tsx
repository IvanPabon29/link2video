/*
  VideoDownloader.tsx
  -------------------------------------------------
  Componente encargado de:
  - Recibir URL del video
  - Seleccionar formato y calidad
  - Llamar al backend mediante videoService
  - Mostrar estado de carga y resultado
*/

import { useState } from "react";
import { videoService, type VideoData } from "../services/videoService";

const VideoDownloader = () => {
  const [url, setUrl] = useState("");
  const [format, setFormat] = useState("mp4");
  const [quality, setQuality] = useState("1080p");

  const [loading, setLoading] = useState(false);
  const [videoProcessed, setVideoProcessed] = useState<VideoData | null>(null);
  const [error, setError] = useState("");

  const handleDownload = async () => {
    if (!url.trim()) {
      setError("Debes ingresar una URL válida.");
      return;
    }

    setLoading(true);
    setError("");
    setVideoProcessed(null);

    try {
      const result = await videoService.downloadVideo({
        url,
        format,
        quality,
      });

      setVideoProcessed(result);
    } catch (err: any) {
      setError(err.detail || "Ocurrió un error procesando el video.");
    }

    setLoading(false);
  };

  return (
    <div className="w-full max-w-xl mx-auto p-5 bg-white rounded-xl shadow-lg">
      <h2 className="text-2xl font-bold text-center mb-4">
        Descargar Video 🔽
      </h2>

      {/* URL INPUT */}
      <label className="block text-sm font-medium mb-1">URL del video</label>
      <input
        type="text"
        placeholder="Pega aquí el enlace de YouTube / TikTok / Instagram"
        className="w-full border rounded-md px-3 py-2 mb-4"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />

      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* FORMATO */}
        <div>
          <label className="block text-sm font-medium mb-1">Formato</label>
          <select
            className="w-full border rounded-md px-2 py-2"
            value={format}
            onChange={(e) => setFormat(e.target.value)}
          >
            <option value="mp4">MP4</option>
            <option value="mp3">MP3</option>
            <option value="webm">WEBM</option>
          </select>
        </div>

        {/* CALIDAD */}
        <div>
          <label className="block text-sm font-medium mb-1">Calidad</label>
          <select
            className="w-full border rounded-md px-2 py-2"
            value={quality}
            onChange={(e) => setQuality(e.target.value)}
          >
            <option value="144p">144p</option>
            <option value="360p">360p</option>
            <option value="720p">720p</option>
            <option value="1080p">1080p</option>
          </select>
        </div>
      </div>

      {/* BOTÓN */}
      <button
        disabled={loading}
        onClick={handleDownload}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-gray-400"
      >
        {loading ? "Procesando..." : "Descargar Video"}
      </button>

      {/* ERROR */}
      {error && (
        <p className="text-red-500 text-center mt-3 font-medium">{error}</p>
      )}

      {/* RESULTADO */}
      {videoProcessed && (
        <div className="mt-6 p-4 border rounded-md bg-gray-50">
          <h3 className="font-bold text-lg mb-2">
            Video procesado correctamente ✅
          </h3>

          <p>
            <strong>Título:</strong> {videoProcessed.title}
          </p>
          <p>
            <strong>Formato:</strong> {videoProcessed.format}
          </p>
          <p>
            <strong>Calidad:</strong> {videoProcessed.quality}
          </p>
          <p>
            <strong>Plataforma:</strong> {videoProcessed.platform}
          </p>

          <a
            href={videoProcessed.download_url}
            download
            className="mt-4 block bg-green-600 text-white text-center py-2 rounded-md font-semibold hover:bg-green-700 transition"
          >
            Descargar archivo
          </a>
        </div>
      )}
    </div>
  );
};

export default VideoDownloader;
