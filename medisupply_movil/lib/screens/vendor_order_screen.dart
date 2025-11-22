import 'package:flutter/material.dart';
import 'package:medisupply_movil/data/data.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:medisupply_movil/styles/styles.dart';

class VendorOrderScreen extends StatefulWidget {
  final VoidCallback onBack;
  const VendorOrderScreen({super.key, required this.onBack});

  @override
  State<VendorOrderScreen> createState() => _VendorOrderScreenState();
}

class _VendorOrderScreenState extends State<VendorOrderScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController = TabController(
    length: 2,
    vsync: this,
  );

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

  final List<Product> _productos = [
    Product(
      id: 1,
      nombre: 'Paracetamol 500mg',
      precio: 250,
      stock: 1000,
      categoria: 'Analgésicos',
    ),
    Product(
      id: 2,
      nombre: 'Ibuprofeno 600mg',
      precio: 350,
      stock: 800,
      categoria: 'Analgésicos',
    ),
    Product(
      id: 3,
      nombre: 'Amoxicilina 875mg',
      precio: 450,
      stock: 600,
      categoria: 'Antibióticos',
    ),
    Product(
      id: 4,
      nombre: 'Insulina Rápida',
      precio: 15000,
      stock: 200,
      categoria: 'Diabetes',
    ),
    Product(
      id: 5,
      nombre: 'Vacuna COVID-19',
      precio: 25000,
      stock: 150,
      categoria: 'Vacunas',
    ),
    Product(
      id: 6,
      nombre: 'Vitamina C',
      precio: 180,
      stock: 500,
      categoria: 'Vitaminas',
    ),
    Product(
      id: 7,
      nombre: 'Multivitamínico',
      precio: 320,
      stock: 400,
      categoria: 'Vitaminas',
    ),
    Product(
      id: 8,
      nombre: 'Glucómetro',
      precio: 45000,
      stock: 50,
      categoria: 'Diabetes',
    ),
    Product(
      id: 9,
      nombre: 'Insulina Rápida',
      precio: 15000,
      stock: 200,
      categoria: 'Diabetes',
    ),
    Product(
      id: 10,
      nombre: 'Vacuna COVID-19',
      precio: 25000,
      stock: 150,
      categoria: 'Vacunas',
    ),
    Product(
      id: 11,
      nombre: 'Vitamina C',
      precio: 180,
      stock: 500,
      categoria: 'Vitaminas',
    ),
    Product(
      id: 12,
      nombre: 'Multivitamínico',
      precio: 320,
      stock: 400,
      categoria: 'Vitaminas',
    ),
    Product(
      id: 13,
      nombre: 'Glucómetro',
      precio: 45000,
      stock: 50,
      categoria: 'Diabetes',
    ),
  ];

  final List<Order> _pedidos = [
    Order(
      id: 1,
      cliente: 'Farmacia Central',
      fecha: '2024-03-20',
      estado: 'Pendiente',
      items: [
        OrderItem(
          productoId: 1,
          nombre: 'Paracetamol 500mg',
          cantidad: 100,
          precio: 250,
        ),
        OrderItem(
          productoId: 2,
          nombre: 'Ibuprofeno 600mg',
          cantidad: 50,
          precio: 350,
        ),
      ],
      total: 42500,
      fechaCreacion: '2024-03-20',
    ),
    Order(
      id: 2,
      cliente: 'Hospital Nacional',
      fecha: '2024-03-19',
      estado: 'Procesando',
      items: [
        OrderItem(
          productoId: 3,
          nombre: 'Amoxicilina 875mg',
          cantidad: 200,
          precio: 450,
        ),
        OrderItem(
          productoId: 4,
          nombre: 'Insulina Rápida',
          cantidad: 10,
          precio: 15000,
        ),
      ],
      total: 240000,
      fechaCreacion: '2024-03-19',
    ),
    Order(
      id: 3,
      cliente: 'Droguería La Salud',
      fecha: '2024-03-18',
      estado: 'Enviado',
      items: [
        OrderItem(
          productoId: 4,
          nombre: 'Insulina Rápida',
          cantidad: 5,
          precio: 15000,
        ),
        OrderItem(
          productoId: 8,
          nombre: 'Glucómetro',
          cantidad: 2,
          precio: 45000,
        ),
      ],
      total: 165000,
      fechaCreacion: '2024-03-18',
    ),
  ];

  List<Order> get _pedidosFiltrados {
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

  int _calculateTotal() {
    int total = 0;
    _cantidades.forEach((prodId, cant) {
      final prod = _productos.firstWhere((p) => p.id == prodId);
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
    if (_clienteSel == null ||
        _clienteSel!.isEmpty ||
        _fechaCtrl.text.isEmpty ||
        _cantidades.isEmpty) {
      return;
    }
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 1));

    final items = _cantidades.entries.map((e) {
      final prod = _productos.firstWhere((p) => p.id == e.key);
      return OrderItem(
        productoId: prod.id,
        nombre: prod.nombre,
        cantidad: e.value,
        precio: prod.precio,
      );
    }).toList();

    setState(() {
      _pedidos.add(
        Order(
          id: _pedidos.length + 1,
          cliente: _clienteSel!,
          fecha: _fechaCtrl.text,
          estado: 'Pendiente',
          items: items,
          total: _calculateTotal(),
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
          subtitle: '${_pedidosFiltrados.length} pedidos',
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
                style: Theme.of(
                  context,
                ).textTheme.titleMedium?.copyWith(fontSize: 16),
              ),
              const SizedBox(height: 18),

              Row(
                spacing: 12,
                children: [
                  Expanded(child: Text('Cliente', style: Theme.of(context).textTheme.titleMedium)),
                  Expanded(child: Text('Fecha', style: Theme.of(context).textTheme.titleMedium))
                ],
              ),
              const SizedBox(height: 2),

              Row(
                spacing: 12,
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      isExpanded: true,
                      icon: const SizedBox.shrink(),
                      value: _clienteSel,
                      items: _clientes.map((c) => DropdownMenuItem(value: c, child: Text(c)),).toList(),
                      onChanged: (v) => setState(() => _clienteSel = v),
                      decoration: _baseInputDecoration().copyWith(
                        hintText: 'Seleccionar',
                        suffixIcon: Icon(AppIcons.chevronDown, size: 16),
                      ),
                      validator: (v) => (v == null || v.isEmpty) ? 'Selecciona un cliente' : null,
                    ),
                  ),

                  Expanded(
                    child: TextFormField(
                      controller: _fechaCtrl,
                      readOnly: true,
                      decoration: _baseInputDecoration().copyWith(
                        hintText: 'mm/dd/yyyy'
                      ),
                      onTap: _pickDate,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              Text('Productos', style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: 8),

              Container(
                constraints: const BoxConstraints(maxHeight: 400),
                decoration: AppStyles.decoration,
                child: ListView.separated(
                  shrinkWrap: true,
                  itemCount: _productos.length,
                  separatorBuilder: (_, __) => Container(),
                  itemBuilder: (context, i) {
                    final p = _productos[i];
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
                                    style: const TextStyle(
                                      fontSize: 14,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    '\$${p.precio.toString()} • Stock: ${p.stock}',
                                    style: const TextStyle(
                                      fontSize: 12,
                                      color: Colors.grey,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            SizedBox(
                              width: 70,
                              child: TextFormField(
                                initialValue: cantidad == 0
                                    ? ''
                                    : cantidad.toString(),
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
                                onChanged: (v) =>
                                    _setQuantity(p.id, int.tryParse(v) ?? 0),
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
                Card(
                  color: Colors.grey.shade100,
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Total del pedido:'),
                        Text(
                          '\$${_calculateTotal()}',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.green,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              const SizedBox(height: 8),
              ConfirmationButton(
                isLoading: _isLoading,
                onTap: _submit,
                idleLabel: 'Registrar Pedido',
                onTapLabel: 'Registrando...',
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHistory(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    final pedidos = _pedidosFiltrados;
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
                decoration: _baseInputDecoration().copyWith(
                  hintText: 'mm/dd/yyyy',
                ),
                onTap: _filterDate,
              ),
            ),

            Expanded(
              child: TextField(
                controller: _filtroClienteCtrl,
                decoration: _baseInputDecoration().copyWith(
                  hintText: 'Cliente...',
                  prefixIcon: Icon(AppIcons.search, size: 16)
                ),
                onChanged: (_) => setState(() {}),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        if (pedidos.isEmpty) ...[
          Container(
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
          ),
        ] else
          Expanded(
            child: ListView.separated(
              itemCount: pedidos.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, i) {
                final p = pedidos[i];
                return Container(
                  decoration: AppStyles.decoration,
                  child: Padding(
                    padding: const EdgeInsets.only(left: 16, top: 18, right: 16, bottom: 24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  p.cliente,
                                  style: textTheme.titleSmall?.copyWith(fontSize: 15),
                                ),
                                Text(
                                  '#${p.id}',
                                  style: textTheme.bodySmall?.copyWith(fontSize: 12),
                                ),
                              ],
                            ),
                            _orderStateBadge(p.estado),
                          ],
                        ),
                        const SizedBox(height: 8),

                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  AppIcons.calendar,
                                  size: 14,
                                  color: AppStyles.grey1,
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  p.fecha,
                                  style: textTheme.bodySmall?.copyWith(fontSize: 12.5, color: AppStyles.grey1),
                                ),
                              ],
                            ),

                            Row(
                              children: [
                                Icon(
                                  AppIcons.package,
                                  size: 14,
                                  color: AppStyles.grey1,
                                ),
                                const SizedBox(width: 4),
                                Text(
                                  '${p.items.length} productos',
                                  style: textTheme.bodySmall?.copyWith(fontSize: 12.5, color: AppStyles.grey1),
                                ),
                              ],
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),

                        ...p.items.map(
                          (it) => Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Expanded(
                                child: Text(
                                  it.nombre,
                                  style: textTheme.bodySmall?.copyWith(fontSize: 12, fontWeight: FontWeight.w500),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              Text(
                                '${it.cantidad} × \$${it.precio}',
                                style: textTheme.bodySmall?.copyWith(fontSize: 12),
                              ),
                            ],
                          ),
                        ),
                        const Divider(height: 16),

                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text('Total:', style: textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w700)),
                            Text(
                              // total price with comma separation
                              '\$${p.total.toString().replaceAllMapped(
                                RegExp(r'(\d+)(\d{3})'),
                                (Match m) => '${m[1]},${m[2]}',
                              )}',
                              style: textTheme.bodySmall?.copyWith(
                                fontWeight: FontWeight.w700,
                                color: AppStyles.green1,
                              ),
                            ),
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

  Widget _orderStateBadge(String estado) {
    final textTheme = Theme.of(context).textTheme;

    Color bg;
    Color fg = Colors.white;
    switch (estado) {
      case 'Pendiente':
        bg = Color(0xffeceef2);
        fg = Colors.black;
        break;
      case 'Procesando':
        bg = AppStyles.orange;
        break;
      case 'Enviado':
        bg = Colors.blue;
        break;
      case 'Entregado':
        bg = Colors.green;
        break;
      case 'Cancelado':
        bg = Colors.red;
        break;
      default:
        bg = Colors.black54;
        break;
    }
    return Container(
      padding: const EdgeInsets.only(left: 10, right: 10, top: 1, bottom: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(9),
      ),
      child: Text(
        estado,
        style: textTheme.bodySmall?.copyWith(
          color: fg,
          fontWeight: FontWeight.w600,
          fontSize: 12,
        ),
      ),
    );
  }

  InputDecoration _baseInputDecoration() {
    return InputDecoration(
      constraints: BoxConstraints.expand(height: 36),
      filled: true,
      fillColor: AppStyles.grey1.withAlpha(30),
      contentPadding: const EdgeInsets.symmetric(
        vertical: 12,
        horizontal: 12,
      ),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8.0),
        borderSide: BorderSide.none,
      ),
    );
  }
}
