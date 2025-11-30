import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:provider/provider.dart';
import 'package:medisupply_movil/utils/utils.dart';
import 'package:medisupply_movil/data/data.dart';
import '../state/app_state.dart';

class ClientHomeScreen extends StatefulWidget {
  final VoidCallback onOpenMenu;
  final void Function(ClientView) onTapCard;
  const ClientHomeScreen({
    super.key,
    required this.onOpenMenu,
    required this.onTapCard
  });

  @override
  State<ClientHomeScreen> createState() => _ClientHomeScreenState();
}

class _ClientHomeScreenState extends State<ClientHomeScreen> {
  late Future<List<Order>> futureOrders;

  String _getMonthOrdersCost(List<Order> orders) {
    final filteredOrders = orders.where((order) {
      final orderDate = DateTime.parse(order.fecha);
      final now = DateTime.now();
      return orderDate.month == now.month && orderDate.year == now.year;
    }).toList();

    final totalCost = filteredOrders.fold<double>(0, (previousValue, order) => previousValue + order.total);
    final formattedCost = toMoneyFormat(totalCost);

    return '\$$formattedCost';
  }

  String _getMonthOrdersCount(List<Order> orders) {
    final filteredOrders = orders.where((order) {
      final orderDate = DateTime.parse(order.fechaCreacion);
      final now = DateTime.now();
      return orderDate.month == now.month && orderDate.year == now.year;
    }).toList();

    final count = filteredOrders.length.toString();
    return count;
  }

  String _getPendingOrders(List<Order> orders) {
    final filteredOrders = orders.where((order) => order.estado == 'Pendiente').toList();
    final count = filteredOrders.length.toString();
    return count;
  }

  String _getUpcomingDeliveries(List<Order> orders) {
    final now = DateTime.now();
    final filteredOrders = orders.where((order) {
      if (order.estado != 'Enviado') return false;
      final deliveryDate = DateTime.parse(order.fecha);
      return deliveryDate.isAfter(now) && deliveryDate.isBefore(now.add(const Duration(days: 7)));
    }).toList();

    final count = filteredOrders.length.toString();
    return count;
  }

