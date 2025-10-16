import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { VendedoresView } from "../components/VendedoresView";

describe("VendedoresView", () => {
  it("renderiza el título y las estadísticas", () => {
    render(<VendedoresView />);
    expect(screen.getByText(/Gestión de Vendedores/i)).toBeInTheDocument();
    expect(screen.getByText(/Total Vendedores/i)).toBeInTheDocument();
    expect(screen.getByText(/Vendedores Activos/i)).toBeInTheDocument();
    expect(screen.getByText(/Vendedores Inactivos/i)).toBeInTheDocument();
    expect(screen.getByText(/Nuevos Este Mes/i)).toBeInTheDocument();
  });

  it("filtra vendedores por nombre", () => {
    render(<VendedoresView />);
    const filtroInput = screen.getByPlaceholderText(/Filtrar por nombre o correo/i);
    fireEvent.change(filtroInput, { target: { value: "Ana" } });
    expect(screen.getByText(/Ana García Rodríguez/i)).toBeInTheDocument();
    expect(screen.queryByText(/Carlos Mendoza Silva/i)).not.toBeInTheDocument();
  });
/*
  it("agrega un nuevo vendedor y llama a onSuccess", async () => {
    const onSuccess = jest.fn();
    render(<VendedoresView onSuccess={onSuccess} />);
    // Abre el formulario
    fireEvent.click(screen.getByText(/Agregar Nuevo Vendedor/i));
    // Completa el formulario
    fireEvent.change(screen.getByPlaceholderText(/Nombre completo del vendedor/i), { target: { value: "Nuevo Vendedor" } });
    fireEvent.change(screen.getByPlaceholderText(/vendedor@medisupply.com/i), { target: { value: "nuevo@medisupply.com" } });
    fireEvent.change(screen.getByPlaceholderText(/Contraseña temporal/i), { target: { value: "123456" } });
    // Envía el formulario
    fireEvent.click(screen.getByRole('button', { name: /Agregar Vendedor/i }));
    // Espera el resultado
 
 
    await waitFor(() => expect(onSuccess).toHaveBeenCalledWith(expect.stringContaining("Nuevo Vendedor")));

// Verifica que "Nuevo Vendedor" aparece en la lista (por ejemplo, en una celda de tabla)
const vendedorEnLista = screen.getAllByText(/Nuevo Vendedor/i).find(
  el => el.tagName === "TD" || el.tagName === "DIV"
);
expect(vendedorEnLista).toBeInTheDocument();

  });
  */
});