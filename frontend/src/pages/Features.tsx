import "../styles/Features.css";

/* =======================================================
   Página: Features (Funcionalidades)
   Descripción:
   Muestra las principales características reales del sistema
   Link2Video: descarga, conversión y compatibilidad.
   ======================================================= */

function Features() {
  const features = [
    {
      icon: "bi bi-youtube",
      title: "Descarga desde múltiples plataformas",
      description:
        "Compatible con YouTube, Facebook, Instagram, TikTok, Twitter y muchas más. Solo pega el enlace y descarga.",
    },
    {
      icon: "bi bi-sliders",
      title: "Formatos y calidades personalizables",
      description:
        "Elige entre MP4, MP3, WEBM o M4A, y ajusta la calidad del video desde 144p hasta 4K según tus necesidades.",
    },
    {
      icon: "bi bi-lightning-charge",
      title: "Conversión rápida y sin esperas",
      description:
        "Nuestro sistema optimiza la conversión para que tus descargas estén listas en cuestión de segundos.",
    },
    {
      icon: "bi bi-cloud-arrow-down",
      title: "Descarga directa y segura",
      description:
        "Guarda tus archivos directamente en tu dispositivo sin registro ni instalación adicional.",
    },
    {
      icon: "bi bi-display",
      title: "Interfaz simple y moderna",
      description:
        "Pega el enlace, selecciona formato y calidad, y descarga. Así de fácil.",
    },
    {
      icon: "bi bi-phone",
      title: "Compatible con todos tus dispositivos",
      description:
        "Funciona perfectamente en computadores, tablets y teléfonos móviles.",
    },
  ];

  return (
    <section className="features-section">
      <div className="features-container">
        <h1 className="features-title">Funcionalidades Principales</h1>
        <p className="features-subtitle">
          Descubre por qué <strong>Link2Video</strong> es la forma más sencilla
          y rápida de descargar videos en línea.
        </p>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <i className={`${feature.icon} feature-icon`}></i>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Features;
