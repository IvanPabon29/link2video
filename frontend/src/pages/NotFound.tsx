/**
 * Página 404 - NotFound
 * ------------------------------------------
 * Muestra un mensaje cuando el usuario intenta acceder
 * a una ruta que no existe dentro del sistema.
 *
 */

import { Link } from "react-router-dom";
import "../styles/NotFound.css";

function NotFound() {
  return (
    <div className="notfound-container">
      <div className="notfound-content">
        <i className="bi bi-exclamation-triangle notfound-icon"></i>
        <h1 className="notfound-title">404</h1>
        <p className="notfound-text">Lo sentimos, la página que buscas no existe.</p>

        <Link to="/" className="notfound-btn">
          <i className="bi bi-house-door me-2"></i>
          Volver al inicio
        </Link>
      </div>
    </div>
  );
}

export default NotFound;
