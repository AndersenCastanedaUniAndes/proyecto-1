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

  final List<Product> _productos = [
    Product(id: 1, nombre: 'Paracetamol 500mg', precio: 250, stock: 1000, categoria: 'Analgésicos'),
    Product(id: 2, nombre: 'Ibuprofeno 600mg', precio: 350, stock: 800, categoria: 'Analgésicos'),
    Product(id: 3, nombre: 'Amoxicilina 875mg', precio: 450, stock: 600, categoria: 'Antibióticos'),
    Product(id: 4, nombre: 'Insulina Rápida', precio: 15000, stock: 200, categoria: 'Diabetes'),
    Product(id: 5, nombre: 'Vacuna COVID-19', precio: 25000, stock: 150, categoria: 'Vacunas'),
    Product(id: 6, nombre: 'Vitamina C', precio: 180, stock: 500, categoria: 'Vitaminas'),
    Product(id: 7, nombre: 'Multivitamínico', precio: 320, stock: 400, categoria: 'Vitaminas'),
    Product(id: 8, nombre: 'Glucómetro', precio: 45000, stock: 50, categoria: 'Diabetes'),
    Product(id: 9, nombre: 'Insulina Rápida', precio: 15000, stock: 200, categoria: 'Diabetes'),
    Product(id: 10, nombre: 'Vacuna COVID-19', precio: 25000, stock: 150, categoria: 'Vacunas'),
    Product(id: 11, nombre: 'Vitamina C', precio: 180, stock: 500, categoria: 'Vitaminas'),
    Product(id: 12, nombre: 'Multivitamínico', precio: 320, stock: 400, categoria: 'Vitaminas'),
    Product(id: 13, nombre: 'Glucómetro', precio: 45000, stock: 50, categoria: 'Diabetes'),
  ];

  final List<Order> _pedidos = [
    Order(
      id: 1,
      cliente: 'Farmacia Central',
      fecha: '2024-03-20',
      estado: 'pendiente',
      items: [
        OrderItem(productoId: 1, nombre: 'Paracetamol 500mg', cantidad: 100, precio: 250),
        OrderItem(productoId: 2, nombre: 'Ibuprofeno 600mg', cantidad: 50, precio: 350),
      ],
      total: 42500,
      fechaCreacion: '2024-03-20',
    ),
    Order(
      id: 2,
      cliente: 'Hospital Nacional',
      fecha: '2024-03-19',
      estado: 'procesando',
      items: [
        OrderItem(productoId: 3, nombre: 'Amoxicilina 875mg', cantidad: 200, precio: 450),
        OrderItem(productoId: 4, nombre: 'Insulina Rápida', cantidad: 10, precio: 15000),
      ],
      total: 240000,
      fechaCreacion: '2024-03-19',
    ),
    Order(
      id: 3,
      cliente: 'Droguería La Salud',
      fecha: '2024-03-18',
      estado: 'enviado',
      items: [
        OrderItem(productoId: 4, nombre: 'Insulina Rápida', cantidad: 5, precio: 15000),
        OrderItem(productoId: 8, nombre: 'Glucómetro', cantidad: 2, precio: 45000),
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
      return OrderItem(productoId: prod.id, nombre: prod.nombre, cantidad: e.value, precio: prod.precio);
    }).toList();

    setState(() {
      _pedidos.add(
        Order(
          id: _pedidos.length + 1,
          cliente: _clienteSel!,
          fecha: _fechaCtrl.text,
          estado: 'pendiente',
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

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

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
                    Text("Nuevo", style: textTheme.labelMedium?.copyWith(fontSize: 13)),
                  ],
                ),
              ),
              Tab(
                iconMargin: EdgeInsets.only(bottom: 2),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  spacing: 8,
                  children: [
                    Icon(AppIcons.shoppingCart, size: 16, color: Colors.black,),
                    Text("Historial", style: textTheme.labelMedium),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),

        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildNuevo(context),
              _buildHistory(context),
            ],
          ),
        )
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
              Text('Nuevo Pedido', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontSize: 16)),
              const SizedBox(height: 18),

              Row(
                spacing: 12,
                children: [
                  Expanded(
                    child: Text('Cliente', style: Theme.of(context).textTheme.labelLarge?.copyWith(fontSize: 15, fontWeight: FontWeight.w600)),
                  ),
                  Expanded(
                    child: Text('Fecha', style: Theme.of(context).textTheme.labelLarge?.copyWith(fontSize: 15, fontWeight: FontWeight.w600)),
                  ),
                ],
              ),
              const SizedBox(height: 6),

              SizedBox(
                height: 36,
                child: Row(
                  spacing: 12,
                  children: [
                    Expanded(
                      child: DropdownButtonFormField<String>(
                        value: _clienteSel,
                        items: _clientes.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                        onChanged: (v) => setState(() => _clienteSel = v),
                        decoration: InputDecoration(

                          filled: true,
                          fillColor: AppStyles.grey1.withAlpha(30),
                          contentPadding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
                          hintText: 'Seleccionar',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8.0),
                            borderSide: BorderSide.none,
                          ),
                        ),
                        validator: (v) => (v == null || v.isEmpty) ? 'Selecciona un cliente' : null,
                      ),
                    ),
                    Expanded(
                      child: TextFormField(
                        controller: _fechaCtrl,
                        readOnly: true,
                        decoration: InputDecoration(
                          hintText: 'mm/dd/yyyy',
                          contentPadding: EdgeInsets.only(left: 12),
                          filled: true,
                          fillColor: AppStyles.grey1.withAlpha(30),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8.0),
                            borderSide: BorderSide.none,
                          ),
                        ),
                        onTap: _pickDate,
                      ),
                    ),
                  ],
                ),
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
                      padding: EdgeInsets.only(left: 12, right: 12, bottom: 8, top: i == 0 ? 12 : 0),
                      child: Container(
                        decoration: AppStyles.decoration.copyWith(borderRadius: BorderRadius.all(Radius.circular(4))),
                        padding: const EdgeInsets.all(8),
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
                Card(
                  color: Colors.grey.shade100,
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Total del pedido:'),
                        Text('\$${_calculateTotal()}', style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
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

  Widget _buildHistory(BuildContext context) {
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
                                _orderStateBadge(p.estado),
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

  Widget _orderStateBadge(String estado) {
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