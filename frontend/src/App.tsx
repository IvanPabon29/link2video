import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Componentes globales
import Header from "./layout/Header";
import Footer from "./layout/Footer";

// Páginas
import Home from "./pages/Home";
import Features from "./pages/Features";
import Contact from "./pages/Contact";
import NotFound from "./pages/NotFound";

// Estilos
import "./App.css";

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Header />

        {/* Contenedor principal flexible */}
        <main className="app-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/features" element={<Features />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </Router>
  );
}

export default App;
