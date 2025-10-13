import { useState, useMemo } from "react";
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
  id: number;
  nombre: string;
  correo: string;
  fechaCreacion: string;
  activo: boolean;
}

interface VendedoresViewProps {
  onSuccess?: (message: string) => void;
}

export function VendedoresView({ onSuccess }: VendedoresViewProps) {
  const [vendedores, setVendedores] = useState<Vendedor[]>([
    {
      id: 1,
      nombre: "Ana García Rodríguez",
      correo: "ana.garcia@medisupply.com",
      fechaCreacion: "2024-01-10",
      activo: true
    },
    {
      id: 2,
      nombre: "Carlos Mendoza Silva",
      correo: "carlos.mendoza@medisupply.com",
      fechaCreacion: "2024-01-25",
      activo: true
    },
    {
      id: 3,
      nombre: "María Elena Vásquez",
      correo: "maria.vasquez@medisupply.com",
      fechaCreacion: "2024-02-15",
      activo: false
    }
  ]);

  const [nuevoVendedor, setNuevoVendedor] = useState({
    nombre: "",
    correo: "",
    password: ""
  });

  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [vendedorEditado, setVendedorEditado] = useState({
    nombre: "",
    correo: "",
    password: ""
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [filtro, setFiltro] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [showEditPassword, setShowEditPassword] = useState(false);
  const itemsPerPage = 5;

  // Filtrar vendedores
  const vendedoresFiltrados = useMemo(() => {
    if (!filtro.trim()) return vendedores;
    return vendedores.filter(vendedor => 
      vendedor.nombre.toLowerCase().includes(filtro.toLowerCase()) ||
      vendedor.correo.toLowerCase().includes(filtro.toLowerCase())
    );
  }, [vendedores, filtro]);

  // Paginación
  const totalPages = Math.ceil(vendedoresFiltrados.length / itemsPerPage);
  const vendedoresPaginados = vendedoresFiltrados.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Verificar si el correo ya existe
  const correoExiste = (correo: string, excludeId?: number) => {
    return vendedores.some(v => v.correo.toLowerCase() === correo.toLowerCase() && v.id !== excludeId);
  };

  const handleAgregarVendedor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nuevoVendedor.nombre.trim() || !nuevoVendedor.correo.trim() || !nuevoVendedor.password.trim()) return;

    // Verificar si el correo ya existe
    if (correoExiste(nuevoVendedor.correo.trim())) {
      setErrorMessage("Ya existe un vendedor registrado con este correo electrónico");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    
    // Simular guardado
    setTimeout(() => {
      const nuevo: Vendedor = {
        id: Math.max(...vendedores.map(v => v.id), 0) + 1,
        nombre: nuevoVendedor.nombre.trim(),
        correo: nuevoVendedor.correo.trim(),
        fechaCreacion: new Date().toISOString().split('T')[0],
        activo: true
      };

      setVendedores([...vendedores, nuevo]);
      setNuevoVendedor({ nombre: "", correo: "", password: "" });
      setIsLoading(false);
      setShowPassword(false);
      setIsFormOpen(false);
      onSuccess?.(`Vendedor "${nuevo.nombre}" agregado exitosamente`);
    }, 1000);
  };

  const iniciarEdicion = (vendedor: Vendedor) => {
    setEditandoId(vendedor.id);
    setVendedorEditado({
      nombre: vendedor.nombre,
      correo: vendedor.correo,
      password: ""
    });
  };

  const cancelarEdicion = () => {
    setEditandoId(null);
    setVendedorEditado({ nombre: "", correo: "", password: "" });
    setErrorMessage("");
    setShowEditPassword(false);
  };

  const guardarEdicion = (id: number) => {
    if (!vendedorEditado.nombre.trim() || !vendedorEditado.correo.trim()) return;

    // Verificar si el correo ya existe (excluyendo el vendedor actual)
    if (correoExiste(vendedorEditado.correo.trim(), id)) {
      setErrorMessage("Ya existe un vendedor registrado con este correo electrónico");
      return;
    }

    setVendedores(vendedores.map(v => 
      v.id === id 
        ? { 
            ...v, 
            nombre: vendedorEditado.nombre.trim(), 
            correo: vendedorEditado.correo.trim()
          }
        : v
    ));
    setEditandoId(null);
    setVendedorEditado({ nombre: "", correo: "", password: "" });
    setErrorMessage("");
    setShowEditPassword(false);
  };

  const eliminarVendedor = (id: number) => {
    setVendedores(vendedores.filter(v => v.id !== id));
  };

  const toggleEstadoVendedor = (id: number) => {
    setVendedores(vendedores.map(v => 
      v.id === id ? { ...v, activo: !v.activo } : v
    ));
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
              {vendedores.filter(v => v.activo).length} activos
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
              {vendedores.filter(v => v.activo).length}
            </div>
            <p className="text-xs text-muted-foreground">
              {Math.round((vendedores.filter(v => v.activo).length / vendedores.length) * 100)}% del total
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
              {vendedores.filter(v => !v.activo).length}
            </div>
            <p className="text-xs text-muted-foreground">
              {vendedores.filter(v => !v.activo).length > 0 ? "Revisar estado" : "Todos activos"}
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
                const fechaCreacion = new Date(v.fechaCreacion);
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
                        value={nuevoVendedor.nombre}
                        onChange={(e) => {
                          setNuevoVendedor({
                            ...nuevoVendedor,
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
                        placeholder="vendedor@medisupply.com"
                        value={nuevoVendedor.correo}
                        onChange={(e) => {
                          setNuevoVendedor({
                            ...nuevoVendedor,
                            correo: e.target.value
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
                        value={nuevoVendedor.password}
                        onChange={(e) => {
                          setNuevoVendedor({
                            ...nuevoVendedor,
                            password: e.target.value
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
                  <div key={vendedor.id} className="border rounded-lg p-4 hover:bg-muted/20 transition-colors">
                    {editandoId === vendedor.id ? (
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
                              value={vendedorEditado.nombre}
                              onChange={(e) => setVendedorEditado({
                                ...vendedorEditado,
                                nombre: e.target.value
                              })}
                              placeholder="Nombre del vendedor"
                              className="pl-10"
                            />
                          </div>
                          <div className="relative">
                            <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                            <Input
                              type="email"
                              value={vendedorEditado.correo}
                              onChange={(e) => setVendedorEditado({
                                ...vendedorEditado,
                                correo: e.target.value
                              })}
                              placeholder="correo@vendedor.com"
                              className="pl-10"
                            />
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            onClick={() => guardarEdicion(vendedor.id)}
                            disabled={!vendedorEditado.nombre.trim() || !vendedorEditado.correo.trim()}
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
                            <h3 className="font-medium">{vendedor.nombre}</h3>
                            <Badge variant="secondary">
                              ID: {vendedor.id}
                            </Badge>
                            <Badge variant={vendedor.activo ? "default" : "secondary"}>
                              {vendedor.activo ? "Activo" : "Inactivo"}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Mail className="h-4 w-4" />
                            {vendedor.correo}
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Registrado: {new Date(vendedor.fechaCreacion).toLocaleDateString('es-ES')}
                          </p>
                        </div>
                        
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            variant={vendedor.activo ? "outline" : "default"}
                            onClick={() => toggleEstadoVendedor(vendedor.id)}
                          >
                            {vendedor.activo ? "Desactivar" : "Activar"}
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
                            onClick={() => eliminarVendedor(vendedor.id)}
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