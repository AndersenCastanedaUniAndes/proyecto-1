import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ProductosView } from "../components/ProductosView";

// Mock config to avoid import.meta in Jest
jest.mock('../config/config', () => ({ __esModule: true, default: { API_BASE_URL: 'http://localhost:8000' } }));

describe("ProductosView", () => {
  const productos = [
    {
      id: 1,
      nombre: "Paracetamol 500mg",
      lote: "L001",
      numeroSerial: "P-001",
      proveedor: "Laboratorios Pharma Plus",
      precioUnidad: 1.0,
      precioTotal: 100.0,
      paisOrigen: "Colombia",
      uom: "unidad",
      cantidad: 100,
      tipoAlmacenamiento: "ambiente",
      fechaCreacion: "2024-01-01",
    },
    {
      id: 2,
      nombre: "Vacuna COVID-19",
      lote: "L002",
      numeroSerial: "V-002",
      proveedor: "Distribuidora Médica Central",
      precioUnidad: 15.5,
      precioTotal: 155.0,
      paisOrigen: "México",
      uom: "paquete",
      cantidad: 10,
      tipoAlmacenamiento: "controlado",
      fechaCreacion: "2024-01-02",
    },
  ];

  beforeEach(() => {
    (globalThis as any).fetch = jest.fn((url: string) => {
      if (url.endsWith('/productos/proveedores')) {
        return Promise.resolve({ ok: true, json: async () => ["Laboratorios Pharma Plus", "Distribuidora Médica Central"] });
      }
      if (url.endsWith('/productos/uom')) {
        return Promise.resolve({ ok: true, json: async () => ["unidad", "paquete"] });
      }
      if (url.endsWith('/productos/tipos_almacenamiento')) {
        return Promise.resolve({ ok: true, json: async () => ["ambiente", "controlado", "hazmat"] });
      }
      if (url.endsWith('/productos/paises')) {
        return Promise.resolve({ ok: true, json: async () => ["Colombia", "México"] });
      }
      if (url.includes('/productos/?skip=0&limit=100')) {
        return Promise.resolve({ ok: true, json: async () => productos });
      }
      return Promise.resolve({ ok: true, json: async () => ({}) });
    });
  });

  afterEach(() => {
    (globalThis as any).fetch = undefined;
    jest.clearAllMocks();
  });
  it("renderiza el título y las estadísticas", async () => {
    render(<ProductosView />);
    expect(screen.getAllByText(/Catálogo de Productos/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Total Productos/i)).toBeInTheDocument();
    expect(screen.getByText(/Almacenamiento/i)).toBeInTheDocument();
    expect(screen.getByText(/Proveedores Únicos/i)).toBeInTheDocument();
    expect(screen.getByText(/Países de Origen/i)).toBeInTheDocument();
    await waitFor(() => expect((globalThis as any).fetch).toHaveBeenCalled());
  });

  it("filtra productos por nombre", async () => {
    render(<ProductosView />);
    // Espera a que los productos se carguen
    await waitFor(() => expect(screen.getByText(/Vacuna COVID-19/i)).toBeInTheDocument());

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