import 'package:flutter/material.dart';
import 'package:medisupply_movil/screens/screens.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:provider/provider.dart';
import 'package:medisupply_movil/utils/utils.dart';
import 'package:medisupply_movil/data/data.dart';
import '../state/app_state.dart';

class ClientHomeScreen extends StatefulWidget {
  const ClientHomeScreen({super.key});

  @override
  State<ClientHomeScreen> createState() => _ClientHomeScreenState();
}

enum _ClientView { home, pedidos, entregas }

class _ClientHomeScreenState extends State<ClientHomeScreen> {
  _ClientView _current = _ClientView.home;
  bool _showUserMenu = false;

  void _goHome() => setState(() => _current = _ClientView.home);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: _buildBody(context),
            ),
          ),
          if (_showUserMenu) UserMenuOverlay(onClose: () => setState(() => _showUserMenu = false)),
        ],
      ),
    );
  }

  Widget _buildBody(BuildContext context) {
    switch (_current) {
      case _ClientView.pedidos:
        return ClientOrdersView(onBack: _goHome);
      case _ClientView.entregas:
        return ClientDeliveriesView(onBack: _goHome);
      case _ClientView.home:
        return _ClientHome(onOpenMenu: () => setState(() => _showUserMenu = true), onTapCard: (v) => setState(() => _current = v));
    }
  }
}

class _ClientHome extends StatefulWidget {
  final VoidCallback onOpenMenu;
  final void Function(_ClientView) onTapCard;
  const _ClientHome({required this.onOpenMenu, required this.onTapCard});

  @override
  State<_ClientHome> createState() => _ClientHomeState();
}

class _ClientHomeState extends State<_ClientHome> {
  bool _isLoadingOrders = false;
  late Future<List<dynamic>> _futureOrders;

  String _getMonthOrdersCost() {
    return '\$285,400';
  }

  String _getMonthOrdersCount() {
    return '15';
  }

  String _getPendingOrders() {
    return '3';
  }

  String _getUpcomingDeliveries() {
    return '2';
  }

  @override
  void initState() {
    super.initState();

    var state = context.read<AppState>();
    _futureOrders = _fetchClientOrders();
  }

