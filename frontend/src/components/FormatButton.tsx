/*
  FormatButton.tsx
  -------------------------------------------
  Botón para seleccionar un formato específico
  (ej: MP4 1080p, MP3 320kbps...)
*/

import "./styles/FormatButton.css";

interface Props {
  label: string;
  onClick: () => void;
}

const FormatButton = ({ label, onClick }: Props) => {
  return (
    <button className="format-btn" onClick={onClick}>
      {label}
    </button>
  );
};

export default FormatButton;
