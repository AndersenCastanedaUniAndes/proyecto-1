import { useState, useMemo, useEffect } from "react";
import config from "../config/config";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Checkbox } from "./ui/checkbox";
import {
  Edit,
  Trash2,
  Save,
  X,
  Plus,
  DollarSign,
  Search,
  ChevronDown,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Eye,
  Target
} from "lucide-react";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";

interface Vendedor {
  usuario_id: number;
  nombre_usuario: string;
  email: string;
  estado: boolean;
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
  onSuccess?: (message: string, tipo?: "success" | "info" | "warning") => void;
}

export function PlanesVentaView({ onSuccess }: PlanesVentaViewProps) {
  const [planesVenta, setPlanesVenta] = useState<PlanVenta[]>([]);
  const [vendedoresDisponibles, setVendedoresDisponibles] = useState<Vendedor[]>([]);
  const [nuevoPlan, setNuevoPlan] = useState({ periodo: "", valorVentas: "", vendedoresSeleccionados: [] as number[] });
  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [planEditado, setPlanEditado] = useState({ periodo: "", valorVentas: "", vendedoresSeleccionados: [] as number[] });
  const [isLoading, setIsLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [filtro, setFiltro] = useState("");
  const [filtroVendedores, setFiltroVendedores] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;
  const token = localStorage.getItem("access_token");

  // Cargar datos iniciales
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [planesRes, vendedoresRes] = await Promise.all([
          fetch(`${config.API_BASE_PLANES_URL}/planes_venta/`, {
            headers: { Authorization: `Bearer ${token}` }
          }),
          fetch(`${config.API_BASE_LOGIN_URL}/vendedores?skip=0&limit=100`, {
            headers: { Authorization: `Bearer ${token}` }
          })
        ]);

        if (!planesRes.ok || !vendedoresRes.ok) throw new Error("Error al cargar datos desde el servidor");

        const planesDataRaw = await planesRes.json();
        const vendedoresData = await vendedoresRes.json();

        const planesData = planesDataRaw.map((p: any) => ({
          id: p.id,
          periodo: p.periodo,
          valorVentas: p.valor_ventas ?? 0,
          fechaCreacion: p.fecha_creacion,
          estado: p.estado,
          vendedores: p.vendedores || []
        }));

        const vendedoresMapped: Vendedor[] = vendedoresData.map((v: any) => ({
          usuario_id: v.usuario_id,
          nombre_usuario: v.nombre_usuario,
          email: v.email,
          estado: v.estado
        }));

        setPlanesVenta(planesData);
        setVendedoresDisponibles(vendedoresMapped);
      } catch (error) {
        console.error(error);
        setErrorMessage("No se pudieron cargar los datos desde el servidor.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  // Filtrado
  const planesFiltrados = useMemo(() => {
    if (!filtro.trim()) return planesVenta;
    return planesVenta.filter(plan =>
      plan.periodo.toLowerCase().includes(filtro.toLowerCase()) ||
      plan.vendedores.some(v => v.nombre_usuario.toLowerCase().includes(filtro.toLowerCase())) ||
      plan.valorVentas.toString().includes(filtro)
    );
  }, [planesVenta, filtro]);

  const totalPages = Math.ceil(planesFiltrados.length / itemsPerPage);
  const planesPaginados = planesFiltrados.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  // Crear plan
  const handleAgregarPlan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nuevoPlan.periodo || !nuevoPlan.valorVentas || nuevoPlan.vendedoresSeleccionados.length === 0) {
      setErrorMessage("Por favor completa todos los campos y selecciona al menos un vendedor");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    try {
      const url = `${config.API_BASE_PLANES_URL}/planes_venta?periodo=${encodeURIComponent(nuevoPlan.periodo)}&valor_ventas=${encodeURIComponent(nuevoPlan.valorVentas)}`;
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(nuevoPlan.vendedoresSeleccionados)
      });

      if (!response.ok) throw new Error("Error al crear el plan de venta");

      await response.json();

      // 🔄 Recargar lista
      const planesRes = await fetch(`${config.API_BASE_PLANES_URL}/planes_venta/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const planesDataRaw = await planesRes.json();
      const planesData = planesDataRaw.map((p: any) => ({
        id: p.id,
        periodo: p.periodo,
        valorVentas: p.valor_ventas ?? 0,
        fechaCreacion: p.fecha_creacion,
        estado: p.estado,
        vendedores: p.vendedores || []
      }));

      setPlanesVenta(planesData);
      setNuevoPlan({ periodo: "", valorVentas: "", vendedoresSeleccionados: [] });
      setIsFormOpen(false);
      onSuccess?.(`Plan de venta creado exitosamente`, "success");
    } catch (error: any) {
      console.error(error);
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Editar plan
  const guardarEdicion = async (id: number) => {
    if (!planEditado.periodo || !planEditado.valorVentas || planEditado.vendedoresSeleccionados.length === 0) {
      setErrorMessage("Por favor completa todos los campos y selecciona al menos un vendedor");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${config.API_BASE_PLANES_URL}/planes_venta/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          periodo: planEditado.periodo,
          valor_ventas: parseFloat(planEditado.valorVentas),
          vendedores_ids: planEditado.vendedoresSeleccionados
        })
      });

      if (!response.ok) throw new Error("Error al actualizar plan de venta");

      const actualizadoRaw = await response.json();

      // Normalizar respuesta del backend a formato frontend
      const actualizado: PlanVenta = {
        id: actualizadoRaw.id ?? actualizadoRaw.plan_id,
        periodo: actualizadoRaw.periodo,
        valorVentas: actualizadoRaw.valor_ventas ?? 0,
        fechaCreacion: actualizadoRaw.fecha_creacion ?? "",
        estado: actualizadoRaw.estado ?? "activo",
        vendedores: actualizadoRaw.vendedores || [],
      };

      setPlanesVenta(prev =>
        prev.map(p => (p.id === id ? actualizado : p))
      );

      //  Recargar lista
      const planesRes = await fetch(`${config.API_BASE_PLANES_URL}/planes_venta/`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const planesDataRaw = await planesRes.json();
      const planesData = planesDataRaw.map((p: any) => ({
        id: p.id,
        periodo: p.periodo,
        valorVentas: p.valor_ventas ?? 0,
        fechaCreacion: p.fecha_creacion,
        estado: p.estado,
        vendedores: p.vendedores || []
      }));

      setPlanesVenta(planesData);

      setEditandoId(null);
      onSuccess?.(`Plan actualizado correctamente`, "info");
    } catch (error: any) {
      console.error(error);
      setErrorMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const eliminarPlan = async (id: number) => {
    if (!confirm("¿Seguro que deseas eliminar este plan de venta?")) return;
    try {
      const response = await fetch(`${config.API_BASE_PLANES_URL}/planes_venta/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!response.ok) throw new Error("Error al eliminar plan de venta");

      setPlanesVenta(planesVenta.filter(p => p.id !== id));
      onSuccess?.(`Plan eliminado correctamente`, "warning");
    } catch (error: any) {
      console.error(error);
      setErrorMessage(error.message);
    }
  };

  const iniciarEdicion = (plan: PlanVenta) => {
    setEditandoId(plan.id);
    setPlanEditado({
      periodo: plan.periodo,
      valorVentas: plan.valorVentas.toString(),
      vendedoresSeleccionados: plan.vendedores.map(v => v.usuario_id)
    });
  };

  const cancelarEdicion = () => {
    setEditandoId(null);
    setPlanEditado({ periodo: "", valorVentas: "", vendedoresSeleccionados: [] });
  };

  const toggleVendedorSeleccionado = (id: number, isEditing = false) => {
    if (isEditing) {
      const nuevos = planEditado.vendedoresSeleccionados.includes(id)
        ? planEditado.vendedoresSeleccionados.filter(v => v !== id)
        : [...planEditado.vendedoresSeleccionados, id];
      setPlanEditado({ ...planEditado, vendedoresSeleccionados: nuevos });
    } else {
      const nuevos = nuevoPlan.vendedoresSeleccionados.includes(id)
        ? nuevoPlan.vendedoresSeleccionados.filter(v => v !== id)
        : [...nuevoPlan.vendedoresSeleccionados, id];
      setNuevoPlan({ ...nuevoPlan, vendedoresSeleccionados: nuevos });
    }
  };

  const getPeriodoLabel = (periodo: string) => {
    const labels: any = { mensual: "Mensual", trimestral: "Trimestral", semestral: "Semestral", anual: "Anual" };
    return labels[periodo] || periodo;
  };

  const getEstadoBadge = (estado: string): "default" | "secondary" | "outline" | "destructive" => {
    const variants = { activo: "default", completado: "secondary", pausado: "outline" } as const;
    return variants[estado as keyof typeof variants] || "secondary";
  };

  return (
    <div className="space-y-8">
      <div>
        <h1>Planes de Venta</h1>
        <p className="text-muted-foreground">Gestiona los objetivos de venta del equipo comercial</p>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            title: "Total Planes",
            value: planesVenta?.length ? planesVenta.length.toLocaleString() : "0",
          },
          {
            title: "Vendedores Activos",
            value: (
              new Set(
                (planesVenta ?? []).flatMap(p =>
                  (p.vendedores ?? []).map(v => v.usuario_id)
                )
              ).size
            ).toLocaleString(),
          },
          {
            title: "Valor Total",
            value: `$${Number(
              (planesVenta ?? []).reduce(
                (a, p) => a + Number(p?.valorVentas ?? 0),
                0
              )
            ).toLocaleString()}`,
          },
          {
            title: "Promedio por Plan",
            value:
              (planesVenta?.length ?? 0) > 0
                ? `$${Number(
                  Math.round(
                    (planesVenta ?? []).reduce(
                      (a, p) => a + Number(p?.valorVentas ?? 0),
                      0
                    ) / (planesVenta?.length ?? 1)
                  )
                ).toLocaleString()}`
                : "$0",
          },
        ].map((stat, index) => (
          <Card
            key={index}
            className="shadow-sm border border-gray-200 rounded-2xl"
          >
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-gray-500 font-medium">
                {stat.title}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-semibold text-gray-900">
                {stat.value}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      {/* 🔹 Formulario de creación */}
      <Collapsible open={isFormOpen} onOpenChange={setIsFormOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors pt-3 pb-2">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Plus className="h-5 w-5" />
                  Crear Nuevo Plan de Venta
                </div>
                <ChevronDown className={`h-4 w-4 transition-transform ${isFormOpen ? "rotate-180" : ""}`} />
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
                    <Label>Período</Label>
                    <Select value={nuevoPlan.periodo} onValueChange={val => setNuevoPlan({ ...nuevoPlan, periodo: val })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecciona período" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="mensual">Mensual</SelectItem>
                        <SelectItem value="trimestral">Trimestral</SelectItem>
                        <SelectItem value="semestral">Semestral</SelectItem>
                        <SelectItem value="anual">Anual</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Valor Ventas</Label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        type="number"
                        placeholder="150000"
                        className="pl-10"
                        value={nuevoPlan.valorVentas}
                        onChange={e => setNuevoPlan({ ...nuevoPlan, valorVentas: e.target.value })}
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <Label>Seleccionar Vendedores</Label>
                  <div className="border rounded-lg p-4 max-h-60 overflow-y-auto">
                    <div className="relative mb-3">
                      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        placeholder="Buscar vendedores..."
                        value={filtroVendedores}
                        onChange={e => setFiltroVendedores(e.target.value)}
                        className="pl-10"
                      />
                    </div>

                    {vendedoresDisponibles
                      .filter(v =>
                        v.nombre_usuario.toLowerCase().includes(filtroVendedores.toLowerCase()) ||
                        v.email.toLowerCase().includes(filtroVendedores.toLowerCase())
                      )
                      .map(v => (
                        <div key={v.usuario_id} className="flex items-center space-x-3 p-2 hover:bg-muted rounded">
                          <Checkbox
                            id={`vend-${v.usuario_id}`}
                            checked={nuevoPlan.vendedoresSeleccionados.includes(v.usuario_id)}
                            onCheckedChange={() => toggleVendedorSeleccionado(v.usuario_id)}
                            disabled={!v.estado}
                          />
                          <div className="flex-1">
                            <label htmlFor={`vend-${v.usuario_id}`} className="cursor-pointer text-sm">
                              {v.nombre_usuario}
                            </label>
                            <p className="text-xs text-muted-foreground">{v.email}</p>
                          </div>
                          {!v.estado && <Badge variant="secondary">Inactivo</Badge>}
                        </div>
                      ))}
                  </div>
                </div>

                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Creando..." : "Crear Plan"}
                </Button>
              </form>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>

      {/* 🔹 Lista de planes */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Planes de Venta Registrados</CardTitle>
              <CardDescription>
                {planesFiltrados.length} de {planesVenta.length} planes mostrados
              </CardDescription>
            </div>
            <div className="w-72 relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Filtrar por vendedor o valor..."
                value={filtro}
                onChange={e => setFiltro(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {planesFiltrados.length === 0 ? (
            <div className="text-center py-8">
              <Target className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-muted-foreground">No hay planes registrados</p>
            </div>
          ) : (
            <>
              {planesPaginados.map((plan, index) => (
                <div
                  key={plan?.id ?? `plan-${index}`}
                  className="border rounded-lg p-4 hover:bg-muted/20 transition-colors mb-3"
                >
                  {editandoId === plan.id ? (
                    // 🔸 Modo edición
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Período</Label>
                          <Select
                            value={planEditado.periodo}
                            onValueChange={val => setPlanEditado({ ...planEditado, periodo: val })}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Selecciona período" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="mensual">Mensual</SelectItem>
                              <SelectItem value="trimestral">Trimestral</SelectItem>
                              <SelectItem value="semestral">Semestral</SelectItem>
                              <SelectItem value="anual">Anual</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        <div className="space-y-2">
                          <Label>Valor Ventas</Label>
                          <Input
                            type="number"
                            value={planEditado.valorVentas}
                            onChange={e => setPlanEditado({ ...planEditado, valorVentas: e.target.value })}
                          />
                        </div>
                      </div>

                      <div className="space-y-3">
                        <Label>Vendedores Asignados</Label>
                        <div className="border rounded-lg p-3 max-h-60 overflow-y-auto">
                          {vendedoresDisponibles.map(v => (
                            <div
                              key={v.usuario_id}
                              className="flex items-center space-x-3 p-1 hover:bg-muted rounded"
                            >
                              <Checkbox
                                id={`edit-v-${v.usuario_id}`}
                                checked={planEditado.vendedoresSeleccionados.includes(v.usuario_id)}
                                onCheckedChange={() => toggleVendedorSeleccionado(v.usuario_id, true)}
                                disabled={!v.estado}
                              />
                              <label
                                htmlFor={`edit-v-${v.usuario_id}`}
                                className="cursor-pointer text-sm flex-1"
                              >
                                {v.nombre_usuario}
                              </label>
                              {!v.estado && <Badge variant="secondary">Inactivo</Badge>}
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => guardarEdicion(plan.id)}
                          disabled={isLoading}
                        >
                          <Save className="h-4 w-4 mr-1" /> Guardar
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={cancelarEdicion}
                          disabled={isLoading}
                        >
                          <X className="h-4 w-4 mr-1" /> Cancelar
                        </Button>
                      </div>
                    </div>
                  ) : (
                    // 🔹 Modo visualización
                    <div className="flex justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-medium">{getPeriodoLabel(plan.periodo)}</h3>
                          <Badge variant={getEstadoBadge(plan.estado)}>{plan.estado}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          Valor: ${plan.valorVentas.toLocaleString()} | Vendedores: {plan.vendedores.length}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button size="sm" variant="outline">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-2xl">
                            <DialogHeader>
                              <DialogTitle>Detalle del Plan</DialogTitle>
                              <DialogDescription>ID: {plan.id}</DialogDescription>
                            </DialogHeader>
                            <div className="space-y-3">
                              <p>
                                <strong>Período:</strong> {getPeriodoLabel(plan.periodo)}
                              </p>
                              <p>
                                <strong>Valor de Ventas:</strong> ${Number(plan.valorVentas ?? 0).toLocaleString()}
                              </p>
                              <p>
                                <strong>Vendedores Asignados:</strong>
                              </p>
                              {(plan.vendedores ?? []).length === 0 ? (
                                <div className="text-muted-foreground text-sm border rounded-md p-3">
                                  No hay vendedores asignados a este plan.
                                </div>
                              ) : (
                                (plan.vendedores ?? []).map((v, i) => (
                                  <div
                                    key={v?.usuario_id ?? `v-${plan.id}-${i}`}
                                    className="border p-2 rounded-md flex justify-between items-center"
                                  >
                                    <div>
                                      <p className="font-medium">{v?.nombre_usuario ?? "Desconocido"}</p>
                                      <p className="text-xs text-muted-foreground">{v?.email ?? "Sin email registrado"}</p>
                                    </div>
                                    <Badge variant={v?.estado ? "default" : "secondary"}>
                                      {v?.estado ? "Activo" : "Inactivo"}
                                    </Badge>
                                  </div>
                                ))
                              )}
                            </div>
                          </DialogContent>
                        </Dialog>
                        <Button size="sm" variant="outline" onClick={() => iniciarEdicion(plan)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => eliminarPlan(plan.id)}>
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
                    Mostrando {((currentPage - 1) * itemsPerPage) + 1} a{" "}
                    {Math.min(currentPage * itemsPerPage, planesFiltrados.length)} de {planesFiltrados.length}
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
        </CardContent>
      </Card>
    </div>
  );
}
