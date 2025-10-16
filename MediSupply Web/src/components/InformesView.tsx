import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { 
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from "recharts";
import { 
  Search,
  Calendar,
  TrendingUp,
  DollarSign,
  Package,
  User,
  FileText,
  Download
} from "lucide-react";

interface Vendedor {
  id: number;
  nombre: string;
  correo: string;
  activo: boolean;
}

interface Venta {
  id: number;
  fecha: string;
  vendedor: string;
  vendedorId: number;
  producto: string;
  cantidad: number;
  valorUnitario: number;
  valorTotal: number;
  cliente: string;
  comision: number;
}

export function InformesView() {
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

  // Datos de ejemplo de ventas
  const ventasData: Venta[] = [
    {
      id: 1,
      fecha: "2024-01-15",
      vendedor: "Ana García Rodríguez",
      vendedorId: 1,
      producto: "Paracetamol 500mg",
      cantidad: 100,
      valorUnitario: 0.25,
      valorTotal: 25.00,
      cliente: "Farmacia Central",
      comision: 2.50
    },
    {
      id: 2,
      fecha: "2024-01-20",
      vendedor: "Ana García Rodríguez", 
      vendedorId: 1,
      producto: "Ibuprofeno 600mg",
      cantidad: 50,
      valorUnitario: 0.35,
      valorTotal: 17.50,
      cliente: "Droguería La Salud",
      comision: 1.75
    },
    {
      id: 3,
      fecha: "2024-02-01",
      vendedor: "Carlos Mendoza Silva",
      vendedorId: 2,
      producto: "Vacuna COVID-19",
      cantidad: 10,
      valorUnitario: 15.50,
      valorTotal: 155.00,
      cliente: "Hospital Nacional",
      comision: 15.50
    },
    {
      id: 4,
      fecha: "2024-02-10",
      vendedor: "Ana García Rodríguez",
      vendedorId: 1,
      producto: "Insulina Rápida",
      cantidad: 5,
      valorUnitario: 25.00,
      valorTotal: 125.00,
      cliente: "Clínica San Juan",
      comision: 12.50
    },
    {
      id: 5,
      fecha: "2024-02-15",
      vendedor: "Roberto Jiménez Luna",
      vendedorId: 4,
      producto: "Paracetamol 500mg",
      cantidad: 200,
      valorUnitario: 0.25,
      valorTotal: 50.00,
      cliente: "Red de Farmacias Unidos",
      comision: 5.00
    },
    {
      id: 6,
      fecha: "2024-03-01",
      vendedor: "Carlos Mendoza Silva",
      vendedorId: 2,
      producto: "Ibuprofeno 600mg",
      cantidad: 75,
      valorUnitario: 0.35,
      valorTotal: 26.25,
      cliente: "Farmacia del Pueblo",
      comision: 2.63
    }
  ];

  const [filtros, setFiltros] = useState({
    vendedorId: "",
    fechaInicial: "",
    fechaFinal: ""
  });

  const [ventasFiltradas, setVentasFiltradas] = useState<Venta[]>([]);
  const [consultaRealizada, setConsultaRealizada] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleConsultar = async () => {
    if (!filtros.vendedorId || !filtros.fechaInicial || !filtros.fechaFinal) {
      alert("Por favor completa todos los campos de filtro");
      return;
    }

    if (new Date(filtros.fechaInicial) > new Date(filtros.fechaFinal)) {
      alert("La fecha inicial no puede ser mayor a la fecha final");
      return;
    }

    setIsLoading(true);

    // Simular consulta
    setTimeout(() => {
      const ventasDelVendedor = ventasData.filter(venta => {
        const fechaVenta = new Date(venta.fecha);
        const fechaInicio = new Date(filtros.fechaInicial);
        const fechaFin = new Date(filtros.fechaFinal);
        
        return venta.vendedorId === parseInt(filtros.vendedorId) &&
               fechaVenta >= fechaInicio &&
               fechaVenta <= fechaFin;
      });

      setVentasFiltradas(ventasDelVendedor);
      setConsultaRealizada(true);
      setIsLoading(false);
    }, 1000);
  };

  const limpiarConsulta = () => {
    setFiltros({
      vendedorId: "",
      fechaInicial: "",
      fechaFinal: ""
    });
    setVentasFiltradas([]);
    setConsultaRealizada(false);
  };

  // Calcular estadísticas
  const estadisticas = {
    totalVentas: ventasFiltradas.length,
    valorTotalVendido: ventasFiltradas.reduce((acc, venta) => acc + venta.valorTotal, 0),
    comisionesTotales: ventasFiltradas.reduce((acc, venta) => acc + venta.comision, 0),
    promedioVenta: ventasFiltradas.length > 0 ? ventasFiltradas.reduce((acc, venta) => acc + venta.valorTotal, 0) / ventasFiltradas.length : 0,
    clientesUnicos: new Set(ventasFiltradas.map(v => v.cliente)).size,
    productosVendidos: ventasFiltradas.reduce((acc, venta) => acc + venta.cantidad, 0)
  };

  // Datos para gráficos
  const ventasPorMes = ventasFiltradas.reduce((acc, venta) => {
    const mes = new Date(venta.fecha).toLocaleDateString('es-ES', { month: 'short', year: 'numeric' });
    const existing = acc.find(item => item.mes === mes);
    if (existing) {
      existing.ventas += venta.valorTotal;
      existing.cantidad += 1;
    } else {
      acc.push({ mes, ventas: venta.valorTotal, cantidad: 1 });
    }
    return acc;
  }, [] as { mes: string; ventas: number; cantidad: number }[]);

  const productosMasVendidos = ventasFiltradas.reduce((acc, venta) => {
    const existing = acc.find(item => item.producto === venta.producto);
    if (existing) {
      existing.cantidad += venta.cantidad;
      existing.valor += venta.valorTotal;
    } else {
      acc.push({ producto: venta.producto, cantidad: venta.cantidad, valor: venta.valorTotal });
    }
    return acc;
  }, [] as { producto: string; cantidad: number; valor: number }[])
  .sort((a, b) => b.valor - a.valor)
  .slice(0, 5);

  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1'];

  const exportarDatos = () => {
    if (ventasFiltradas.length === 0) return;

    const vendedorSeleccionado = vendedoresDisponibles.find(v => v.id === parseInt(filtros.vendedorId));
    const csvContent = [
      // Headers
      "ID,Fecha,Vendedor,Producto,Cantidad,Valor Unitario,Valor Total,Cliente,Comisión",
      // Data
      ...ventasFiltradas.map(venta => 
        `${venta.id},${venta.fecha},${venta.vendedor},${venta.producto},${venta.cantidad},${venta.valorUnitario},${venta.valorTotal},${venta.cliente},${venta.comision}`
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", `informe_ventas_${vendedorSeleccionado?.nombre}_${filtros.fechaInicial}_${filtros.fechaFinal}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1>Informes de Ventas</h1>
        <p className="text-muted-foreground">
          Consulta y analiza el desempeño de ventas por vendedor y período
        </p>
      </div>

      {/* Filtros de consulta */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Filtros de Consulta
          </CardTitle>
          <CardDescription>
            Selecciona los criterios para generar el informe de ventas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div className="space-y-2">
              <Label htmlFor="vendedor">Vendedor</Label>
              <Select value={filtros.vendedorId} onValueChange={(value) => 
                setFiltros({...filtros, vendedorId: value})
              }>
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un vendedor" />
                </SelectTrigger>
                <SelectContent>
                  {vendedoresDisponibles.map((vendedor) => (
                    <SelectItem key={vendedor.id} value={vendedor.id.toString()}>
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4" />
                        {vendedor.nombre}
                        {!vendedor.activo && <Badge variant="secondary" className="ml-2">Inactivo</Badge>}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="fechaInicial">Fecha Inicial</Label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="fechaInicial"
                  type="date"
                  value={filtros.fechaInicial}
                  onChange={(e) => setFiltros({...filtros, fechaInicial: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="fechaFinal">Fecha Final</Label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="fechaFinal"
                  type="date"
                  value={filtros.fechaFinal}
                  onChange={(e) => setFiltros({...filtros, fechaFinal: e.target.value})}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <Button 
                onClick={handleConsultar}
                disabled={isLoading}
                className="flex-1"
              >
                {isLoading ? "Consultando..." : "Consultar"}
              </Button>
              <Button 
                variant="outline" 
                onClick={limpiarConsulta}
                disabled={isLoading}
              >
                Limpiar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Resultados de la consulta */}
      {consultaRealizada && (
        <>
          {/* Estadísticas generales */}
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Total Ventas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{estadisticas.totalVentas}</div>
                <p className="text-xs text-muted-foreground">transacciones</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Valor Total</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${estadisticas.valorTotalVendido.toFixed(2)}</div>
                <p className="text-xs text-muted-foreground">vendido</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Comisiones</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">${estadisticas.comisionesTotales.toFixed(2)}</div>
                <p className="text-xs text-muted-foreground">ganadas</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Promedio/Venta</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${estadisticas.promedioVenta.toFixed(2)}</div>
                <p className="text-xs text-muted-foreground">por transacción</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Clientes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{estadisticas.clientesUnicos}</div>
                <p className="text-xs text-muted-foreground">únicos</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Productos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{estadisticas.productosVendidos}</div>
                <p className="text-xs text-muted-foreground">unidades</p>
              </CardContent>
            </Card>
          </div>

          {/* Gráficos */}
          {ventasFiltradas.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Ventas por Período</CardTitle>
                  <CardDescription>Evolución de las ventas en el tiempo</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={ventasPorMes}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="mes" />
                      <YAxis />
                      <Tooltip formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Ventas']} />
                      <Line type="monotone" dataKey="ventas" stroke="#8884d8" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Productos Más Vendidos</CardTitle>
                  <CardDescription>Top 5 por valor de ventas</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={productosMasVendidos}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={120}
                        paddingAngle={5}
                        dataKey="valor"
                        label={(entry) => `$${entry.valor.toFixed(2)}`}
                      >
                        {productosMasVendidos.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(value) => [`$${Number(value).toFixed(2)}`, 'Valor']} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="mt-4 space-y-1">
                    {productosMasVendidos.map((producto, index) => (
                      <div key={producto.producto} className="flex items-center gap-2 text-sm">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: colors[index] }}
                        />
                        <span>{producto.producto}</span>
                        <span className="ml-auto">{producto.cantidad} unid.</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Lista detallada de ventas */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Detalle de Ventas</CardTitle>
                  <CardDescription>
                    {ventasFiltradas.length} venta{ventasFiltradas.length !== 1 ? 's' : ''} encontrada{ventasFiltradas.length !== 1 ? 's' : ''}
                  </CardDescription>
                </div>
                {ventasFiltradas.length > 0 && (
                  <Button onClick={exportarDatos} variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Exportar CSV
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {ventasFiltradas.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">
                    No se encontraron ventas para los criterios seleccionados
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Intenta con un rango de fechas más amplio o selecciona otro vendedor
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {ventasFiltradas.map((venta) => (
                    <div key={venta.id} className="border rounded-lg p-4 hover:bg-muted/20 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1 flex-1">
                          <div className="flex items-center gap-3 flex-wrap">
                            <h3 className="font-medium">{venta.producto}</h3>
                            <Badge variant="outline">ID: {venta.id}</Badge>
                            <Badge variant="secondary">{venta.cantidad} unid.</Badge>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-muted-foreground">
                            <div>
                              <span className="font-medium">Cliente:</span> {venta.cliente}
                            </div>
                            <div>
                              <span className="font-medium">Fecha:</span> {new Date(venta.fecha).toLocaleDateString('es-ES')}
                            </div>
                            <div>
                              <span className="font-medium">Valor Unit.:</span> ${venta.valorUnitario.toFixed(2)}
                            </div>
                            <div>
                              <span className="font-medium">Total:</span> ${venta.valorTotal.toFixed(2)}
                            </div>
                          </div>
                        </div>
                        
                        <div className="text-right ml-4">
                          <p className="font-medium text-green-600">
                            +${venta.comision.toFixed(2)}
                          </p>
                          <p className="text-xs text-muted-foreground">comisión</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Mensaje inicial */}
      {!consultaRealizada && (
        <Card>
          <CardContent className="text-center py-12">
            <TrendingUp className="mx-auto h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="font-medium mb-2">Genera tu Informe de Ventas</h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              Selecciona un vendedor y un rango de fechas para consultar las ventas realizadas y generar estadísticas detalladas.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}