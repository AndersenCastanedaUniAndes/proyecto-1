import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ProveedoresView } from "../components/ProveedoresView";
import config from "../config/config";

beforeEach(() => {
  jest.clearAllMocks();
});

test("filtra proveedores por nombre", async () => {
  // 🔹 Mock de respuesta de la API
  const mockProveedores = [
    { id: 1, nombre: "Laboratorios Pharma Plus", correoElectronico: "pharma@plus.com", fechaCreacion: "2025-10-20T00:00:00" },
    { id: 2, nombre: "Distribuidora Médica Central", correoElectronico: "ventas@medicacentral.com", fechaCreacion: "2025-10-19T00:00:00" },
  ];

  // 🔹 Mockear fetch
  globalThis.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve(mockProveedores),
    })
  ) as jest.Mock;

  render(<ProveedoresView onSuccess={jest.fn()} />);

  // 🔹 Esperar a que los proveedores se carguen
  await waitFor(() => {
    expect(screen.getByText(/Laboratorios Pharma Plus/i)).toBeInTheDocument();
  });

  // 🔹 Filtrar por nombre
  const filtroInput = screen.getByPlaceholderText(/Filtrar por nombre o correo/i);
  fireEvent.change(filtroInput, { target: { value: "Pharma" } });

  // 🔹 Verificar resultados filtrados
  expect(screen.getByText(/Laboratorios Pharma Plus/i)).toBeInTheDocument();
  expect(screen.queryByText(/Distribuidora Médica Central/i)).not.toBeInTheDocument();
});
