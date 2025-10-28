import "../styles/About.css";

/* =======================================================
   Página: About (Acerca de)
   Descripción:
   Presenta la información general sobre Link2Video,
   su propósito, filosofía y las ventajas clave del sistema.
   ======================================================= */

function About() {
  const values = [
    {
      icon: "bi bi-lightbulb",
      title: "Nuestra Misión",
      description:
        "Ofrecer una plataforma práctica, moderna y segura que permita descargar videos fácilmente desde múltiples fuentes en diferentes formatos y calidades.",
    },
    {
      icon: "bi bi-people",
      title: "Para Todos",
      description:
        "Diseñado para usuarios de todos los niveles: desde principiantes hasta creadores de contenido que buscan eficiencia y velocidad.",
    },
    {
      icon: "bi bi-shield-lock",
      title: "Seguridad y Privacidad",
      description:
        "No almacenamos tus enlaces ni información personal. Cada descarga se procesa de forma temporal y segura.",
    },
    {
      icon: "bi bi-rocket-takeoff",
      title: "Innovación Constante",
      description:
        "Trabajamos continuamente para integrar más plataformas, mejorar el rendimiento y mantener una experiencia intuitiva.",
    },
  ];

  return (
    <section className="about-section">
      <div className="about-container">
        {/* Título principal */}
        <h1 className="about-title">Acerca de Link2Video</h1>

        {/* Subtítulo introductorio */}
        <p className="about-subtitle">
          Link2Video nació con el objetivo de simplificar la forma en que los
          usuarios descargan y gestionan contenido multimedia en línea, ofreciendo
          una experiencia moderna, ágil y segura.
        </p>

        {/* Grid de valores */}
        <div className="about-grid">
          {values.map((value, index) => (
            <div key={index} className="about-card">
              <i className={`${value.icon} about-icon`}></i>
              <h3 className="about-card-title">{value.title}</h3>
              <p className="about-card-text">{value.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default About;
