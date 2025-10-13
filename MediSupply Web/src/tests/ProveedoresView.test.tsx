import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ProveedoresView } from "../components/ProveedoresView";

describe("ProveedoresView", () => {
  it("renderiza el título y las estadísticas", () => {
    render(<ProveedoresView onSuccess={jest.fn()} />);
    expect(screen.getByText(/Gestión de Proveedores/i)).toBeInTheDocument();
    expect(screen.getByText(/Total Proveedores/i)).toBeInTheDocument();
    expect(screen.getByText(/Promedio Mensual/i)).toBeInTheDocument();
    expect(screen.getByText(/Estado del Sistema/i)).toBeInTheDocument();
  });

  it("filtra proveedores por nombre", () => {
    render(<ProveedoresView onSuccess={jest.fn()} />);
    const filtroInput = screen.getByPlaceholderText(/Filtrar por nombre o correo/i);
    fireEvent.change(filtroInput, { target: { value: "Pharma" } });
    expect(screen.getByText(/Laboratorios Pharma Plus/i)).toBeInTheDocument();
    expect(screen.queryByText(/Distribuidora Médica Central/i)).not.toBeInTheDocument();
  });

  /*
  it("agrega un nuevo proveedor y llama a onSuccess", async () => {
    const onSuccess = jest.fn();
    render(<ProveedoresView onSuccess={onSuccess} />);
    // Abre el formulario
    fireEvent.click(screen.getByText(/Agregar Nuevo Proveedor/i));
    // Completa el formulario
    fireEvent.change(screen.getByPlaceholderText(/Ingresa el nombre del proveedor/i), { target: { value: "Nuevo Proveedor" } });
    fireEvent.change(screen.getByPlaceholderText(/contacto@proveedor.com/i), { target: { value: "nuevo@proveedor.com" } });
    // Envía el formulario
    fireEvent.click(screen.getByRole('button', { name: /Agregar Proveedor/i }));
    // Espera el resultado
    await waitFor(() => expect(onSuccess).toHaveBeenCalledWith(expect.stringContaining("Nuevo Proveedor")));
    expect(screen.getAllByText(/Nuevo Proveedor/i).length).toBeGreaterThan(0);
  });
  */
});