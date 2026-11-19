/*
  src/utils/errorHandler.ts
  --------------------------------------
  Extrae mensajes de error amigables enviados por FastAPI (campo 'detail'),
  incluyendo respuestas de error cuando Axios usa responseType: 'blob'.
*/

import axios from "axios";

export async function extractApiErrorMessage(
  error: unknown,
  fallbackMessage: string
): Promise<string> {
  if (!axios.isAxiosError(error) || !error.response) {
    return "No se pudo conectar con el servidor. Verifica tu conexión a internet.";
  }

  const data = error.response.data;

  // Caso 1: La respuesta de error vino como Blob (ocurre en /video/download)
  if (data instanceof Blob) {
    try {
      const text = await data.text();
      const parsed = JSON.parse(text);
      if (parsed?.detail) {
        return typeof parsed.detail === "string"
          ? parsed.detail
          : fallbackMessage;
      }
    } catch {
      return fallbackMessage;
    }
  }

  // Caso 2: La respuesta vino como JSON estándar (ocurre en /video/info)
  if (data && typeof data === "object" && "detail" in data) {
    const detail = (data as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    // Si Pydantic devuelve un array de validación (ej. URL mal formada)
    if (Array.isArray(detail) && detail.length > 0 && detail[0]?.msg) {
      return "El formato de la URL ingresada no es válido.";
    }
  }

  return fallbackMessage;
}
