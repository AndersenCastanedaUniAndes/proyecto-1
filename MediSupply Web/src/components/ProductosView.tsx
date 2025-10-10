import { useState, useMemo,useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { 
  Edit, 
  Trash2, 
  Save, 
  X, 
  Plus, 
  Package, 
  Search, 
  ChevronDown, 
  AlertCircle, 
  ChevronLeft, 
  ChevronRight,
  Thermometer,
  MapPin,
  Hash,
  DollarSign,
  Upload,
  FileSpreadsheet
} from "lucide-react";

interface Producto {
  id: number;
  nombre: string;
  lote: string;
  numeroSerial: string;
  proveedor: string;
  precioUnidad: number;
  precioTotal: number;
  paisOrigen: string;
  uom: "unidad" | "paquete" | "caja" | "pallet";
  cantidad: number;
  tipoAlmacenamiento: "ambiente" | "controlado" | "hazmat";
  temperaturaMin?: number;
  temperaturaMax?: number;
  fechaCreacion: string;
}

const proveedoresDisponibles = [
  "Laboratorios Pharma Plus",
  "Distribuidora Médica Central", 
  "Farmacéutica del Valle"
];

const paisesDisponibles = [
  "Argentina", "Brasil", "Chile", "Colombia", "España", "Estados Unidos",
  "Francia", "Alemania", "India", "México", "Reino Unido", "Suiza"
];

interface ProductosViewProps {
  onSuccess?: (message: string) => void;
}

export function ProductosView({ onSuccess }: ProductosViewProps) {
  const [productos, setProductos] = useState<Producto[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
  const cargarProductos = async () => {
    try {
      setIsLoading(true);
      const response = await fetch("http://localhost:8000/productos/?skip=0&limit=100");
      if (!response.ok) {
        throw new Error(`Error al cargar productos: ${response.statusText}`);
      }
      const data = await response.json();
      console.log("--------------"+data.length);
      setProductos(data);
    } catch (error: any) {
      console.error(error);
      setErrorMessage("No se pudieron cargar los productos desde el servidor.");
    } finally {
      setIsLoading(false);
    }
  };

  cargarProductos();
}, []);




  const [nuevoProducto, setNuevoProducto] = useState({
    nombre: "",
    lote: "",
    numeroSerial: "",
    proveedor: "",
    precioUnidad: "",
    precioTotal: "",
    paisOrigen: "",
    uom: "",
    cantidad: "",
    tipoAlmacenamiento: "",
    temperaturaMin: "",
    temperaturaMax: ""
  });

  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [productoEditado, setProductoEditado] = useState({
    nombre: "",
    lote: "",
    numeroSerial: "",
    proveedor: "",
    precioUnidad: "",
    precioTotal: "",
    paisOrigen: "",
    uom: "",
    cantidad: "",
    tipoAlmacenamiento: "",
    temperaturaMin: "",
    temperaturaMax: ""
  });


  const [isFormOpen, setIsFormOpen] = useState(false);
  const [filtro, setFiltro] = useState("");  
  const [currentPage, setCurrentPage] = useState(1);
  const [uploadingFile, setUploadingFile] = useState(false);
  const itemsPerPage = 5;

  // Filtrar productos
  const productosFiltrados = useMemo(() => {
    if (!filtro.trim()) return productos;
    return productos.filter(producto => 
      producto.nombre.toLowerCase().includes(filtro.toLowerCase()) ||
      producto.proveedor.toLowerCase().includes(filtro.toLowerCase())
    );
  }, [productos, filtro]);

  // Paginación
  const totalPages = Math.ceil(productosFiltrados.length / itemsPerPage);
  const productosPaginados = productosFiltrados.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Calcular precio total basado en precio unitario y cantidad
  const calcularPrecioTotal = (precioUnidad: string, cantidad: string) => {
    const precio = parseFloat(precioUnidad) || 0;
    const cant = parseFloat(cantidad) || 0;
    return (precio * cant).toFixed(2);
  };

  const handleAgregarProducto = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const datosCompletos = Object.values(nuevoProducto).every(valor => {
      if (nuevoProducto.tipoAlmacenamiento === "ambiente") {
        return valor.trim() !== "" || valor === nuevoProducto.temperaturaMin || valor === nuevoProducto.temperaturaMax;
      }
      return valor.trim() !== "";
    });

    if (!datosCompletos) {
      setErrorMessage("Por favor completa todos los campos requeridos");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    
    setTimeout(() => {
      const nuevo: Producto = {
        id: Math.max(...productos.map(p => p.id), 0) + 1,
        nombre: nuevoProducto.nombre.trim(),
        lote: nuevoProducto.lote.trim(),
        numeroSerial: nuevoProducto.numeroSerial.trim(),
        proveedor: nuevoProducto.proveedor,
        precioUnidad: parseFloat(nuevoProducto.precioUnidad),
        precioTotal: parseFloat(nuevoProducto.precioTotal),
        paisOrigen: nuevoProducto.paisOrigen,
        uom: nuevoProducto.uom as any,
        cantidad: parseInt(nuevoProducto.cantidad),
        tipoAlmacenamiento: nuevoProducto.tipoAlmacenamiento as any,
        ...(nuevoProducto.tipoAlmacenamiento !== "ambiente" && {
          temperaturaMin: parseFloat(nuevoProducto.temperaturaMin),
          temperaturaMax: parseFloat(nuevoProducto.temperaturaMax)
        }),
        fechaCreacion: new Date().toISOString().split('T')[0]
      };

      setProductos([...productos, nuevo]);
      setNuevoProducto({
        nombre: "",
        lote: "",
        numeroSerial: "",
        proveedor: "",
        precioUnidad: "",
        precioTotal: "",
        paisOrigen: "",
        uom: "",
        cantidad: "",
        tipoAlmacenamiento: "",
        temperaturaMin: "",
        temperaturaMax: ""
      });
      setIsLoading(false);
      setIsFormOpen(false);
      onSuccess?.(`Producto "${nuevo.nombre}" agregado exitosamente`);
    }, 1000);
  };

  const iniciarEdicion = (producto: Producto) => {
    setEditandoId(producto.id);
    setProductoEditado({
      nombre: producto.nombre,
      lote: producto.lote,
      numeroSerial: producto.numeroSerial,
      proveedor: producto.proveedor,
      precioUnidad: producto.precioUnidad.toString(),
      precioTotal: producto.precioTotal.toString(),
      paisOrigen: producto.paisOrigen,
      uom: producto.uom,
      cantidad: producto.cantidad.toString(),
      tipoAlmacenamiento: producto.tipoAlmacenamiento,
      temperaturaMin: producto.temperaturaMin?.toString() || "",
      temperaturaMax: producto.temperaturaMax?.toString() || ""
    });
  };

  const cancelarEdicion = () => {
    setEditandoId(null);
    setProductoEditado({
      nombre: "",
      lote: "",
      numeroSerial: "",
      proveedor: "",
      precioUnidad: "",
      precioTotal: "",
      paisOrigen: "",
      uom: "",
      cantidad: "",
      tipoAlmacenamiento: "",
      temperaturaMin: "",
      temperaturaMax: ""
    });
    setErrorMessage("");
  };

  const guardarEdicion = (id: number) => {
    const datosCompletos = Object.entries(productoEditado).every(([key, valor]) => {
      if (productoEditado.tipoAlmacenamiento === "ambiente" && (key === "temperaturaMin" || key === "temperaturaMax")) {
        return true;
      }
      return valor.trim() !== "";
    });

    if (!datosCompletos) {
      setErrorMessage("Por favor completa todos los campos requeridos");
      return;
    }

    setProductos(productos.map(p => 
      p.id === id 
        ? { 
            ...p, 
            nombre: productoEditado.nombre.trim(),
            lote: productoEditado.lote.trim(),
            numeroSerial: productoEditado.numeroSerial.trim(),
            proveedor: productoEditado.proveedor,
            precioUnidad: parseFloat(productoEditado.precioUnidad),
            precioTotal: parseFloat(productoEditado.precioTotal),
            paisOrigen: productoEditado.paisOrigen,
            uom: productoEditado.uom as any,
            cantidad: parseInt(productoEditado.cantidad),
            tipoAlmacenamiento: productoEditado.tipoAlmacenamiento as any,
            ...(productoEditado.tipoAlmacenamiento !== "ambiente" && {
              temperaturaMin: parseFloat(productoEditado.temperaturaMin),
              temperaturaMax: parseFloat(productoEditado.temperaturaMax)
            })
          }
        : p
    ));
    setEditandoId(null);
    setProductoEditado({
      nombre: "",
      lote: "",
      numeroSerial: "",
      proveedor: "",
      precioUnidad: "",
      precioTotal: "",
      paisOrigen: "",
      uom: "",
      cantidad: "",
      tipoAlmacenamiento: "",
      temperaturaMin: "",
      temperaturaMax: ""
    });
    setErrorMessage("");
  };

  const eliminarProducto = (id: number) => {
    setProductos(productos.filter(p => p.id !== id));
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validar que sea un archivo Excel o CSV
    const allowedTypes = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv'];
    if (!allowedTypes.includes(file.type)) {
      setErrorMessage("Por favor selecciona un archivo Excel (.xlsx, .xls) o CSV");
      return;
    }

    setUploadingFile(true);
    setErrorMessage("");

    // Simular procesamiento del archivo
    setTimeout(() => {
      // Aquí iría la lógica real de procesamiento del archivo
      // Por ahora simulamos la carga de productos de ejemplo
      const nuevosProductos: Producto[] = [
        {
          id: Math.max(...productos.map(p => p.id), 0) + 1,
          nombre: "Ibuprofeno 600mg",
          lote: "IB2024001",
          numeroSerial: "IBU600-2024-001",
          proveedor: "Laboratorios Pharma Plus",
          precioUnidad: 0.35,
          precioTotal: 350.00,
          paisOrigen: "México",
          uom: "caja",
          cantidad: 1000,
          tipoAlmacenamiento: "ambiente",
          fechaCreacion: new Date().toISOString().split('T')[0]
        },
        {
          id: Math.max(...productos.map(p => p.id), 0) + 2,
          nombre: "Insulina Rápida",
          lote: "IN2024001", 
          numeroSerial: "INS-RAP-2024-001",
          proveedor: "Distribuidora Médica Central",
          precioUnidad: 25.00,
          precioTotal: 2500.00,
          paisOrigen: "Dinamarca",
          uom: "unidad",
          cantidad: 100,
          tipoAlmacenamiento: "controlado",
          temperaturaMin: 2,
          temperaturaMax: 8,
          fechaCreacion: new Date().toISOString().split('T')[0]
        }
      ];

      setProductos([...productos, ...nuevosProductos]);
      setUploadingFile(false);
      
      onSuccess?.(`Se han cargado ${nuevosProductos.length} productos exitosamente`);
    }, 2000);

    // Limpiar el input
    event.target.value = '';
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1>Catálogo de Productos</h1>
        <p className="text-muted-foreground">
          Gestiona el inventario y catálogo de productos farmacéuticos
        </p>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Total Productos</CardTitle>
            <CardDescription>Productos registrados</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{productos.length}</div>
            <p className="text-xs text-muted-foreground">
              Valor total: ${productos.reduce((acc, p) => acc + p.precioTotal, 0).toFixed(2)}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Almacenamiento</CardTitle>
            <CardDescription>Productos por tipo</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>Ambiente:</span>
                <span>{productos.filter(p => p.tipoAlmacenamiento === "ambiente").length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Controlado:</span>
                <span>{productos.filter(p => p.tipoAlmacenamiento === "controlado").length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Hazmat:</span>
                <span>{productos.filter(p => p.tipoAlmacenamiento === "hazmat").length}</span>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Proveedores Únicos</CardTitle>
            <CardDescription>Proveedores activos</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Set(productos.map(p => p.proveedor)).size}
            </div>
            <p className="text-xs text-muted-foreground">
              {proveedoresDisponibles.length} disponibles
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Países de Origen</CardTitle>
            <CardDescription>Diversidad geográfica</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Set(productos.map(p => p.paisOrigen)).size}
            </div>
            <p className="text-xs text-muted-foreground">
              países representados
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Formulario para agregar nuevo producto */}
      <Collapsible open={isFormOpen} onOpenChange={setIsFormOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors pt-3 pb-2">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Plus className="h-5 w-5" />
                  Agregar Nuevo Producto
                </div>
                <ChevronDown className={`h-4 w-4 transition-transform ${isFormOpen ? 'rotate-180' : ''}`} />
              </CardTitle>
            </CardHeader>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent>
              {errorMessage && (
                <Alert variant="destructive" className="mb-4">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{errorMessage}</AlertDescription>
                </Alert>
              )}
              <form onSubmit={handleAgregarProducto} className="space-y-6">
                {/* Información básica */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="nombre">Nombre del Producto</Label>
                    <div className="relative">
                      <Package className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="nombre"
                        placeholder="Nombre del producto"
                        value={nuevoProducto.nombre}
                        onChange={(e) => {
                          setNuevoProducto({...nuevoProducto, nombre: e.target.value});
                          setErrorMessage("");
                        }}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="lote">Lote</Label>
                    <div className="relative">
                      <Hash className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="lote"
                        placeholder="Número de lote"
                        value={nuevoProducto.lote}
                        onChange={(e) => {
                          setNuevoProducto({...nuevoProducto, lote: e.target.value});
                          setErrorMessage("");
                        }}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="numeroSerial">Número Serial</Label>
                    <div className="relative">
                      <Hash className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="numeroSerial"
                        placeholder="Número serial"
                        value={nuevoProducto.numeroSerial}
                        onChange={(e) => {
                          setNuevoProducto({...nuevoProducto, numeroSerial: e.target.value});
                          setErrorMessage("");
                        }}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Proveedor y origen */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="proveedor">Proveedor</Label>
                    <Select value={nuevoProducto.proveedor} onValueChange={(value) => {
                      setNuevoProducto({...nuevoProducto, proveedor: value});
                      setErrorMessage("");
                    }}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecciona un proveedor" />
                      </SelectTrigger>
                      <SelectContent>
                        {proveedoresDisponibles.map((proveedor) => (
                          <SelectItem key={proveedor} value={proveedor}>
                            {proveedor}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="paisOrigen">País de Origen</Label>
                    <Select value={nuevoProducto.paisOrigen} onValueChange={(value) => {
                      setNuevoProducto({...nuevoProducto, paisOrigen: value});
                      setErrorMessage("");
                    }}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecciona un país" />
                      </SelectTrigger>
                      <SelectContent>
                        {paisesDisponibles.map((pais) => (
                          <SelectItem key={pais} value={pais}>
                            <div className="flex items-center gap-2">
                              <MapPin className="h-4 w-4" />
                              {pais}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Precios y cantidades */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="precioUnidad">Precio Unitario ($)</Label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="precioUnidad"
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        value={nuevoProducto.precioUnidad}
                        onChange={(e) => {
                          const newValue = e.target.value;
                          const precioTotal = calcularPrecioTotal(newValue, nuevoProducto.cantidad);
                          setNuevoProducto({
                            ...nuevoProducto, 
                            precioUnidad: newValue,
                            precioTotal: precioTotal
                          });
                          setErrorMessage("");
                        }}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="cantidad">Cantidad</Label>
                    <Input
                      id="cantidad"
                      type="number"
                      placeholder="0"
                      value={nuevoProducto.cantidad}
                      onChange={(e) => {
                        const newValue = e.target.value;
                        const precioTotal = calcularPrecioTotal(nuevoProducto.precioUnidad, newValue);
                        setNuevoProducto({
                          ...nuevoProducto, 
                          cantidad: newValue,
                          precioTotal: precioTotal
                        });
                        setErrorMessage("");
                      }}
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="uom">UOM</Label>
                    <Select value={nuevoProducto.uom} onValueChange={(value) => {
                      setNuevoProducto({...nuevoProducto, uom: value});
                      setErrorMessage("");
                    }}>
                      <SelectTrigger>
                        <SelectValue placeholder="Unidad de medida" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="unidad">Unidad</SelectItem>
                        <SelectItem value="paquete">Paquete</SelectItem>
                        <SelectItem value="caja">Caja</SelectItem>
                        <SelectItem value="pallet">Pallet</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="precioTotal">Precio Total ($)</Label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="precioTotal"
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        value={nuevoProducto.precioTotal}
                        onChange={(e) => {
                          setNuevoProducto({...nuevoProducto, precioTotal: e.target.value});
                          setErrorMessage("");
                        }}
                        className="pl-10 bg-muted"
                        readOnly
                      />
                    </div>
                  </div>
                </div>

                {/* Almacenamiento */}
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="tipoAlmacenamiento">Tipo de Almacenamiento</Label>
                      <Select value={nuevoProducto.tipoAlmacenamiento} onValueChange={(value) => {
                        setNuevoProducto({
                          ...nuevoProducto, 
                          tipoAlmacenamiento: value,
                          ...(value === "ambiente" && { temperaturaMin: "", temperaturaMax: "" })
                        });
                        setErrorMessage("");
                      }}>
                        <SelectTrigger>
                          <SelectValue placeholder="Tipo de almacenamiento" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="ambiente">Ambiente</SelectItem>
                          <SelectItem value="controlado">Controlado</SelectItem>
                          <SelectItem value="hazmat">Hazmat</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    {nuevoProducto.tipoAlmacenamiento && nuevoProducto.tipoAlmacenamiento !== "ambiente" && (
                      <>
                        <div className="space-y-2">
                          <Label htmlFor="temperaturaMin">Temperatura Mínima (°C)</Label>
                          <div className="relative">
                            <Thermometer className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                              id="temperaturaMin"
                              type="number"
                              placeholder="-80"
                              value={nuevoProducto.temperaturaMin}
                              onChange={(e) => {
                                setNuevoProducto({...nuevoProducto, temperaturaMin: e.target.value});
                                setErrorMessage("");
                              }}
                              className="pl-10"
                              required
                            />
                          </div>
                        </div>
                        
                        <div className="space-y-2">
                          <Label htmlFor="temperaturaMax">Temperatura Máxima (°C)</Label>
                          <div className="relative">
                            <Thermometer className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                              id="temperaturaMax"
                              type="number"
                              placeholder="8"
                              value={nuevoProducto.temperaturaMax}
                              onChange={(e) => {
                                setNuevoProducto({...nuevoProducto, temperaturaMax: e.target.value});
                                setErrorMessage("");
                              }}
                              className="pl-10"
                              required
                            />
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                </div>
                
                <div className="flex gap-4 items-center">
                  <Button type="submit" disabled={isLoading}>
                    {isLoading ? "Agregando..." : "Agregar Producto"}
                  </Button>
                  
                  <div className="border-l border-muted pl-4">
                    <Label htmlFor="file-upload" className="cursor-pointer">
                      <div className="flex items-center gap-2 px-4 py-2 border border-dashed border-muted-foreground rounded-lg hover:bg-muted/50 transition-colors">
                        {uploadingFile ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                            <span>Cargando archivo...</span>
                          </>
                        ) : (
                          <>
                            <Upload className="h-4 w-4" />
                            <span>Cargar archivo</span>
                            <FileSpreadsheet className="h-4 w-4 text-muted-foreground" />
                          </>
                        )}
                      </div>
                    </Label>
                    <input
                      id="file-upload"
                      type="file"
                      accept=".xlsx,.xls,.csv"
                      onChange={handleFileUpload}
                      disabled={uploadingFile}
                      className="hidden"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Formatos: Excel (.xlsx, .xls) o CSV
                    </p>
                  </div>
                </div>
              </form>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>

      {/* Lista de productos existentes */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Productos Registrados</CardTitle>
              <CardDescription>
                {productosFiltrados.length} de {productos.length} producto{productos.length !== 1 ? 's' : ''} mostrado{productosFiltrados.length !== 1 ? 's' : ''}
              </CardDescription>
            </div>
            <div className="w-72">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Filtrar por nombre o proveedor..."
                  value={filtro}
                  onChange={(e) => {
                    setFiltro(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="pl-10"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {productosFiltrados.length === 0 ? (
              <div className="text-center py-8">
                <Package className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  {filtro ? "No se encontraron productos con ese filtro" : "No hay productos registrados"}
                </p>
                <p className="text-sm text-muted-foreground">
                  {filtro ? "Intenta con otros términos de búsqueda" : "Agrega tu primer producto usando el formulario de arriba"}
                </p>
              </div>
            ) : (
              <>
                {productosPaginados.map((producto) => (
                  <div key={producto.id} className="border rounded-lg p-4 hover:bg-muted/20 transition-colors">
                    {editandoId === producto.id ? (
                      /* Modo edición - simplificado para mostrar campos principales */
                      <div className="space-y-3">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                          <Input
                            value={productoEditado.nombre}
                            onChange={(e) => setProductoEditado({
                              ...productoEditado,
                              nombre: e.target.value
                            })}
                            placeholder="Nombre del producto"
                          />
                          <Input
                            value={productoEditado.lote}
                            onChange={(e) => setProductoEditado({
                              ...productoEditado,
                              lote: e.target.value
                            })}
                            placeholder="Lote"
                          />
                          <Select value={productoEditado.proveedor} onValueChange={(value) => 
                            setProductoEditado({...productoEditado, proveedor: value})
                          }>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {proveedoresDisponibles.map((proveedor) => (
                                <SelectItem key={proveedor} value={proveedor}>
                                  {proveedor}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            onClick={() => guardarEdicion(producto.id)}
                          >
                            <Save className="h-4 w-4 mr-1" />
                            Guardar
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline" 
                            onClick={cancelarEdicion}
                          >
                            <X className="h-4 w-4 mr-1" />
                            Cancelar
                          </Button>
                        </div>
                      </div>
                    ) : (
                      /* Modo visualización */
                      <div className="flex items-start justify-between">
                        <div className="space-y-2 flex-1">
                          <div className="flex items-center gap-3 flex-wrap">
                            <h3 className="font-medium">{producto.nombre}</h3>
                            <Badge variant="secondary">ID: {producto.id}</Badge>
                            <Badge variant="outline">Lote: {producto.lote}</Badge>
                            <Badge 
                              variant={
                                producto.tipoAlmacenamiento === "ambiente" ? "secondary" :
                                producto.tipoAlmacenamiento === "controlado" ? "default" : "destructive"
                              }
                            >
                              {producto.tipoAlmacenamiento.charAt(0).toUpperCase() + producto.tipoAlmacenamiento.slice(1)}
                            </Badge>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-muted-foreground">
                            <div>
                              <span className="font-medium">Proveedor:</span> {producto.proveedor}
                            </div>
                            <div>
                              <span className="font-medium">Cantidad:</span> {producto.cantidad} {producto.uom}
                            </div>
                            <div>
                              <span className="font-medium">Precio Unit.:</span> ${producto.precioUnidad.toFixed(2)}
                            </div>
                            <div>
                              <span className="font-medium">Total:</span> ${producto.precioTotal.toFixed(2)}
                            </div>
                            <div>
                              <span className="font-medium">País:</span> {producto.paisOrigen}
                            </div>
                            <div>
                              <span className="font-medium">Serial:</span> {producto.numeroSerial}
                            </div>
                            {producto.temperaturaMin !== undefined && (
                              <div>
                                <span className="font-medium">Temp.:</span> {producto.temperaturaMin}°C a {producto.temperaturaMax}°C
                              </div>
                            )}
                            <div>
                              <span className="font-medium">Registrado:</span> {new Date(producto.fechaCreacion).toLocaleDateString('es-ES')}
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex gap-2 ml-4">
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => iniciarEdicion(producto)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => eliminarProducto(producto.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                
                {/* Paginación */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between pt-4 border-t">
                    <p className="text-sm text-muted-foreground">
                      Mostrando {((currentPage - 1) * itemsPerPage) + 1} a {Math.min(currentPage * itemsPerPage, productosFiltrados.length)} de {productosFiltrados.length} resultados
                    </p>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(currentPage - 1)}
                        disabled={currentPage === 1}
                      >
                        <ChevronLeft className="h-4 w-4" />
                        Anterior
                      </Button>
                      
                      <div className="flex gap-1">
                        {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                          <Button
                            key={page}
                            variant={currentPage === page ? "default" : "outline"}
                            size="sm"
                            onClick={() => setCurrentPage(page)}
                            className="w-8 h-8 p-0"
                          >
                            {page}
                          </Button>
                        ))}
                      </div>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage(currentPage + 1)}
                        disabled={currentPage === totalPages}
                      >
                        Siguiente
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}