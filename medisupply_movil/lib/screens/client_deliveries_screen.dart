import 'package:flutter/material.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/data/data.dart';
import 'package:medisupply_movil/utils/utils.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:provider/provider.dart';

class ClientDeliveriesScreen extends StatefulWidget {
  final VoidCallback onBack;
  const ClientDeliveriesScreen({super.key, required this.onBack});

  @override
  State<ClientDeliveriesScreen> createState() => _ClientDeliveriesScreenState();
}

class _ClientDeliveriesScreenState extends State<ClientDeliveriesScreen> {
  bool _isLoadingHistory = false;

  // Filtros
  final _filtroFechaCtrl = TextEditingController(); // filtra por fecha del pedido
  final _filtroEstadoCtrl = TextEditingController(); // filtra por estado de entrega

  late List<Order> _orders = [];

  List<Order> get _filteredOrders {
    final fFecha = _filtroFechaCtrl.text.trim();
    final fEstado = _filtroEstadoCtrl.text.trim().toLowerCase();
    return _orders.where((p) {
      final okFecha = fFecha.isEmpty || p.fecha.contains(fFecha);
      final okEstado = fEstado.isEmpty || p.estado.toLowerCase().contains(fEstado);
      return okFecha && okEstado;
    }).toList();
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
  void initState() {
    super.initState();
    _loadHistory();
  }

  @override
  void dispose() {
    _filtroFechaCtrl.dispose();
    _filtroEstadoCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final orders = _filteredOrders;

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

        // Filters Labels
        Row(
          spacing: 12,
          children: [
            Expanded(child: Text('Filtrar por fecha', style: textTheme.titleSmall?.copyWith(fontSize: 13))),
            Expanded(child: Text('Filtrar por cliente', style: textTheme.titleSmall?.copyWith(fontSize: 13)))
          ],
        ),
        const SizedBox(height: 2),

        // Date and Status Filters
        Row(
          spacing: 12,
          children: [
            Expanded(
              child: TextField(
                controller: _filtroFechaCtrl,
                decoration: baseInputDecoration().copyWith(
                  hintText: 'mm/dd/yyyy',
                  suffixIcon: Icon(AppIcons.calendar, size: 14, color: Colors.white),
                ),
                onChanged: (_) => setState(() {}),
              ),
            ),
            Expanded(
              child: TextField(
                controller: _filtroEstadoCtrl,
                decoration: baseInputDecoration().copyWith(
                  hintText: 'Cliente...',
                  prefixIcon: Icon(AppIcons.search, size: 14),
                ),
                onChanged: (_) => setState(() {}),
              ),
            ),
          ]
        ),
        const SizedBox(height: 12),

        orders.isEmpty ? Container(
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
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, i) {
              final order = orders[i];
              return OrderDetailsCard(order: order);
            },
          ),
        ),
      ],
    );
  }
}