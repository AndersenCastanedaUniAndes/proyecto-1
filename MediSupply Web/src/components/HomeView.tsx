import { useState } from "react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "./ui/sidebar";
import {
  Users,
  Package,
  UserCheck,
  ClipboardList,
  BarChart3,
  Archive,
  Route,
  Pill,
  Bell,
  Search,
  LogOut,
  Trash2,
  CheckCircle,
  Info,
  AlertTriangle,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Badge } from "./ui/badge";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "./ui/popover";
import { Separator } from "./ui/separator";
import { ScrollArea } from "./ui/scroll-area";
import { toast } from "sonner@2.0.3";
import { ProveedoresView } from "./ProveedoresView";
import { ProductosView } from "./ProductosView";
import { VendedoresView } from "./VendedoresView";
import { PlanesVentaView } from "./PlanesVentaView";
import { InformesView } from "./InformesView";
import { InventarioView } from "./InventarioView";
import { RutasEntregaView } from "./RutasEntregaView";

interface HomeViewProps {
  onLogout: () => void;
}

interface Notificacion {
  id: number;
  mensaje: string;
  tipo: "success" | "info" | "warning";
  fecha: Date;
  leida: boolean;
}

type NavigationSection =
  | "proveedores"
  | "productos"
  | "vendedores"
  | "planes-venta"
  | "informes"
  | "inventario"
  | "rutas";

const navigationItems = [
  {
    id: "proveedores" as NavigationSection,
    label: "Proveedores",
    icon: Users,
  },
  {
    id: "productos" as NavigationSection,
    label: "Productos",
    icon: Package,
  },
  {
    id: "vendedores" as NavigationSection,
    label: "Vendedores",
    icon: UserCheck,
  },
  {
    id: "planes-venta" as NavigationSection,
    label: "Planes de Venta",
    icon: ClipboardList,
  },
  {
    id: "informes" as NavigationSection,
    label: "Informes",
    icon: BarChart3,
  },
  {
    id: "inventario" as NavigationSection,
    label: "Inventario",
    icon: Archive,
  },
  {
    id: "rutas" as NavigationSection,
    label: "Programación de Rutas",
    icon: Route,
  },
];

