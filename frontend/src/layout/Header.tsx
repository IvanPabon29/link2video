/**
 * ===========================================
 *  Header Component - Link2Video
 * ===========================================
 * Este componente representa la barra de navegación principal del sitio.
 * 
 * Características:
 * - Incluye el logo y enlaces de navegación a las secciones principales.
 * - Es totalmente responsive gracias a Bootstrap 5.
 * - Usa `NavLink` de React Router para evitar recargas completas.
 * - Cambia el fondo al hacer scroll para mejorar la legibilidad.
 * 
 */

import { useEffect } from "react";
import { Link, NavLink } from "react-router-dom";
import "../styles/Header.css";

function Header() {
  // Efecto para cambiar el color del navbar al hacer scroll
  useEffect(() => {
    const handleScroll = () => {
      const navbar = document.querySelector(".navbar");
      if (window.scrollY > 20) {
        navbar?.classList.add("scrolled");
      } else {
        navbar?.classList.remove("scrolled");
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <header>
      <nav className="navbar navbar-expand-lg navbar-dark custom-navbar shadow-sm">
        <div className="container">
          {/* ===== Logo o nombre de la marca ===== */}
          <Link className="navbar-brand fw-bold" to="/">
            Link2Video
          </Link>

          {/* ===== Botón menú (responsive) ===== */}
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNav"
            aria-controls="navbarNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>

          {/* ===== Enlaces de navegación ===== */}
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item">
                <NavLink to="/" end className="nav-link">
                  Inicio
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink to="/features" className="nav-link">
                  Funcionalidades
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink to="/about" className="nav-link">
                  Acerca de
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink to="/contact" className="nav-link">
                  Contacto
                </NavLink>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </header>
  );
}

export default Header;
