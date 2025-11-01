/* =======================================================
   Página: TermsConditions
   Descripción:
   Página que muestra los Términos y Condiciones del uso 
   de la plataforma Link2Video. Contiene estructura clara, 
   diseño profesional y coherente con el tema global.
   ======================================================= */

import "../styles/TermsConditions.css";

function TermsConditions() {
  return (
    <section className="terms-section">
      <div className="terms-container">
        {/* ===== Título principal ===== */}
        <h1 className="terms-title">Términos y Condiciones</h1>
        <p className="terms-intro">
          Al utilizar Link2Video, aceptas los siguientes términos y condiciones.
          Te recomendamos leerlos cuidadosamente antes de usar nuestros servicios.
        </p>

        {/* ===== Contenido principal ===== */}
        <div className="terms-content">
          <h2>1. Uso del servicio</h2>
          <p>
            Link2Video permite descargar videos desde múltiples plataformas públicas.
            El usuario es responsable de cumplir con las leyes de derechos de autor 
            y términos de servicio de cada sitio desde el cual descargue contenido.
          </p>

          <h2>2. Propiedad intelectual</h2>
          <p>
            Todo el contenido de la web, incluyendo diseño, código y materiales visuales,
            pertenece a Link2Video. Está prohibido su uso no autorizado.
          </p>

          <h2>3. Responsabilidad del usuario</h2>
          <p>
            Link2Video no se hace responsable del uso indebido de los archivos descargados.
            El usuario acepta no emplear el servicio para actividades ilícitas.
          </p>

          <h2>4. Limitación de responsabilidad</h2>
          <p>
            No garantizamos disponibilidad continua del servicio ni ausencia total de errores.
            Nos reservamos el derecho de modificar o suspender la plataforma sin previo aviso.
          </p>

          <h2>5. Modificaciones</h2>
          <p>
            Link2Video podrá actualizar estos términos en cualquier momento.
            Los cambios entrarán en vigor una vez sean publicados en esta página.
          </p>
        </div>
      </div>
    </section>
  );
}

export default TermsConditions;
