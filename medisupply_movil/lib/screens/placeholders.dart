import 'package:flutter/material.dart';
import 'package:medisupply_movil/screens/screens.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:provider/provider.dart';
import '../state/app_state.dart';

enum _VendorScreen { home, clientes, visitas, pedidos, recomendaciones }

class VendorScreen extends StatefulWidget {
  const VendorScreen({super.key});

  @override
  State<VendorScreen> createState() => _VendorScreenState();
}

class _VendorScreenState extends State<VendorScreen> {
  _VendorScreen _current = _VendorScreen.home;
  bool _showUserMenu = false;

  void _goHome() => setState(() => _current = _VendorScreen.home);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: switch (_current) {
                _VendorScreen.clientes => VendorClientsScreen(onBack: _goHome),
                _VendorScreen.visitas => VendorVisitsView(onBack: _goHome),
                _VendorScreen.pedidos => VendorOrdersView(onBack: _goHome),
                _VendorScreen.recomendaciones => _SimpleSubView(title: 'Recomendaciones', onBack: _goHome, child: const Text('Generación de recomendaciones próximamente...')),
                _VendorScreen.home => _VendorHome(onOpenMenu: () => setState(() => _showUserMenu = true), onTapCard: (view) => setState(() => _current = view)),
              },
            ),
          ),
          if (_showUserMenu) _UserMenuOverlay(onClose: () => setState(() => _showUserMenu = false)),
        ],
      ),
    );
  }
}

class _VendorHome extends StatelessWidget {
  final VoidCallback onOpenMenu;
  final void Function(_VendorScreen) onTapCard;
  const _VendorHome({required this.onOpenMenu, required this.onTapCard});

  String _getSales() {
    return '\$45,670';
  }

  String _getSalesPercentage() {
    return '87%';
  }

  String _getActiveClients() {
    return '24';
  }

