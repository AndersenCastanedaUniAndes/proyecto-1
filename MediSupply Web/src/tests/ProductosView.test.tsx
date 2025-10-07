import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ProductosView } from "../components/ProductosView";

describe("ProductosView", () => {
  it("renderiza el título y las estadísticas", () => {
    render(<ProductosView />);
    expect(screen.getAllByText(/Catálogo de Productos/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Total Productos/i)).toBeInTheDocument();
    expect(screen.getByText(/Almacenamiento/i)).toBeInTheDocument();
    expect(screen.getByText(/Proveedores Únicos/i)).toBeInTheDocument();
    expect(screen.getByText(/Países de Origen/i)).toBeInTheDocument();
  });

  it("filtra productos por nombre", () => {
    render(<ProductosView />);
    const filtroInput = screen.getByPlaceholderText(/Filtrar por nombre o proveedor/i);
    fireEvent.change(filtroInput, { target: { value: "Paracetamol" } });
    expect(screen.getByText(/Paracetamol 500mg/i)).toBeInTheDocument();
    expect(screen.queryByText(/Vacuna COVID-19/i)).not.toBeInTheDocument();
  });

  /*
  it("agrega un nuevo producto y llama a onSuccess", async () => {
    const onSuccess = jest.fn();
    render(<ProductosView onSuccess={onSuccess} />);
    // Abre el formulario
    fireEvent.click(screen.getByText(/Agregar Nuevo Producto/i));
    // Completa el formulario
    fireEvent.change(screen.getByPlaceholderText(/Nombre del producto/i), { target: { value: "Nuevo Producto" } });
    fireEvent.change(screen.getByPlaceholderText(/Número de lote/i), { target: { value: "NP2024001" } });
    fireEvent.change(screen.getByPlaceholderText(/Número serial/i), { target: { value: "NP-2024-001" } });
    fireEvent.click(screen.getByText(/Selecciona un proveedor/i));
    fireEvent.click(screen.getByText(/Laboratorios Pharma Plus/i));
    fireEvent.click(screen.getByText(/Selecciona un país/i));
    fireEvent.click(screen.getByText(/Colombia/i));
    fireEvent.change(screen.getByPlaceholderText("0.00"), { target: { value: "1.00" } });
    fireEvent.change(screen.getByPlaceholderText("0"), { target: { value: "10" } });
    fireEvent.click(screen.getByText(/Unidad de medida/i));
    fireEvent.click(screen.getByText(/Unidad/i));
    fireEvent.click(screen.getByText(/Tipo de almacenamiento/i));
    fireEvent.click(screen.getByText(/Ambiente/i));
    // Envía el formulario
    fireEvent.click(screen.getByRole('button', { name: /Agregar Producto/i }));
    // Espera el resultado
    await waitFor(() => expect(onSuccess).toHaveBeenCalledWith(expect.stringContaining("Nuevo Producto")));
    expect(screen.getAllByText(/Nuevo Producto/i).length).toBeGreaterThan(0);
  });
  */
});