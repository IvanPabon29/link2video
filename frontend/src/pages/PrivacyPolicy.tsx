/* =======================================================
   Página: PrivacyPolicy
   Descripción:
   Página que presenta la Política de Privacidad de Link2Video.
   Explica cómo se recopilan, usan y protegen los datos de los usuarios.
   ======================================================= */

import "../styles/PrivacyPolicy.css";

function PrivacyPolicy() {
  return (
    <section className="privacy-section">
      <div className="privacy-container">
        {/* ===== Título principal ===== */}
        <h1 className="privacy-title">Política de Privacidad</h1>
        <p className="privacy-intro">
          En Link2Video, valoramos tu privacidad y protegemos tu información personal.
          A continuación te explicamos cómo manejamos tus datos.
        </p>

        {/* ===== Contenido principal ===== */}
        <div className="privacy-content">
          <h2>1. Información recopilada</h2>
          <p>
            Recopilamos información mínima necesaria, como el correo electrónico y 
            datos técnicos básicos para mejorar la experiencia de uso del sitio.
          </p>

          <h2>2. Uso de la información</h2>
          <p>
            La información recopilada se usa exclusivamente para optimizar nuestros servicios,
            garantizar la seguridad del sitio y responder a consultas de los usuarios.
          </p>

          <h2>3. Protección de datos</h2>
          <p>
            Implementamos medidas de seguridad adecuadas para proteger tus datos personales
            contra accesos no autorizados, pérdida o alteración.
          </p>

          <h2>4. Cookies</h2>
          <p>
            Link2Video puede utilizar cookies para analizar el tráfico del sitio y mejorar 
            la funcionalidad. Puedes desactivar las cookies en la configuración de tu navegador.
          </p>

          <h2>5. Contacto</h2>
          <p>
            Si tienes preguntas sobre esta política, puedes escribirnos a:
            <strong> soporte@link2video.com</strong>
          </p>
        </div>
      </div>
    </section>
  );
}

export default PrivacyPolicy;
