import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';

class _Pedido {
  final int id;
  final String fecha;
  final String estado; // pendiente | procesando | enviado | entregado
  final List<String> productos;
  final int valor;
  _Pedido({required this.id, required this.fecha, required this.estado, required this.productos, required this.valor});
}

class _Cliente {
  final int id;
  final String nombre;
  final String direccion;
  final String telefono;
  final String correo;
  final int pedidosPendientes;
  final String ultimaVisita; // ISO string
  final int valorTotal;
  final List<_Pedido> pedidos;
  _Cliente({
    required this.id,
    required this.nombre,
    required this.direccion,
    required this.telefono,
    required this.correo,
    required this.pedidosPendientes,
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

  late final List<_Cliente> _clientes = [
    _Cliente(
      id: 1,
      nombre: 'Farmacia Central',
      direccion: 'Av. Principal 123, Centro',
      telefono: '+57 1 234-5678',
      correo: 'contacto@farmaciacentral.com',
      pedidosPendientes: 3,
      ultimaVisita: '2024-03-15',
      valorTotal: 850000,
      pedidos: [
        _Pedido(id: 101, fecha: '2024-03-20', estado: 'pendiente', productos: ['Paracetamol 500mg', 'Ibuprofeno 600mg'], valor: 250000),
        _Pedido(id: 102, fecha: '2024-03-18', estado: 'procesando', productos: ['Amoxicilina 875mg'], valor: 180000),
      ],
    ),
    _Cliente(
      id: 2,
      nombre: 'Droguería La Salud',
      direccion: 'Calle 85 #15-20, Zona Norte',
      telefono: '+57 1 345-6789',
      correo: 'ventas@lasalud.com',
      pedidosPendientes: 1,
      ultimaVisita: '2024-03-18',
      valorTotal: 420000,
      pedidos: [
        _Pedido(id: 201, fecha: '2024-03-19', estado: 'pendiente', productos: ['Insulina Rápida', 'Glucómetro'], valor: 420000),
      ],
    ),
    _Cliente(
      id: 3,
      nombre: 'Hospital Nacional',
      direccion: 'Carrera 30 #45-67, Sur',
      telefono: '+57 1 456-7890',
      correo: 'compras@hospitalnacional.gov.co',
      pedidosPendientes: 5,
      ultimaVisita: '2024-03-10',
      valorTotal: 1250000,
      pedidos: [
        _Pedido(id: 301, fecha: '2024-03-21', estado: 'pendiente', productos: ['Antibióticos varios', 'Material quirúrgico'], valor: 750000),
        _Pedido(id: 302, fecha: '2024-03-20', estado: 'pendiente', productos: ['Vacunas', 'Jeringas'], valor: 500000),
      ],
    ),
    _Cliente(
      id: 4,
      nombre: 'Red Farmacias Unidos',
      direccion: 'Av. Caracas #78-45, Occidente',
      telefono: '+57 1 567-8901',
      correo: 'pedidos@unidos.com',
      pedidosPendientes: 2,
      ultimaVisita: '2024-03-17',
      valorTotal: 320000,
      pedidos: [
        _Pedido(id: 401, fecha: '2024-03-19', estado: 'pendiente', productos: ['Analgésicos', 'Antigripales'], valor: 180000),
        _Pedido(id: 402, fecha: '2024-03-17', estado: 'pendiente', productos: ['Vitaminas', 'Suplementos'], valor: 140000),
      ],
    ),
  ];

  List<_Cliente> get _filtrados {
    final q = _filtro.trim().toLowerCase();
    if (q.isEmpty) return _clientes;
    return _clientes
        .where((c) => c.nombre.toLowerCase().contains(q) || c.direccion.toLowerCase().contains(q))
        .toList();
  }

  String _getPendingOrders() {
    return '11';
  }

  String _getTotalValue() {
    return '\$1250000';
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    if (_seleccionado != null) {
      final c = _seleccionado!;
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              IconButton(onPressed: () => setState(() => _seleccionado = null), icon: const Icon(Icons.arrow_back)),
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(c.nombre, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                const SizedBox(height: 2),
                const Text('Información detallada del cliente', style: TextStyle(fontSize: 12, color: Colors.grey)),
              ])
            ],
          ),
          const SizedBox(height: 8),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                children: [
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Información de Contacto', style: Theme.of(context).textTheme.titleSmall),
                          const SizedBox(height: 8),
                          _iconRow(Icons.location_on_outlined, c.direccion),
                          _iconRow(Icons.phone_outlined, c.telefono),
                          _iconRow(Icons.mail_outline, c.correo, isEmail: true),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Row(children: [
                    Expanded(child: _CardStat(color: Colors.orange, value: c.pedidosPendientes.toString(), caption: 'Pedidos Pendientes')),
                    const SizedBox(width: 12),
                    Expanded(child: _CardStat(color: Colors.green, value: '${c.valorTotal}', caption: 'Valor Total')),
                  ]),
                  const SizedBox(height: 8),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                        Text('Pedidos Recientes', style: Theme.of(context).textTheme.titleSmall),
                        const SizedBox(height: 8),
                        ...c.pedidos.map((p) => _pedidoTile(p)).toList(),
                      ]),
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
        Row(
          children: [
            IconButton(onPressed: widget.onBack, icon: Icon(AppIcons.arrowLeft)),
            Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('Mis Clientes', style: textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w600)),
              Text('${_filtrados.length} clientes', style: textTheme.bodySmall),
            ])
          ],
        ),
        const SizedBox(height: 28),

        AppInputField(
          label: 'Buscar por nombre o dirección...',
          prefixIconData: AppIcons.search,
          onChanged: (v) => setState(() => _filtro = v),
        ),
        const SizedBox(height: 12),

        QuickStats(
          stat1Color: AppStyles.blue1,
          stat1Title: 'Pedidos Pendientes',
          stat1Value: _getPendingOrders(),
          stat2Color: AppStyles.green1,
          stat2Title: 'Valor Total',
          stat2Value: _getTotalValue(),
        ),
        const SizedBox(height: 12),

        if (_filtrados.isEmpty)
          NotFoundSection(
            iconData: AppIcons.package,
            label: 'No se encontraron clientes',
          )
        else
          Expanded(
            child: ListView.separated(
              itemCount: _filtrados.length,
              separatorBuilder: (_, __) => const SizedBox(height: 8),
              itemBuilder: (context, i) {
                final c = _filtrados[i];
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
                                  if (c.pedidosPendientes > 0)
                                    _Badge(
                                      label: '${c.pedidosPendientes} pendientes',
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
                                  Text('\$${c.valorTotal}', style: textTheme.labelMedium?.copyWith(fontSize: 12, color: AppStyles.green1)),
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
  }

  Widget _iconRow(IconData icon, String text, {bool isEmail = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        children: [
          Icon(icon, size: 18, color: Colors.grey[600]),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: TextStyle(fontSize: 13, color: isEmail ? Colors.blue : Colors.black87),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _pedidoTile(_Pedido p) {
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
            _estadoBadge(p.estado),
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

  Widget _estadoBadge(String estado) {
    Color bg;
    Color fg = Colors.white;
    switch (estado) {
      case 'pendiente':
        bg = Colors.grey; fg = Colors.white; break;
      case 'procesando':
        bg = Colors.orange; break;
      case 'enviado':
        bg = Colors.blue; break;
      case 'entregado':
        bg = Colors.green; break;
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