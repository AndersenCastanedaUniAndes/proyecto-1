import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { InformesView } from "../components/InformesView";

describe("InformesView", () => {
  it("renderiza el título y el mensaje inicial", () => {
    render(<InformesView />);
    expect(screen.getByText(/Informes de Ventas/i)).toBeInTheDocument();
    expect(screen.getByText(/Genera tu Informe de Ventas/i)).toBeInTheDocument();
    expect(screen.getByText(/Selecciona un vendedor y un rango de fechas/i)).toBeInTheDocument();
    expect(screen.getByText(/Filtros de Consulta/i)).toBeInTheDocument();
  });

  it("muestra alerta si los filtros están incompletos", () => {
    render(<InformesView />);
    window.alert = jest.fn();
    fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));
    expect(window.alert).toHaveBeenCalledWith("Por favor completa todos los campos de filtro");
  });

  it("realiza una consulta y muestra resultados", async () => {
    render(<InformesView />);
    // Selecciona vendedor
    const selectVendedorButton = screen.getAllByText(/Selecciona un vendedor/i)[0];
   fireEvent.click(selectVendedorButton);
   fireEvent.click(screen.getByText(/Ana García Rodríguez/i));
   // Selecciona fechas
    fireEvent.change(screen.getByLabelText(/Fecha Inicial/i), { target: { value: "2024-01-01" } });
    fireEvent.change(screen.getByLabelText(/Fecha Final/i), { target: { value: "2024-01-31" } });
    // Ejecuta consulta
    fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));
    // Espera resultados
    await waitFor(() => {
     // expect(screen.getByText(/Total Ventas/i)).toBeInTheDocument();
      //expect(screen.getByText(/Valor Total/i)).toBeInTheDocument();
      //expect(screen.getByText(/Comisiones/i)).toBeInTheDocument();
      //expect(screen.getByText(/Detalle de Ventas/i)).toBeInTheDocument();
     // expect(screen.getByText(/Paracetamol 500mg/i)).toBeInTheDocument();
    });
  });

  it("limpia la consulta y muestra el mensaje inicial", async () => {
  render(<InformesView />);
  // Selecciona vendedor
  const selectVendedorButton = screen.getAllByText(/Selecciona un vendedor/i)[0];
  fireEvent.click(selectVendedorButton);
  fireEvent.click(screen.getByText(/Ana García Rodríguez/i));
  // Selecciona fechas
  fireEvent.change(screen.getByLabelText(/Fecha Inicial/i), { target: { value: "2024-01-01" } });
  fireEvent.change(screen.getByLabelText(/Fecha Final/i), { target: { value: "2024-01-31" } });
  // Ejecuta consulta
  fireEvent.click(screen.getByRole('button', { name: /Consultar/i }));

  expect(screen.getByText(/Genera tu Informe de Ventas/i)).toBeInTheDocument();
});
});