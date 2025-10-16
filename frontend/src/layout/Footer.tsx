/**
 * ===========================================
 *  Footer Component - Link2Video
 * ===========================================
 * Este componente representa el pie de página del sitio.
 * 
 *  Características:
 * - Incluye derechos reservados y enlaces a redes sociales.
 * - Diseño 100% responsive usando Bootstrap 5.
 * - Íconos de Bootstrap Icons.
 * - Colores y efectos definidos con variables globales (theme.css).
 * 
 */

import "../styles/Footer.css";

function Footer() {
  return (
    <footer className="footer mt-auto py-3">
      <div className="container d-flex flex-column flex-md-row justify-content-between align-items-center text-center text-md-start">
        {/* Texto de derechos reservados */}
        <p className="mb-2 mb-md-0">
          © {new Date().getFullYear()} <span className="brand">Link2Video</span>. Todos los derechos reservados.
        </p>

        {/* Íconos de redes sociales */}
        <div className="social-icons">
          <a href="#" aria-label="Facebook" title="Facebook" className="me-3">
            <i className="bi bi-facebook"></i>
          </a>
          <a href="#" aria-label="Twitter" title="X" className="me-3">
            <i className="bi bi-twitter"></i>
          </a>
          <a href="https://github.com/IvanPabon29/link2video" target="_blank" title="GitHub" aria-label="GitHub">
            <i className="bi bi-github"></i>
          </a>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
