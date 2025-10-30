import { useState, useEffect } from "react";
import config from "../config/config";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import {
  Search,
  Calendar,
  TrendingUp,
  User,
  FileText,
  Download
} from "lucide-react";
import {
  ResponsiveContainer,
  CartesianGrid,
  Tooltip,
  XAxis,
  YAxis,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from "recharts";

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
  vendedor_id: number;
  producto: string;
  cantidad: number;
  valor_unitario: number;
  valor_total: number;
  cliente: string;
  comision: number;
}

export function InformesView() {
  const [vendedoresDisponibles, setVendedoresDisponibles] = useState<Vendedor[]>([]);
  const [isLoadingVendedores, setIsLoadingVendedores] = useState(false);

  const [filtros, setFiltros] = useState({ vendedorId: "", fechaInicial: "", fechaFinal: "" });
  const [ventasFiltradas, setVentasFiltradas] = useState<Venta[]>([]);
  const [consultaRealizada, setConsultaRealizada] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // 🔹 Cargar vendedores al iniciar
  useEffect(() => {
    const fetchVendedores = async () => {
      setIsLoadingVendedores(true);
      try {
        const token = localStorage.getItem("access_token");
        const response = await fetch(`${config.API_BASE_LOGIN_URL}/vendedores?skip=0&limit=100`, {
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {})
          }
        });

        if (!response.ok) throw new Error("Error al cargar vendedores");
        const data = await response.json();

        const vendedoresMapeados = data.map((v: any) => ({
          id: v.usuario_id,
          nombre: v.nombre_usuario,
          correo: v.email,
          activo: v.estado
        }));

        setVendedoresDisponibles(vendedoresMapeados);
      } catch (error) {
        console.error("Error cargando vendedores:", error);
      } finally {
        setIsLoadingVendedores(false);
      }
    };

    fetchVendedores();
  }, []);

  // 🔹 Consultar ventas desde el backend
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

    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`${config.API_BASE_VENTAS_URL}/ventas/?skip=0&limit=500`, {
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        }
      });

      if (!response.ok) throw new Error("Error al cargar ventas");
      const data = await response.json();

      // 🔹 Filtrar por vendedor y rango de fechas
      const ventasFiltradasBackend = data.filter((venta: any) => {
        const fechaVenta = new Date(venta.fecha);
        const fechaInicio = new Date(filtros.fechaInicial);
        const fechaFin = new Date(filtros.fechaFinal);
        return (
          venta.vendedor_id === parseInt(filtros.vendedorId) &&
          fechaVenta >= fechaInicio &&
          fechaVenta <= fechaFin
        );
      });

      setVentasFiltradas(ventasFiltradasBackend);
      setConsultaRealizada(true);
    } catch (error) {
      console.error("Error cargando ventas:", error);
      alert("Error al cargar ventas. Intenta nuevamente.");
    } finally {
      setIsLoading(false);
    }
  };

  const limpiarConsulta = () => {
    setFiltros({ vendedorId: "", fechaInicial: "", fechaFinal: "" });
    setVentasFiltradas([]);
    setConsultaRealizada(false);
  };

  // 📊 Calcular estadísticas
  const estadisticas = {
    totalVentas: ventasFiltradas.length,
    valorTotalVendido: ventasFiltradas.reduce((acc, v) => acc + v.valor_total, 0),
    comisionesTotales: ventasFiltradas.reduce((acc, v) => acc + v.comision, 0),
    promedioVenta: ventasFiltradas.length > 0
      ? ventasFiltradas.reduce((acc, v) => acc + v.valor_total, 0) / ventasFiltradas.length
      : 0,
    clientesUnicos: new Set(ventasFiltradas.map(v => v.cliente)).size,
    productosVendidos: ventasFiltradas.reduce((acc, v) => acc + v.cantidad, 0)
  };

  // 📈 Datos para gráficos
  const ventasPorMes = ventasFiltradas.reduce((acc: any[], venta) => {
    const mes = new Date(venta.fecha).toLocaleDateString("es-ES", { month: "short", year: "numeric" });
    const existente = acc.find(item => item.mes === mes);
    if (existente) {
      existente.ventas += venta.valor_total;
    } else {
      acc.push({ mes, ventas: venta.valor_total });
    }
    return acc;
  }, []);

  const productosMasVendidos = ventasFiltradas.reduce((acc: any[], venta) => {
    const existente = acc.find(item => item.producto === venta.producto);
    if (existente) {
      existente.cantidad += venta.cantidad;
      existente.valor += venta.valor_total;
    } else {
      acc.push({ producto: venta.producto, cantidad: venta.cantidad, valor: venta.valor_total });
    }
    return acc;
  }, []).sort((a, b) => b.valor - a.valor).slice(0, 5);

  const colores = ["#8884d8", "#82ca9d", "#ffc658", "#ff7c7c", "#8dd1e1"];

  // 💾 Exportar CSV
  const exportarCSV = () => {
    if (ventasFiltradas.length === 0) return;
    const encabezados = ["Fecha", "Vendedor", "Producto", "Cantidad", "Valor Unitario", "Valor Total", "Cliente", "Comisión"];
    const filas = ventasFiltradas.map(v =>
      [v.fecha, v.vendedor, v.producto, v.cantidad, v.valor_unitario, v.valor_total, v.cliente, v.comision]
    );
    const csvContent = [encabezados, ...filas].map(e => e.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "informe_ventas.csv";
    link.click();
  };

  return (
    <div className="space-y-8">
      <div>
        <h1>Informes de Ventas</h1>
        <p className="text-muted-foreground">
          Consulta y analiza el desempeño de ventas por vendedor y período
        </p>
      </div>

      {/* FILTROS */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" /> Filtros de Consulta
          </CardTitle>
          <CardDescription>Selecciona los criterios para generar el informe</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
            <div className="space-y-2">
              <Label>Vendedor</Label>
              <Select
                value={filtros.vendedorId}
                onValueChange={(value) => setFiltros({ ...filtros, vendedorId: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona un vendedor" />
                </SelectTrigger>
                <SelectContent>
                  {isLoadingVendedores ? (
                    <SelectItem value="loading" disabled>Cargando...</SelectItem>
                  ) : vendedoresDisponibles.length > 0 ? (
                    vendedoresDisponibles.map(v => (
                      <SelectItem key={v.id} value={v.id.toString()}>
                        {v.nombre} {!v.activo && <Badge variant="secondary">Inactivo</Badge>}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="empty" disabled>No hay vendedores</SelectItem>
                  )}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Fecha Inicial</Label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input type="date" value={filtros.fechaInicial} onChange={(e) => setFiltros({ ...filtros, fechaInicial: e.target.value })} className="pl-10" />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Fecha Final</Label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input type="date" value={filtros.fechaFinal} onChange={(e) => setFiltros({ ...filtros, fechaFinal: e.target.value })} className="pl-10" />
              </div>
            </div>

            <div className="flex gap-2">
              <Button onClick={handleConsultar} disabled={isLoading}>{isLoading ? "Consultando..." : "Consultar"}</Button>
              <Button variant="outline" onClick={limpiarConsulta}>Limpiar</Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* RESULTADOS */}
      {consultaRealizada && ventasFiltradas.length > 0 && (
        <>
          {/* Estadísticas */}
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <Card><CardHeader><CardTitle>Total Ventas</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{estadisticas.totalVentas}</div></CardContent></Card>
            <Card><CardHeader><CardTitle>Valor Total</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">${estadisticas.valorTotalVendido.toFixed(2)}</div></CardContent></Card>
            <Card><CardHeader><CardTitle>Comisiones</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold text-green-600">${estadisticas.comisionesTotales.toFixed(2)}</div></CardContent></Card>
            <Card><CardHeader><CardTitle>Promedio</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">${estadisticas.promedioVenta.toFixed(2)}</div></CardContent></Card>
            <Card><CardHeader><CardTitle>Clientes</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{estadisticas.clientesUnicos}</div></CardContent></Card>
            <Card><CardHeader><CardTitle>Productos</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{estadisticas.productosVendidos}</div></CardContent></Card>
          </div>

          {/* Gráficos */}
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
                    <Tooltip formatter={(value) => [`$${Number(value).toFixed(2)}`, "Ventas"]} />
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
                      dataKey="valor"
                      nameKey="producto"
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      label={(entry) => `$${entry.valor.toFixed(2)}`}
                    >
                      {productosMasVendidos.map((_, i) => (
                        <Cell key={i} fill={colores[i % colores.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`$${Number(value).toFixed(2)}`, "Valor"]} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 space-y-1">
                  {productosMasVendidos.map((p, i) => (
                    <div key={p.producto} className="flex items-center gap-2 text-sm">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: colores[i] }} />
                      <span>{p.producto}</span>
                      <span className="ml-auto">{p.cantidad} unid.</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Detalle de Ventas */}
          <Card>
            <CardHeader className="flex justify-between items-center">
              <div>
                <CardTitle>Detalle de Ventas</CardTitle>
                <CardDescription>{ventasFiltradas.length} venta(s) encontradas</CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={exportarCSV}>
                <Download className="h-4 w-4 mr-2" /> Exportar CSV
              </Button>
            </CardHeader>
            <CardContent>
              {ventasFiltradas.map((venta) => (
                <div key={venta.id} className="border rounded-lg p-4 mb-3 hover:bg-muted/50 transition">
                  <div className="flex justify-between">
                    <div>
                      <h4 className="font-medium">{venta.producto}</h4>
                      <p className="text-sm text-muted-foreground">
                        Cliente: {venta.cliente} — Fecha: {new Date(venta.fecha).toLocaleDateString("es-ES")}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm">Valor Unit.: ${venta.valor_unitario.toFixed(2)}</p>
                      <p className="font-semibold">Total: ${venta.valor_total.toFixed(2)}</p>
                      <p className="text-green-600 text-sm font-medium">
                        +${venta.comision.toFixed(2)} comisión
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </>
      )}

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
