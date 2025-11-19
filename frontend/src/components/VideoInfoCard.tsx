/*
  VideoInfoCard.tsx
  -------------------------------------------
  Tarjeta informativa que muestra los datos del
  video consultado: miniatura, título, autor y
  duración. Totalmente presentacional.
*/

import "./styles/VideoInfoCard.css";

interface Props {
  thumbnail: string;
  title: string;
  duration: string;
}

const VideoInfoCard = ({ thumbnail, title, duration }: Props) => {
  return (
    <div className="video-info-card">
      <img src={thumbnail} alt={title} className="video-info-thumb" />

      <div className="video-info-details">
        <h3 className="video-info-title">{title}</h3>
        <span className="video-info-duration">{duration}</span>
      </div>
    </div>
  );
};

export default VideoInfoCard;
