import 'package:flutter/material.dart';
import 'package:medisupply_movil/data/data.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/utils/utils.dart';

class OrderDetailsCard extends StatelessWidget {
  const OrderDetailsCard({
    super.key,
    required this.order,
  });

  final Order order;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

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
                      order.cliente,
                      style: textTheme.titleSmall?.copyWith(fontSize: 15),
                    ),
                    Text(
                      '#${order.id}',
                      style: textTheme.bodySmall?.copyWith(fontSize: 12),
                    ),
                  ],
                ),
                _orderStateBadge(order.estado, textTheme),
              ],
            ),
            const SizedBox(height: 8),

            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(AppIcons.calendar, size: 14, color: AppStyles.grey1),
                    const SizedBox(width: 4),

                    Text(
                      order.fecha,
                      style: textTheme.bodySmall?.copyWith(fontSize: 12.5, color: AppStyles.grey1),
                    ),
                  ],
                ),

                Row(
                  children: [
                    Icon(AppIcons.package, size: 14, color: AppStyles.grey1),
                    const SizedBox(width: 4),

                    Text(
                      '${order.items.length} productos',
                      style: textTheme.bodySmall?.copyWith(fontSize: 12.5, color: AppStyles.grey1),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 8),

            Text('Productos:', style: textTheme.bodySmall?.copyWith(fontSize: 12, fontWeight: FontWeight.w700)),
            const SizedBox(height: 6),

            ...order.items.map((it) => Column(
              children: [
                Container(
                  decoration: AppStyles.decoration.copyWith(
                    color: AppStyles.grey2.withAlpha(150),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: AppStyles.grey2.withAlpha(150), width: 0)
                  ),
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  child: Row(
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
                          '${it.cantidad} unidades',
                          style: textTheme.bodySmall?.copyWith(fontSize: 12),
                        ),
                      ],
                    ),
                ),
                const SizedBox(height: 4),
              ],
            ),
            ),
            const SizedBox(height: 12),

            // Esperando programacion de entregas,
            // Contenedor con texto "Esperando programación de entregas..."
            if (order.estado == 'Pendiente')
              Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: Color(0xffeff6ff),
                  borderRadius: BorderRadius.circular(8),
                ),
                padding: const EdgeInsets.all(12),
                child: Text(
                  'Esperando programación de la entrega',
                  style: textTheme.bodySmall?.copyWith(
                    fontSize: 13,
                    color: AppStyles.blue1,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),

          ],
        ),
      ),
    );
  }

  Widget _orderStateBadge(String estado, TextTheme textTheme) {
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
}