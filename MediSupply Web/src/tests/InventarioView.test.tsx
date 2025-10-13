import '@testing-library/jest-dom';
import { render, screen, fireEvent } from "@testing-library/react";
import { InventarioView } from "../components/InventarioView";

describe("InventarioView", () => {
  it("renderiza el título y las estadísticas", () => {
    render(<InventarioView />);
    expect(screen.getAllByRole('heading', { name: /Inventario/i })[0]).toBeInTheDocument();
    expect(screen.getByText(/Total Productos/i)).toBeInTheDocument();
    expect(screen.getByText(/Disponibles/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Existencias Bajas/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Agotados/i)).toBeInTheDocument();
    expect(screen.getByText(/Valor Total/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Bodegas/i).length).toBeGreaterThan(0);
  });

  it("filtra productos por nombre", () => {
    render(<InventarioView />);
    const filtroInput = screen.getByPlaceholderText(/Filtrar por nombre, SKU, lote o proveedor/i);
    fireEvent.change(filtroInput, { target: { value: "Ibuprofeno" } });
    expect(screen.getByText(/Ibuprofeno 600mg/i)).toBeInTheDocument();
    expect(screen.queryByText(/Paracetamol 500mg/i)).not.toBeInTheDocument();
  });

  it("muestra mensaje si no hay productos con el filtro", () => {
    render(<InventarioView />);
    const filtroInput = screen.getByPlaceholderText(/Filtrar por nombre, SKU, lote o proveedor/i);
    fireEvent.change(filtroInput, { target: { value: "NoExiste" } });
    expect(screen.getByText(/No se encontraron productos con ese filtro/i)).toBeInTheDocument();
  });

it("muestra el detalle de inventario al hacer clic en Detalle", () => {
  render(<InventarioView />);
  const detalleButton = screen.getAllByRole('button', { name: /Detalle/i })[0];
  fireEvent.click(detalleButton);
  expect(screen.getByText(/Detalle de Inventario/i)).toBeInTheDocument();
  expect(screen.getByText(/Información detallada del producto/i)).toBeInTheDocument();
  // Verifica que al menos un elemento existe con ese texto
  expect(screen.getAllByText(/Distribución por Bodegas/i).length).toBeGreaterThan(0);
});
});