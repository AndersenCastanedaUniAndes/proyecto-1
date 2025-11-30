import 'package:flutter/material.dart';
import 'package:medisupply_movil/data/data.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/utils/utils.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:provider/provider.dart';

class VendorOrderScreen extends StatefulWidget {
  final VoidCallback onBack;
  const VendorOrderScreen({super.key, required this.onBack});

  @override
  State<VendorOrderScreen> createState() => _VendorOrderScreenState();
}

class _VendorOrderScreenState extends State<VendorOrderScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController = TabController(length: 2, vsync: this);

  // Nuevo pedido
  final _formKey = GlobalKey<FormState>();
  String? _clienteSel;
  final _fechaCtrl = TextEditingController();
  bool _isCreatingOrder = false;
  bool _isLoadingClients = false;
  bool _isLoadingInventory = false;
  bool _isLoadingHistory = false;

  final Map<int, int> _cantidades = {}; // productoId -> cantidad

  // Filtros historial
  final _filtroFechaCtrl = TextEditingController();
  final _filtroClienteCtrl = TextEditingController();

  late Map<int, String> _clients = const {};

  late List<Product> _products = [];

  late List<Order> _orders = [];

  List<Order> get _filteredOrders {
    final fFecha = _filtroFechaCtrl.text.trim();
    final fCli = _filtroClienteCtrl.text.trim().toLowerCase();
    return _orders.where((p) {
      final fechaOk = fFecha.isEmpty || p.fecha.contains(fFecha);
      final clienteOk = fCli.isEmpty || p.cliente.toLowerCase().contains(fCli);
      return fechaOk && clienteOk;
    }).toList();
  }

  @override
  void initState() {
    super.initState();
    _loadClients();
    _loadInventory();
    _loadHistory();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _fechaCtrl.dispose();
    _filtroFechaCtrl.dispose();
    _filtroClienteCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadClients() async {
    setState(() => _isLoadingClients = true);

    final state = context.read<AppState>();

    final response = await getClientsSmall(state.id, state.token);
    setState(() => _isLoadingClients = false);

    try {
      _clients = response;
    } catch (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al cargar los clientes: $error'),
        ),
      );
    }
  }

  Future<void> _loadInventory() async {
    setState(() => _isLoadingInventory = true);

    final state = context.read<AppState>();

    final products = await getInventory(state.id, state.token);
    setState(() => _isLoadingInventory = false);

    try {
      _products = products;
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

    final response = await getVendorOrders(state.id, state.token);
    setState(() => _isLoadingHistory = false);

    try {
      _orders = response;
    } catch (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al cargar el historial de pedidos: $error'),
        ),
      );
    }
  }

  double _calculateTotal() {
    double total = 0;
    _cantidades.forEach((prodId, cant) {
      final prod = _products.firstWhere((p) => p.id == prodId);
      total += prod.precio * cant;
    });
    return total;
  }

  void _setQuantity(int productoId, int cantidad) {
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
    } else {
      _fechaCtrl.clear();
    }
    setState(() {});
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
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
      'vendedor': state.userName,
      'vendedor_id': state.id,
      'productos': productos,
      'cliente': _clienteSel,
      'cliente_id': _clients.entries.firstWhere((entry) => entry.value == _clienteSel!).key,
      'comision': (_calculateTotal() * 0.05).round(),
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
      _clienteSel = null;
      _fechaCtrl.clear();
      _cantidades.clear();
      _isCreatingOrder = false;
      _tabController.index = 1; // ir a historial
    });
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

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ScreenTitleAndBackNavigation(
          title: 'Pedidos',
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
                      "Nuevo",
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
                    Text("Historial", style: textTheme.labelMedium),
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
              _buildHistory(context),
            ],
          ),
        ),
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
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'Nuevo Pedido',
                  style: textTheme.titleMedium?.copyWith(fontSize: 16),
                ),
                const SizedBox(height: 18),

                Row(
                  spacing: 12,
                  children: [
                    Expanded(child: Text('Cliente', style: textTheme.titleMedium)),
                    Expanded(child: Text('Fecha', style: textTheme.titleMedium))
                  ],
                ),
                const SizedBox(height: 2),

                Row(
                  spacing: 12,
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        dropdownColor: Colors.white,
                        menuMaxHeight: 300,
                        isExpanded: true,
                        icon: const SizedBox.shrink(),
                        value: _clienteSel,
                        items: _clients.values.map((c) => DropdownMenuItem(
                          value: c,
                          child: Text(c, style: textTheme.bodySmall),
                        )).toList(),
                        onChanged: (v) => setState(() => _clienteSel = v),
                        decoration: baseInputDecoration().copyWith(
                          hintText: _isLoadingClients ? 'Cargando...' : 'Seleccionar',
                          suffixIcon: Icon(AppIcons.chevronDown, size: 16),
                        ),
                        validator: (v) => (v == null || v.isEmpty) ? 'Selecciona un cliente' : null,
                      ),
                    ),

                    Expanded(
                      child: TextFormField(
                        controller: _fechaCtrl,
                        readOnly: true,
                        decoration: baseInputDecoration().copyWith(
                          hintText: 'mm/dd/yyyy',
                          suffixIcon: Icon(AppIcons.calendar, size: 14, color: Colors.white)
                        ),
                        onTap: _pickDate,
                        validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                Text('Productos', style: textTheme.labelLarge),
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
                                  onChanged: (v) => _setQuantity(p.id, int.tryParse(v) ?? 0),
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
                  isEnabled: !_isLoadingClients && !_isLoadingInventory,
                  isLoading: _isCreatingOrder,
                  onTap: _submit,
                  idleLabel: 'Registrar Pedido',
                  onTapLabel: 'Registrando...',
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHistory(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final orders = _filteredOrders;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          spacing: 12,
          children: [
            Expanded(child: Text('Filtrar por fecha', style: textTheme.titleMedium)),
            Expanded(child: Text('Filtrar por cliente', style: textTheme.titleMedium,))
          ],
        ),
        const SizedBox(height: 2),

        Row(
          spacing: 12,
          children: [
            Expanded(
              child: TextFormField(
                controller: _filtroFechaCtrl,
                readOnly: true,
                decoration: baseInputDecoration().copyWith(
                  hintText: 'mm/dd/yyyy',
                  suffixIcon: Icon(AppIcons.calendar, size: 14, color: Colors.white)
                ),
                onTap: _filterDate,
              ),
            ),

            Expanded(
              child: TextField(
                controller: _filtroClienteCtrl,
                decoration: baseInputDecoration().copyWith(
                  hintText: 'Cliente...',
                  prefixIcon: Icon(AppIcons.search, size: 14)
                ),
                onChanged: (_) => setState(() {}),
              ),
            ),
          ],
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
