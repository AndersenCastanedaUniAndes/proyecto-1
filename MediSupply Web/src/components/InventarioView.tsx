import { useState, useMemo, useEffect } from "react";
import config from "../config/config";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { 
  Package, 
  Search, 
  Eye, 
  ChevronLeft, 
  ChevronRight,
  Warehouse,
  AlertTriangle,
  CheckCircle,
  XCircle,
  BarChart3,
  Hash,
  MapPin
} from "lucide-react";

interface Bodega {
  id: number;
  nombre: string;
  direccion: string;
  cantidad_disponible: number;
  pasillo: string;
  estante: string;
}

interface ProductoInventario {
  id: number;
  nombre: string;
  lote: string;
  sku: string;
  stock_total: number;
  stock_minimo: number;
  status: "disponible" | "existencias bajas" | "agotado";
  bodegas: Bodega[];
  fecha_ultima_actualizacion: string;
  proveedor: string;
  categoria: string;
  valor_unitario: number;
}

export function InventarioView() {
  const [productosInventario, setInventario] = useState<ProductoInventario[]>([]);

  const [filtro, setFiltro] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 6;

  useEffect(() => {
    const cargarInventario = async () => {
      try {
        const response = await fetch(`${config.API_BASE_INVENTARIO_URL}/inventario/productos`);
        if (!response.ok) throw new Error("Error al cargar proveedores");
        const data = await response.json();
        setInventario(data);
      } catch (error) {
        console.error("Error al cargar proveedores:", error);
        setInventario([]);
      }
    };

    cargarInventario();
  }, []);

  // Filtrar productos
  const productosFiltrados = useMemo(() => {
    if (!filtro.trim()) return productosInventario;
    return productosInventario.filter(producto => 
      producto.nombre.toLowerCase().includes(filtro.toLowerCase()) ||
      producto.sku.toLowerCase().includes(filtro.toLowerCase()) ||
      producto.lote.toLowerCase().includes(filtro.toLowerCase()) ||
      producto.proveedor.toLowerCase().includes(filtro.toLowerCase())
    );
  }, [productosInventario, filtro]);

  // Paginación
  const totalPages = Math.ceil(productosFiltrados.length / itemsPerPage);
  const productosPaginados = productosFiltrados.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // Funciones auxiliares
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "disponible":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "existencias bajas":
        return <AlertTriangle className="h-4 w-4 text-orange-500" />;
      case "agotado":
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <CheckCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "disponible":
        return <Badge variant="default" className="bg-green-500">Disponible</Badge>;
      case "existencias bajas":
        return <Badge variant="destructive" className="bg-orange-500">Existencias Bajas</Badge>;
      case "agotado":
        return <Badge variant="destructive">Agotado</Badge>;
      default:
        return <Badge variant="secondary">Desconocido</Badge>;
    }
  };

  const getStatusLabel = (status: string) => {
    const labels = {
      "disponible": "Disponible",
      "existencias bajas": "Existencias Bajas",
      "agotado": "Agotado"
    };
    return labels[status as keyof typeof labels] || status;
  };

  // Estadísticas generales
  const estadisticas = {
    totalProductos: productosInventario.length,
    disponibles: productosInventario.filter(p => p.status === "disponible").length,
    existenciasBajas: productosInventario.filter(p => p.status === "existencias bajas").length,
    agotados: productosInventario.filter(p => p.status === "agotado").length,
    valorTotalInventario: productosInventario.reduce((acc, p) => acc + (p.stock_total * p.valor_unitario), 0),
    bodegasUnicas: new Set(productosInventario.flatMap(p => p.bodegas.map(b => b.nombre))).size
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1>Inventario</h1>
        <p className="text-muted-foreground">
          Consulta y supervisa el stock de productos en todas las bodegas
        </p>
      </div>

      {/* Estadísticas rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total Productos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estadisticas.totalProductos}</div>
            <p className="text-xs text-muted-foreground">registrados</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Disponibles</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{estadisticas.disponibles}</div>
            <p className="text-xs text-muted-foreground">en stock</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Existencias Bajas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{estadisticas.existenciasBajas}</div>
            <p className="text-xs text-muted-foreground">stock bajo</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Agotados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{estadisticas.agotados}</div>
            <p className="text-xs text-muted-foreground">sin stock</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Valor Total</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${estadisticas.valorTotalInventario.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">inventario</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Bodegas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estadisticas.bodegasUnicas}</div>
            <p className="text-xs text-muted-foreground">ubicaciones</p>
          </CardContent>
        </Card>
      </div>

      {/* Lista de productos */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Productos en Inventario</CardTitle>
              <CardDescription>
                {productosFiltrados.length} de {productosInventario.length} producto{productosInventario.length !== 1 ? 's' : ''} mostrado{productosFiltrados.length !== 1 ? 's' : ''}
              </CardDescription>
            </div>
            <div className="w-72">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Filtrar por nombre, SKU, lote o proveedor..."
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
                  {filtro ? "No se encontraron productos con ese filtro" : "No hay productos en inventario"}
                </p>
                <p className="text-sm text-muted-foreground">
                  {filtro ? "Intenta con otros términos de búsqueda" : "Los productos aparecerán aquí una vez sean registrados"}
                </p>
              </div>
            ) : (
              <>
                {productosPaginados.map((producto) => (
                  <div key={producto.id} className="border rounded-lg p-4 hover:bg-muted/20 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="space-y-2 flex-1">
                        <div className="flex items-center gap-3 flex-wrap">
                          <h3 className="font-medium">{producto.nombre}</h3>
                          <Badge variant="outline">SKU: {producto.sku}</Badge>
                          <Badge variant="secondary">Lote: {producto.lote}</Badge>
                          {getStatusBadge(producto.status)}
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                          <div className="flex items-center gap-2">
                            <Package className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Stock:</span> 
                            <span className={producto.stock_total <= producto.stock_minimo ? 'text-orange-600 font-medium' : ''}>
                              {producto.stock_total.toLocaleString()} unid.
                            </span>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <BarChart3 className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Min.:</span> {producto.stock_minimo.toLocaleString()} unid.
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <Warehouse className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Bodegas:</span> {producto.bodegas.length}
                          </div>
                          
                          <div className="flex items-center gap-2">
                            {getStatusIcon(producto.status)}
                            <span className="font-medium">Estado:</span> {getStatusLabel(producto.status)}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-muted-foreground">
                          <div>
                            <span className="font-medium">Proveedor:</span> {producto.proveedor}
                          </div>
                          <div>
                            <span className="font-medium">Categoría:</span> {producto.categoria}
                          </div>
                          <div>
                            <span className="font-medium">Valor Unit.:</span> ${producto.valor_unitario.toFixed(2)}
                          </div>
                        </div>
                        
                        <p className="text-xs text-muted-foreground">
                          Última actualización: {new Date(producto.fecha_ultima_actualizacion).toLocaleDateString('es-ES')}
                        </p>
                      </div>
                      
                      <div className="ml-4">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button size="sm" variant="outline">
                              <Eye className="h-4 w-4 mr-1" />
                              Detalle
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-3xl">
                            <DialogHeader>
                              <DialogTitle>Detalle de Inventario - {producto.nombre}</DialogTitle>
                              <DialogDescription>
                                Información detallada del producto y su distribución por bodegas
                              </DialogDescription>
                            </DialogHeader>
                            
                            <div className="space-y-6">
                              {/* Información general */}
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <h4 className="font-medium mb-2">Información del Producto</h4>
                                  <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                      <span>Nombre:</span>
                                      <span className="font-medium">{producto.nombre}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>SKU:</span>
                                      <span className="font-medium">{producto.sku}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Lote:</span>
                                      <span className="font-medium">{producto.lote}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Categoría:</span>
                                      <span className="font-medium">{producto.categoria}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Proveedor:</span>
                                      <span className="font-medium">{producto.proveedor}</span>
                                    </div>
                                  </div>
                                </div>
                                
                                <div>
                                  <h4 className="font-medium mb-2">Stock y Valores</h4>
                                  <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                      <span>Stock Total:</span>
                                      <span className={`font-medium ${producto.stock_total <= producto.stock_minimo ? 'text-orange-600' : ''}`}>
                                        {producto.stock_total.toLocaleString()} unid.
                                      </span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Stock Mínimo:</span>
                                      <span className="font-medium">{producto.stock_minimo.toLocaleString()} unid.</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Valor Unitario:</span>
                                      <span className="font-medium">${producto.valor_unitario.toFixed(2)}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Valor Total:</span>
                                      <span className="font-medium">${(producto.stock_total * producto.valor_unitario).toLocaleString()}</span>
                                    </div>
                                    <div className="flex justify-between">
                                      <span>Estado:</span>
                                      {getStatusBadge(producto.status)}
                                    </div>
                                  </div>
                                </div>
                              </div>
                              
                              {/* Distribución por bodegas */}
                              <div>
                                <h4 className="font-medium mb-3 flex items-center gap-2">
                                  <Warehouse className="h-4 w-4" />
                                  Distribución por Bodegas ({producto.bodegas.length})
                                </h4>
                                
                                {producto.bodegas.length === 0 ? (
                                  <div className="text-center py-8 border border-dashed rounded-lg">
                                    <Package className="mx-auto h-8 w-8 text-muted-foreground mb-2" />
                                    <p className="text-muted-foreground">No hay stock en ninguna bodega</p>
                                    <p className="text-sm text-muted-foreground">El producto está agotado</p>
                                  </div>
                                ) : (
                                  <div className="space-y-3">
                                    {producto.bodegas.map((bodega) => (
                                      <div key={bodega.id} className="border rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-2">
                                          <h5 className="font-medium">{bodega.nombre}</h5>
                                          <Badge variant="outline">
                                            {bodega.cantidad_disponible.toLocaleString()} unid.
                                          </Badge>
                                        </div>
                                        
                                        <div className="grid grid-cols-2 gap-4 text-sm text-muted-foreground">
                                          <div className="flex items-center gap-2">
                                            <MapPin className="h-4 w-4" />
                                            <span>Pasillo:</span>
                                            <span className="font-medium">{bodega.pasillo}</span>
                                          </div>
                                          <div className="flex items-center gap-2">
                                            <Hash className="h-4 w-4" />
                                            <span>Estante:</span>
                                            <span className="font-medium">{bodega.estante}</span>
                                          </div>
                                        </div>
                                        
                                        <div className="mt-2">
                                          <div className="flex justify-between text-xs text-muted-foreground mb-1">
                                            <span>Porcentaje del total</span>
                                            <span>{Math.round((bodega.cantidad_disponible / producto.stock_total) * 100)}%</span>
                                          </div>
                                          <div className="w-full bg-muted rounded-full h-2">
                                            <div 
                                              className="bg-primary h-2 rounded-full transition-all"
                                              style={{ 
                                                width: `${(bodega.cantidad_disponible / producto.stock_total) * 100}%` 
                                              }}
                                            />
                                          </div>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                              
                              <div className="pt-4 border-t text-xs text-muted-foreground">
                                Última actualización: {new Date(producto.fecha_ultima_actualizacion).toLocaleDateString('es-ES')} a las {new Date(producto.fecha_ultima_actualizacion).toLocaleTimeString('es-ES')}
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>
                      </div>
                    </div>
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