  String _getVisitsToday() {
    return '8';
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          HomeCard(
            gradient: LinearGradient(colors: [AppStyles.blue1, AppStyles.blue2]),
            title: '¡Hola, Carlos!',
            subtitle: 'Vendedor MediSupply',
            onTap: onOpenMenu,
            stat1Title: 'Ventas este mes',
            stat1Value: _getSales(),
            stat2Title: 'Meta alcanzada',
            stat2Value: _getSalesPercentage(),
          ),
          const SizedBox(height: 16),

          QuickStats(
            stat1Color: AppStyles.green1,
            stat1Title: 'Clientes Activos',
            stat1Value: _getActiveClients(),
            stat2Color: AppStyles.blue1,
            stat2Title: 'Visitas Hoy',
            stat2Value: _getVisitsToday(),
          ),
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
                  _MenuCard(
                    color: AppStyles.menuCardBlue,
                    icon: AppIcons.clients,
                    title: 'Clientes',
                    description: 'Gestiona tu cartera de clientes',
                    badge: '24 clientes',
                    onTap: () => onTapCard(_VendorScreen.clientes),
                  ),

                  _MenuCard(
                    color: AppStyles.menuCardGreen,
                    icon: AppIcons.pin,
                    title: 'Visitas',
                    description: 'Registra y revisa tus visitas',
                    badge: '8 hoy',
                    onTap: () => onTapCard(_VendorScreen.visitas),
                  ),

                  _MenuCard(
                    color: Color(0xFFFF6900),
                    icon: AppIcons.shoppingCart,
                    title: 'Pedidos',
                    description: 'Gestiona pedidos de clientes',
                    badge: '12 pendientes',
                    onTap: () => onTapCard(_VendorScreen.pedidos),
                  ),

                  _MenuCard(
                    color: Color(0xFFad46ff),
                    icon: AppIcons.lightbulb,
                    title: 'Recomendaciones',
                    description: 'Generación de recomendaciones',
                    badge: 'Próximamente',
                    onTap: () => onTapCard(_VendorScreen.recomendaciones),
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
          if (_showUserMenu) _UserMenuOverlay(onClose: () => setState(() => _showUserMenu = false)),
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

class _ClientHome extends StatelessWidget {
  final VoidCallback onOpenMenu;
  final void Function(_ClientView) onTapCard;
  const _ClientHome({required this.onOpenMenu, required this.onTapCard});

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
  Widget build(BuildContext context) {
    final pendingOrders = _getPendingOrders();

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          HomeCard(
            gradient: LinearGradient(colors: [AppStyles.green1, AppStyles.green2]),
            title: '¡Hola, Farmacia Central!',
            subtitle: 'Cliente MediSupply',
            onTap: onOpenMenu,
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
                  _MenuCard(
                    color: AppStyles.menuCardBlue,
                    icon: AppIcons.shoppingCart,
                    title: 'Pedidos',
                    description: 'Crear y gestionar tus pedidos',
                    badge: '$pendingOrders pendientes',
                    onTap: () => onTapCard(_ClientView.pedidos),
                  ),
                  _MenuCard(
                    color: AppStyles.menuCardGreen,
                    icon: AppIcons.shipping,
                    title: 'Entregas',
                    description: 'Consultar entregas programadas',
                    badge: '2 próximas',
                    onTap: () => onTapCard(_ClientView.entregas),
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

class _UserMenuOverlay extends StatelessWidget {
  final VoidCallback onClose;
  const _UserMenuOverlay({required this.onClose});

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Positioned.fill(
      child: GestureDetector(
        onTap: onClose,
        child: Container(
          color: Colors.black.withAlpha(128),
          child: Center(
            child: GestureDetector(
              onTap: () {},
              child: Container(
                margin: const EdgeInsets.symmetric(horizontal: 24),
                padding: const EdgeInsets.all(26),
                decoration: AppStyles.decoration.copyWith(color: Colors.white),
                width: 360,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      height: 64,
                      width: 64,
                      decoration: BoxDecoration(color: Color(0xFFDBEAFE), shape: BoxShape.circle),
                      child: Icon(AppIcons.user, size: 36, color: AppStyles.blue1),
                    ),
                    const SizedBox(height: 16),

                    Text('Usuario', style: textTheme.bodyLarge?.copyWith(fontSize: 18, fontWeight: FontWeight.w600)),
                    Text('MediSupply', style: textTheme.bodyMedium?.copyWith(fontSize: 14, fontWeight: FontWeight.w400)),
                    const SizedBox(height: 36),

                    Align(
                      alignment: Alignment.centerLeft,
                      child: Padding(
                        padding: const EdgeInsets.only(left: 12.0),
                        child: AppClickableText(
                          mainAxisAlignment: MainAxisAlignment.start,
                          onTap: () {
                            onClose();
                            context.read<AppState>().logout();
                          },
                          label: 'Cerrar Sesión',
                          icon: AppIcons.logout,
                          iconSize: 18,
                          spacing: 22,
                          overrideColor: AppStyles.red1,
                          overrideFontWeight: FontWeight.w500,
                          textTheme: textTheme.copyWith(bodySmall: textTheme.bodySmall?.copyWith(fontSize: 15))
                        ),
                      ),
                    )
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _MenuCard extends StatelessWidget {
  const _MenuCard({
    required this.color,
    required this.icon,
    required this.title,
    required this.description,
    required this.badge,
    required this.onTap,
    // required this.textTheme,
  });

  final Color color;
  final IconData icon;
  final String title;
  final String description;
  final String badge;
  final VoidCallback onTap;
  // final TextTheme textTheme;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: AppStyles.decoration,
        padding: const EdgeInsets.all(12),
        child: Column(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              height: 48,
              width: 48,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
              child: Icon(icon, size: 24, color: Colors.white,),
            ),
            const SizedBox(height: 8),

            Text(title, style: textTheme.labelLarge?.copyWith(fontSize: 15, fontWeight: FontWeight.w600)),
            const SizedBox(height: 4),

            Flexible(
              child: Text(
                description,
                textAlign: TextAlign.center,
                style: textTheme.bodySmall?.copyWith(fontSize: 12),
                softWrap: true,
                overflow: TextOverflow.fade,
              ),
            ),
            const SizedBox(height: 6),

            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(color: Colors.grey.shade200, borderRadius: BorderRadius.circular(10)),
              child: Text(badge, style: textTheme.bodySmall?.copyWith(fontSize: 12, fontWeight: FontWeight.w500)),
            ),
          ],
        ),
      ),
    );
  }
}

class _SimpleSubView extends StatelessWidget {
  final String title;
  final Widget child;
  final VoidCallback onBack;
  const _SimpleSubView({required this.title, required this.child, required this.onBack});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            IconButton(onPressed: onBack, icon: const Icon(Icons.arrow_back)),
            Text(title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
          ],
        ),
        const SizedBox(height: 12),
        Expanded(
          child: Center(
            child: child,
          ),
        ),
      ],
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

// =================== VENDEDOR - CLIENTES VIEW ===================







// =================== VENDEDOR - VISITAS VIEW ===================
class VendorVisitsView extends StatefulWidget {
  final VoidCallback onBack;
  const VendorVisitsView({super.key, required this.onBack});

  @override
  State<VendorVisitsView> createState() => _VendorVisitsViewState();
}

class _VendorVisitsViewState extends State<VendorVisitsView>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController = TabController(length: 2, vsync: this);

  // Form state
  final _formKey = GlobalKey<FormState>();
  String? _clienteSel;
  final _fechaCtrl = TextEditingController();
  final _horaCtrl = TextEditingController();
  final _localizacionCtrl = TextEditingController();
  final _hallazgosCtrl = TextEditingController();
  final _sugerenciasCtrl = TextEditingController();
  bool _isLoading = false;

  // Filters
  final _filtroFechaCtrl = TextEditingController();
  final _filtroClienteCtrl = TextEditingController();

  final List<String> _clientes = const [
    'Farmacia Central',
    'Droguería La Salud',
    'Hospital Nacional',
    'Red Farmacias Unidos',
    'Clínica San Juan',
  ];

  late final List<_Visita> _visitasBase = [
    _Visita(
      id: 1,
      cliente: 'Farmacia Central',
      fecha: '2024-03-20',
      hora: '09:30',
      direccion: 'Av. Principal 123, Centro',
      hallazgos:
          'Cliente requiere mayor stock de analgésicos para temporada de gripe. Inventario actual bajo en paracetamol y ibuprofeno.',
      sugerencias: const ['Paracetamol 500mg x 500 unidades', 'Ibuprofeno 600mg x 300 unidades', 'Antigripales variados'],
      fechaCreacion: '2024-03-20',
    ),
    _Visita(
      id: 2,
      cliente: 'Hospital Nacional',
      fecha: '2024-03-19',
      hora: '14:15',
      direccion: 'Carrera 30 #45-67, Sur',
      hallazgos:
          'Necesidad urgente de antibióticos para área de emergencias. Personal médico reporta escasez en tratamientos post-quirúrgicos.',
      sugerencias: const ['Amoxicilina 875mg', 'Cefalexina 500mg', 'Material quirúrgico estéril'],
      fechaCreacion: '2024-03-19',
    ),
  ];

  List<_Visita> get _visitasFiltradas {
    final fFecha = _filtroFechaCtrl.text.trim();
    final fCli = _filtroClienteCtrl.text.trim().toLowerCase();
    return _visitasBase.where((v) {
      final fechaOk = fFecha.isEmpty || v.fecha.contains(fFecha);
      final clienteOk = fCli.isEmpty || v.cliente.toLowerCase().contains(fCli);
      return fechaOk && clienteOk;
    }).toList();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _fechaCtrl.dispose();
    _horaCtrl.dispose();
    _localizacionCtrl.dispose();
    _hallazgosCtrl.dispose();
    _sugerenciasCtrl.dispose();
    _filtroFechaCtrl.dispose();
    _filtroClienteCtrl.dispose();
    super.dispose();
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

  Future<void> _pickTime() async {
    final now = TimeOfDay.now();
    final picked = await showTimePicker(context: context, initialTime: now);
    if (picked != null) {
      _horaCtrl.text = picked.format(context);
      setState(() {});
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 1));
    // Simular guardado en _visitasBase (inmutable en runtime, pero aquí recreamos)
    final nueva = _Visita(
      id: _visitasBase.length + 1,
      cliente: _clienteSel!,
      fecha: _fechaCtrl.text.trim(),
      hora: _horaCtrl.text.trim(),
      direccion: _localizacionCtrl.text.trim(),
      hallazgos: _hallazgosCtrl.text.trim(),
      sugerencias: _sugerenciasCtrl.text
          .split('\n')
          .map((e) => e.trim())
          .where((e) => e.isNotEmpty)
          .toList(),
      fechaCreacion: DateTime.now().toIso8601String().substring(0, 10),
    );
    setState(() {
      _visitasBase.add(nueva);
      _clienteSel = null;
      _fechaCtrl.clear();
      _horaCtrl.clear();
      _localizacionCtrl.clear();
      _hallazgosCtrl.clear();
      _sugerenciasCtrl.clear();
      _isLoading = false;
      _tabController.index = 1; // Ir al historial
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
              Text('Visitas', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
              Text('${_visitasFiltradas.length} registros', style: const TextStyle(fontSize: 12, color: Colors.grey)),
            ])
          ],
        ),
        const SizedBox(height: 8),
        TabBar(
          controller: _tabController,
          indicatorColor: Theme.of(context).colorScheme.primary,
          tabs: const [
            Tab(icon: Icon(Icons.add), text: 'Registrar'),
            Tab(icon: Icon(Icons.feed_outlined), text: 'Historial'),
          ],
        ),
        const SizedBox(height: 8),
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildRegistrar(context),
              _buildHistorial(context),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRegistrar(BuildContext context) {
    return SingleChildScrollView(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text('Nueva Visita', style: Theme.of(context).textTheme.titleSmall),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: _clienteSel,
                  items: _clientes
                      .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                      .toList(),
                  onChanged: (v) => setState(() => _clienteSel = v),
                  decoration: const InputDecoration(labelText: 'Cliente'),
                  validator: (v) => v == null || v.isEmpty ? 'Selecciona un cliente' : null,
                ),
                const SizedBox(height: 12),
                Row(children: [
                  Expanded(
                    child: TextFormField(
                      controller: _fechaCtrl,
                      readOnly: true,
                      decoration: const InputDecoration(labelText: 'Fecha', prefixIcon: Icon(Icons.calendar_today)),
                      onTap: _pickDate,
                      validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _horaCtrl,
                      readOnly: true,
                      decoration: const InputDecoration(labelText: 'Hora', prefixIcon: Icon(Icons.access_time)),
                      onTap: _pickTime,
                      validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                    ),
                  ),
                ]),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _localizacionCtrl,
                  decoration: const InputDecoration(labelText: 'Localización', hintText: 'Dirección del cliente', prefixIcon: Icon(Icons.place_outlined)),
                  validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _hallazgosCtrl,
                  decoration: const InputDecoration(labelText: 'Hallazgos Técnicos o Clínicos'),
                  maxLines: 3,
                  validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _sugerenciasCtrl,
                  decoration: const InputDecoration(labelText: 'Sugerencias de Producto', hintText: 'Uno por línea'),
                  maxLines: 3,
                ),
                const SizedBox(height: 16),
                ConfirmationButton(
                  isLoading: _isLoading,
                  onTap: _submit,
                  idleLabel: 'Registrar Visita',
                  onTapLabel: 'Registrando...'
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHistorial(BuildContext context) {
    final visits = _visitasFiltradas;
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
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: _filtroClienteCtrl,
              decoration: const InputDecoration(labelText: 'Filtrar por cliente', prefixIcon: Icon(Icons.search)),
              onChanged: (_) => setState(() {}),
            ),
          ),
        ]),
        const SizedBox(height: 12),
        Expanded(
          child: visits.isEmpty
              ? Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: const [
                        Icon(Icons.event_busy, size: 48, color: Colors.grey),
                        SizedBox(height: 8),
                        Text('No se encontraron visitas', style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  ),
                )
              : ListView.separated(
                  itemCount: visits.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, i) {
                    final v = visits[i];
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(v.cliente, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                                _idBadge('ID: ${v.id}')
                              ],
                            ),
                            const SizedBox(height: 8),
                            Row(children: [
                              const Icon(Icons.calendar_today, size: 14, color: Colors.grey),
                              const SizedBox(width: 4),
                              Text(v.fecha, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                              const SizedBox(width: 16),
                              const Icon(Icons.access_time, size: 14, color: Colors.grey),
                              const SizedBox(width: 4),
                              Text(v.hora, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                            ]),
                            const SizedBox(height: 8),
                            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                              const Icon(Icons.place_outlined, size: 14, color: Colors.grey),
                              const SizedBox(width: 4),
                              Expanded(child: Text(v.direccion, style: const TextStyle(fontSize: 12, color: Colors.grey))),
                            ]),
                            const SizedBox(height: 12),
                            Row(children: const [
                              Icon(Icons.description_outlined, size: 14),
                              SizedBox(width: 4),
                              Text('Hallazgos', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                            ]),
                            Text(v.hallazgos, style: const TextStyle(fontSize: 12, color: Colors.black87)),
                            if (v.sugerencias.isNotEmpty) ...[
                              const SizedBox(height: 8),
                              Row(children: const [
                                Icon(Icons.lightbulb_outline, size: 14),
                                SizedBox(width: 4),
                                Text('Sugerencias', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                              ]),
                              const SizedBox(height: 4),
                              Wrap(
                                spacing: 6,
                                runSpacing: 6,
                                children: v.sugerencias
                                    .map((s) => Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                          decoration: BoxDecoration(
                                            color: Colors.grey.shade200,
                                            borderRadius: BorderRadius.circular(12),
                                          ),
                                          child: Text(s, style: const TextStyle(fontSize: 11)),
                                        ))
                                    .toList(),
                              ),
                            ]
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

  Widget _idBadge(String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: Colors.grey.shade200, borderRadius: BorderRadius.circular(12)),
      child: Text(text, style: const TextStyle(fontSize: 11)),
    );
  }
}

class _Visita {
  final int id;
  final String cliente;
  final String fecha; // YYYY-MM-DD
  final String hora; // HH:mm
  final String direccion;
  final String hallazgos;
  final List<String> sugerencias;
  final String fechaCreacion; // YYYY-MM-DD
  _Visita({
    required this.id,
    required this.cliente,
    required this.fecha,
    required this.hora,
    required this.direccion,
    required this.hallazgos,
    required this.sugerencias,
    required this.fechaCreacion,
  });
}

// =================== VENDEDOR - PEDIDOS VIEW ===================
class VendorOrdersView extends StatefulWidget {
  final VoidCallback onBack;
  const VendorOrdersView({super.key, required this.onBack});

  @override
  State<VendorOrdersView> createState() => _VendorOrdersViewState();
}

class _VendorOrdersViewState extends State<VendorOrdersView>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController = TabController(length: 2, vsync: this);

  // Nuevo pedido
  String? _clienteSel;
  final _fechaCtrl = TextEditingController();
  bool _isLoading = false;
  final Map<int, int> _cantidades = {}; // productoId -> cantidad

  // Filtros historial
  final _filtroFechaCtrl = TextEditingController();
  final _filtroClienteCtrl = TextEditingController();

  final List<String> _clientes = const [
    'Farmacia Central',
    'Droguería La Salud',
    'Hospital Nacional',
    'Red Farmacias Unidos',
    'Clínica San Juan',
  ];

  final List<_Producto> _productos = [
    _Producto(id: 1, nombre: 'Paracetamol 500mg', precio: 250, stock: 1000, categoria: 'Analgésicos'),
    _Producto(id: 2, nombre: 'Ibuprofeno 600mg', precio: 350, stock: 800, categoria: 'Analgésicos'),
    _Producto(id: 3, nombre: 'Amoxicilina 875mg', precio: 450, stock: 600, categoria: 'Antibióticos'),
    _Producto(id: 4, nombre: 'Insulina Rápida', precio: 15000, stock: 200, categoria: 'Diabetes'),
    _Producto(id: 5, nombre: 'Vacuna COVID-19', precio: 25000, stock: 150, categoria: 'Vacunas'),
    _Producto(id: 6, nombre: 'Vitamina C', precio: 180, stock: 500, categoria: 'Vitaminas'),
    _Producto(id: 7, nombre: 'Multivitamínico', precio: 320, stock: 400, categoria: 'Vitaminas'),
    _Producto(id: 8, nombre: 'Glucómetro', precio: 45000, stock: 50, categoria: 'Diabetes'),
  ];

  final List<_PedidoOrden> _pedidos = [
    _PedidoOrden(
      id: 1,
      cliente: 'Farmacia Central',
      fecha: '2024-03-20',
      estado: 'pendiente',
      items: [
        _PedidoItemOrden(productoId: 1, nombre: 'Paracetamol 500mg', cantidad: 100, precio: 250),
        _PedidoItemOrden(productoId: 2, nombre: 'Ibuprofeno 600mg', cantidad: 50, precio: 350),
      ],
      total: 42500,
      fechaCreacion: '2024-03-20',
    ),
    _PedidoOrden(
      id: 2,
      cliente: 'Hospital Nacional',
      fecha: '2024-03-19',
      estado: 'procesando',
      items: [
        _PedidoItemOrden(productoId: 3, nombre: 'Amoxicilina 875mg', cantidad: 200, precio: 450),
        _PedidoItemOrden(productoId: 4, nombre: 'Insulina Rápida', cantidad: 10, precio: 15000),
      ],
      total: 240000,
      fechaCreacion: '2024-03-19',
    ),
    _PedidoOrden(
      id: 3,
      cliente: 'Droguería La Salud',
      fecha: '2024-03-18',
      estado: 'enviado',
      items: [
        _PedidoItemOrden(productoId: 4, nombre: 'Insulina Rápida', cantidad: 5, precio: 15000),
        _PedidoItemOrden(productoId: 8, nombre: 'Glucómetro', cantidad: 2, precio: 45000),
      ],
      total: 165000,
      fechaCreacion: '2024-03-18',
    ),
  ];

  List<_PedidoOrden> get _pedidosFiltrados {
    final fFecha = _filtroFechaCtrl.text.trim();
    final fCli = _filtroClienteCtrl.text.trim().toLowerCase();
    return _pedidos.where((p) {
      final fechaOk = fFecha.isEmpty || p.fecha.contains(fFecha);
      final clienteOk = fCli.isEmpty || p.cliente.toLowerCase().contains(fCli);
      return fechaOk && clienteOk;
    }).toList();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _fechaCtrl.dispose();
    _filtroFechaCtrl.dispose();
    _filtroClienteCtrl.dispose();
    super.dispose();
  }

  int _calcularTotal() {
    int total = 0;
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
    if (_clienteSel == null || _clienteSel!.isEmpty || _fechaCtrl.text.isEmpty || _cantidades.isEmpty) {
      return;
    }
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 1));

    final items = _cantidades.entries.map((e) {
      final prod = _productos.firstWhere((p) => p.id == e.key);
      return _PedidoItemOrden(productoId: prod.id, nombre: prod.nombre, cantidad: e.value, precio: prod.precio);
    }).toList();

    setState(() {
      _pedidos.add(
        _PedidoOrden(
          id: _pedidos.length + 1,
          cliente: _clienteSel!,
          fecha: _fechaCtrl.text,
          estado: 'pendiente',
          items: items,
          total: _calcularTotal(),
          fechaCreacion: DateTime.now().toIso8601String().substring(0, 10),
        ),
      );
      _clienteSel = null;
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
              Text('Pedidos', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
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
              Text('Nuevo Pedido', style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: 12),
              Row(children: [
                Expanded(
                  child: DropdownButtonFormField<String>(
                    value: _clienteSel,
                    items: _clientes.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                    onChanged: (v) => setState(() => _clienteSel = v),
                    decoration: const InputDecoration(labelText: 'Cliente'),
                    validator: (v) => (v == null || v.isEmpty) ? 'Selecciona un cliente' : null,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _fechaCtrl,
                    readOnly: true,
                    decoration: const InputDecoration(labelText: 'Fecha', prefixIcon: Icon(Icons.calendar_today)),
                    onTap: _pickDate,
                  ),
                ),
              ]),
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
                onTap: _submit,
                idleLabel: 'Registrar Pedido',
                onTapLabel: 'Registrando...'
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
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: _filtroClienteCtrl,
              decoration: const InputDecoration(labelText: 'Filtrar por cliente', prefixIcon: Icon(Icons.search)),
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

class _Producto {
  final int id;
  final String nombre;
  final int precio;
  final int stock;
  final String categoria;
  _Producto({required this.id, required this.nombre, required this.precio, required this.stock, required this.categoria});
}

class _PedidoItemOrden {
  final int productoId;
  final String nombre;
  final int cantidad;
  final int precio;
  _PedidoItemOrden({required this.productoId, required this.nombre, required this.cantidad, required this.precio});
}

class _PedidoOrden {
  final int id;
  final String cliente;
  final String fecha;
  final String estado; // pendiente | procesando | enviado | entregado | cancelado
  final List<_PedidoItemOrden> items;
  final int total;
  final String fechaCreacion;
  _PedidoOrden({required this.id, required this.cliente, required this.fecha, required this.estado, required this.items, required this.total, required this.fechaCreacion});
}

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

  final List<_Producto> _productos = [
    _Producto(id: 1, nombre: 'Paracetamol 500mg', precio: 250, stock: 1000, categoria: 'Analgésicos'),
    _Producto(id: 2, nombre: 'Ibuprofeno 600mg', precio: 350, stock: 800, categoria: 'Analgésicos'),
    _Producto(id: 3, nombre: 'Amoxicilina 875mg', precio: 450, stock: 600, categoria: 'Antibióticos'),
    _Producto(id: 4, nombre: 'Insulina Rápida', precio: 15000, stock: 200, categoria: 'Diabetes'),
    _Producto(id: 5, nombre: 'Vacuna COVID-19', precio: 25000, stock: 150, categoria: 'Vacunas'),
    _Producto(id: 6, nombre: 'Vitamina C', precio: 180, stock: 500, categoria: 'Vitaminas'),
    _Producto(id: 7, nombre: 'Multivitamínico', precio: 320, stock: 400, categoria: 'Vitaminas'),
    _Producto(id: 8, nombre: 'Glucómetro', precio: 45000, stock: 50, categoria: 'Diabetes'),
  ];

  final List<_PedidoOrden> _pedidos = [
    _PedidoOrden(
      id: 1,
      cliente: 'Farmacia Central',
      fecha: '2024-03-20',
      estado: 'pendiente',
      items: [
        _PedidoItemOrden(productoId: 1, nombre: 'Paracetamol 500mg', cantidad: 100, precio: 250),
        _PedidoItemOrden(productoId: 2, nombre: 'Ibuprofeno 600mg', cantidad: 50, precio: 350),
      ],
      total: 42500,
      fechaCreacion: '2024-03-20',
    ),
    _PedidoOrden(
      id: 2,
      cliente: 'Farmacia Central',
      fecha: '2024-03-19',
      estado: 'procesando',
      items: [
        _PedidoItemOrden(productoId: 3, nombre: 'Amoxicilina 875mg', cantidad: 200, precio: 450),
        _PedidoItemOrden(productoId: 4, nombre: 'Insulina Rápida', cantidad: 10, precio: 15000),
      ],
      total: 240000,
      fechaCreacion: '2024-03-19',
    ),
  ];

  List<_PedidoOrden> get _pedidosFiltrados {
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

  int _calcularTotal() {
    int total = 0;
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
      return _PedidoItemOrden(productoId: prod.id, nombre: prod.nombre, cantidad: e.value, precio: prod.precio);
    }).toList();

    setState(() {
      _pedidos.add(
        _PedidoOrden(
          id: _pedidos.length + 1,
          cliente: _clienteActual,
          fecha: _fechaCtrl.text,
          estado: 'pendiente',
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
