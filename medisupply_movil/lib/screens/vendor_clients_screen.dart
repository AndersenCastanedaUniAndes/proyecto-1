import 'package:flutter/material.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/data/data.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'dart:convert';
import 'package:medisupply_movil/utils/utils.dart';
import 'package:medisupply_movil/utils/requests.dart';
import 'package:provider/provider.dart';

class _Pedido {
  final int id;
  final String fecha;
  final String estado; // Pendiente | Procesando | Enviado | Entregado
  final List<String> productos;
  final double valor;
  _Pedido({required this.id, required this.fecha, required this.estado, required this.productos, required this.valor});

  @override
  String toString() {
    return 'Pedido{id: $id, fecha: $fecha, estado: $estado, productos: $productos, valor: $valor}';
  }
}

class _Cliente {
  final int id;
  final String nombre;
  final String direccion;
  final String telefono;
  final String correo;
  final String ultimaVisita; // ISO string
  final double valorTotal;
  final List<_Pedido> pedidos;
  _Cliente({
    required this.id,
    required this.nombre,
    required this.direccion,
    required this.telefono,
    required this.correo,
    required this.ultimaVisita,
    required this.valorTotal,
    required this.pedidos,
  });
}

class VendorClientsScreen extends StatefulWidget {
  final VoidCallback onBack;
  const VendorClientsScreen({super.key, required this.onBack});

  @override
  State<VendorClientsScreen> createState() => _VendorClientsScreenState();
}

class _VendorClientsScreenState extends State<VendorClientsScreen> {
  String _filtro = '';
  _Cliente? _seleccionado;
  late Future<List<_Cliente>> _futureClientes;
  late Future<List<dynamic>> futureOrders;

  @override
  void initState() {
    super.initState();
    _futureClientes = _fetchClientes();
  }

  Future<List<_Cliente>> _fetchClientes() async {
    final state = context.read<AppState>();

    final response = await Future.wait([
      getClients(state.id, state.token),
      getVendorOrders(state.id, state.token),
    ]);

    final clients = response[0];
    final orders = response[1] as List<Order>;

    return clients.map<_Cliente>((raw) {
      final json = raw as Map<String, dynamic>;

      final pedidos = <_Pedido>[];
      for (var order in orders) {
        if (order.clienteId == json['id']) {
          pedidos.add(_Pedido(
            id: order.id,
            fecha: order.fecha,
            estado: order.estado,
            productos: order.items.map((p) => p.nombre).toList(),
            valor: order.total,
          ));
        }
      }

      return _Cliente(
        id: json['id'] as int,
        nombre: json['empresa'] as String,
        direccion: (json['direccion'] ?? '') as String,
        telefono: (json['telefono'] ?? '') as String,
        correo: (json['email'] ?? '') as String,
        ultimaVisita: (json['ultima visita'] ?? '') as String,
        valorTotal: pedidos.fold<double>(0, (acc, p) => acc + p.valor),
        pedidos: pedidos,
      );
    }).toList();
  }

  List<_Cliente> _filtrar(List<_Cliente> clientes) {
    final q = _filtro.trim().toLowerCase();
    if (q.isEmpty) return clientes;
    return clientes
        .where((c) => c.nombre.toLowerCase().contains(q) || c.direccion.toLowerCase().contains(q))
        .toList();
  }

  String _getPendingOrders(List<_Cliente> clientes) {
    final total = clientes.fold<int>(0, (acc, c) => acc + c.pedidos.where((p) => p.estado == 'Pendiente').length);
    return total.toString();
  }

