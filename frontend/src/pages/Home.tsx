/* =======================================================
   Página: Home
   Descripción:
   Página principal del sistema Link2Video. Permite al
   usuario pegar el enlace de un video, elegir el formato
   y calidad, y comenzar la descarga. Incluye secciones
   informativas sobre características, pasos y CTA final.
   ======================================================= */

import "../styles/Home.css";
import { useState } from "react";

function Home() {
  // Estado para almacenar el enlace ingresado
  const [videoURL, setVideoURL] = useState("");

  // Maneja el cambio del campo de entrada
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setVideoURL(e.target.value);
  };

  // Maneja el envío del formulario (simulado)
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!videoURL.trim()) {
      alert("Por favor, ingresa un enlace válido.");
      return;
    }
    alert(`Procesando descarga para: ${videoURL}`);
    setVideoURL("");
  };

  return (
    <section className="home-section">
      <div className="home-container">
        {/* ===== HERO PRINCIPAL ===== */}
        <div className="hero text-center">
          <h1 className="hero-title">
            Descarga tus videos favoritos <span>rápido y fácil</span>
          </h1>
          <p className="hero-text">
            Convierte y descarga videos de YouTube, TikTok, Instagram, Facebook, X y más,
            sin instalar nada.
          </p>

          {/* ===== FORMULARIO PRINCIPAL ===== */}
          <form className="hero-form" onSubmit={handleSubmit}>
            <input
              type="url"
              id="link"
              placeholder="Pega aquí el enlace del video..."
              className="hero-input"
              value={videoURL}
              onChange={handleChange}
              required
            />
            <button type="submit" className="hero-btn">
              <i className="bi bi-download me-2"></i> Descargar
            </button>
          </form>
        </div>

        {/* ===== SECCIÓN DE FUNCIONALIDADES ===== */}
        <div className="features-section text-center">
          <h2 className="section-title">¿Por qué elegir Link2Video?</h2>
          <div className="row g-4 mt-4">
            <div className="col-md-4 feature-item">
              <i className="bi bi-lightning-charge-fill feature-icon"></i>
              <h5>Rápido y eficiente</h5>
              <p>Obtén tus descargas en segundos, sin esperas ni registros.</p>
            </div>

            <div className="col-md-4 feature-item">
              <i className="bi bi-display feature-icon"></i>
              <h5>Compatible con todo</h5>
              <p>Funciona en cualquier navegador y dispositivo sin instalar nada.</p>
            </div>

            <div className="col-md-4 feature-item">
              <i className="bi bi-hdmi-fill feature-icon"></i>
              <h5>Alta calidad</h5>
              <p>Descarga en la resolución y formato que prefieras.</p>
            </div>
          </div>
        </div>

        {/* ===== SECCIÓN DE PASOS ===== */}
        <div className="steps-section text-center">
          <h2 className="section-title">¿Cómo funciona?</h2>
          <div className="row g-4 mt-4">
            <div className="col-md-4 step-item">
              <div className="step-circle">1</div>
              <p>Pega el enlace del video que deseas descargar.</p>
            </div>
            <div className="col-md-4 step-item">
              <div className="step-circle">2</div>
              <p>Selecciona el formato y la calidad que prefieras.</p>
            </div>
            <div className="col-md-4 step-item">
              <div className="step-circle">3</div>
              <p>Haz clic en <strong>Descargar</strong> y espera unos segundos.</p>
            </div>
          </div>
        </div>

        {/* ===== SECCIÓN CTA FINAL ===== */}
        <div className="cta-section text-center">
          <h2>¡Empieza a descargar ahora mismo!</h2>
          <button className="cta-btn">
            <i className="bi bi-play-fill me-2"></i> Probar gratis
          </button>
        </div>
      </div>
    </section>
  );
}

export default Home;