  @override
  void initState() {
    super.initState();

    var state = context.read<AppState>();
    futureOrders = getClientOrders(state.id, state.token);
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Home Card
          FutureBuilder(
            future: futureOrders,
            builder: (context, snapshot) {
              String monthSpent = '...';
              String monthOrders = '...';

              if (snapshot.connectionState == ConnectionState.active) {
                monthSpent = '...';
              } else if (snapshot.hasError) {
                monthSpent = '-';
              } else if (snapshot.hasData) {
                final orders = snapshot.data!;
                monthSpent = _getMonthOrdersCost(orders);
                monthOrders = _getMonthOrdersCount(orders);
              }

              return HomeCard(
                gradient: LinearGradient(colors: [AppStyles.green1, AppStyles.green2]),
                title: '¡Hola, ${state.userName}!',
                subtitle: 'Cliente MediSupply',
                onTap: widget.onOpenMenu,
                stat1Title: 'Total este mes',
                stat1Value: monthSpent,
                stat2Title: 'Pedidos realizados',
                stat2Value: monthOrders,
              );
            }
          ),
          const SizedBox(height: 16),

          // Quick Stats
          FutureBuilder(
            future: futureOrders,
            builder: (context, asyncSnapshot) {
              String pendingOrders = '...';
              String upcomingDeliveries = '...';

              if (asyncSnapshot.connectionState == ConnectionState.active) {
                pendingOrders = '...';
                upcomingDeliveries = '...';
              } else if (asyncSnapshot.hasError) {
                pendingOrders = '-';
                upcomingDeliveries = '-';
              } else if (asyncSnapshot.hasData) {
                final orders = asyncSnapshot.data!;
                pendingOrders = _getPendingOrders(orders);
                upcomingDeliveries = _getUpcomingDeliveries(orders);
              }

              return QuickStats(
                stat1Color: AppStyles.blue1,
                stat1Title: 'Pedidos Pendientes',
                stat1Value: pendingOrders,
                stat2Color: AppStyles.green1,
                stat2Title: 'Entregas Próximas',
                stat2Value: upcomingDeliveries,
              );
            }
          ),
          const SizedBox(height: 16),

          Container(
            decoration: AppStyles.decoration,
            child: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Actividad Reciente', style: Theme.of(context).textTheme.bodyMedium),
                  const SizedBox(height: 38),

                  FutureBuilder(
                    future: futureOrders,
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.active || snapshot.connectionState == ConnectionState.waiting) {
                        return const Loading();
                      } else if (snapshot.hasError) {
                        return Text('Error: ${snapshot.error}');
                      }

                      final orders = snapshot.data!;

                      final filteredOrders = orders.where((order) {
                        final orderDate = DateTime.parse(order.fecha);
                        final now = DateTime.now();
                        return orderDate.month == now.month && orderDate.year == now.year;
                      }).toList();

                      if (filteredOrders.isEmpty) {
                        return const Text('No hay actividad reciente.');
                      }

                      // list the 3 most recent orders
                      final recentOrders = filteredOrders.take(3).toList();
                      return Column(
                        children: recentOrders.map((order) {
                          final orderDate = DateTime.parse(order.fecha);
                          final formattedDate = '${orderDate.day}/${orderDate.month}/${orderDate.year}';

                          return Padding(
                            padding: const EdgeInsets.only(bottom: 12.0),
                            child: _activityRow(
                              context,
                              bg: AppStyles.blue1.withAlpha(50),
                              icon: AppIcons.shoppingCart,
                              iconColor: AppStyles.blue1,
                              title: 'Pedido #${order.id}',
                              subtitle: 'Fecha: $formattedDate',
                              badgeText: order.estado,
                              badgeColor: AppStyles.grey2,
                              badgeTextColor: Colors.black,
                            ),
                          );
                        }).toList(),
                      );
                    },
                  )
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Menu Cards
          FutureBuilder(
            future: futureOrders,
            builder: (context, asyncSnapshot) {
              String pendingOrders = '...';
              String upcomingDeliveries = '...';

              if (asyncSnapshot.connectionState == ConnectionState.active) {
                pendingOrders = '...';
                upcomingDeliveries = '...';
              } else if (asyncSnapshot.hasError) {
                pendingOrders = '-';
                upcomingDeliveries = '-';
              } else if (asyncSnapshot.hasData) {
                final orders = asyncSnapshot.data!;
                pendingOrders = _getPendingOrders(orders);
                upcomingDeliveries = _getUpcomingDeliveries(orders);
              }

              return LayoutBuilder(
                builder: (context, constraints) {
                  const itemWidth = 190.0;
                  final crossAxisCount = (constraints.maxWidth / itemWidth).floor().clamp(1, 4);

                  return GridView.count(
                    shrinkWrap: true,
                    crossAxisCount: crossAxisCount,
                    childAspectRatio: 1,
                    mainAxisSpacing: 12,
                    crossAxisSpacing: 12,
                    children: [
                      MenuCard(
                        color: AppStyles.menuCardBlue,
                        icon: AppIcons.shoppingCart,
                        title: 'Pedidos',
                        description: 'Crear y gestionar tus pedidos',
                        badge: '$pendingOrders pendientes',
                        onTap: () => widget.onTapCard(ClientView.pedidos),
                      ),
                      MenuCard(
                        color: AppStyles.menuCardGreen,
                        icon: AppIcons.shipping,
                        title: 'Entregas',
                        description: 'Consultar entregas programadas',
                        badge: '$upcomingDeliveries próximas',
                        onTap: () => widget.onTapCard(ClientView.entregas),
                      ),
                    ],
                  );
                },
              );
            }
          ),
        ],
      ),
    );
  }

  Widget _activityRow(
    BuildContext context, {
    required Color bg,
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required String badgeText,
    required Color badgeColor,
    required Color badgeTextColor,
  }) {
    return Container(
      decoration: AppStyles.decoration,
      padding: const EdgeInsets.all(8),
      child: Row(
        children: [
          Container(
            height: 32,
            width: 32,
            decoration: BoxDecoration(color: bg, shape: BoxShape.circle),
            child: Icon(icon, color: iconColor, size: 18),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.grey)),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(color: badgeColor, borderRadius: BorderRadius.circular(12)),
            child: Text(badgeText, style: TextStyle(fontSize: 11, color: badgeTextColor)),
          ),
        ],
      ),
    );
  }
}