  String _getTotalValue(List<_Cliente> clientes) {
    final total = clientes.fold<double>(0, (acc, c) => acc + c.valorTotal);
    return '\$$total';
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    context.watch<AppState>();

    return FutureBuilder(
      future: _futureClientes,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(
            child: Text(
              'Error cargando clientes: ${snapshot.error}',
              style: textTheme.bodyMedium?.copyWith(color: Colors.red),
            ),
          );
        }

        final clientes = snapshot.data ?? [];
        final filtrados = _filtrar(clientes);

        if (_seleccionado != null) {
          final c = _seleccionado!;
          final pedidosPendientes = c.pedidos.where((p) => p.estado == 'Pendiente').length;

          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              ScreenTitleAndBackNavigation(
                title: c.nombre,
                subtitle: 'Información detallada del cliente',
                textTheme: textTheme,
                onBack: () => setState(() => _seleccionado = null),
              ),
              const SizedBox(height: 20),

              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    spacing: 4,
                    children: [
                      Container(
                        decoration: AppStyles.decoration,
                        child: Padding(
                          padding: const EdgeInsets.symmetric(vertical: 22, horizontal: 20),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Información de Contacto', style: textTheme.labelLarge),
                              const SizedBox(height: 20),
                              _iconRow(AppIcons.pin, c.direccion),
                              _iconRow(AppIcons.phone, c.telefono),
                              _iconRow(AppIcons.mail, c.correo),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),

                      QuickStats(
                        stat1Color: AppStyles.orange,
                        stat1Title: 'Pedidos Pendientes',
                        stat1Value: pedidosPendientes.toString(),
                        stat2Color: AppStyles.green1,
                        stat2Title: 'Valor Total',
                        stat2Value: '\$${c.valorTotal}',
                      ),
                      const SizedBox(height: 8),

                      Container(
                        decoration: AppStyles.decoration,
                        child: Padding(
                          padding: const EdgeInsets.all(22),
                          child: Column(
                            spacing: 4,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Pedidos Recientes', style: textTheme.titleSmall),
                              const SizedBox(height: 18),
                              if (c.pedidos.isEmpty) ...[
                                Text('Este cliente no ha realizado pedidos aún.', style: textTheme.bodySmall)
                              ]
                              else ...c.pedidos.map((p) => _pedidoTile(p)),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              )
            ],
          );
        }

        // Vista de lista
        return Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ScreenTitleAndBackNavigation(
              title: 'Mis Clientes',
              subtitle: '${filtrados.length} clientes',
              textTheme: textTheme,
              onBack: widget.onBack,
            ),
            const SizedBox(height: 18),

            AppInputField(
              label: 'Buscar por nombre o dirección...',
              prefixIconData: AppIcons.search,
              onChanged: (v) => setState(() => _filtro = v),
            ),
            const SizedBox(height: 12),

            QuickStats(
              stat1Color: AppStyles.blue1,
              stat1Title: 'Pedidos Pendientes',
              stat1Value: _getPendingOrders(clientes),
              stat2Color: AppStyles.green1,
              stat2Title: 'Valor Total',
              stat2Value: _getTotalValue(clientes),
            ),
            const SizedBox(height: 12),

            if (filtrados.isEmpty)
              NotFoundSection(
                iconData: AppIcons.package,
                label: 'No se encontraron clientes',
              )
            else
              Expanded(
                child: ListView.separated(
                  itemCount: filtrados.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, i) {
                    final c = filtrados[i];
                    final pedidosPendientes = c.pedidos.where((p) => p.estado == 'Pendiente').length;

                    return GestureDetector(
                      onTap: () => setState(() => _seleccionado = c),
                      child: Container(
                        decoration: AppStyles.decoration,
                        padding: const EdgeInsets.all(12.0),
                        child: Row(
                          children: [
                            Expanded(
                              child: Column(
                                spacing: 6,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text(c.nombre, style: textTheme.titleSmall),
                                      if (pedidosPendientes > 0)
                                        _Badge(
                                          label: '$pedidosPendientes pendientes',
                                          color: AppStyles.red2,
                                          textStyle: textTheme.bodySmall?.copyWith(fontSize: 12, fontWeight: FontWeight.w500, color: Colors.white),
                                        ),
                                    ],
                                  ),
                                  Row(
                                    spacing: 4,
                                    children: [
                                      Icon(AppIcons.pin, size: 14, color: AppStyles.grey1),
                                      Text(c.direccion, style: textTheme.labelMedium?.copyWith(color: AppStyles.grey1, fontWeight: FontWeight.w400)),
                                    ],
                                  ),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Text('Última visita: ${c.ultimaVisita}', style: textTheme.labelMedium?.copyWith(color: AppStyles.grey1, fontWeight: FontWeight.w400)),

                                      if (pedidosPendientes > 0) ...[
                                        Text('\$${c.valorTotal}', style: textTheme.labelMedium?.copyWith(fontSize: 12, color: AppStyles.green1)),
                                      ]
                                    ],
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 12),
                            Icon(AppIcons.chevronRight, size: 18,),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
          ],
        );
      },
    );
  }

  Widget _iconRow(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Icon(icon, size: 18, color: Colors.grey[600]),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: TextStyle(fontSize: 13, color: Colors.black87),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  (Color background, Color foreground) _estadoBadge(String estado) {
    Color backgroundColor;
    Color foregroundColor = Colors.white;
    switch (estado) {
      case 'Pendiente':
        backgroundColor = AppStyles.grey2;
        foregroundColor = Colors.black;
        break;
      case 'Procesando':
        backgroundColor = AppStyles.orange;
        break;
      case 'Enviado':
        backgroundColor = AppStyles.blue1;
        break;
      case 'Entregado':
        backgroundColor = AppStyles.green1;
        break;
      default:
        backgroundColor = Colors.black54;
        break;
    }

    return (backgroundColor, foregroundColor);
  }

  Widget _pedidoTile(_Pedido p) {
    final textTheme = Theme.of(context).textTheme;

    final estadoBadge = _estadoBadge(p.estado);

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Pedido #${p.id}', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
            Tag(
              title: p.estado,
              textTheme: textTheme.labelMedium!,
              backgroundColor: estadoBadge.$1,
              foregroundColor: estadoBadge.$2,
            ),
          ],
        ),
        const SizedBox(height: 4),

        Text(p.fecha, style: const TextStyle(fontSize: 11, color: Colors.grey)),
        const SizedBox(height: 4),

        Text(p.productos.join(', '), style: const TextStyle(fontSize: 12, color: Colors.grey)),
        const SizedBox(height: 6),

        Text('\$${p.valor}', style: const TextStyle(fontSize: 12, color: Colors.green)),
      ]),
    );
  }
}

class _Badge extends StatelessWidget {
  const _Badge({
    required this.label,
    required this.color,
    this.textStyle
  });

  final String label;
  final Color color;
  final TextStyle? textStyle;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.only(left: 10, right: 10, top: 0, bottom: 4),
      decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(8)),
      child: Text(label, style: textStyle),
    );
  }
}

class _CardStat extends StatelessWidget {
  final Color color;
  final String value;
  final String caption;
  const _CardStat({required this.color, required this.value, required this.caption});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Color(0x2A000000), width: 1)
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: color)),
            Text(caption, style: const TextStyle(fontSize: 12, color: Colors.black54)),
            const SizedBox(height: 4),
          ],
        ),
      ),
    );
  }
}