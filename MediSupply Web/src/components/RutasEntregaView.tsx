import { useEffect, useState, useMemo } from "react";
import axios from "axios";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { Checkbox } from "./ui/checkbox";
import { Textarea } from "./ui/textarea";
import { Switch } from "./ui/switch";
import {
  Edit,
  Trash2,
  Save,
  X,
  Plus,
  Truck,
  Search,
  ChevronDown,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  MapPin,
  Clock,
  Package,
  Thermometer,
  Weight,
  Eye,
  Navigation,
  CheckCircle,
  PlayCircle,
  PauseCircle,
  Route
} from "lucide-react";

interface Pedido {
  id: number;
  cliente: string;
  direccion: string;
  latitud: number;
  longitud: number;
  volumen: number; // m³
  peso: number; // kg
  ventanaInicio: string; // HH:MM
  ventanaFin: string; // HH:MM
  productos: string[];
  valor: number;
  seleccionado: boolean;
}

interface PuntoEntrega {
  id: number;
  pedidoId: number;
  direccion: string;
  latitud: number;
  longitud: number;
  estado: "pendiente" | "en-transcurso" | "entregado";
  horaEstimada: string;
  horaReal?: string;
  observaciones?: string;
}

interface RutaEntrega {
  id: number;
  nombre: string;
  conductor: string;
  vehiculo: string;
  capacidadVolumen: number;
  capacidadPeso: number;
  temperaturaControlada: boolean;
  fechaRuta: string;
  horaInicio: string;
  estado: "planificada" | "en-progreso" | "completada" | "cancelada";
  puntosEntrega: PuntoEntrega[];
  fechaCreacion: string;
  distanciaTotal: number; // km
  tiempoEstimado: number; // minutos
}

