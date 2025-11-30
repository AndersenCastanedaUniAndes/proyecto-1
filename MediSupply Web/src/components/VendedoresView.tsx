import { useState, useMemo, useEffect } from "react";
import config from "../config/config";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Alert, AlertDescription } from "./ui/alert";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import {
  Edit,
  Trash2,
  Save,
  X,
  Plus,
  Mail,
  User,
  Search,
  ChevronDown,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Eye,
  EyeOff,
  Lock,
  UserCheck
} from "lucide-react";

interface Vendedor {
  usuario_id: number;
  nombre_usuario: string;
  email: string;
  rol: string;
  contrasena: string;
  estado: boolean;
  created_at: Date;
}

interface VendedoresViewProps {
  onSuccess: (mensaje: string, tipo?: "success" | "info" | "warning") => void;

}

export function VendedoresView({ onSuccess }: VendedoresViewProps) {
  const [vendedores, setVendedores] = useState<Vendedor[]>([]);

  const [nuevoVendedor, setNuevoVendedor] = useState({
    nombre_usuario: "",
    email: "",
    contrasena: ""
  });

  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [vendedorEditado, setVendedorEditado] = useState({
    nombre_usuario: "",
    email: "",
    contrasena: ""
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [filtro, setFiltro] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [showEditPassword, setShowEditPassword] = useState(false);
  const itemsPerPage = 5;


  //  Cargar vendedores desde el backend
  useEffect(() => {
    const cargarVendedores = async () => {
      const token = localStorage.getItem("access_token");
      const tokenType = localStorage.getItem("token_type") || "Bearer";

      if (!token) {
        setErrorMessage("No se encontró un token de autenticación. Inicia sesión nuevamente.");
        return;
      }
      try {
        setIsLoading(true);
        setErrorMessage("");

        const response = await fetch(
          `${config.API_BASE_LOGIN_URL}/vendedores?skip=0&limit=100`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `${tokenType} ${token}`,
            },
          }
        );
        if (!response.ok) {
          // Intentar extraer mensaje de error del backend
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || "Error al cargar los vendedores");
        }

        const data = await response.json();
        setVendedores(data);

      } catch (error: any) {
        console.error("Error al cargar vendedores:", error);
        setErrorMessage(error.message || "No se pudieron cargar los vendedores desde el servidor.");
      } finally {
        setIsLoading(false);
      }
    };
    cargarVendedores();
  }, []);


  // Filtrar vendedores
  const vendedoresFiltrados = useMemo(() => {
    if (!filtro.trim()) return vendedores;
    return vendedores.filter(
      (v) =>
        v.nombre_usuario.toLowerCase().includes(filtro.toLowerCase()) ||
        v.email.toLowerCase().includes(filtro.toLowerCase())
    );
  }, [vendedores, filtro]);

  // Paginación
  const totalPages = Math.ceil(vendedoresFiltrados.length / itemsPerPage);
  const vendedoresPaginados = vendedoresFiltrados.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  //  Crear vendedor (POST)
  const handleAgregarVendedor = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validar campos requeridos
    if (!nuevoVendedor.nombre_usuario || !nuevoVendedor.email || !nuevoVendedor.contrasena) {
      setErrorMessage("Por favor completa todos los campos requeridos.");
      return;
    }

    // Obtener token del localStorage
    const token = localStorage.getItem("access_token");
    const tokenType = localStorage.getItem("token_type") || "Bearer";

    if (!token) {
      setErrorMessage("No se encontró el token de autenticación. Inicia sesión nuevamente.");
      return;
    }

    try {
      setIsLoading(true);
      setErrorMessage("");

      const response = await fetch(`${config.API_BASE_LOGIN_URL}/vendedor`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `${tokenType} ${token}`,
        },
        body: JSON.stringify({
          nombre_usuario: nuevoVendedor.nombre_usuario.trim(),
          email: nuevoVendedor.email.trim(),
          contrasena: nuevoVendedor.contrasena.trim(),
          rol: "vendedor"
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || errData.message || "Error al crear el vendedor");
      }

      const nuevo = await response.json();

      // Actualizar lista y limpiar formulario
      setVendedores((prev) => [...prev, nuevo]);
      setNuevoVendedor({ nombre_usuario: "", email: "", contrasena: "" });
      setIsFormOpen(false);

      onSuccess?.(`Vendedor "${nuevo.nombre_usuario}" agregado exitosamente`, "success");
    } catch (error: any) {
      console.error("Error al agregar vendedor:", error);
      setErrorMessage(error.message || "Error al agregar vendedor");
    } finally {
      setIsLoading(false);
    }
  };


  //  Editar vendedor (PUT)
  const guardarEdicion = async (id: number) => {
    if (!vendedorEditado.nombre_usuario.trim() || !vendedorEditado.email.trim()) {
      setErrorMessage("Por favor completa todos los campos requeridos antes de guardar.");
      return;
    }

    // Obtener token del localStorage
    const token = localStorage.getItem("access_token");
    const tokenType = localStorage.getItem("token_type") || "Bearer";

    if (!token) {
      setErrorMessage("No se encontró el token de autenticación. Inicia sesión nuevamente.");
      return;
    }

    try {
      setIsLoading(true);
      setErrorMessage("");

      const response = await fetch(`${config.API_BASE_LOGIN_URL}/vendedor/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `${tokenType} ${token}`,
        },
        body: JSON.stringify({
          nombre_usuario: vendedorEditado.nombre_usuario.trim(),
          email: vendedorEditado.email.trim(),
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || errData.message || "Error al actualizar el vendedor");
      }

      const actualizado = await response.json();

      // Actualizar lista local
      setVendedores((prev) =>
        prev.map((v) => (v.usuario_id === id ? actualizado : v))
      );

      setEditandoId(null);
      onSuccess?.(`Vendedor "${actualizado.nombre_usuario}" actualizado correctamente`, "info");
    } catch (error: any) {
      console.error("Error al actualizar vendedor:", error);
      setErrorMessage(error.message || "Error al actualizar vendedor");
    } finally {
      setIsLoading(false);
    }
  };

  //  Eliminar vendedor (DELETE)
  const eliminarVendedor = async (id: number) => {
    if (!confirm("¿Seguro que deseas eliminar este vendedor?")) return;

    // Obtener token desde localStorage
    const token = localStorage.getItem("access_token");
    const tokenType = localStorage.getItem("token_type") || "Bearer";

    if (!token) {
      setErrorMessage("No se encontró el token de autenticación. Inicia sesión nuevamente.");
      return;
    }

    try {
      setIsLoading(true);
      setErrorMessage("");

      const response = await fetch(`${config.API_BASE_LOGIN_URL}/vendedor/${id}`, {
        method: "DELETE",
        headers: {
          "Authorization": `${tokenType} ${token}`,
        },
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || errData.message || "Error al eliminar el vendedor");
      }

      // Actualizar lista local de vendedores
      setVendedores((prev) => prev.filter((v) => v.usuario_id !== id));

      onSuccess?.("Vendedor eliminado correctamente", "warning");
    } catch (error: any) {
      console.error("Error al eliminar vendedor:", error);
      setErrorMessage(error.message || "Error al eliminar vendedor");
    } finally {
      setIsLoading(false);
    }
  };

  // Activar/Desactivar vendedor
  const toggleEstadoVendedor = async (id: number) => {
    try {
      const vendedor = vendedores.find((v) => v.usuario_id === id);
      if (!vendedor) return;

      const token = localStorage.getItem("access_token");
      const tokenType = localStorage.getItem("token_type") || "Bearer";

      if (!token) {
        setErrorMessage("No se encontró token de autenticación");
        return;
      }

      const response = await fetch(`${config.API_BASE_LOGIN_URL}/vendedor/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `${tokenType} ${token}`,
        },
        body: JSON.stringify({

          nombre_usuario: vendedor.nombre_usuario,
          email: vendedor.email,
          contrasena: vendedor.contrasena,
          rol: vendedor.rol,
          estado: !vendedor.estado

        }), // cambia estado (true/false)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Error al cambiar estado del vendedor");
      }

      const actualizado = await response.json();

      setVendedores(vendedores.map((v) => (v.usuario_id === id ? actualizado : v)));
      onSuccess?.(
        `Vendedor "${actualizado.nombre_usuario}" ${actualizado.estado ? "activado" : "desactivado"}`,
        "info"
      );
    } catch (error: any) {
      console.error("Error al cambiar estado del vendedor:", error);
      setErrorMessage(error.message);
    }
  };


  //  Control edición
  const iniciarEdicion = (v: Vendedor) => {
    setEditandoId(v.usuario_id);
    setVendedorEditado({ nombre_usuario: v.nombre_usuario, email: v.email, contrasena: "" });
  };
  const cancelarEdicion = () => {
    setEditandoId(null);
    setVendedorEditado({ nombre_usuario: "", email: "", contrasena: "" });
    setErrorMessage("");
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1>Gestión de Vendedores</h1>
        <p className="text-muted-foreground">
          Administra y supervisa el equipo de vendedores
        </p>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Total Vendedores</CardTitle>
            <CardDescription>Vendedores registrados</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{vendedores.length}</div>
            <p className="text-xs text-muted-foreground">
              {vendedores.filter(v => v.estado).length} activos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Vendedores Activos</CardTitle>
            <CardDescription>Estado actual</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {vendedores.filter(v => v.estado).length}
            </div>
            <p className="text-xs text-muted-foreground">
              {Math.round((vendedores.filter(v => v.estado).length / vendedores.length) * 100)}% del total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Vendedores Inactivos</CardTitle>
            <CardDescription>Requieren atención</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {vendedores.filter(v => !v.estado).length}
            </div>
            <p className="text-xs text-muted-foreground">
              {vendedores.filter(v => !v.estado).length > 0 ? "Revisar estado" : "Todos activos"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Nuevos Este Mes</CardTitle>
            <CardDescription>Vendedores recientes</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {vendedores.filter(v => {
                const fechaCreacion = new Date(v.created_at);
                const hoy = new Date();
                const inicioMes = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
                return fechaCreacion >= inicioMes;
              }).length}
            </div>
            <p className="text-xs text-muted-foreground">
              En los últimos 30 días
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Formulario para agregar nuevo vendedor */}
      <Collapsible open={isFormOpen} onOpenChange={setIsFormOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors pt-3 pb-2">
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Plus className="h-5 w-5" />
                  Agregar Nuevo Vendedor
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
              <form onSubmit={handleAgregarVendedor} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="nombre">Nombre Completo</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="nombre"
                        placeholder="Nombre completo del vendedor"
                        value={nuevoVendedor.nombre_usuario}
                        onChange={(e) => {
                          setNuevoVendedor({
                            ...nuevoVendedor,
                            nombre_usuario: e.target.value
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
                        placeholder="vendedor@medisupply.com"
                        value={nuevoVendedor.email}
                        onChange={(e) => {
                          setNuevoVendedor({
                            ...nuevoVendedor,
                            email: e.target.value
                          });
                          setErrorMessage("");
                        }}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="password">Contraseña</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Contraseña temporal"
                        value={nuevoVendedor.contrasena}
                        onChange={(e) => {
                          setNuevoVendedor({
                            ...nuevoVendedor,
                            contrasena: e.target.value
                          });
                          setErrorMessage("");
                        }}
                        className="pl-10 pr-10"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Agregando..." : "Agregar Vendedor"}
                </Button>
              </form>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>

      {/* Lista de vendedores existentes */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Vendedores Registrados</CardTitle>
              <CardDescription>
                {vendedoresFiltrados.length} de {vendedores.length} vendedor{vendedores.length !== 1 ? 'es' : ''} mostrado{vendedoresFiltrados.length !== 1 ? 's' : ''}
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
            {vendedoresFiltrados.length === 0 ? (
              <div className="text-center py-8">
                <UserCheck className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  {filtro ? "No se encontraron vendedores con ese filtro" : "No hay vendedores registrados"}
                </p>
                <p className="text-sm text-muted-foreground">
                  {filtro ? "Intenta con otros términos de búsqueda" : "Agrega tu primer vendedor usando el formulario de arriba"}
                </p>
              </div>
            ) : (
              <>
                {vendedoresPaginados.map((vendedor) => (
                  <div key={vendedor.usuario_id} className="border rounded-lg p-4 hover:bg-muted/20 transition-colors">
                    {editandoId === vendedor.usuario_id ? (
                      /* Modo edición */
                      <div className="space-y-3">
                        {errorMessage && (
                          <Alert variant="destructive">
                            <AlertCircle className="h-4 w-4" />
                            <AlertDescription>{errorMessage}</AlertDescription>
                          </Alert>
                        )}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          <div className="relative">
                            <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                              value={vendedorEditado.nombre_usuario}
                              onChange={(e) => setVendedorEditado({
                                ...vendedorEditado,
                                nombre_usuario: e.target.value
                              })}
                              placeholder="Nombre del vendedor"
                              className="pl-10"
                            />
                          </div>
                          <div className="relative">
                            <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                              type="email"
                              value={vendedorEditado.email}
                              onChange={(e) => setVendedorEditado({
                                ...vendedorEditado,
                                email: e.target.value
                              })}
                              placeholder="correo@vendedor.com"
                              className="pl-10"
                            />
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => guardarEdicion(vendedor.usuario_id)}
                            disabled={!vendedorEditado.nombre_usuario.trim() || !vendedorEditado.email.trim()}
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
                        <div className="space-y-1 flex-1">
                          <div className="flex items-center gap-3">
                            <h3 className="font-medium">{vendedor.nombre_usuario}</h3>
                            <Badge variant="secondary">
                              ID: {vendedor.usuario_id}
                            </Badge>
                            <Badge variant={vendedor.estado ? "default" : "secondary"}>
                              {vendedor.estado ? "Activo" : "Inactivo"}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Mail className="h-4 w-4" />
                            {vendedor.email}
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Registrado: {new Date(vendedor.created_at).toLocaleDateString('es-ES')}
                          </p>
                        </div>

                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant={vendedor.estado ? "outline" : "default"}
                            onClick={() => toggleEstadoVendedor(vendedor.usuario_id)}
                          >
                            {vendedor.estado ? "Desactivar" : "Activar"}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => iniciarEdicion(vendedor)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => eliminarVendedor(vendedor.usuario_id)}
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
                      Mostrando {((currentPage - 1) * itemsPerPage) + 1} a {Math.min(currentPage * itemsPerPage, vendedoresFiltrados.length)} de {vendedoresFiltrados.length} resultados
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