import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Componentes globales
import Header from "./components/Header";
import Footer from "./components/Footer";

// Páginas
import Home from "./pages/Home";
import Features from "./pages/Features";
import Contact from "./pages/Contact";
import NotFound from "./pages/NotFound";

function App() {
  return (
    <Router>
      <div className="d-flex flex-column min-vh-100">
        <Header />

        {/* Contenido dinámico según la ruta */}
        <main className="flex-grow-1 container mt-5 pt-4">
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
