import "../styles/Footer.css";

function Footer() {
  return (
    <footer className="footer bg-dark text-light py-3 mt-auto">
      <div className="container d-flex flex-column flex-md-row justify-content-between align-items-center">
        <p className="mb-0">© {new Date().getFullYear()} Link2Video. Todos los derechos reservados.</p>
        <div className="social-icons mt-2 mt-md-0">
          <a href="#" className="text-light me-3">
            <i className="bi bi-facebook"></i>
          </a>
          <a href="#" className="text-light me-3">
            <i className="bi bi-twitter"></i>
          </a>
          <a href="#" className="text-light">
            <i className="bi bi-github"></i>
          </a>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
