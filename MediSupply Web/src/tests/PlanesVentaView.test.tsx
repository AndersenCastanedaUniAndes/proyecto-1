import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { PlanesVentaView } from "../components/PlanesVentaView";

// Datos simulados
const mockPlanes = [
  {
    id: 1,
    periodo: "mensual",
    valor_ventas: 150000,
    vendedores: [
      { usuario_id: 1, nombre_usuario: "Vendedor 1", email: "vendedor1@example.com", estado: true },
    ],
    fecha_creacion: "2025-01-01",
    estado: "activo",
  },
  {
    id: 2,
    periodo: "trimestral",
    valor_ventas: 450000,
    vendedores: [
      { usuario_id: 2, nombre_usuario: "Vendedor 2", email: "vendedor2@example.com", estado: true },
    ],
    fecha_creacion: "2025-01-02",
    estado: "activo",
  },
];

const mockVendedores = [
  { usuario_id: 1, nombre_usuario: "Vendedor 1", email: "vendedor1@example.com", estado: true },
  { usuario_id: 2, nombre_usuario: "Vendedor 2", email: "vendedor2@example.com", estado: true },
  { usuario_id: 3, nombre_usuario: "Vendedor 3", email: "vendedor3@example.com", estado: false },
];

// Mock de config
jest.mock("../config/config", () => ({
  API_BASE_PLANES_URL: "http://localhost:3000/api",
  API_BASE_LOGIN_URL: "http://localhost:3000/auth",
}));

// Configuración inicial
beforeEach(() => {
  Storage.prototype.getItem = jest.fn((key) => {
    if (key === "access_token") return "fake-token";
    return null;
  });
  window.HTMLElement.prototype.scrollIntoView = jest.fn();
});

const mockFetch = () => {
  globalThis.fetch = jest.fn((url) => {
    if (url.includes("/planes_venta/")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockPlanes),
      });
    } else if (url.includes("/vendedores")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockVendedores),
      });
    } else {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({}),
      });
    }
  }) as jest.Mock;
};

describe("PlanesVentaView", () => {

  /*
  it("renderiza correctamente con datos simulados", async () => {
    mockFetch();
    render(<PlanesVentaView />);

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /Planes de Venta/i, level: 1 })).toBeInTheDocument();
    });

    // Espera a que los datos se carguen y se rendericen
    await waitFor(() => {
      expect(screen.getByText("2")).toBeInTheDocument();
      expect(screen.getByText(/\$600,000/i)).toBeInTheDocument();
      expect(screen.getByText(/\$300,000/i)).toBeInTheDocument();
    });
  });
*/
  it("filtra planes por texto ingresado", async () => {
    mockFetch();
    render(<PlanesVentaView />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Filtrar por vendedor o valor/i)).toBeInTheDocument();
    });

    const filterInput = screen.getByPlaceholderText(/Filtrar por vendedor o valor/i);
    fireEvent.change(filterInput, { target: { value: "mensual" } });

    await waitFor(() => {
      expect(screen.getByText(/Mensual/i)).toBeInTheDocument();
      expect(screen.queryByText(/Trimestral/i)).not.toBeInTheDocument();
    });
  });

  /*
  it("permite crear un nuevo plan", async () => {
    mockFetch();
    render(<PlanesVentaView />);

    const createButton = screen.getByText(/Crear Nuevo Plan de Venta/i);
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByText(/Selecciona período/i)).toBeInTheDocument();
    });

    const periodoSelect = screen.getByText(/Selecciona período/i);
    fireEvent.click(periodoSelect);

    const anualOptions = screen.getAllByText(/Anual/i);
    fireEvent.click(anualOptions[1]);

    const valorInput = screen.getByPlaceholderText(/150000/i);
    fireEvent.change(valorInput, { target: { value: "600000" } });

    const vendedorCheckbox = screen.getByLabelText(/Vendedor 3/i);
    fireEvent.click(vendedorCheckbox);

    const submitButton = screen.getByText(/Crear Plan/i);
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/planes_venta"),
        expect.objectContaining({
          method: "POST",
        })
      );
    });
  });

  */
  it("permite editar un plan existente", async () => {
    mockFetch();
    render(<PlanesVentaView />);

    await waitFor(() => {
      expect(screen.getByText(/Mensual/i)).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole("button");
    fireEvent.click(editButtons[1]);

    await waitFor(() => {
      expect(screen.getByDisplayValue("150000")).toBeInTheDocument();
    });

    const valorInput = screen.getByDisplayValue("150000");
    fireEvent.change(valorInput, { target: { value: "200000" } });

    const saveButton = screen.getByText(/Guardar/i);
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/planes_venta/1"),
        expect.objectContaining({
          method: "PUT",
        })
      );
    });
  });

  it("permite eliminar un plan", async () => {
    mockFetch();
    window.confirm = jest.fn(() => true);
    render(<PlanesVentaView />);

    await waitFor(() => {
      expect(screen.getByText(/Mensual/i)).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole("button");
    fireEvent.click(deleteButtons[2]);

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining("/planes_venta/1"),
        expect.objectContaining({
          method: "DELETE",
        })
      );
    });
  });

  /*
  it("muestra mensaje de error si falla el servidor", async () => {
    globalThis.fetch = jest.fn(() =>
      Promise.reject(new Error("Error del servidor"))
    ) as jest.Mock;

    render(<PlanesVentaView />);

    await waitFor(() => {
      expect(screen.getByText(/No se pudieron cargar los datos desde el servidor/i)).toBeInTheDocument();
    });
  });
  */
});