export function HomeView({ onLogout }: HomeViewProps) {
  const [activeSection, setActiveSection] =
    useState<NavigationSection>("proveedores");
  const [notificaciones, setNotificaciones] = useState<
    Notificacion[]
  >([
    {
      id: 1,
      mensaje: "Sistema MediSupply iniciado correctamente",
      tipo: "success",
      fecha: new Date(Date.now() - 5 * 60000), // 5 minutos atrás
      leida: false,
    },
    {
      id: 2,
      mensaje:
        "Bienvenido al sistema de distribución farmacéutica",
      tipo: "info",
      fecha: new Date(Date.now() - 2 * 60000), // 2 minutos atrás
      leida: false,
    },
  ]);
  const [notificacionesAbiertas, setNotificacionesAbiertas] =
    useState(false);

  const agregarNotificacion = (
    mensaje: string,
    tipo: "success" | "info" | "warning" = "success",
  ) => {
    const nuevaNotificacion: Notificacion = {
      id: Date.now(),
      mensaje,
      tipo,
      fecha: new Date(),
      leida: false,
    };
    setNotificaciones((prev) => [nuevaNotificacion, ...prev]);

    // Mostrar toast según el tipo
    if (tipo === "success") {
      toast.success(mensaje);
    } else if (tipo === "warning") {
      toast.warning?.(mensaje) || toast(mensaje);
    } else {
      toast.info?.(mensaje) || toast(mensaje);
    }
  };

  const marcarTodasComoLeidas = () => {
    setNotificaciones((prev) =>
      prev.map((n) => ({ ...n, leida: true })),
    );
  };

  const limpiarNotificaciones = () => {
    setNotificaciones([]);
    setNotificacionesAbiertas(false);
  };

  const notificacionesNoLeidas = notificaciones.filter(
    (n) => !n.leida,
  ).length;

  const handleLogout = () => {
    toast.success("Sesión cerrada correctamente");
    onLogout();
  };

  const handleNotificacionesChange = (open: boolean) => {
    setNotificacionesAbiertas(open);
    if (open) {
      // Marcar como leídas cuando se abre el popover
      setTimeout(() => marcarTodasComoLeidas(), 500);
    }
  };

  const renderMainContent = () => {
    switch (activeSection) {
      case "proveedores":
        return (
          <ProveedoresView onSuccess={agregarNotificacion} />
        );

      case "productos":
        return (
          <ProductosView onSuccess={agregarNotificacion} />
        );

      case "vendedores":
        return (
          <VendedoresView onSuccess={agregarNotificacion} />
        );

      case "planes-venta":
        return (
          <PlanesVentaView onSuccess={agregarNotificacion} />
        );

      case "informes":
        return <InformesView />;

      case "inventario":
        return <InventarioView />;

      case "rutas":
        return (
          <RutasEntregaView onSuccess={agregarNotificacion} />
        );

      default:
        return (
          <div className="space-y-6">
            <div>
              <h1>
                {
                  navigationItems.find(
                    (item) => item.id === activeSection,
                  )?.label
                }
              </h1>
              <p className="text-muted-foreground">
                Esta sección está en desarrollo. Pronto estará
                disponible.
              </p>
            </div>
            <Card>
              <CardContent className="pt-6">
                <div className="text-center">
                  <Package className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p>Funcionalidad en construcción</p>
                </div>
              </CardContent>
            </Card>
          </div>
        );
    }
  };

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        {/* Sidebar */}
        <Sidebar>
          <SidebarHeader className="border-b p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <Pill className="h-5 w-5 text-primary-foreground" />
              </div>
              <div>
                <h2 className="font-semibold">MediSupply</h2>
                <p className="text-xs text-muted-foreground">
                  Sistema de Distribución
                </p>
              </div>
            </div>
          </SidebarHeader>

          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  {navigationItems.map((item) => (
                    <SidebarMenuItem key={item.id}>
                      <SidebarMenuButton
                        isActive={activeSection === item.id}
                        onClick={() =>
                          setActiveSection(item.id)
                        }
                      >
                        <item.icon className="h-4 w-4" />
                        <span>{item.label}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </Sidebar>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {/* Top Header */}
          <header className="border-b bg-background px-6 pt-4 pb-5 relative z-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <SidebarTrigger />
                {/* <div className="relative max-w-md">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Buscar en MediSupply..."
                    className="pl-10 w-80"
                  />
                </div> */}
              </div>

              <div className="flex items-center gap-3">
                <Popover
                  open={notificacionesAbiertas}
                  onOpenChange={handleNotificacionesChange}
                >
                  <PopoverTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="relative"
                    >
                      <Bell className="h-4 w-4" />
                      {notificacionesNoLeidas > 0 && (
                        <Badge
                          variant="destructive"
                          className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
                        >
                          {notificacionesNoLeidas > 99
                            ? "99+"
                            : notificacionesNoLeidas}
                        </Badge>
                      )}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent
                    className="popover-notificaciones w-80 p-0 z-[60]"
                    side="bottom"
                    align="end"
                    sideOffset={0}
                    alignOffset={0}
                    avoidCollisions={false}
                    style={{ transform: 'none', position: 'fixed', top: '10px', right: '10px' }}
                  >
                    <div className="flex items-center justify-between px-3 py-2 border-b">
                      <h4 className="font-medium">
                        Notificaciones
                      </h4>
                      {notificaciones.length > 0 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={limpiarNotificaciones}
                          className="h-8 px-2"
                        >
                          <Trash2 className="h-3 w-3 mr-1" />
                          Limpiar
                        </Button>
                      )}
                    </div>

                    <ScrollArea className="h-64">
                      {notificaciones.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-8 text-center">
                          <Bell className="h-8 w-8 text-muted-foreground mb-2" />
                          <p className="text-sm text-muted-foreground">
                            No hay notificaciones
                          </p>
                        </div>
                      ) : (
                        <div className="space-y-1">
                          {notificaciones.map(
                            (notificacion) => (
                              <div
                                key={notificacion.id}
                                className={`p-3 hover:bg-muted/50 transition-colors border-l-2 ${
                                  notificacion.tipo ===
                                  "success"
                                    ? "border-l-green-500"
                                    : notificacion.tipo ===
                                        "warning"
                                      ? "border-l-yellow-500"
                                      : "border-l-blue-500"
                                } ${!notificacion.leida ? "bg-muted/20" : ""}`}
                              >
                                <div className="flex items-start gap-2">
                                  {notificacion.tipo ===
                                  "success" ? (
                                    <CheckCircle className="h-4 w-4 mt-0.5 flex-shrink-0 text-green-500" />
                                  ) : notificacion.tipo ===
                                    "warning" ? (
                                    <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0 text-yellow-500" />
                                  ) : (
                                    <Info className="h-4 w-4 mt-0.5 flex-shrink-0 text-blue-500" />
                                  )}
                                  <div className="flex-1 min-w-0">
                                    <p className="text-sm text-foreground break-words">
                                      {notificacion.mensaje}
                                    </p>
                                    <p className="text-xs text-muted-foreground mt-1">
                                      {notificacion.fecha.toLocaleTimeString(
                                        "es-ES",
                                        {
                                          hour: "2-digit",
                                          minute: "2-digit",
                                        },
                                      )}{" "}
                                      -{" "}
                                      {notificacion.fecha.toLocaleDateString(
                                        "es-ES",
                                        {
                                          day: "2-digit",
                                          month: "2-digit",
                                        },
                                      )}
                                    </p>
                                  </div>
                                  {!notificacion.leida && (
                                    <div className="w-2 h-2 bg-primary rounded-full flex-shrink-0 mt-1" />
                                  )}
                                </div>
                              </div>
                            ),
                          )}
                        </div>
                      )}
                    </ScrollArea>
                  </PopoverContent>
                </Popover>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="flex items-center gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Cerrar Sesión</span>
                </Button>
              </div>
            </div>
          </header>

          {/* Main Content Area */}
          <main className="flex-1 p-6 bg-muted/10">
            {renderMainContent()}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}