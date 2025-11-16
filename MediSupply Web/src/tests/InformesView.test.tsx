import "@testing-library/jest-dom";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { InformesView } from "../components/InformesView";

// 🧩 Mock de fetch global
globalThis.fetch = jest.fn((url) => {
  if (url.toString().includes("vendedores")) {
    return Promise.resolve({
      ok: true,
      json: async () => [
        { usuario_id: 1, nombre_usuario: "Ana García Rodríguez", email: "ana@example.com", estado: true },
        { usuario_id: 2, nombre_usuario: "Carlos Mendoza", email: "carlos@example.com", estado: true },
      ],
    });
  }

  if (url.toString().includes("ventas")) {
    return Promise.resolve({
      ok: true,
      json: async () => [
        {
          id: 1,
          fecha: "2025-01-15",
          vendedor: "Ana García Rodríguez",
          vendedor_id: 1,
          producto: "Paracetamol 500mg",
          cantidad: 100,
          valor_unitario: 0.25,
          valor_total: 25.0,
          cliente: "Farmacia Central",
          comision: 2.5,
        },
      ],
    });
  }

  return Promise.reject(new Error("Endpoint no reconocido"));
}) as jest.Mock;

describe("InformesView (con datos del backend simulado)", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.setItem("access_token", "fake_token_123");
  });

  it("renderiza correctamente los textos iniciales", async () => {
    render(<InformesView />);
    expect(await screen.findByText(/Informes de Ventas/i)).toBeInTheDocument();
    expect(screen.getByText(/Filtros de Consulta/i)).toBeInTheDocument();
    expect(screen.getByText(/Genera tu Informe de Ventas/i)).toBeInTheDocument();
  });

  it("muestra alerta si los filtros están incompletos", async () => {
    render(<InformesView />);
    window.alert = jest.fn();
    const btnConsultar = await screen.findByRole("button", { name: /Consultar/i });
    fireEvent.click(btnConsultar);
    expect(window.alert).toHaveBeenCalledWith("Por favor completa todos los campos de filtro");
  });



});
