/*
  FormatList.tsx
  -------------------------------------------
  Lista de formatos disponibles agrupados y ordenados.
  - Filtra para dejar SOLO MP4, MP3 y M4A.
  - Ordena primero por extensión.
  - Luego ordena por resolución o bitrate.
  - Renderiza secciones separadas: Video / Audio
*/

import FormatButton from "./FormatButton";
import type { VideoFormat } from "../types/VideoFormat";
import "./styles/FormatList.css";

interface Props {
  formats: VideoFormat[];
  onSelect: (format: VideoFormat) => void;
}

const FormatList = ({ formats, onSelect }: Props) => {

  /*
    1. LIMPIAR FORMATS — eliminar formatos inválidos y no deseados
       SOLO PERMITIMOS: MP4, MP3 y M4A
  */
  const cleanFormats = formats.filter(f => {
    const ext = (f.extension || f.format || "").toLowerCase();
    // Lista blanca de formatos permitidos
    const allowedFormats = ["mp4", "mp3", "m4a"];
    
    return allowedFormats.includes(ext) && ext.trim() !== "";
  });

  /*
    2. ORDEN POR TIPO DE FORMATO (extensión)
       Orden deseado: mp4, mp3, m4a
  */
  const formatOrder = ["mp4", "mp3", "m4a"];

  const sortByExtension = (a: VideoFormat, b: VideoFormat) => {
    const extA = (a.extension || a.format || "").toLowerCase();
    const extB = (b.extension || b.format || "").toLowerCase();

    const posA = formatOrder.indexOf(extA);
    const posB = formatOrder.indexOf(extB);

    // Si no está en la lista (pos = -1), lo mandamos al final
    return (posA === -1 ? 999 : posA) - (posB === -1 ? 999 : posB);
  };

  /*
    3. ORDEN INTERNO
       - VIDEO → por resolución (altura)
       - AUDIO → por bitrate
  */
  const sortInternal = (a: VideoFormat, b: VideoFormat) => {
    // VIDEO → mayor resolución arriba
    if (a.type === "video" && b.type === "video") {
      return (b.height || 0) - (a.height || 0);
    }

    // AUDIO → mayor bitrate arriba
    if (a.type === "audio" && b.type === "audio") {
      return (b.bitrate || 0) - (a.bitrate || 0);
    }

    return 0;
  };

  /*
    4. APLICAR ORDEN FINAL
  */
  const finalFormats = [...cleanFormats]
    .sort(sortByExtension)
    .sort(sortInternal);

  /*
    5. AGRUPAR video y audio
  */
  const videoFormats = finalFormats.filter(f => f.type === "video");
  const audioFormats = finalFormats.filter(f => f.type === "audio");

  /*
    6. EVITAR CRASH: siempre usar string seguro en labels
  */
  const getLabelSafe = (f: VideoFormat) =>
    `${(f.extension || f.format || "??").toString().toUpperCase()} • ${f.quality}`;

  return (
    <div className="format-list">
      <h3 className="format-title">Selecciona un formato:</h3>

      {/* SECCIÓN VIDEO */}
      {videoFormats.length > 0 && (
        <>
          <h4 className="format-subtitle">Video (MP4)</h4>
          <div className="format-grid">
            {videoFormats.map((f, index) => (
              <FormatButton
                key={index}
                label={getLabelSafe(f)}
                onClick={() => onSelect(f)}
              />
            ))}
          </div>
        </>
      )}

      {/* SECCIÓN AUDIO */}
      {audioFormats.length > 0 && (
        <>
          <h4 className="format-subtitle">Audio</h4>
          <div className="format-grid">
            {audioFormats.map((f, index) => (
              <FormatButton
                key={index}
                label={getLabelSafe(f)}
                onClick={() => onSelect(f)}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default FormatList;
