import '@testing-library/jest-dom';
import { render, screen, fireEvent } from "@testing-library/react";
import { InventarioView } from "../components/InventarioView";

// Mock de datos reales para los tests
const mockProductos = [
  {
    id: 1,
    nombre: "Ibuprofeno 600mg",
    lote: "L123",
    sku: "SKU-001",
    stock_total: 100,
    stock_minimo: 20,
    status: "disponible",
    bodegas: [
      {
        id: 10,
        nombre: "Bodega Central",
        direccion: "Calle 123",
        cantidad_disponible: 60,
        pasillo: "A",
        estante: "5",
      }
    ],
    fecha_ultima_actualizacion: "2024-01-01",
    proveedor: "ACME",
    categoria: "Medicamentos",
    valor_unitario: 5000,
  },
  {
    id: 2,
    nombre: "Paracetamol 500mg",
    lote: "L999",
    sku: "SKU-999",
    stock_total: 0,
    stock_minimo: 10,
    status: "agotado",
    bodegas: [],
    fecha_ultima_actualizacion: "2024-01-01",
    proveedor: "Bayer",
    categoria: "Medicamentos",
    valor_unitario: 4000,
  }
];

// Mock global de fetch para Jest
beforeEach(() => {
  globalThis.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve(mockProductos),
    })
  ) as unknown as typeof fetch;
});

describe("InventarioView", () => {

  it("renderiza el título y las estadísticas", async () => {
    render(<InventarioView />);

    // Evita error por texto repetido "Inventario"
    const headings = await screen.findAllByRole("heading", { name: /Inventario/i });
    expect(headings.length).toBeGreaterThan(0);

    expect(screen.getByText(/Total Productos/i)).toBeInTheDocument();
    expect(screen.getByText(/Disponibles/i)).toBeInTheDocument();
    expect(screen.getByText(/Existencias Bajas/i)).toBeInTheDocument();
    expect(screen.getByText(/Agotados/i)).toBeInTheDocument();
    expect(screen.getByText(/Valor Total/i)).toBeInTheDocument();

    // FIX: “Bodegas” aparece más de una vez
    const bodegasMatches = screen.queryAllByText(/Bodegas/i);
    expect(bodegasMatches.length).toBeGreaterThan(0);
  });

  it("filtra productos por nombre", async () => {
    render(<InventarioView />);

    const input = await screen.findByPlaceholderText(/Filtrar por nombre/i);

    fireEvent.change(input, { target: { value: "Ibuprofeno" } });

    expect(await screen.findByText(/Ibuprofeno 600mg/i)).toBeInTheDocument();
    expect(screen.queryByText(/Paracetamol 500mg/i)).not.toBeInTheDocument();
  });

  it("muestra mensaje si no hay productos con el filtro", async () => {
    render(<InventarioView />);

    const input = await screen.findByPlaceholderText(/Filtrar por nombre/i);

    fireEvent.change(input, { target: { value: "NoExiste" } });

    expect(await screen.findByText(/No se encontraron productos con ese filtro/i))
      .toBeInTheDocument();
  });

  it("muestra el detalle de inventario al hacer clic en Detalle", async () => {
    render(<InventarioView />);

    // Obtiene todos los botones "Detalle"
    const detalleButtons = await screen.findAllByRole("button", { name: /Detalle/i });

    // Usa el primero
    fireEvent.click(detalleButtons[0]);

    // Título del modal (también puede estar duplicado)
    const modalTitle = await screen.findAllByText(/Detalle de Inventario/i);
    expect(modalTitle.length).toBeGreaterThan(0);

    // Descripción del modal
    const descripcion = await screen.findAllByText(/Información detallada del producto/i);
    expect(descripcion.length).toBeGreaterThan(0);

    // FIX: texto duplicado “Distribución por Bodegas”
    const distribuciones = screen.queryAllByText(/Distribución por Bodegas/i);
    expect(distribuciones.length).toBeGreaterThan(0);
  });

});
