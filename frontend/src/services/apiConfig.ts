/*
  apiConfig.ts
  --------------------------------------
  Configuración central de Axios para manejar las peticiones HTTP
  hacia el backend.

*/

import axios from "axios";

// Crear instancia de Axios con configuración base
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;
