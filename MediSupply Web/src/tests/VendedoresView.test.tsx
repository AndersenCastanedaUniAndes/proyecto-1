import React from "react";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { VendedoresView } from "../components/VendedoresView";

// ✅ Mock estable de configuración (sin dependencias circulares)
jest.mock("../config/config", () => ({
  __esModule: true,
  default: {
    API_BASE_LOGIN_URL: "http://localhost:8001",
  },
}));

// 🧩 Mock global fetch con tipo correcto
const mockFetch = jest.fn() as jest.MockedFunction<typeof fetch>;
globalThis.fetch = mockFetch;

// 🧩 Simular localStorage antes de cada test
beforeEach(() => {
  localStorage.setItem("access_token", "fake_token");
  localStorage.setItem("token_type", "Bearer");
  mockFetch.mockReset();
});

// Limpieza después de cada test
afterEach(() => {
  jest.restoreAllMocks();
  localStorage.clear();
  jest.clearAllMocks();
});

// ✅ Mock de callback de éxito
const mockOnSuccess = jest.fn();

// ✅ Silenciar warnings de act() o refs (Radix UI / react-dialog)
beforeAll(() => {
  const originalError = console.error;
  console.error = (...args) => {
    if (
      /Function components cannot be given refs/i.test(args[0]) ||
      /not wrapped in act/i.test(args[0])
    ) {
      return;
    }
    originalError(...args);
  };
});

describe("🧩 VendedoresView", () => {
  it("debe renderizar el encabezado correctamente", () => {
    render(<VendedoresView onSuccess={mockOnSuccess} />);
    expect(screen.getByText("Gestión de Vendedores")).toBeInTheDocument();
  });



  it("debe cargar vendedores correctamente desde el backend", async () => {
    const mockVendedores = [
      { usuario_id: 1, nombre_usuario: "Carlos Pérez", email: "carlos@test.com" },
      { usuario_id: 2, nombre_usuario: "Ana Gómez", email: "ana@test.com" },
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockVendedores,
    } as Response);

    render(<VendedoresView onSuccess={mockOnSuccess} />);

    await waitFor(() => {
      expect(screen.getByText("Carlos Pérez")).toBeInTheDocument();
      expect(screen.getByText("Ana Gómez")).toBeInTheDocument();
    });
  });
 

});
