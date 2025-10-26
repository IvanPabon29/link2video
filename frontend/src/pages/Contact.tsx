/* =======================================================
   Página: Contact
   Descripción:
   Página de contacto con formulario funcional, íconos
   y diseño coherente con el tema global (theme.css).
   ======================================================= */

import "../styles/Contact.css";
import { useState } from "react";

function Contact() {
  // Estado para manejar los datos del formulario
  const [formData, setFormData] = useState({
    nombre: "",
    email: "",
    mensaje: "",
  });

  // Maneja los cambios en los campos del formulario
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // Maneja el envío del formulario
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Formulario enviado:", formData);
    alert("¡Gracias por contactarnos! Te responderemos pronto.");
    setFormData({ nombre: "", email: "", mensaje: "" });
  };

  return (
    <section className="contact-section">
      <div className="contact-container">
        {/* Título principal */}
        <h1 className="contact-title">Contáctanos</h1>
        <p className="contact-text">
          Si tienes dudas, comentarios o sugerencias, completa el formulario o escríbenos a:
          <strong> soporte@link2video.com</strong>
        </p>

        <div className="contact-content">
          {/* Información de contacto */}
          <div className="contact-info">
            <div className="info-item">
              <i className="bi bi-geo-alt-fill"></i>
              <p>Bogotá, Colombia</p>
            </div>
            <div className="info-item">
              <i className="bi bi-envelope-fill"></i>
              <p>soporte@link2video.com</p>
            </div>
            <div className="info-item">
              <i className="bi bi-telephone-fill"></i>
              <p>+57 300 123 4567</p>
            </div>
          </div>

          {/* Formulario de contacto */}
          <form className="contact-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="nombre">Nombre</label>
              <input
                type="text"
                id="nombre"
                name="nombre"
                value={formData.nombre}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="correo">Correo electrónico</label>
              <input
                type="email"
                id="correo"
                name="correo"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="mensaje">Mensaje</label>
              <textarea
                id="mensaje"
                name="mensaje"
                rows={4}
                value={formData.mensaje}
                onChange={handleChange}
                required
              ></textarea>
            </div>

            <button type="submit" className="contact-btn">
              <i className="bi bi-send-fill me-2"></i> Enviar mensaje
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}

export default Contact;
