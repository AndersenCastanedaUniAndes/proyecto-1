import 'package:flutter/material.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:medisupply_movil/data/data.dart';
import 'package:medisupply_movil/utils/utils.dart';
import 'package:provider/provider.dart';

class ClientOrdersScreen extends StatefulWidget {
  final VoidCallback onBack;
  const ClientOrdersScreen({super.key, required this.onBack});

  @override
  State<ClientOrdersScreen> createState() => _ClientOrdersScreenState();
}

class _ClientOrdersScreenState extends State<ClientOrdersScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController = TabController(length: 2, vsync: this);

  // Nuevo pedido (para cliente actual)
  final _fechaCtrl = TextEditingController();
  bool _isCreatingOrder = false;
  final Map<int, int> _cantidades = {}; // productoId -> cantidad
  bool _isLoadingInventory = false;
  bool _isLoadingHistory = false;

  // Filtros historial
  final _filtroFechaCtrl = TextEditingController();

  late List<Product> _products = [];

  late List<Order> _orders = [];

  List<Order> get _filteredOrders {
    final fFecha = _filtroFechaCtrl.text.trim();
    return _orders.where((p) {
      final fechaOk = fFecha.isEmpty || p.fecha.contains(fFecha);
      return fechaOk;
    }).toList();
  }

  @override
  void initState() {
    super.initState();
    _loadInventory();
    _loadHistory();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _fechaCtrl.dispose();
    _filtroFechaCtrl.dispose();
    super.dispose();
  }

  double _calculateTotal() {
    double total = 0;
    _cantidades.forEach((prodId, cant) {
      final prod = _products.firstWhere((p) => p.id == prodId);
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

  Future<void> _submit() async {
    if (_fechaCtrl.text.isEmpty || _cantidades.isEmpty) {
      return;
    }

    setState(() => _isCreatingOrder = true);

    final state = context.read<AppState>();

    final productos = _cantidades.entries.map((e) {
      final prod = _products.firstWhere((p) => p.id == e.key);
      return {
        'producto': prod.nombre,
        'producto_id': prod.id,
        'cantidad': e.value,
        'valor_unitario': prod.precio,
        'valor_total': prod.precio * e.value,
      };
    }).toList();

    final response = await createOrder({
      'fecha': _fechaCtrl.text.trim(),
      'vendedor': 'none',
      'vendedor_id': -1,
      'productos': productos,
      'cliente': state.userName,
      'cliente_id': state.id,
      'comision': 0,
    }, state.id, state.token);

    setState(() => _isCreatingOrder = false);

    if (response.statusCode != 201) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error ${response.statusCode}: ${response.body}'),
        ),
      );
      return;
    }

    _loadHistory();

    setState(() {
      _fechaCtrl.clear();
      _cantidades.clear();
      _isCreatingOrder = false;
      _tabController.index = 1; // ir a historial
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
    } else {
      _fechaCtrl.clear();
    }
    setState(() {});
  }

  Future<void> _filterDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: now,
      firstDate: DateTime(now.year - 1),
      lastDate: DateTime(now.year + 2),
    );
    if (picked != null) {
      _filtroFechaCtrl.text = picked.toIso8601String().substring(0, 10);
    } else {
      _filtroFechaCtrl.clear();
    }
    setState(() {});
  }

  Future<void> _loadInventory() async {
    setState(() => _isLoadingInventory = true);

    final state = context.read<AppState>();

    final response = await getInventory(state.id, state.token);
    setState(() => _isLoadingInventory = false);

    try {
      _products = response;
    } catch (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al cargar el inventario: $error'),
        ),
      );
    }
  }

  Future<void> _loadHistory() async {
    setState(() => _isLoadingHistory = true);

    final state = context.read<AppState>();

    final response = await getClientOrders(state.id, state.token);
    setState(() => _isLoadingHistory = false);

    try {
      _orders = response;
    } catch (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al cargar el inventario: $error'),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ScreenTitleAndBackNavigation(
          title: 'Mis Pedidos',
          subtitle: '${_filteredOrders.length} pedidos',
          textTheme: textTheme,
          onBack: widget.onBack,
        ),
        const SizedBox(height: 18),

        Container(
          height: 36,
          decoration: BoxDecoration(
            color: const Color(0xFFF1F1F4), // light gray background
            borderRadius: BorderRadius.circular(20),
          ),
          padding: const EdgeInsets.all(3),
          child: TabBar(
            controller: _tabController,
            indicator: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
            ),
            labelColor: Colors.black,
            unselectedLabelColor: Colors.black54,
            indicatorSize: TabBarIndicatorSize.tab,
            dividerColor: Colors.transparent,
            overlayColor: WidgetStateProperty.all(Colors.transparent),
            tabs: [
              Tab(
                iconMargin: EdgeInsets.only(bottom: 2),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  spacing: 8,
                  children: [
                    Icon(AppIcons.add, size: 16, color: Colors.black),
                    Text(
                      "Crear Pedido",
                      style: textTheme.labelMedium?.copyWith(fontSize: 13),
                    ),
                  ],
                ),
              ),
              Tab(
                iconMargin: EdgeInsets.only(bottom: 2),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  spacing: 8,
                  children: [
                    Icon(AppIcons.shoppingCart, size: 16, color: Colors.black),
                    Text("Mis Pedidos", style: textTheme.labelMedium),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),

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
    final textTheme = Theme.of(context).textTheme;

    return SingleChildScrollView(
      child: Container(
        decoration: AppStyles.decoration,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Nuevo Pedido',
                style: textTheme.titleMedium?.copyWith(fontSize: 16),
              ),
              const SizedBox(height: 12),

              Text('Fecha', style: textTheme.titleMedium),
              const SizedBox(height: 2),

              TextFormField(
                controller: _fechaCtrl,
                readOnly: true,
                decoration: baseInputDecoration().copyWith(
                  hintText: 'mm/dd/yyyy',
                  suffixIcon: Icon(AppIcons.calendar, size: 14, color: Colors.white)
                ),
                onTap: _pickDate,
                validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
              ),
              const SizedBox(height: 20),

              Text('Productos', style: textTheme.titleMedium),
              const SizedBox(height: 8),

              Container(
                constraints: const BoxConstraints(minHeight: 162),
                decoration: AppStyles.decoration,
                child: _isLoadingInventory
                  ? Loading()
                  : ListView.separated(
                    shrinkWrap: true,
                    itemCount: _products.length,
                    separatorBuilder: (_, __) => Container(),
                    itemBuilder: (context, i) {
                      final p = _products[i];
                      final cantidad = _cantidades[p.id] ?? 0;
                      return Padding(
                        padding: EdgeInsets.only(
                          left: 12,
                          right: 12,
                          bottom: 8,
                          top: i == 0 ? 12 : 0,
                        ),
                        child: Container(
                          decoration: AppStyles.decoration.copyWith(
                            borderRadius: BorderRadius.all(Radius.circular(4)),
                          ),
                          padding: const EdgeInsets.all(8),
                          child: Row(
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      p.nombre,
                                      style: textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)
                                    ),
                                    const SizedBox(height: 2),
                                    Text(
                                      '\$${toMoneyFormat(p.precio)} • Stock: ${p.stock}',
                                      style: textTheme.bodySmall?.copyWith(fontSize: 12, color: AppStyles.grey1)
                                    ),
                                  ],
                                ),
                              ),
                              SizedBox(
                                width: 70,
                                child: TextFormField(
                                  initialValue: cantidad == 0 ? '' : cantidad.toString(),
                                  keyboardType: TextInputType.number,
                                  decoration: InputDecoration(
                                    hintText: '0',
                                    contentPadding: EdgeInsets.only(left: 12),
                                    filled: true,
                                    fillColor: AppStyles.grey1.withAlpha(30),
                                    border: OutlineInputBorder(
                                      borderRadius: BorderRadius.circular(8.0),
                                      borderSide: BorderSide.none,
                                    ),
                                  ),
                                  onChanged: (v) => _setCantidad(p.id, int.tryParse(v) ?? 0),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
              ),
              const SizedBox(height: 12),

              if (_cantidades.isNotEmpty)
                Container(
                  decoration: AppStyles.decoration,
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Total del pedido:', style: textTheme.bodySmall,),
                        Text(
                          '\$${toMoneyFormat(_calculateTotal())}',
                          style: textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.bold, color: AppStyles.green1)
                        ),
                      ],
                    ),
                  ),
                ),
              const SizedBox(height: 8),

              ConfirmationButton(
                isEnabled: !_isLoadingInventory && _cantidades.isNotEmpty,
                isLoading: _isCreatingOrder,
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
    final textTheme = Theme.of(context).textTheme;
    final orders = _filteredOrders;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text('Filtrar por fecha', style: textTheme.titleMedium),
        const SizedBox(height: 2),

        TextFormField(
          controller: _filtroFechaCtrl,
          readOnly: true,
          decoration: baseInputDecoration().copyWith(
            hintText: 'mm/dd/yyyy',
            suffixIcon: Icon(AppIcons.calendar, size: 14, color: Colors.white)
          ),
          onTap: _filterDate,
        ),
        const SizedBox(height: 12),

        _isLoadingHistory ? Loading()
        : orders.isEmpty ? Container(
          decoration: AppStyles.decoration,
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(AppIcons.shoppingCart, size: 48, color: AppStyles.grey1),
                SizedBox(height: 8),
                Text(
                  'No se encontraron pedidos',
                  style: TextStyle(color: AppStyles.grey1),
                ),
              ],
            ),
          ),
        )
        : Expanded(
          child: ListView.separated(
            itemCount: orders.length,
            separatorBuilder: (_, __) => const SizedBox(height: 12),
            itemBuilder: (context, i) {
              final order = orders[i];
              return OrderCard(order: order);
            },
          ),
        ),
      ],
    );
  }
}