  Future<List<Order>> _fetchClientOrders() async {
    setState(() => _isLoadingOrders = true);

    final state = context.read<AppState>();

    final response = getClientOrders(state.id, state.token);

    setState(() => _isLoadingOrders = false);

    return response;
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final pendingOrders = _getPendingOrders();

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          HomeCard(
            gradient: LinearGradient(colors: [AppStyles.green1, AppStyles.green2]),
            title: '¡Hola, ${state.userName}!',
            subtitle: 'Cliente MediSupply',
            onTap: widget.onOpenMenu,
            stat1Title: 'Total este mes',
            stat1Value: _getMonthOrdersCost(),
            stat2Title: 'Pedidos realizados',
            stat2Value: _getMonthOrdersCount(),
          ),
          const SizedBox(height: 16),

          QuickStats(
            stat1Color: AppStyles.blue1,
            stat1Title: 'Pedidos Pendientes',
            stat1Value: pendingOrders,
            stat2Color: AppStyles.green1,
            stat2Title: 'Entregas Próximas',
            stat2Value: _getUpcomingDeliveries(),
          ),
          const SizedBox(height: 16),

          const _RecentActivity(),
          const SizedBox(height: 16),

          LayoutBuilder(
            builder: (context, constraints) {
              const itemWidth = 190.0;
              final crossAxisCount = (constraints.maxWidth / itemWidth).floor().clamp(1, 4);

              return GridView.count(
                shrinkWrap: true,
                crossAxisCount: crossAxisCount,
                childAspectRatio: 1,
                mainAxisSpacing: 12,
                crossAxisSpacing: 12,
                children: [
                  MenuCard(
                    color: AppStyles.menuCardBlue,
                    icon: AppIcons.shoppingCart,
                    title: 'Pedidos',
                    description: 'Crear y gestionar tus pedidos',
                    badge: '$pendingOrders pendientes',
                    onTap: () => widget.onTapCard(_ClientView.pedidos),
                  ),
                  MenuCard(
                    color: AppStyles.menuCardGreen,
                    icon: AppIcons.shipping,
                    title: 'Entregas',
                    description: 'Consultar entregas programadas',
                    badge: '2 próximas',
                    onTap: () => widget.onTapCard(_ClientView.entregas),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}



class _RecentActivity extends StatelessWidget {
  const _RecentActivity();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: AppStyles.decoration,
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Actividad Reciente', style: Theme.of(context).textTheme.bodyMedium),
            const SizedBox(height: 38),

            _activityRow(
              context,
              bg: Colors.blue[100]!,
              icon: AppIcons.package,
              iconColor: Colors.blue[700]!,
              title: 'Pedido #1025',
              subtitle: 'Procesando - \$145,200',
              badgeText: 'Hoy',
              badgeColor: Colors.grey.shade200,
              badgeTextColor: Colors.black87,
            ),
            const SizedBox(height: 8),

            _activityRow(
              context,
              bg: Colors.green[100]!,
              icon: AppIcons.shipping,
              iconColor: Colors.green[700]!,
              title: 'Entrega #1022',
              subtitle: 'Completada - \$89,500',
              badgeText: 'Ayer',
              badgeColor: Colors.green,
              badgeTextColor: Colors.white,
            ),
            const SizedBox(height: 8),

            _activityRow(
              context,
              bg: Colors.orange[100]!,
              icon: Icons.schedule,
              iconColor: Colors.orange[700]!,
              title: 'Entrega Programada',
              subtitle: 'Mañana 10:00 AM',
              badgeText: 'Próxima',
              badgeColor: Colors.orange,
              badgeTextColor: Colors.white,
            ),
          ],
        ),
      ),
    );
  }

  Widget _activityRow(
    BuildContext context, {
    required Color bg,
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required String badgeText,
    required Color badgeColor,
    required Color badgeTextColor,
  }) {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.shade300),
        borderRadius: BorderRadius.circular(8),
      ),
      padding: const EdgeInsets.all(8),
      child: Row(
        children: [
          Container(
            height: 32,
            width: 32,
            decoration: BoxDecoration(color: bg, shape: BoxShape.circle),
            child: Icon(icon, color: iconColor, size: 18),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.grey)),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(color: badgeColor, borderRadius: BorderRadius.circular(12)),
            child: Text(badgeText, style: TextStyle(fontSize: 11, color: badgeTextColor)),
          ),
        ],
      ),
    );
  }
}


// =================== VENDEDOR - PEDIDOS VIEW ===================

// =================== CLIENTE - PEDIDOS VIEW ===================
class ClientOrdersView extends StatefulWidget {
  final VoidCallback onBack;
  const ClientOrdersView({super.key, required this.onBack});

  @override
  State<ClientOrdersView> createState() => _ClientOrdersViewState();
}

// =================== CLIENTE - ENTREGAS VIEW ===================
class ClientDeliveriesView extends StatefulWidget {
  final VoidCallback onBack;
  const ClientDeliveriesView({super.key, required this.onBack});

  @override
  State<ClientDeliveriesView> createState() => _ClientDeliveriesViewState();
}

class _ClientDeliveriesViewState extends State<ClientDeliveriesView> {
  // Cliente actual placeholder
  final String _clienteActual = 'Farmacia Central';

  // Filtros
  final _filtroFechaCtrl = TextEditingController(); // filtra por fecha del pedido
  final _filtroEstadoCtrl = TextEditingController(); // filtra por estado de entrega