export function RutasEntregaView() {
  // Datos de ejemplo de pedidos listos para despacho
  const API_URL = import.meta.env.VITE_API_BASE_RUTAS_URL || "http://localhost:8005";
  const pedidosDisponibles: Pedido[] = [];

  const [rutasEntrega, setRutasEntrega] = useState<RutaEntrega[]>([]);

  const [pedidos, setPedidos] = useState<Pedido[]>(pedidosDisponibles);

  const [nuevaRuta, setNuevaRuta] = useState({
    nombre: "",
    conductor: "",
    vehiculo: "",
    capacidadVolumen: "",
    capacidadPeso: "",
    temperaturaControlada: false,
    fechaRuta: "",
    horaInicio: "",
    pedidosSeleccionados: [] as number[]
  });

  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [rutaEditada, setRutaEditada] = useState({
    nombre: "",
    conductor: "",
    vehiculo: "",
    capacidadVolumen: "",
    capacidadPeso: "",
    temperaturaControlada: false,
    fechaRuta: "",
    horaInicio: ""
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [filtro, setFiltro] = useState("");
  const [filtroPedidos, setFiltroPedidos] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [rutaDetalleAbierta, setRutaDetalleAbierta] = useState<RutaEntrega | null>(null);
  const itemsPerPage = 5;

  // Filtrar rutas
  const rutasFiltradas = useMemo(() => {
    if (!filtro.trim()) return rutasEntrega;
    return rutasEntrega.filter(ruta =>
      ruta.nombre.toLowerCase().includes(filtro.toLowerCase()) ||
      ruta.conductor.toLowerCase().includes(filtro.toLowerCase()) ||
      ruta.vehiculo.toLowerCase().includes(filtro.toLowerCase()) ||
      ruta.estado.toLowerCase().includes(filtro.toLowerCase())
    );
  }, [rutasEntrega, filtro]);

  // Filtrar pedidos en el selector
  const pedidosFiltrados = useMemo(() => {
    if (!filtroPedidos.trim()) return pedidos;
    return pedidos.filter(pedido =>
      pedido.cliente.toLowerCase().includes(filtroPedidos.toLowerCase()) ||
      pedido.direccion.toLowerCase().includes(filtroPedidos.toLowerCase())
    );
  }, [pedidos, filtroPedidos]);

  // Paginación
  const totalPages = Math.ceil(rutasFiltradas.length / itemsPerPage);
  const rutasPaginadas = rutasFiltradas.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Calcular totales de pedidos seleccionados
  const pedidosSeleccionados = pedidos.filter(p => nuevaRuta.pedidosSeleccionados.includes(p.id));
  const volumenTotal = pedidosSeleccionados.reduce((acc, p) => acc + p.volumen, 0);
  const pesoTotal = pedidosSeleccionados.reduce((acc, p) => acc + p.peso, 0);
  const valorTotal = pedidosSeleccionados.reduce((acc, p) => acc + p.valor, 0);


  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [rutasRes, pedidosRes] = await Promise.all([
          axios.get(`${API_URL}/rutas/rutas-entrega?skip=0&limit=100`),
          axios.get(`${API_URL}/rutas/pedidos?skip=0&limit=100`)
        ]);

        // 🔧 Normalizar nombres de campos
        const rutasNormalizadas = rutasRes.data.map((r: any) => ({
          id: r.id,
          nombre: r.nombre,
          conductor: r.conductor,
          vehiculo: r.vehiculo,
          capacidadVolumen: r.capacidad_volumen,
          capacidadPeso: r.capacidad_peso,
          temperaturaControlada: r.temperatura_controlada,
          fechaRuta: r.fecha_ruta,
          horaInicio: r.hora_inicio,
          estado: r.estado,
          fechaCreacion: r.fecha_creacion,
          distanciaTotal: r.distancia_total,
          tiempoEstimado: r.tiempo_estimado,
          puntosEntrega: r.puntosEntrega || []
        }));

        setRutasEntrega(rutasNormalizadas);
        setPedidos(pedidosRes.data);
      } catch (error) {
        console.error("Error al cargar datos:", error);
        setErrorMessage("No se pudieron cargar las rutas o pedidos.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);



  const handleAgregarRuta = async (e: React.FormEvent) => {
    e.preventDefault();

    // 🔍 Validaciones de campos requeridos
    if (
      !nuevaRuta.nombre ||
      !nuevaRuta.conductor ||
      !nuevaRuta.vehiculo ||
      !nuevaRuta.capacidadVolumen ||
      !nuevaRuta.capacidadPeso ||
      !nuevaRuta.fechaRuta ||
      !nuevaRuta.horaInicio ||
      nuevaRuta.pedidosSeleccionados.length === 0
    ) {
      setErrorMessage("Por favor completa todos los campos y selecciona al menos un pedido");
      return;
    }

    // 🔍 Validaciones de capacidad
    if (volumenTotal > parseFloat(nuevaRuta.capacidadVolumen)) {
      setErrorMessage("El volumen total de los pedidos excede la capacidad del vehículo");
      return;
    }

    if (pesoTotal > parseFloat(nuevaRuta.capacidadPeso)) {
      setErrorMessage("El peso total de los pedidos excede la capacidad del vehículo");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");

    try {
      // 🔧 Crear puntos de entrega a partir de los pedidos seleccionados
      const pedidosSeleccionadosData = pedidos.filter(p =>
        nuevaRuta.pedidosSeleccionados.includes(p.id)
      );

      const puntosEntrega = pedidosSeleccionadosData
        .sort((a, b) => a.ventanaInicio.localeCompare(b.ventanaInicio))
        .map((pedido) => ({
          pedidoId: pedido.id,
          direccion: pedido.direccion,
          latitud: pedido.latitud,
          longitud: pedido.longitud,
          estado: "pendiente",
          horaEstimada: nuevaRuta.horaInicio,  
          horaReal: nuevaRuta.horaInicio,
          observaciones: ""   
        }));   

      // 🧱 Construir el JSON en formato correcto para el backend
      const nuevaRutaPayload = {
        nombre: nuevaRuta.nombre,
        conductor: nuevaRuta.conductor,
        vehiculo: nuevaRuta.vehiculo,
        capacidadVolumen: parseFloat(nuevaRuta.capacidadVolumen),
        capacidadPeso: parseFloat(nuevaRuta.capacidadPeso),
        temperaturaControlada: nuevaRuta.temperaturaControlada,
        fechaRuta: nuevaRuta.fechaRuta,
        horaInicio: nuevaRuta.horaInicio,
        estado: "planificada",
        distanciaTotal: Math.round((Math.random() * 50 + 10) * 10) / 10,
        tiempoEstimado: puntosEntrega.length * 45 + 30,
        puntosEntrega: puntosEntrega
      };

      console.log("Payload de nueva ruta:", nuevaRutaPayload);
      // 🚀 Enviar la nueva ruta al backend
      const response = await axios.post(`${API_URL}/rutas/rutas-entrega`, nuevaRutaPayload);



      // 🔁 Normalizar la respuesta del backend
      const rutaCreada = {
        id: response.data.id,
        nombre: response.data.nombre,
        conductor: response.data.conductor,
        vehiculo: response.data.vehiculo,
        capacidadVolumen: response.data.capacidad_volumen,
        capacidadPeso: response.data.capacidad_peso,
        temperaturaControlada: response.data.temperatura_controlada,
        fechaRuta: response.data.fecha_ruta,
        horaInicio: response.data.hora_inicio,
        estado: response.data.estado,
        fechaCreacion: response.data.fecha_creacion,
        distanciaTotal: response.data.distancia_total,
        tiempoEstimado: response.data.tiempo_estimado,
        puntosEntrega: response.data.puntos_entrega || [],
      };

      // ✅ Actualizar el estado local
      setRutasEntrega([...rutasEntrega, rutaCreada]);
      setPedidos(pedidos.filter(p => !nuevaRuta.pedidosSeleccionados.includes(p.id)));

      // 🔄 Reset del formulario
      setNuevaRuta({
        nombre: "",
        conductor: "",
        vehiculo: "",
        capacidadVolumen: "",
        capacidadPeso: "",
        temperaturaControlada: false,
        fechaRuta: "",
        horaInicio: "",
        pedidosSeleccionados: [],
      });

    } catch (error) {
      console.error("Error al crear la ruta:", error);
      setErrorMessage("No se pudo crear la ruta. Verifica los datos o intenta más tarde.");
    } finally {
      setIsLoading(false);
    }
  };

  const iniciarEdicion = (ruta: RutaEntrega) => {
    setEditandoId(ruta.id);
    setRutaEditada({
      nombre: ruta.nombre,
      conductor: ruta.conductor,
      vehiculo: ruta.vehiculo,
      capacidadVolumen: ruta.capacidadVolumen.toString(),
      capacidadPeso: ruta.capacidadPeso.toString(),
      temperaturaControlada: ruta.temperaturaControlada,
      fechaRuta: ruta.fechaRuta,
      horaInicio: ruta.horaInicio
    });
  };

  const cancelarEdicion = () => {
    setEditandoId(null);
    setRutaEditada({
      nombre: "",
      conductor: "",
      vehiculo: "",
      capacidadVolumen: "",
      capacidadPeso: "",
      temperaturaControlada: false,
      fechaRuta: "",
      horaInicio: ""
    });
    setErrorMessage("");
  };

  const guardarEdicion = (id: number) => {
    if (!rutaEditada.nombre || !rutaEditada.conductor || !rutaEditada.vehiculo ||
      !rutaEditada.capacidadVolumen || !rutaEditada.capacidadPeso ||
      !rutaEditada.fechaRuta || !rutaEditada.horaInicio) {
      setErrorMessage("Por favor completa todos los campos obligatorios");
      return;
    }

    setRutasEntrega(rutasEntrega.map(r =>
      r.id === id
        ? {
          ...r,
          nombre: rutaEditada.nombre,
          conductor: rutaEditada.conductor,
          vehiculo: rutaEditada.vehiculo,
          capacidadVolumen: parseFloat(rutaEditada.capacidadVolumen),
          capacidadPeso: parseFloat(rutaEditada.capacidadPeso),
          temperaturaControlada: rutaEditada.temperaturaControlada,
          fechaRuta: rutaEditada.fechaRuta,
          horaInicio: rutaEditada.horaInicio
        }
        : r
    ));
    setEditandoId(null);
    setRutaEditada({
      nombre: "",
      conductor: "",
      vehiculo: "",
      capacidadVolumen: "",
      capacidadPeso: "",
      temperaturaControlada: false,
      fechaRuta: "",
      horaInicio: ""
    });
    setErrorMessage("");
  };


  const eliminarRuta = async (id: number) => {
    try {
      await axios.delete(`${API_URL}/rutas-entrega/${id}`);
      setRutasEntrega(rutasEntrega.filter(r => r.id !== id));
    } catch (error) {
      console.error("Error eliminando ruta:", error);
    }
  };

  const togglePedidoSeleccionado = (pedidoId: number) => {
    const nuevosSeleccionados = nuevaRuta.pedidosSeleccionados.includes(pedidoId)
      ? nuevaRuta.pedidosSeleccionados.filter(id => id !== pedidoId)
      : [...nuevaRuta.pedidosSeleccionados, pedidoId];

    setNuevaRuta({
      ...nuevaRuta,
      pedidosSeleccionados: nuevosSeleccionados
    });
    setErrorMessage("");
  };

  const getEstadoIcon = (estado: string) => {
    switch (estado) {
      case "planificada":
        return <PauseCircle className="h-4 w-4 text-blue-500" />;
      case "en-progreso":
        return <PlayCircle className="h-4 w-4 text-orange-500" />;
      case "completada":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "cancelada":
        return <X className="h-4 w-4 text-red-500" />;
      default:
        return <PauseCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getEstadoBadge = (estado: string) => {
    switch (estado) {
      case "planificada":
        return <Badge variant="secondary">Planificada</Badge>;
      case "en-progreso":
        return <Badge variant="default" className="bg-orange-500">En Progreso</Badge>;
      case "completada":
        return <Badge variant="default" className="bg-green-500">Completada</Badge>;
      case "cancelada":
        return <Badge variant="destructive">Cancelada</Badge>;
      default:
        return <Badge variant="secondary">Desconocido</Badge>;
    }
  };

  const getEstadoPuntoIcon = (estado: string) => {
    switch (estado) {
      case "pendiente":
        return <Clock className="h-4 w-4 text-gray-500" />;
      case "en-transcurso":
        return <Truck className="h-4 w-4 text-orange-500" />;
      case "entregado":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getEstadoPuntoBadge = (estado: string) => {
    switch (estado) {
      case "pendiente":
        return <Badge variant="secondary">Pendiente</Badge>;
      case "en-transcurso":
        return <Badge variant="default" className="bg-orange-500">En Tránsito</Badge>;
      case "entregado":
        return <Badge variant="default" className="bg-green-500">Entregado</Badge>;
      default:
        return <Badge variant="secondary">Desconocido</Badge>;
    }
  };

  // Estadísticas generales
  const estadisticas = {
    totalRutas: rutasEntrega.length,
    planificadas: rutasEntrega.filter(r => r.estado === "planificada").length,
    enProgreso: rutasEntrega.filter(r => r.estado === "en-progreso").length,
    completadas: rutasEntrega.filter(r => r.estado === "completada").length,
    distanciaTotal: rutasEntrega.reduce((acc, r) => acc + r.distanciaTotal, 0),
    tiempoTotal: rutasEntrega.reduce((acc, r) => acc + r.tiempoEstimado, 0),
    pedidosDisponibles: pedidos.length
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1>Programación de Rutas</h1>
        <p className="text-muted-foreground">
          Planifica y gestiona las rutas de entrega optimizando recursos y tiempos
        </p>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-center">Total Rutas</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center text-center">
            <div className="text-2xl font-bold">{estadisticas.totalRutas}</div>
            <p className="text-xs text-muted-foreground">registradas</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-center">Planificadas</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center text-center">
            <div className="text-2xl font-bold text-blue-600">{estadisticas.planificadas}</div>
            <p className="text-xs text-muted-foreground">listas</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-center">En Progreso</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center text-center">
            <div className="text-2xl font-bold text-orange-600">{estadisticas.enProgreso}</div>
            <p className="text-xs text-muted-foreground">activas</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-center">Completadas</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center text-center">
            <div className="text-2xl font-bold text-green-600">{estadisticas.completadas}</div>
            <p className="text-xs text-muted-foreground">finalizadas</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-center">Distancia Total</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center text-center">
            <div className="text-2xl font-bold">{estadisticas.distanciaTotal.toFixed(1)} km</div>
            <p className="text-xs text-muted-foreground">recorrida</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-center">Tiempo Total</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center text-center">
            <div className="text-2xl font-bold">{Math.round(estadisticas.tiempoTotal / 60)}h</div>
            <p className="text-xs text-muted-foreground">estimado</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-center">Pedidos</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center text-center">
            <div className="text-2xl font-bold">{estadisticas.pedidosDisponibles}</div>
            <p className="text-xs text-muted-foreground">disponibles</p>
          </CardContent>
        </Card>
      </div>

      {/* Formulario para crear nueva ruta */}
      <Collapsible open={isFormOpen} onOpenChange={setIsFormOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors pt-3 pb-2">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Plus className="h-5 w-5" />
                  Crear Nueva Ruta de Entrega
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
              <form onSubmit={handleAgregarRuta} className="space-y-6">
                {/* Información básica de la ruta */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="nombre">Nombre de la Ruta</Label>
                    <Input
                      id="nombre"
                      placeholder="Ej: Ruta Centro-Norte"
                      value={nuevaRuta.nombre}
                      onChange={(e) => {
                        setNuevaRuta({ ...nuevaRuta, nombre: e.target.value });
                        setErrorMessage("");
                      }}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="conductor">Conductor</Label>
                    <Input
                      id="conductor"
                      placeholder="Nombre del conductor"
                      value={nuevaRuta.conductor}
                      onChange={(e) => {
                        setNuevaRuta({ ...nuevaRuta, conductor: e.target.value });
                        setErrorMessage("");
                      }}
                      required
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="vehiculo">Vehículo</Label>
                    <Input
                      id="vehiculo"
                      placeholder="Ej: Camión Frigorífico - ABC123"
                      value={nuevaRuta.vehiculo}
                      onChange={(e) => {
                        setNuevaRuta({ ...nuevaRuta, vehiculo: e.target.value });
                        setErrorMessage("");
                      }}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <Thermometer className="h-4 w-4" />
                      Temperatura Controlada
                    </Label>
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={nuevaRuta.temperaturaControlada}
                        onCheckedChange={(checked) => {
                          setNuevaRuta({ ...nuevaRuta, temperaturaControlada: checked });
                          setErrorMessage("");
                        }}
                      />
                      <span className="text-sm text-muted-foreground">
                        {nuevaRuta.temperaturaControlada ? "Sí" : "No"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Capacidades del vehículo */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="capacidadVolumen">Capacidad de Volumen (m³)</Label>
                    <div className="relative">
                      <Package className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="capacidadVolumen"
                        type="number"
                        step="0.1"
                        placeholder="15.0"
                        value={nuevaRuta.capacidadVolumen}
                        onChange={(e) => {
                          setNuevaRuta({ ...nuevaRuta, capacidadVolumen: e.target.value });
                          setErrorMessage("");
                        }}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="capacidadPeso">Capacidad de Peso (kg)</Label>
                    <div className="relative">
                      <Weight className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="capacidadPeso"
                        type="number"
                        step="1"
                        placeholder="1000"
                        value={nuevaRuta.capacidadPeso}
                        onChange={(e) => {
                          setNuevaRuta({ ...nuevaRuta, capacidadPeso: e.target.value });
                          setErrorMessage("");
                        }}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Fecha y hora */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="fechaRuta">Fecha de la Ruta</Label>
                    <Input
                      id="fechaRuta"
                      type="date"
                      value={nuevaRuta.fechaRuta}
                      onChange={(e) => {
                        setNuevaRuta({ ...nuevaRuta, fechaRuta: e.target.value });
                        setErrorMessage("");
                      }}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="horaInicio">Hora de Inicio</Label>
                    <Input
                      id="horaInicio"
                      type="time"
                      value={nuevaRuta.horaInicio}
                      onChange={(e) => {
                        setNuevaRuta({ ...nuevaRuta, horaInicio: e.target.value });
                        setErrorMessage("");
                      }}
                      required
                    />
                  </div>
                </div>

                {/* Selección de pedidos */}
                <div className="space-y-3">
                  <Label>Seleccionar Pedidos para la Ruta</Label>

                  <div className="border rounded-lg p-4 max-h-80 overflow-y-auto">
                    <div className="mb-3">
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                          placeholder="Buscar pedidos por cliente o dirección..."
                          value={filtroPedidos}
                          onChange={(e) => setFiltroPedidos(e.target.value)}
                          className="pl-10"
                        />
                      </div>
                    </div>

                    <div className="space-y-3">
                      {pedidosFiltrados.length === 0 ? (
                        <p className="text-sm text-muted-foreground text-center py-4">
                          No se encontraron pedidos disponibles
                        </p>
                      ) : (
                        pedidosFiltrados.map((pedido) => (
                          <div key={pedido.id} className="border rounded-lg p-3">
                            <div className="flex items-start space-x-3">
                              <Checkbox
                                id={`pedido-${pedido.id}`}
                                checked={nuevaRuta.pedidosSeleccionados.includes(pedido.id)}
                                onCheckedChange={() => togglePedidoSeleccionado(pedido.id)}
                              />
                              <div className="flex-1 space-y-2">
                                <div className="flex items-center justify-between">
                                  <label
                                    htmlFor={`pedido-${pedido.id}`}
                                    className="font-medium cursor-pointer"
                                  >
                                    {pedido.cliente}
                                  </label>
                                  <Badge variant="outline">${pedido.valor.toFixed(2)}</Badge>
                                </div>

                                <div className="text-sm text-muted-foreground">
                                  <div className="flex items-center gap-1 mb-1">
                                    <MapPin className="h-3 w-3" />
                                    {pedido.direccion}
                                  </div>
                                  <div className="grid grid-cols-2 gap-2">
                                    <div>Vol: {pedido.volumen}m³ | Peso: {pedido.peso}kg</div>
                                    <div>Ventana: {pedido.ventanaInicio} - {pedido.ventanaFin}</div>
                                  </div>
                                  <div className="mt-1">
                                    <span className="text-xs">Productos: {pedido.productos.join(", ")}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {/* Resumen de selección */}
                  {nuevaRuta.pedidosSeleccionados.length > 0 && (
                    <div className="bg-muted p-3 rounded-lg">
                      <h4 className="font-medium mb-2">Resumen de Pedidos Seleccionados</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                        <div>
                          <span className="font-medium">Pedidos:</span> {nuevaRuta.pedidosSeleccionados.length}
                        </div>
                        <div>
                          <span className="font-medium">Volumen:</span> {volumenTotal.toFixed(1)}m³
                        </div>
                        <div>
                          <span className="font-medium">Peso:</span> {pesoTotal}kg
                        </div>
                        <div>
                          <span className="font-medium">Valor:</span> ${valorTotal.toFixed(2)}
                        </div>
                      </div>

                      {/* Alertas de capacidad */}
                      {nuevaRuta.capacidadVolumen && volumenTotal > parseFloat(nuevaRuta.capacidadVolumen) && (
                        <Alert variant="destructive" className="mt-2">
                          <AlertCircle className="h-4 w-4" />
                          <AlertDescription>
                            El volumen total ({volumenTotal.toFixed(1)}m³) excede la capacidad del vehículo ({nuevaRuta.capacidadVolumen}m³)
                          </AlertDescription>
                        </Alert>
                      )}

                      {nuevaRuta.capacidadPeso && pesoTotal > parseFloat(nuevaRuta.capacidadPeso) && (
                        <Alert variant="destructive" className="mt-2">
                          <AlertCircle className="h-4 w-4" />
                          <AlertDescription>
                            El peso total ({pesoTotal}kg) excede la capacidad del vehículo ({nuevaRuta.capacidadPeso}kg)
                          </AlertDescription>
                        </Alert>
                      )}
                    </div>
                  )}
                </div>

                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Creando Ruta..." : "Crear Ruta de Entrega"}
                </Button>
              </form>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>

      {/* Lista de rutas */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Rutas de Entrega Registradas</CardTitle>
              <CardDescription>
                {rutasFiltradas.length} de {rutasEntrega.length} ruta{rutasEntrega.length !== 1 ? 's' : ''} mostrada{rutasFiltradas.length !== 1 ? 's' : ''}
              </CardDescription>
            </div>
            <div className="w-72">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Filtrar por nombre, conductor o vehículo..."
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
            {rutasFiltradas.length === 0 ? (
              <div className="text-center py-8">
                <Route className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  {filtro ? "No se encontraron rutas con ese filtro" : "No hay rutas de entrega registradas"}
                </p>
                <p className="text-sm text-muted-foreground">
                  {filtro ? "Intenta con otros términos de búsqueda" : "Crea tu primera ruta de entrega usando el formulario de arriba"}
                </p>
              </div>
            ) : (
              <>
                {rutasPaginadas.map((ruta) => (
                  <div key={ruta.id} className="border rounded-lg p-4 hover:bg-muted/20 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="space-y-2 flex-1">
                        <div className="flex items-center gap-3 flex-wrap">
                          <h3 className="font-medium">{ruta.nombre}</h3>
                          <Badge variant="outline">ID: {ruta.id}</Badge>
                          {getEstadoBadge(ruta.estado)}
                          {ruta.temperaturaControlada && (
                            <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                              <Thermometer className="h-3 w-3 mr-1" />
                              Temp. Controlada
                            </Badge>
                          )}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                          <div className="flex items-center gap-2">
                            <Truck className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Conductor:</span> {ruta.conductor}
                          </div>

                          <div className="flex items-center gap-2">
                            <Package className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Entregas:</span> {ruta.puntosEntrega.length}
                          </div>

                          <div className="flex items-center gap-2">
                            <Navigation className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Distancia:</span> {ruta.distanciaTotal}km
                          </div>

                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Tiempo:</span> {Math.round(ruta.tiempoEstimado / 60)}h {ruta.tiempoEstimado % 60}m
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                          <div>
                            <span className="font-medium">Vehículo:</span> {ruta.vehiculo}
                          </div>
                          <div>
                            <span className="font-medium">Fecha:</span> {new Date(ruta.fechaRuta).toLocaleDateString('es-ES')}
                          </div>
                          <div>
                            <span className="font-medium">Hora Inicio:</span> {ruta.horaInicio}
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-muted-foreground">
                          <div>
                            <span className="font-medium">Capacidad:</span> {ruta.capacidadVolumen}m³ / {ruta.capacidadPeso}kg
                          </div>
                          <div>
                            <span className="font-medium">Creada:</span> {new Date(ruta.fechaCreacion).toLocaleDateString('es-ES')}
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-2 ml-4">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button size="sm" variant="outline">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                            <DialogHeader>
                              <DialogTitle>Detalle de Ruta - {ruta.nombre}</DialogTitle>
                              <DialogDescription>
                                Información completa de la ruta y secuencia de entregas
                              </DialogDescription>
                            </DialogHeader>

                            <div className="space-y-6">
                              {/* Información general */}
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                  <h4 className="font-medium mb-3">Información de la Ruta</h4>
                                  <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                      <span>Nombre:</span>
                                      <span className="font-medium">{ruta.nombre}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Conductor:</span>
                                      <span className="font-medium">{ruta.conductor}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Vehículo:</span>
                                      <span className="font-medium">{ruta.vehiculo}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Estado:</span>
                                      {getEstadoBadge(ruta.estado)}
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Temp. Controlada:</span>
                                      <span className="font-medium">{ruta.temperaturaControlada ? "Sí" : "No"}</span>
                                    </div>
                                  </div>
                                </div>

                                <div>
                                  <h4 className="font-medium mb-3">Detalles Operativos</h4>
                                  <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                      <span>Fecha:</span>
                                      <span className="font-medium">{new Date(ruta.fechaRuta).toLocaleDateString('es-ES')}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Hora Inicio:</span>
                                      <span className="font-medium">{ruta.horaInicio}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Capacidad Vol.:</span>
                                      <span className="font-medium">{ruta.capacidadVolumen}m³</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Capacidad Peso:</span>
                                      <span className="font-medium">{ruta.capacidadPeso}kg</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Distancia Total:</span>
                                      <span className="font-medium">{ruta.distanciaTotal}km</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Tiempo Estimado:</span>
                                      <span className="font-medium">{Math.round(ruta.tiempoEstimado / 60)}h {ruta.tiempoEstimado % 60}m</span>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Secuencia de entregas */}
                              <div>
                                <h4 className="font-medium mb-3 flex items-center gap-2">
                                  <Navigation className="h-4 w-4" />
                                  Secuencia de Entregas ({ruta.puntosEntrega.length || 0})
                                </h4>

                                <div className="space-y-3">
                                  {(ruta.puntosEntrega ?? []).map((punto, index) => (
                                    <div key={punto.id} className="border rounded-lg p-4">
                                      <div className="flex items-start justify-between mb-2">
                                        <div className="flex items-center gap-3">
                                          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-medium">
                                            {index + 1}
                                          </div>
                                          <div>
                                            <h5 className="font-medium">Entrega #{punto.pedidoId}</h5>
                                            <p className="text-sm text-muted-foreground">{punto.direccion}</p>
                                          </div>
                                        </div>
                                        {getEstadoPuntoBadge(punto.estado)}
                                      </div>

                                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm ml-11">
                                        <div>
                                          <span className="font-medium">Hora Estimada:</span> {punto.horaEstimada}
                                        </div>
                                        {punto.horaReal && (
                                          <div>
                                            <span className="font-medium">Hora Real:</span> {punto.horaReal}
                                          </div>
                                        )}
                                        <div>
                                          <span className="font-medium">Coordenadas:</span> {punto.latitud.toFixed(4)}, {punto.longitud.toFixed(4)}
                                        </div>
                                      </div>

                                      {punto.observaciones && (
                                        <div className="mt-2 ml-11">
                                          <p className="text-sm">
                                            <span className="font-medium">Observaciones:</span> {punto.observaciones}
                                          </p>
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>

                              <div className="pt-4 border-t text-xs text-muted-foreground">
                                Ruta creada el {new Date(ruta.fechaCreacion).toLocaleDateString('es-ES')}
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>

                        {editandoId === ruta.id ? (
                          <div className="flex gap-1">
                            <Button
                              size="sm"
                              onClick={() => guardarEdicion(ruta.id)}
                            >
                              <Save className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={cancelarEdicion}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        ) : (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => iniciarEdicion(ruta)}
                              disabled={ruta.estado === "completada"}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => eliminarRuta(ruta.id)}
                              disabled={ruta.estado === "en-progreso"}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>

                    {/* Formulario de edición */}
                    {editandoId === ruta.id && (
                      <div className="mt-4 pt-4 border-t space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label>Nombre de la Ruta</Label>
                            <Input
                              value={rutaEditada.nombre}
                              onChange={(e) => setRutaEditada({ ...rutaEditada, nombre: e.target.value })}
                              placeholder="Nombre de la ruta"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Conductor</Label>
                            <Input
                              value={rutaEditada.conductor}
                              onChange={(e) => setRutaEditada({ ...rutaEditada, conductor: e.target.value })}
                              placeholder="Nombre del conductor"
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <Label>Vehículo</Label>
                            <Input
                              value={rutaEditada.vehiculo}
                              onChange={(e) => setRutaEditada({ ...rutaEditada, vehiculo: e.target.value })}
                              placeholder="Información del vehículo"
                            />
                          </div>
                          <div className="space-y-2">
                            <Label>Fecha de la Ruta</Label>
                            <Input
                              type="date"
                              value={rutaEditada.fechaRuta}
                              onChange={(e) => setRutaEditada({ ...rutaEditada, fechaRuta: e.target.value })}
                            />
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {/* Paginación */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between pt-4 border-t">
                    <p className="text-sm text-muted-foreground">
                      Mostrando {((currentPage - 1) * itemsPerPage) + 1} a {Math.min(currentPage * itemsPerPage, rutasFiltradas.length)} de {rutasFiltradas.length} resultados
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