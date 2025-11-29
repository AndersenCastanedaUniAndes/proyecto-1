import 'package:flutter/material.dart';
import 'package:medisupply_movil/screens/vendor_visits_screen.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import 'package:medisupply_movil/data/data.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/utils/utils.dart';
import 'package:medisupply_movil/utils/requests.dart';

enum VendorScreenEnum { home, clientes, visitas, pedidos, recomendaciones }

class VendorHome extends StatefulWidget {
  final VoidCallback onOpenMenu;
  final void Function(VendorScreenEnum) onTapCard;
  const VendorHome({
    super.key,
    required this.onOpenMenu,
    required this.onTapCard
  });

  @override
  State<VendorHome> createState() => _VendorHomeState();
}

class _VendorHomeState extends State<VendorHome> {
  late Future<List<dynamic>> futureActiveClients;
  late Future<List<Visita>> futureVisitsToday;
  late Future<List<Order>> futureOrders;
  late Future<List<SalesPlan>> futureSalesPlans;
  late Future<List> combinedOrdersAndSalesPlans;

  String _getSalesPercentage() {
    return '87%';
  }

  @override
  void initState() {
    super.initState();

    final state = context.read<AppState>();
    futureActiveClients = getClients(state.id, state.token);
    futureVisitsToday = getVisits(state.id, state.token);
    futureOrders = getVendorOrders(state.id, state.token);
    futureSalesPlans = getSalesPlans(state.id, state.token);

    combinedOrdersAndSalesPlans = Future.wait([futureOrders, futureSalesPlans]);
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          FutureBuilder(
            future: combinedOrdersAndSalesPlans,
            builder: (context, snapshot) {
              String monthSales = '...';
              String salesGoal = '...';

              if (snapshot.connectionState == ConnectionState.waiting) {
                monthSales = '...';
                salesGoal = '...';
              } else if (snapshot.hasError) {
                monthSales = '-';
                salesGoal = '-';
              } else if (snapshot.hasData) {
                final orders = snapshot.data![0] as List<Order>;

                final filteredOrders = orders.where((order) {
                  final orderDate = DateTime.parse(order.fecha);
                  final now = DateTime.now();
                  return orderDate.year == now.year && orderDate.month == now.month;
                });

                // total sells price with comma separation
                final totalSales = filteredOrders.fold<double>(0, (previousValue, order) => previousValue + order.total);
                monthSales = toMoneyFormat(totalSales);

                final plans = snapshot.data![1] as List<SalesPlan>;

                // all active sales plans
                final activePlans = plans.where((plan) => plan.state == 'activo').toList();
                double totalGoal = 0;
                for (var plan in activePlans) {
                  totalGoal += (plan.totalSales / plan.sellers);
                }

                double percentage = totalGoal == 0 ? 0 : (totalSales / totalGoal) * 100;
                salesGoal = '${toMoneyFormat(percentage)}%';
              }

              return HomeCard(
                gradient: LinearGradient(colors: [AppStyles.blue1, AppStyles.blue2]),
                title: '¡Hola, ${state.userName}!',
                subtitle: 'Vendedor MediSupply',
                onTap: widget.onOpenMenu,
                stat1Title: 'Ventas este mes',
                stat1Value: '\$$monthSales',
                stat2Title: 'Meta alcanzada',
                stat2Value: salesGoal,
              );
            }
          ),
          const SizedBox(height: 16),

          Row(
            spacing: 12,
            children: [
              FutureBuilder(
                future: futureActiveClients,
                builder: (context, snapshot) {
                  String activeClientsLabel = '...';

                  if (snapshot.connectionState == ConnectionState.waiting) {
                    activeClientsLabel = '...';
                  } else if (snapshot.hasError) {
                    activeClientsLabel = '-';
                  } else if (snapshot.hasData) {
                    activeClientsLabel = snapshot.data!.length.toString();
                  }

                  return Expanded(
                    child: CardStat(color: AppStyles.green1, value: activeClientsLabel, caption: 'Clientes Activos')
                  );
                }
              ),

              FutureBuilder(
                future: futureVisitsToday,
                builder: (context, snapshot) {
                  String visitsTodayLabel = '...';

                  if (snapshot.connectionState == ConnectionState.waiting) {
                    visitsTodayLabel = '...';
                  } else if (snapshot.hasError) {
                    visitsTodayLabel = '-';
                  } else if (snapshot.hasData) {
                    visitsTodayLabel = _getTodayVisitsCount(snapshot.data!).toString();
                  }

                  return Expanded(
                    child: CardStat(color: AppStyles.blue1, value: visitsTodayLabel, caption: 'Visitas Hoy')
                  );
                }
              ),
            ],
          ),
          const SizedBox(height: 16),

          LayoutBuilder(
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
                  FutureBuilder(
                    future: futureActiveClients,
                    builder: (context, snapshot) {
                      String badgeText = '...';

                      if (snapshot.connectionState == ConnectionState.waiting) {
                        badgeText = 'Cargando...';
                      } else if (snapshot.hasError) {
                        badgeText = 'Error';
                      } else if (snapshot.hasData) {
                        badgeText = '${snapshot.data!.length} clientes';
                      }

                      return MenuCard(
                        color: AppStyles.menuCardBlue,
                        icon: AppIcons.clients,
                        title: 'Clientes',
                        description: 'Gestiona tu cartera de clientes',
                        badge: badgeText,
                        onTap: () => widget.onTapCard(VendorScreenEnum.clientes),
                      );
                    },
                  ),

                  FutureBuilder(
                    future: futureVisitsToday,
                    builder: (context, snapshot) {
                      String badgeText = '...';

                      if (snapshot.connectionState == ConnectionState.waiting) {
                        badgeText = 'Cargando...';
                      } else if (snapshot.hasError) {
                        badgeText = 'Error';
                      } else if (snapshot.hasData) {
                        final count = _getTodayVisitsCount(snapshot.data!);

                        badgeText = '$count hoy';
                      }

                      return MenuCard(
                        color: AppStyles.menuCardGreen,
                        icon: AppIcons.pin,
                        title: 'Visitas',
                        description: 'Registra y revisa tus visitas',
                        badge: badgeText,
                        onTap: () => widget.onTapCard(VendorScreenEnum.visitas),
                      );
                    },
                  ),

                  FutureBuilder(
                    future: futureOrders,
                    builder: (context, snapshot) {
                      String badgeText = '...';

                      if (snapshot.connectionState == ConnectionState.waiting) {
                        badgeText = 'Cargando...';
                      } else if (snapshot.hasError) {
                        badgeText = 'Error';
                      } else if (snapshot.hasData) {
                        final orders = snapshot.data!;
                        badgeText = '${orders.length} pedidos';
                      }

                      return MenuCard(
                        color: Color(0xFFFF6900),
                        icon: AppIcons.shoppingCart,
                        title: 'Pedidos',
                        description: 'Gestiona pedidos de clientes',
                        badge: badgeText,
                        onTap: () => widget.onTapCard(VendorScreenEnum.pedidos),
                      );
                    }
                  ),

                  MenuCard(
                    color: Color(0xFFad46ff),
                    icon: AppIcons.lightbulb,
                    title: 'Recomendaciones',
                    description: 'Generación de recomendaciones',
                    badge: 'Próximamente',
                    onTap: () => widget.onTapCard(VendorScreenEnum.recomendaciones),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  int _getTodayVisitsCount(List<Visita> visits) {
    final now = DateTime.now();
    int count = 0;

    for (var item in visits) {
      final visitaDate = DateTime.parse(item.fecha);
      if (visitaDate.year == now.year &&
          visitaDate.month == now.month &&
          visitaDate.day == now.day) {
        count++;
      }
    }

    return count;
  }
}