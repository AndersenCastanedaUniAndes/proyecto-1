import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';

class HomeCard extends StatelessWidget {
  const HomeCard({
    super.key,
    required this.gradient,
    required this.title,
    required this.subtitle,
    required this.onTap,
    required this.stat1Title,
    required this.stat1Value,
    required this.stat2Title,
    required this.stat2Value,
  });

  final LinearGradient gradient;
  final String title;
  final String subtitle;
  final VoidCallback onTap;
  final String stat1Title;
  final String stat1Value;
  final String stat2Title;
  final String stat2Value;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(14),
      ),
      padding: const EdgeInsets.all(28),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w600)),
                  Text(subtitle, style: TextStyle(color: Colors.white, fontSize: 14)),
                ],
              ),
              Row(children: [
                // IconButton(onPressed: () {}, icon: Icon(AppIcons.notification, size: 18, color: Colors.white)),
                IconButton(onPressed: onTap, icon: Icon(AppIcons.user, size: 18, color: Colors.white)),
              ]),
            ],
          ),
          const SizedBox(height: 12),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            spacing: 10,
            children: [
              _MiniStat(title: stat1Title, value: stat1Value, valueColor: Colors.white),
              _MiniStat(title: stat2Title, value: stat2Value, valueColor: Colors.white),
            ],
          ),
        ],
      ),
    );
  }
}

class _MiniStat extends StatelessWidget {
  final String title;
  final String value;
  final Color? valueColor;
  const _MiniStat({required this.title, required this.value, this.valueColor});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: valueColor)),
        Text(title, style: const TextStyle(color: Colors.white, fontSize: 12)),
      ],
    );
  }
}