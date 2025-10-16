import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Componentes globales de estructura
import Header from "./layout/Header";
import Footer from "./layout/Footer";

// Páginas del sitio
import Home from "./pages/Home";
import Features from "./pages/Features";
import Contact from "./pages/Contact";
import NotFound from "./pages/NotFound";

// Estilos base del layout (no globales)
import "./App.css";

function App() {
  return (
    <Router>
      {/* 
        Estructura principal:
        - flex-column para apilar header, contenido y footer
        - min-vh-100 para ocupar toda la altura de la pantalla
      */}
      <div className="app-container d-flex flex-column min-vh-100">
        {/* Header global */}
        <Header />

        {/* Contenido que cambia según la ruta */}
        <main className="app-main flex-grow-1 container mt-5 pt-4">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/features" element={<Features />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>

        {/* Footer global */}
        <Footer />
      </div>
    </Router>
  );
}

export default App;
