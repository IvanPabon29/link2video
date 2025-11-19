/*
  FormatList.tsx
  -------------------------------------------
  Lista de formatos disponibles. Renderiza un
  FormatButton por cada formato de la API.
*/

import FormatButton from "./FormatButton";
import "./styles/FormatList.css";

interface Format {
    format: string;   // "mp4" | mp3 | webm | wav...
    quality: string; // ej: 720p | 1080p | 2K | 4K...

}

interface Props {
  formats: Format[];
  onSelect: (format: Format) => void;
}

const FormatList = ({ formats, onSelect }: Props) => {
  return (
    <div className="format-list">
      <h3 className="format-title">Selecciona un formato:</h3>

      <div className="format-grid">
        {formats.map((f, index) => (
          <FormatButton
            key={index}
            label={`${f.format.toUpperCase()} • ${f.quality}`}
            onClick={() => onSelect(f)}
          />
        ))}
      </div>
    </div>
  );
};

export default FormatList;
