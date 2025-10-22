import { useState, useMemo,useEffect } from "react";
import config from "../config/config";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { Edit, Trash2, Save, X, Plus, Mail, User, Search, ChevronDown, AlertCircle, ChevronLeft, ChevronRight } from "lucide-react";

interface Proveedor {
  id: number;
  nombre: string;
  correoElectronico: string;
  fechaCreacion: string;
}

interface ProveedoresViewProps {
  onSuccess: (mensaje: string, tipo?: "success" | "info" | "warning") => void;
}  

export function ProveedoresView({ onSuccess }: ProveedoresViewProps) {
const [proveedores, setProveedores] = useState<Proveedor[]>([]);
  const [nuevoProveedor, setNuevoProveedor] = useState({ nombre: "", correo: "" });
  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [proveedorEditado, setProveedorEditado] = useState({ nombre: "", correo: "" });
  const [isLoading, setIsLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [filtro, setFiltro] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

    //  Cargar proveedores desde el microservicio
  useEffect(() => {
    const cargarProveedores = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`${config.API_BASE_PROVEEDORES_URL}/proveedores/`);
        if (!response.ok) throw new Error("Error al cargar los proveedores");
        const data = await response.json();
        setProveedores(data);
      } catch (error) {
        console.error("Error al cargar proveedores:", error);
        setErrorMessage("No se pudieron cargar los proveedores desde el servidor.");
      } finally {
        setIsLoading(false);
      }
    };
    cargarProveedores();
  }, []);

  // Filtrar proveedores
  const proveedoresFiltrados = useMemo(() => {
    if (!filtro.trim()) return proveedores;
    return proveedores.filter(
      (proveedor) =>
        proveedor.nombre.toLowerCase().includes(filtro.toLowerCase()) ||
        proveedor.correoElectronico.toLowerCase().includes(filtro.toLowerCase())
    );
  }, [proveedores, filtro]);

  // Paginación
  const totalPages = Math.ceil(proveedoresFiltrados.length / itemsPerPage);
  const proveedoresPaginados = proveedoresFiltrados.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

