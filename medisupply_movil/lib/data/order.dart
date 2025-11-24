import 'package:medisupply_movil/data/order_item.dart';

class Order {
  final int id;
  final String cliente;
  final int clienteId;
  final String fecha;
  final String estado; // Pendiente | Procesando | Enviado | Entregado | Cancelado
  final List<OrderItem> items;
  final double total;
  final String fechaCreacion;

  Order({required this.id, required this.cliente, required this.clienteId, required this.fecha, required this.estado, required this.items, required this.total, required this.fechaCreacion});

  @override
  String toString() {
    return 'Order{id: $id, cliente: $cliente, clienteId: $clienteId, fecha: $fecha, estado: $estado, items: $items, total: $total, fechaCreacion: $fechaCreacion}';
  }
}