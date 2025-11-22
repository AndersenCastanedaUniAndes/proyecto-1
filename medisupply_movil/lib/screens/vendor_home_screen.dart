import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:provider/provider.dart';
import 'dart:convert';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/utils/utils.dart';
import 'package:medisupply_movil/utils/requests.dart';

enum VendorScreenEnum { home, clientes, visitas, pedidos, recomendaciones }

class VendorHome extends StatelessWidget {
  final VoidCallback onOpenMenu;
  final void Function(VendorScreenEnum) onTapCard;
  const VendorHome({
    super.key,
    required this.onOpenMenu,
    required this.onTapCard
  });

  String _getSales(String id, String token) {
    getSailes(id, token);
    return '\$45,670';
  }

  String _getSalesPercentage() {
    return '87%';
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();

    final futureActiveClients = getClients(state.id, state.token);
    final futureVisitsToday = getVisits(state.id, state.token);

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          HomeCard(
            gradient: LinearGradient(colors: [AppStyles.blue1, AppStyles.blue2]),
            title: '¡Hola, ${state.userName}!',
            subtitle: 'Vendedor MediSupply',
            onTap: onOpenMenu,
            stat1Title: 'Ventas este mes',
            stat1Value: _getSales(state.id, state.token),
            stat2Title: 'Meta alcanzada',
            stat2Value: _getSalesPercentage(),
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
                    final clients = snapshot.data!.body;
                    activeClientsLabel = jsonDecode(clients).length.toString();
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
                    final clients = snapshot.data!.body;
                    visitsTodayLabel = jsonDecode(clients).length.toString();
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
                        final body = snapshot.data!.body;
                        final decoded = jsonDecode(body);

                        badgeText = '${decoded.length} clientes';
                      }

                      return MenuCard(
                        color: AppStyles.menuCardBlue,
                        icon: AppIcons.clients,
                        title: 'Clientes',
                        description: 'Gestiona tu cartera de clientes',
                        badge: badgeText,
                        onTap: () => onTapCard(VendorScreenEnum.clientes),
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
                        final body = snapshot.data!.body;
                        final decoded = jsonDecode(body);

                        print("decoded visits: $decoded");

                        badgeText = '${decoded.length} hoy';
                      }

                      return MenuCard(
                        color: AppStyles.menuCardGreen,
                        icon: AppIcons.pin,
                        title: 'Visitas',
                        description: 'Registra y revisa tus visitas',
                        badge: badgeText,
                        onTap: () => onTapCard(VendorScreenEnum.visitas),
                      );
                    },
                  ),

                  MenuCard(
                    color: Color(0xFFFF6900),
                    icon: AppIcons.shoppingCart,
                    title: 'Pedidos',
                    description: 'Gestiona pedidos de clientes',
                    badge: '12 pendientes',
                    onTap: () => onTapCard(VendorScreenEnum.pedidos),
                  ),

                  MenuCard(
                    color: Color(0xFFad46ff),
                    icon: AppIcons.lightbulb,
                    title: 'Recomendaciones',
                    description: 'Generación de recomendaciones',
                    badge: 'Próximamente',
                    onTap: () => onTapCard(VendorScreenEnum.recomendaciones),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }
}