//  Crear proveedor (POST)
  const handleAgregarProveedor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nuevoProveedor.nombre.trim() || !nuevoProveedor.correo.trim()) return;

    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await fetch(`${config.API_BASE_PROVEEDORES_URL}/proveedores/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nombre: nuevoProveedor.nombre.trim(),
          correoElectronico: nuevoProveedor.correo.trim(),
          estado: "activo"
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Error al agregar proveedor");
      }

      const nuevo = await response.json();
      setProveedores([...proveedores, nuevo]);
      setNuevoProveedor({ nombre: "", correo: "" });
      setIsFormOpen(false);
      onSuccess?.(`Proveedor "${nuevo.nombre}" agregado exitosamente`, "success");
    } catch (error: any) {
      console.error(error);
      setErrorMessage(error.message || "Error al agregar proveedor");
    } finally {
      setIsLoading(false);
    }
  };

  // Iniciar edición
  const iniciarEdicion = (proveedor: Proveedor) => {
    setEditandoId(proveedor.id);
    setProveedorEditado({ nombre: proveedor.nombre, correo: proveedor.correoElectronico });
  };

  // Cancelar edición
  const cancelarEdicion = () => {
    setEditandoId(null);
    setProveedorEditado({ nombre: "", correo: "" });
  };

  // 🔹 Guardar cambios (PUT)
  const guardarEdicion = async (id: number) => {
    if (!proveedorEditado.nombre.trim() || !proveedorEditado.correo.trim()) return;

    setIsLoading(true);
    setErrorMessage("");

    try {
      const response = await fetch(`${config.API_BASE_PROVEEDORES_URL}/proveedores/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nombre: proveedorEditado.nombre.trim(),
          correoElectronico: proveedorEditado.correo.trim(),
          estado: "activo"
        }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Error al actualizar proveedor");
      }

      const actualizado = await response.json();
      setProveedores(
        proveedores.map((p) => (p.id === id ? actualizado : p))
      );
      setEditandoId(null);
      setProveedorEditado({ nombre: "", correo: "" });
      onSuccess?.(`Proveedor "${actualizado.nombre}" actualizado correctamente`, "info");
    } catch (error: any) {
      console.error(error);
      setErrorMessage(error.message || "Error al actualizar proveedor");
    } finally {
      setIsLoading(false);
    }
  };

  // 🔹 Eliminar proveedor (DELETE)
  const eliminarProveedor = async (id: number) => {
    if (!confirm("¿Seguro que deseas eliminar este proveedor?")) return;

    try {
      const response = await fetch(`${config.API_BASE_PROVEEDORES_URL}/proveedores/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Error al eliminar proveedor");

      setProveedores(proveedores.filter((p) => p.id !== id));
      onSuccess?.(`Proveedor eliminado correctamente`, "warning");
    } catch (error: any) {
      console.error(error);
      setErrorMessage(error.message || "Error al eliminar proveedor");
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1>Gestión de Proveedores</h1>
        <p className="text-muted-foreground">
          Administra y supervisa todos los proveedores farmacéuticos
        </p>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Total Proveedores</CardTitle>
            <CardDescription>Proveedores activos</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{proveedores.length}</div>
            <p className="text-xs text-muted-foreground">
              {proveedores.length > 0 ? `Último agregado: ${new Date(proveedores[0]?.fechaCreacion).toLocaleDateString('es-ES')}` : 'Ningún proveedor registrado'}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Promedio Mensual</CardTitle>
            <CardDescription>Nuevos proveedores por mes</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">2.5</div>
            <p className="text-xs text-muted-foreground">Basado en los últimos 6 meses</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Estado del Sistema</CardTitle>
            <CardDescription>Conectividad con proveedores</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 bg-green-500 rounded-full"></div>
              <span>Activo</span>
            </div>
            <p className="text-xs text-muted-foreground">Todos los sistemas funcionando</p>
          </CardContent>
        </Card>
      </div>

      {/* Formulario para agregar nuevo proveedor */}
      <Collapsible open={isFormOpen} onOpenChange={setIsFormOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors pt-3 pb-2">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Plus className="h-5 w-5" />
                  Agregar Nuevo Proveedor
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
              <form onSubmit={handleAgregarProveedor} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="nombre">Nombre del Proveedor</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="nombre"
                        placeholder="Ingresa el nombre del proveedor"
                        value={nuevoProveedor.nombre}
                        onChange={(e) => {
                          setNuevoProveedor({
                            ...nuevoProveedor,
                            nombre: e.target.value
                          });
                          setErrorMessage("");
                        }}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="correo">Correo Electrónico</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="correo"
                        type="email"
                        placeholder="contacto@proveedor.com"
                        value={nuevoProveedor.correo}
                        onChange={(e) => {
                          setNuevoProveedor({
                            ...nuevoProveedor,
                            correo: e.target.value
                          });
                          setErrorMessage("");
                        }}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>
                </div>
                
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Agregando..." : "Agregar Proveedor"}
                </Button>
              </form>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>

      {/* Lista de proveedores existentes */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Proveedores Registrados</CardTitle>
              <CardDescription>
                {proveedoresFiltrados.length} de {proveedores.length} proveedor{proveedores.length !== 1 ? 'es' : ''} mostrado{proveedoresFiltrados.length !== 1 ? 's' : ''}
              </CardDescription>
            </div>
            <div className="w-72">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Filtrar por nombre o correo..."
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
            {proveedoresFiltrados.length === 0 ? (
              <div className="text-center py-8">
                <User className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  {filtro ? "No se encontraron proveedores con ese filtro" : "No hay proveedores registrados"}
                </p>
                <p className="text-sm text-muted-foreground">
                  {filtro ? "Intenta con otros términos de búsqueda" : "Agrega tu primer proveedor usando el formulario de arriba"}
                </p>
              </div>
            ) : (
              <>
                {proveedoresPaginados.map((proveedor) => (
                <div key={proveedor.id} className="border rounded-lg p-4 hover:bg-muted/20 transition-colors">
                  {editandoId === proveedor.id ? (
                    /* Modo edición */
                    <div className="space-y-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="relative">
                          <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                          <Input
                            value={proveedorEditado.nombre}
                            onChange={(e) => setProveedorEditado({
                              ...proveedorEditado,
                              nombre: e.target.value
                            })}
                            placeholder="Nombre del proveedor"
                            className="pl-10"
                          />
                        </div>
                        <div className="relative">
                          <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                          <Input
                            type="email"
                            value={proveedorEditado.correo}
                            onChange={(e) => setProveedorEditado({
                              ...proveedorEditado,
                              correo: e.target.value
                            })}
                            placeholder="correo@proveedor.com"
                            className="pl-10"
                          />
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          onClick={() => guardarEdicion(proveedor.id)}
                          disabled={!proveedorEditado.nombre.trim() || !proveedorEditado.correo.trim()}
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
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-3">
                          <h3 className="font-medium">{proveedor.nombre}</h3>
                          <Badge variant="secondary">
                            ID: {proveedor.id}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Mail className="h-4 w-4" />
                          {proveedor.correoElectronico}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Registrado: {new Date(proveedor.fechaCreacion).toLocaleDateString('es-ES')}
                        </p>
                      </div>
                      
                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => iniciarEdicion(proveedor)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => eliminarProveedor(proveedor.id)}
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
                    Mostrando {((currentPage - 1) * itemsPerPage) + 1} a {Math.min(currentPage * itemsPerPage, proveedoresFiltrados.length)} de {proveedoresFiltrados.length} resultados
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