  final List<_PedidoEntrega> _pedidos = [
    _PedidoEntrega(
      idPedido: 1025,
      cliente: 'Farmacia Central',
      fechaPedido: '2024-03-20',
      total: 145200,
      items: 6,
      estadoEntrega: 'en_ruta',
      entregas: const [
        _SlotEntrega(fecha: '2024-03-21', franja: '08:00 - 11:00', estado: 'programada'),
        _SlotEntrega(fecha: '2024-03-21', franja: '11:00 - 12:00', estado: 'en_ruta'),
      ],
    ),
    _PedidoEntrega(
      idPedido: 1024,
      cliente: 'Farmacia Central',
      fechaPedido: '2024-03-18',
      total: 89500,
      items: 3,
      estadoEntrega: 'entregada',
      entregas: const [
        _SlotEntrega(fecha: '2024-03-19', franja: '09:00 - 12:00', estado: 'entregada'),
      ],
    ),
    _PedidoEntrega(
      idPedido: 1023,
      cliente: 'Farmacia Central',
      fechaPedido: '2024-03-17',
      total: 210300,
      items: 9,
      estadoEntrega: 'programada',
      entregas: const [
        _SlotEntrega(fecha: '2024-03-23', franja: '14:00 - 17:00', estado: 'programada'),
      ],
    ),
    _PedidoEntrega(
      idPedido: 1022,
      cliente: 'Farmacia Central',
      fechaPedido: '2024-03-15',
      total: 120000,
      items: 4,
      estadoEntrega: 'reprogramada',
      entregas: const [
        _SlotEntrega(fecha: '2024-03-16', franja: '10:00 - 12:00', estado: 'cancelada'),
        _SlotEntrega(fecha: '2024-03-20', franja: '15:00 - 18:00', estado: 'programada'),
      ],
    ),
  ];

  List<_PedidoEntrega> get _filtrados {
    final fFecha = _filtroFechaCtrl.text.trim();
    final fEstado = _filtroEstadoCtrl.text.trim().toLowerCase();
    return _pedidos.where((p) {
      final okCliente = p.cliente == _clienteActual;
      final okFecha = fFecha.isEmpty || p.fechaPedido.contains(fFecha);
      final okEstado = fEstado.isEmpty || p.estadoEntrega.toLowerCase().contains(fEstado);
      return okCliente && okFecha && okEstado;
    }).toList();
  }

  @override
  void dispose() {
    _filtroFechaCtrl.dispose();
    _filtroEstadoCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final pedidos = _filtrados;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            IconButton(onPressed: widget.onBack, icon: const Icon(Icons.arrow_back)),
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Pedidos y Entregas', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
              Text('${pedidos.length} pedidos', style: const TextStyle(fontSize: 12, color: Colors.grey)),
            ])
          ],
        ),
        const SizedBox(height: 8),
        Row(children: [
          Expanded(
            child: TextField(
              controller: _filtroFechaCtrl,
              decoration: const InputDecoration(labelText: 'Filtrar por fecha de pedido (YYYY-MM-DD)', prefixIcon: Icon(Icons.calendar_today)),
              onChanged: (_) => setState(() {}),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: _filtroEstadoCtrl,
              decoration: const InputDecoration(labelText: 'Filtrar por estado de entrega', prefixIcon: Icon(Icons.search)),
              onChanged: (_) => setState(() {}),
            ),
          ),
        ]),
        const SizedBox(height: 12),
        Expanded(
          child: pedidos.isEmpty
              ? Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: const [
                        Icon(Icons.history, size: 48, color: Colors.grey),
                        SizedBox(height: 8),
                        Text('No se encontraron pedidos', style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  ),
                )
              : ListView.separated(
                  itemCount: pedidos.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, i) {
                    final p = pedidos[i];
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                  Text('Pedido #${p.idPedido}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                                  Text(p.cliente, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                ]),
                                _estadoEntregaBadge(p.estadoEntrega),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Row(children: [
                                  const Icon(Icons.calendar_today, size: 14, color: Colors.grey),
                                  const SizedBox(width: 4),
                                  Text(p.fechaPedido, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                ]),
                                Row(children: [
                                  const Icon(Icons.inventory_2_outlined, size: 14, color: Colors.grey),
                                  const SizedBox(width: 4),
                                  Text('${p.items} items', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                ]),
                                Row(children: [
                                  const Icon(Icons.attach_money, size: 14, color: Colors.grey),
                                  const SizedBox(width: 4),
                                  Text('\$${p.total}', style: const TextStyle(fontSize: 12, color: Colors.green)),
                                ]),
                              ],
                            ),
                            const SizedBox(height: 10),
                            Row(children: const [
                              Icon(Icons.local_shipping_outlined, size: 14),
                              SizedBox(width: 4),
                              Text('Entregas', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                            ]),
                            const SizedBox(height: 6),
                            Wrap(
                              spacing: 6,
                              runSpacing: 6,
                              children: p.entregas.map((s) {
                                final badgeColor = _slotColor(s.estado);
                                final label = '${s.fecha} • ${s.franja}';
                                return Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                  decoration: BoxDecoration(color: badgeColor.withOpacity(0.12), borderRadius: BorderRadius.circular(12), border: Border.all(color: badgeColor.withOpacity(0.35))),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(_slotIcon(s.estado), size: 12, color: badgeColor),
                                      const SizedBox(width: 4),
                                      Text(label, style: TextStyle(fontSize: 11, color: badgeColor)),
                                    ],
                                  ),
                                );
                              }).toList(),
                            )
                          ],
                        ),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }

  Color _slotColor(String estado) {
    switch (estado) {
      case 'programada':
        return Colors.blueGrey;
      case 'en_ruta':
        return Colors.blue;
      case 'entregada':
        return Colors.green;
      case 'cancelada':
        return Colors.red;
      default:
        return Colors.black54;
    }
  }

  IconData _slotIcon(String estado) {
    switch (estado) {
      case 'programada':
        return Icons.event_available_outlined;
      case 'en_ruta':
        return Icons.local_shipping_outlined;
      case 'entregada':
        return Icons.check_circle_outline;
      case 'cancelada':
        return Icons.cancel_outlined;
      default:
        return Icons.help_outline;
    }
  }

  Widget _estadoEntregaBadge(String estado) {
    // estados de entrega: programada | en_ruta | entregada | reprogramada
    late Color bg;
    Color fg = Colors.white;
    switch (estado) {
      case 'programada':
        bg = Colors.blueGrey; break;
      case 'en_ruta':
        bg = Colors.blue; break;
      case 'entregada':
        bg = Colors.green; break;
      case 'reprogramada':
        bg = Colors.orange; break;
      default:
        bg = Colors.black54; break;
    }
    final label = estado.replaceAll('_', ' ');
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(12)),
      child: Text(label[0].toUpperCase() + label.substring(1), style: TextStyle(fontSize: 11, color: fg)),
    );
  }
}

