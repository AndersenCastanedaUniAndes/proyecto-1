import 'package:medisupply_movil/data/order_item.dart';

class Order {
  final int id;
  final String cliente;
  final String fecha;
  final String estado; // Pendiente | Procesando | Enviado | Entregado | Cancelado
  final List<OrderItem> items;
  final int total;
  final String fechaCreacion;
  Order({required this.id, required this.cliente, required this.fecha, required this.estado, required this.items, required this.total, required this.fechaCreacion});
}