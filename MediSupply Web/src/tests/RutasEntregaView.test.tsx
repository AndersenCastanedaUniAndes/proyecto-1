import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RutasEntregaView  } from "../components/RutasEntregaView"; 


// Mock ResizeObserver para evitar ReferenceError en jsdom
beforeAll(() => {
  (globalThis as any).ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
});

describe('RutasEntregaView', () => {

  it('renderiza correctamente el título y las estadísticas iniciales', () => {
    render(<RutasEntregaView />);

    // Título principal
    expect(screen.getAllByRole('heading', { name: /Programación de Rutas/i })[0])
      .toBeInTheDocument();

    // Verifica tarjetas de estadísticas
    expect(screen.getByText(/Total Rutas/i)).toBeInTheDocument();
    expect(screen.getByText(/Planificadas/i)).toBeInTheDocument();
   expect(screen.getAllByText(/En Progreso/i).length).toBeGreaterThan(0);

    expect(screen.getByText(/Completadas/i)).toBeInTheDocument();
    expect(screen.getByText(/Pedidos/i)).toBeInTheDocument();
  });

  it('filtra rutas existentes según el texto ingresado', async () => {
    render(<RutasEntregaView />);
    
    const filtroInput = screen.getByPlaceholderText(/Filtrar por nombre, conductor o vehículo/i);
    fireEvent.change(filtroInput, { target: { value: 'Centro-Norte' } });

    await waitFor(() => {
      expect(screen.getByText(/Ruta Centro-Norte/i)).toBeInTheDocument();
      expect(screen.queryByText(/Ruta Sur-Occidente/i)).not.toBeInTheDocument();
    });
  });






});