class _PedidoEntrega {
  final int idPedido;
  final String cliente;
  final String fechaPedido; // YYYY-MM-DD
  final int total;
  final int items;
  final String estadoEntrega; // programada | en_ruta | entregada | reprogramada
  final List<_SlotEntrega> entregas; // slots programados o realizados
  const _PedidoEntrega({
    required this.idPedido,
    required this.cliente,
    required this.fechaPedido,
    required this.total,
    required this.items,
    required this.estadoEntrega,
    required this.entregas,
  });
}

class _SlotEntrega {
  final String fecha; // YYYY-MM-DD
  final String franja; // HH:mm - HH:mm
  final String estado; // programada | en_ruta | entregada | cancelada
  const _SlotEntrega({required this.fecha, required this.franja, required this.estado});
}

class _ClientOrdersViewState extends State<ClientOrdersView>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController = TabController(length: 2, vsync: this);

  // Para cliente actual (placeholder): 'Farmacia Central'
  final String _clienteActual = 'Farmacia Central';

  // Nuevo pedido (para cliente actual)
  final _fechaCtrl = TextEditingController();
  bool _isLoading = false;
  final Map<int, int> _cantidades = {}; // productoId -> cantidad

  // Filtros historial
  final _filtroFechaCtrl = TextEditingController();

  final List<Product> _productos = [
    Product(id: 1, nombre: 'Paracetamol 500mg', precio: 250, stock: 1000, categoria: 'Analgésicos'),
    Product(id: 2, nombre: 'Ibuprofeno 600mg', precio: 350, stock: 800, categoria: 'Analgésicos'),
    Product(id: 3, nombre: 'Amoxicilina 875mg', precio: 450, stock: 600, categoria: 'Antibióticos'),
    Product(id: 4, nombre: 'Insulina Rápida', precio: 15000, stock: 200, categoria: 'Diabetes'),
    Product(id: 5, nombre: 'Vacuna COVID-19', precio: 25000, stock: 150, categoria: 'Vacunas'),
    Product(id: 6, nombre: 'Vitamina C', precio: 180, stock: 500, categoria: 'Vitaminas'),
    Product(id: 7, nombre: 'Multivitamínico', precio: 320, stock: 400, categoria: 'Vitaminas'),
    Product(id: 8, nombre: 'Glucómetro', precio: 45000, stock: 50, categoria: 'Diabetes'),
  ];

  final List<Order> _pedidos = [
    Order(
      id: 1,
      cliente: 'Farmacia Central',
      clienteId: 1,
      fecha: '2024-03-20',
      estado: 'Pendiente',
      items: [
        OrderItem(id: 1, nombre: 'Paracetamol 500mg', cantidad: 100, precio: 250),
        OrderItem(id: 2, nombre: 'Ibuprofeno 600mg', cantidad: 50, precio: 350),
      ],
      total: 42500,
      fechaCreacion: '2024-03-20',
    ),
    Order(
      id: 2,
      cliente: 'Farmacia Central',
      clienteId: 1,
      fecha: '2024-03-19',
      estado: 'Procesando',
      items: [
        OrderItem(id: 3, nombre: 'Amoxicilina 875mg', cantidad: 200, precio: 450),
        OrderItem(id: 4, nombre: 'Insulina Rápida', cantidad: 10, precio: 15000),
      ],
      total: 240000,
      fechaCreacion: '2024-03-19',
    ),
  ];

  List<Order> get _pedidosFiltrados {
    final fFecha = _filtroFechaCtrl.text.trim();
    return _pedidos.where((p) {
      final mismoCliente = p.cliente == _clienteActual;
      final fechaOk = fFecha.isEmpty || p.fecha.contains(fFecha);
      return mismoCliente && fechaOk;
    }).toList();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _fechaCtrl.dispose();
    _filtroFechaCtrl.dispose();
    super.dispose();
  }

  double _calcularTotal() {
    double total = 0;
    _cantidades.forEach((prodId, cant) {
      final prod = _productos.firstWhere((p) => p.id == prodId);
      total += prod.precio * cant;
    });
    return total;
  }

  void _setCantidad(int productoId, int cantidad) {
    setState(() {
      if (cantidad <= 0) {
        _cantidades.remove(productoId);
      } else {
        _cantidades[productoId] = cantidad;
      }
    });
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: now,
      firstDate: DateTime(now.year - 1),
      lastDate: DateTime(now.year + 2),
    );
    if (picked != null) {
      _fechaCtrl.text = picked.toIso8601String().substring(0, 10);
      setState(() {});
    }
  }

  Future<void> _submit() async {
    if (_fechaCtrl.text.isEmpty || _cantidades.isEmpty) {
      return;
    }
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 1));

    final items = _cantidades.entries.map((e) {
      final prod = _productos.firstWhere((p) => p.id == e.key);
      return OrderItem(id: prod.id, nombre: prod.nombre, cantidad: e.value, precio: prod.precio);
    }).toList();

    setState(() {
      _pedidos.add(
        Order(
          id: _pedidos.length + 1,
          cliente: _clienteActual,
          clienteId: 0,
          fecha: _fechaCtrl.text,
          estado: 'Pendiente',
          items: items,
          total: _calcularTotal(),
          fechaCreacion: DateTime.now().toIso8601String().substring(0, 10),
        ),
      );
      _fechaCtrl.clear();
      _cantidades.clear();
      _isLoading = false;
      _tabController.index = 1; // ir a historial
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          children: [
            IconButton(onPressed: widget.onBack, icon: const Icon(Icons.arrow_back)),
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Mis Pedidos', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
              Text('${_pedidosFiltrados.length} pedidos', style: const TextStyle(fontSize: 12, color: Colors.grey)),
            ])
          ],
        ),
        const SizedBox(height: 8),
        TabBar(
          controller: _tabController,
          indicatorColor: Theme.of(context).colorScheme.primary,
          tabs: const [
            Tab(icon: Icon(Icons.add), text: 'Nuevo'),
            Tab(icon: Icon(Icons.shopping_cart_outlined), text: 'Historial'),
          ],
        ),
        const SizedBox(height: 8),
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildNuevo(context),
              _buildHistorial(context),
            ],
          ),
        )
      ],
    );
  }

  Widget _buildNuevo(BuildContext context) {
    return SingleChildScrollView(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Crear Nuevo Pedido', style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: 12),

              Text('Productos', style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: 8),

              Container(
                constraints: const BoxConstraints(maxHeight: 300),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade300),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: ListView.separated(
                  shrinkWrap: true,
                  itemCount: _productos.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, i) {
                    final p = _productos[i];
                    final cantidad = _cantidades[p.id] ?? 0;
                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8),
                      child: Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(p.nombre, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                                const SizedBox(height: 2),
                                Text('\$${p.precio.toString()} • Stock: ${p.stock}', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                              ],
                            ),
                          ),
                          SizedBox(
                            width: 70,
                            child: TextFormField(
                              initialValue: cantidad == 0 ? '' : cantidad.toString(),
                              keyboardType: TextInputType.number,
                              decoration: const InputDecoration(labelText: 'Cant'),
                              onChanged: (v) => _setCantidad(p.id, int.tryParse(v) ?? 0),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 12),

              if (_cantidades.isNotEmpty)
                Card(
                  color: Colors.grey.shade100,
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Total del pedido:'),
                        Text('\$${_calcularTotal()}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
                      ],
                    ),
                  ),
                ),
              const SizedBox(height: 8),

              ConfirmationButton(
                isLoading: _isLoading,
                isEnabled: _cantidades.isNotEmpty,
                onTap: _submit,
                idleLabel: 'Crear Pedido',
                onTapLabel: 'Creando pedido...'
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHistorial(BuildContext context) {
    final pedidos = _pedidosFiltrados;
    return Column(
      children: [
        Row(children: [
          Expanded(
            child: TextField(
              controller: _filtroFechaCtrl,
              decoration: const InputDecoration(labelText: 'Filtrar por fecha (YYYY-MM-DD)', prefixIcon: Icon(Icons.calendar_today)),
              onChanged: (_) => setState(() {}),
            ),
          ),
        ]),
        const SizedBox(height: 12),
        Expanded(
          child: pedidos.isEmpty
              ? Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: const [
                        Icon(Icons.remove_shopping_cart_outlined, size: 48, color: Colors.grey),
                        SizedBox(height: 8),
                        Text('No se encontraron pedidos', style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  ),
                )
              : ListView.separated(
                  itemCount: pedidos.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, i) {
                    final p = pedidos[i];
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                  Text(p.cliente, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                                  Text('#${p.id}', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                ]),
                                _estadoPedidoBadge(p.estado),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Row(children: [
                                  const Icon(Icons.calendar_today, size: 14, color: Colors.grey),
                                  const SizedBox(width: 4),
                                  Text(p.fecha, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                ]),
                                Row(children: [
                                  const Icon(Icons.inventory_2_outlined, size: 14, color: Colors.grey),
                                  const SizedBox(width: 4),
                                  Text('${p.items.length} productos', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                ]),
                              ],
                            ),
                            const SizedBox(height: 8),
                            ...p.items.map((it) => Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Expanded(child: Text(it.nombre, overflow: TextOverflow.ellipsis)),
                                    Text('${it.cantidad} × \$${it.precio}', style: const TextStyle(color: Colors.grey)),
                                  ],
                                )),
                            const Divider(height: 16),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text('Total:'),
                                Text('\$${p.total}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }

  Widget _estadoPedidoBadge(String estado) {
    Color bg;
    Color fg = Colors.white;
    switch (estado) {
      case 'pendiente':
        bg = Colors.grey; break;
      case 'procesando':
        bg = Colors.orange; break;
      case 'enviado':
        bg = Colors.blue; break;
      case 'entregado':
        bg = Colors.green; break;
      case 'cancelado':
        bg = Colors.red; break;
      default:
        bg = Colors.black54; break;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(12)),
      child: Text(estado[0].toUpperCase() + estado.substring(1), style: TextStyle(fontSize: 11, color: fg)),
    );
  }
}

class AdminHomeScreen extends StatelessWidget {
  const AdminHomeScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return _homeScaffold(context, 'Inicio Admin');
  }
}

Widget _homeScaffold(BuildContext context, String title) {
  final state = context.watch<AppState>();
  return Scaffold(
    appBar: AppBar(
      title: Text(title),
      actions: [
        Center(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12.0),
            child: Text(state.userType?.name ?? ''),
          ),
        ),
        IconButton(
          onPressed: () => context.read<AppState>().logout(),
          icon: const Icon(Icons.logout),
        ),
      ],
    ),
    body: const Center(child: Text('Contenido próximamente...')),
  );
}

// Eliminado _PlaceholderScaffold: ya no se utiliza tras implementar pantallas completas
