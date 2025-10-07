import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { PlanesVentaView } from "../components/PlanesVentaView";

// 🧩 Mock global para evitar el error:
// ReferenceError: ResizeObserver is not defined
(globalThis as any).ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
};

describe("PlanesVentaView", () => {
  it("renderiza el título y las estadísticas", () => {
    render(<PlanesVentaView />);
    expect(screen.getAllByRole('heading', { name: /Planes de Venta/i })[0]).toBeInTheDocument();
    expect(screen.getByText(/Total Planes/i)).toBeInTheDocument();
    expect(screen.getByText(/Valor Total/i)).toBeInTheDocument();
    expect(screen.getByText(/Vendedores Activos/i)).toBeInTheDocument();
    expect(screen.getByText(/Promedio por Plan/i)).toBeInTheDocument();
  });

  it("filtra planes por período", () => {
    render(<PlanesVentaView />);
    const filtroInput = screen.getByPlaceholderText(/Filtrar por período, vendedor o valor/i);
    fireEvent.change(filtroInput, { target: { value: "mensual" } });
    expect(screen.getByText(/Plan Mensual/i)).toBeInTheDocument();
    expect(screen.queryByText(/Plan Trimestral/i)).not.toBeInTheDocument();
  });

  /*
it("agrega un nuevo plan y llama a onSuccess", async () => {
  const onSuccess = jest.fn();
  render(<PlanesVentaView onSuccess={onSuccess} />);

  // Abre el formulario
  fireEvent.click(screen.getByText(/Crear Nuevo Plan de Venta/i));

  // Abre el Select
  fireEvent.click(screen.getByText(/Selecciona el período/i));

  // Espera y selecciona la opción "Mensual" del menú
  const mensualOptions = await screen.findAllByText(/Mensual/i);
  fireEvent.click(mensualOptions[mensualOptions.length - 1]);

  // Ingresa valor de ventas
  fireEvent.change(screen.getByPlaceholderText(/150000.00/i), {
    target: { value: "20000" },
  });

  // Selecciona un vendedor
  fireEvent.click(screen.getByLabelText(/Ana García Rodríguez/i));

  // Envía el formulario
  fireEvent.click(screen.getByRole("button", { name: /Crear Plan de Venta/i }));

  // Espera el resultado del callback
  await waitFor(() =>
    expect(onSuccess).toHaveBeenCalledWith(
      expect.stringContaining("creado exitosamente")
    )
  );

  // Verifica que el nuevo plan aparezca en la lista
  expect(screen.getAllByText(/Plan Mensual/i).length).toBeGreaterThan(0);
});
*/

});
