import { useState, useMemo } from "react";
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
import { 
  Edit, 
  Trash2, 
  Save, 
  X, 
  Plus, 
  Target, 
  Search, 
  ChevronDown, 
  AlertCircle, 
  ChevronLeft, 
  ChevronRight,
  DollarSign,
  Calendar,
  Users,
  Eye,
  Filter
} from "lucide-react";

interface Vendedor {
  id: number;
  nombre: string;
  correo: string;
  activo: boolean;
}

interface PlanVenta {
  id: number;
  periodo: "mensual" | "trimestral" | "semestral" | "anual";
  valorVentas: number;
  vendedores: Vendedor[];
  fechaCreacion: string;
  estado: "activo" | "completado" | "pausado";
}

interface PlanesVentaViewProps {
  onSuccess?: (message: string) => void;
}

export function PlanesVentaView({ onSuccess }: PlanesVentaViewProps) {
  // Datos de ejemplo de vendedores
  const vendedoresDisponibles: Vendedor[] = [
    {
      id: 1,
      nombre: "Ana García Rodríguez",
      correo: "ana.garcia@medisupply.com",
      activo: true
    },
    {
      id: 2,
      nombre: "Carlos Mendoza Silva", 
      correo: "carlos.mendoza@medisupply.com",
      activo: true
    },
    {
      id: 3,
      nombre: "María Elena Vásquez",
      correo: "maria.vasquez@medisupply.com",
      activo: false
    },
    {
      id: 4,
      nombre: "Roberto Jiménez Luna",
      correo: "roberto.jimenez@medisupply.com",
      activo: true
    }
  ];

  const [planesVenta, setPlanesVenta] = useState<PlanVenta[]>([
    {
      id: 1,
      periodo: "trimestral",
      valorVentas: 150000,
      vendedores: [vendedoresDisponibles[0], vendedoresDisponibles[1]],
      fechaCreacion: "2024-01-15",
      estado: "activo"
    },
    {
      id: 2,
      periodo: "mensual",
      valorVentas: 45000,
      vendedores: [vendedoresDisponibles[2]],
      fechaCreacion: "2024-02-01", 
      estado: "completado"
    },
    {
      id: 3,
      periodo: "anual",
      valorVentas: 500000,
      vendedores: vendedoresDisponibles.filter(v => v.activo),
      fechaCreacion: "2024-01-01",
      estado: "activo"
    }
  ]);

  const [nuevoPlan, setNuevoPlan] = useState({
    periodo: "",
    valorVentas: "",
    vendedoresSeleccionados: [] as number[]
  });

  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [planEditado, setPlanEditado] = useState({
    periodo: "",
    valorVentas: "",
    vendedoresSeleccionados: [] as number[]
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [filtro, setFiltro] = useState("");
  const [filtroVendedores, setFiltroVendedores] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [planDetalleAbierto, setPlanDetalleAbierto] = useState<PlanVenta | null>(null);
  const itemsPerPage = 5;

  // Filtrar planes de venta
  const planesFiltrados = useMemo(() => {
    if (!filtro.trim()) return planesVenta;
    return planesVenta.filter(plan => 
      plan.periodo.toLowerCase().includes(filtro.toLowerCase()) ||
      plan.vendedores.some(v => v.nombre.toLowerCase().includes(filtro.toLowerCase())) ||
      plan.valorVentas.toString().includes(filtro)
    );
  }, [planesVenta, filtro]);

  // Filtrar vendedores en el selector
  const vendedoresFiltrados = useMemo(() => {
    if (!filtroVendedores.trim()) return vendedoresDisponibles;
    return vendedoresDisponibles.filter(vendedor => 
      vendedor.nombre.toLowerCase().includes(filtroVendedores.toLowerCase()) ||
      vendedor.correo.toLowerCase().includes(filtroVendedores.toLowerCase())
    );
  }, [filtroVendedores]);

  // Paginación
  const totalPages = Math.ceil(planesFiltrados.length / itemsPerPage);
  const planesPaginados = planesFiltrados.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleAgregarPlan = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!nuevoPlan.periodo || !nuevoPlan.valorVentas || nuevoPlan.vendedoresSeleccionados.length === 0) {
      setErrorMessage("Por favor completa todos los campos y selecciona al menos un vendedor");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    
    setTimeout(() => {
      const vendedoresSeleccionados = vendedoresDisponibles.filter(v => 
        nuevoPlan.vendedoresSeleccionados.includes(v.id)
      );

      const nuevo: PlanVenta = {
        id: Math.max(...planesVenta.map(p => p.id), 0) + 1,
        periodo: nuevoPlan.periodo as any,
        valorVentas: parseFloat(nuevoPlan.valorVentas),
        vendedores: vendedoresSeleccionados,
        fechaCreacion: new Date().toISOString().split('T')[0],
        estado: "activo"
      };

      setPlanesVenta([...planesVenta, nuevo]);
      setNuevoPlan({
        periodo: "",
        valorVentas: "",
        vendedoresSeleccionados: []
      });
      setIsLoading(false);
      setIsFormOpen(false);
      onSuccess?.(`Plan de venta ${getPeriodoLabel(nuevo.periodo).toLowerCase()} creado exitosamente`);
    }, 1000);
  };

  const iniciarEdicion = (plan: PlanVenta) => {
    setEditandoId(plan.id);
    setPlanEditado({
      periodo: plan.periodo,
      valorVentas: plan.valorVentas.toString(),
      vendedoresSeleccionados: plan.vendedores.map(v => v.id)
    });
  };

  const cancelarEdicion = () => {
    setEditandoId(null);
    setPlanEditado({
      periodo: "",
      valorVentas: "",
      vendedoresSeleccionados: []
    });
    setErrorMessage("");
  };

  const guardarEdicion = (id: number) => {
    if (!planEditado.periodo || !planEditado.valorVentas || planEditado.vendedoresSeleccionados.length === 0) {
      setErrorMessage("Por favor completa todos los campos y selecciona al menos un vendedor");
      return;
    }

    const vendedoresSeleccionados = vendedoresDisponibles.filter(v => 
      planEditado.vendedoresSeleccionados.includes(v.id)
    );

    setPlanesVenta(planesVenta.map(p => 
      p.id === id 
        ? { 
            ...p, 
            periodo: planEditado.periodo as any,
            valorVentas: parseFloat(planEditado.valorVentas),
            vendedores: vendedoresSeleccionados
          }
        : p
    ));
    setEditandoId(null);
    setPlanEditado({
      periodo: "",
      valorVentas: "",
      vendedoresSeleccionados: []
    });
    setErrorMessage("");
  };

  const eliminarPlan = (id: number) => {
    setPlanesVenta(planesVenta.filter(p => p.id !== id));
  };

  const toggleVendedorSeleccionado = (vendedorId: number, isEditing: boolean = false) => {
    if (isEditing) {
      const nuevosSeleccionados = planEditado.vendedoresSeleccionados.includes(vendedorId)
        ? planEditado.vendedoresSeleccionados.filter(id => id !== vendedorId)
        : [...planEditado.vendedoresSeleccionados, vendedorId];
      
      setPlanEditado({
        ...planEditado,
        vendedoresSeleccionados: nuevosSeleccionados
      });
    } else {
      const nuevosSeleccionados = nuevoPlan.vendedoresSeleccionados.includes(vendedorId)
        ? nuevoPlan.vendedoresSeleccionados.filter(id => id !== vendedorId)
        : [...nuevoPlan.vendedoresSeleccionados, vendedorId];
      
      setNuevoPlan({
        ...nuevoPlan,
        vendedoresSeleccionados: nuevosSeleccionados
      });
    }
    setErrorMessage("");
  };

  const getPeriodoLabel = (periodo: string) => {
    const labels = {
      "mensual": "Mensual",
      "trimestral": "Trimestral", 
      "semestral": "Semestral",
      "anual": "Anual"
    };
    return labels[periodo as keyof typeof labels] || periodo;
  };

  const getEstadoBadge = (estado: string) => {
    const variants = {
      "activo": "default",
      "completado": "secondary",
      "pausado": "outline"
    };
    return variants[estado as keyof typeof variants] || "secondary";
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1>Planes de Venta</h1>
        <p className="text-muted-foreground">
          Gestiona y supervisa los planes de venta del equipo comercial
        </p>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Total Planes</CardTitle>
            <CardDescription>Planes de venta activos</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{planesVenta.length}</div>
            <p className="text-xs text-muted-foreground">
              {planesVenta.filter(p => p.estado === 'activo').length} activos
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Valor Total</CardTitle>
            <CardDescription>Objetivos de venta</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${planesVenta.reduce((acc, p) => acc + p.valorVentas, 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              Total de objetivos
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Vendedores Activos</CardTitle>
            <CardDescription>En planes de venta</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Set(planesVenta.flatMap(p => p.vendedores.map(v => v.id))).size}
            </div>
            <p className="text-xs text-muted-foreground">
              vendedores únicos
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Promedio por Plan</CardTitle>
            <CardDescription>Valor promedio</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${planesVenta.length > 0 ? Math.round(planesVenta.reduce((acc, p) => acc + p.valorVentas, 0) / planesVenta.length).toLocaleString() : '0'}
            </div>
            <p className="text-xs text-muted-foreground">
              por plan de venta
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Formulario para crear nuevo plan */}
      <Collapsible open={isFormOpen} onOpenChange={setIsFormOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors pt-3 pb-2">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Plus className="h-5 w-5" />
                  Crear Nuevo Plan de Venta
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
              <form onSubmit={handleAgregarPlan} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="periodo">Período de Tiempo</Label>
                    <Select value={nuevoPlan.periodo} onValueChange={(value) => {
                      setNuevoPlan({...nuevoPlan, periodo: value});
                      setErrorMessage("");
                    }}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecciona el período" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="mensual">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            Mensual
                          </div>
                        </SelectItem>
                        <SelectItem value="trimestral">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            Trimestral
                          </div>
                        </SelectItem>
                        <SelectItem value="semestral">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            Semestral
                          </div>
                        </SelectItem>
                        <SelectItem value="anual">
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            Anual
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="valorVentas">Valor de Ventas ($)</Label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="valorVentas"
                        type="number"
                        step="0.01"
                        placeholder="150000.00"
                        value={nuevoPlan.valorVentas}
                        onChange={(e) => {
                          setNuevoPlan({...nuevoPlan, valorVentas: e.target.value});
                          setErrorMessage("");
                        }}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Selección de vendedores */}
                <div className="space-y-3">
                  <Label>Seleccionar Vendedores</Label>
                  
                  <div className="border rounded-lg p-4 max-h-60 overflow-y-auto">
                    <div className="mb-3">
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                          placeholder="Buscar vendedores..."
                          value={filtroVendedores}
                          onChange={(e) => setFiltroVendedores(e.target.value)}
                          className="pl-10"
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      {vendedoresFiltrados.length === 0 ? (
                        <p className="text-sm text-muted-foreground text-center py-4">
                          No se encontraron vendedores
                        </p>
                      ) : (
                        vendedoresFiltrados.map((vendedor) => (
                          <div key={vendedor.id} className="flex items-center space-x-3 p-2 hover:bg-muted rounded">
                            <Checkbox
                              id={`vendedor-${vendedor.id}`}
                              checked={nuevoPlan.vendedoresSeleccionados.includes(vendedor.id)}
                              onCheckedChange={() => toggleVendedorSeleccionado(vendedor.id)}
                              disabled={!vendedor.activo}
                            />
                            <div className="flex-1">
                              <label
                                htmlFor={`vendedor-${vendedor.id}`}
                                className={`text-sm cursor-pointer ${!vendedor.activo ? 'text-muted-foreground' : ''}`}
                              >
                                {vendedor.nombre}
                              </label>
                              <p className="text-xs text-muted-foreground">{vendedor.correo}</p>
                            </div>
                            {!vendedor.activo && (
                              <Badge variant="secondary" className="text-xs">Inactivo</Badge>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                  
                  {nuevoPlan.vendedoresSeleccionados.length > 0 && (
                    <p className="text-sm text-muted-foreground">
                      {nuevoPlan.vendedoresSeleccionados.length} vendedor{nuevoPlan.vendedoresSeleccionados.length !== 1 ? 'es' : ''} seleccionado{nuevoPlan.vendedoresSeleccionados.length !== 1 ? 's' : ''}
                    </p>
                  )}
                </div>
                
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Creando..." : "Crear Plan de Venta"}
                </Button>
              </form>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>

      {/* Lista de planes de venta */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Planes de Venta Registrados</CardTitle>
              <CardDescription>
                {planesFiltrados.length} de {planesVenta.length} plan{planesVenta.length !== 1 ? 'es' : ''} mostrado{planesFiltrados.length !== 1 ? 's' : ''}
              </CardDescription>
            </div>
            <div className="w-72">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Filtrar por período, vendedor o valor..."
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
            {planesFiltrados.length === 0 ? (
              <div className="text-center py-8">
                <Target className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  {filtro ? "No se encontraron planes con ese filtro" : "No hay planes de venta registrados"}
                </p>
                <p className="text-sm text-muted-foreground">
                  {filtro ? "Intenta con otros términos de búsqueda" : "Crea tu primer plan de venta usando el formulario de arriba"}
                </p>
              </div>
            ) : (
              <>
                {planesPaginados.map((plan) => (
                  <div key={plan.id} className="border rounded-lg p-4 hover:bg-muted/20 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="space-y-2 flex-1">
                        <div className="flex items-center gap-3 flex-wrap">
                          <h3 className="font-medium">Plan {getPeriodoLabel(plan.periodo)}</h3>
                          <Badge variant="secondary">ID: {plan.id}</Badge>
                          <Badge variant={getEstadoBadge(plan.estado) as any}>
                            {plan.estado.charAt(0).toUpperCase() + plan.estado.slice(1)}
                          </Badge>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                          <div>
                            <span className="font-medium">Período:</span> {getPeriodoLabel(plan.periodo)}
                          </div>
                          <div>
                            <span className="font-medium">Valor de Ventas:</span> ${plan.valorVentas.toLocaleString()}
                          </div>
                          <div>
                            <span className="font-medium">
                              {plan.vendedores.length === 1 ? 'Vendedor:' : `${plan.vendedores.length} Vendedores:`}
                            </span> {
                              plan.vendedores.length === 1 
                                ? plan.vendedores[0].nombre 
                                : `${plan.vendedores.length} asignados`
                            }
                          </div>
                        </div>
                        
                        <p className="text-xs text-muted-foreground">
                          Creado: {new Date(plan.fechaCreacion).toLocaleDateString('es-ES')}
                        </p>
                      </div>
                      
                      <div className="flex gap-2 ml-4">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button size="sm" variant="outline">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-2xl">
                            <DialogHeader>
                              <DialogTitle>Detalle del Plan de Venta</DialogTitle>
                              <DialogDescription>
                                Plan {getPeriodoLabel(plan.periodo)} - ID: {plan.id}
                              </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <Label>Período</Label>
                                  <p className="font-medium">{getPeriodoLabel(plan.periodo)}</p>
                                </div>
                                <div>
                                  <Label>Valor de Ventas</Label>
                                  <p className="font-medium">${plan.valorVentas.toLocaleString()}</p>
                                </div>
                              </div>
                              
                              <div>
                                <Label>Vendedores Asignados ({plan.vendedores.length})</Label>
                                <div className="mt-2 space-y-2">
                                  {plan.vendedores.map((vendedor) => (
                                    <div key={vendedor.id} className="flex items-center justify-between p-2 border rounded">
                                      <div>
                                        <p className="font-medium">{vendedor.nombre}</p>
                                        <p className="text-sm text-muted-foreground">{vendedor.correo}</p>
                                      </div>
                                      <Badge variant={vendedor.activo ? "default" : "secondary"}>
                                        {vendedor.activo ? "Activo" : "Inactivo"}
                                      </Badge>
                                    </div>
                                  ))}
                                </div>
                              </div>
                              
                              <div className="pt-4 border-t">
                                <div className="flex justify-between text-sm">
                                  <span>Estado:</span>
                                  <Badge variant={getEstadoBadge(plan.estado) as any}>
                                    {plan.estado.charAt(0).toUpperCase() + plan.estado.slice(1)}
                                  </Badge>
                                </div>
                                <div className="flex justify-between text-sm mt-2">
                                  <span>Fecha de Creación:</span>
                                  <span>{new Date(plan.fechaCreacion).toLocaleDateString('es-ES')}</span>
                                </div>
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>
                        
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => iniciarEdicion(plan)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => eliminarPlan(plan.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
                
                {/* Paginación */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between pt-4 border-t">
                    <p className="text-sm text-muted-foreground">
                      Mostrando {((currentPage - 1) * itemsPerPage) + 1} a {Math.min(currentPage * itemsPerPage, planesFiltrados.length)} de {planesFiltrados.length} resultados
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