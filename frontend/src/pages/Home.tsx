/*
  Home.tsx
  ----------------------------------------
  Página principal del sistema Link2Video. Permite al
  usuario pegar el enlace de un video, elegir el formato
  y calidad, y comenzar la descarga.

  -Rendeiza elcomponente VideoDownloader.
*/

import VideoDownloader from "../components/VideoDownloader";

const Home = () => {
  return (
    <main style={{ padding: "2rem" }}>
      <VideoDownloader />
    </main>
  );
};

export default Home;
