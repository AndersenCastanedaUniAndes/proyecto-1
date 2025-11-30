import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';

class MenuCard extends StatelessWidget {
  const MenuCard({
    super.key,
    required this.color,
    required this.icon,
    required this.title,
    required this.description,
    required this.badge,
    required this.onTap,
    // required this.textTheme,
  });

  final Color color;
  final IconData icon;
  final String title;
  final String description;
  final String badge;
  final VoidCallback onTap;
  // final TextTheme textTheme;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: AppStyles.decoration,
        padding: const EdgeInsets.all(12),
        child: Column(
          mainAxisSize: MainAxisSize.max,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              height: 48,
              width: 48,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
              child: Icon(icon, size: 24, color: Colors.white,),
            ),
            const SizedBox(height: 8),

            Text(title, style: textTheme.labelLarge?.copyWith(fontSize: 15, fontWeight: FontWeight.w600)),
            const SizedBox(height: 4),

            Flexible(
              child: Text(
                description,
                textAlign: TextAlign.center,
                style: textTheme.bodySmall?.copyWith(fontSize: 12),
                softWrap: true,
                overflow: TextOverflow.fade,
              ),
            ),
            const SizedBox(height: 6),

            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(color: AppStyles.grey2, borderRadius: BorderRadius.circular(10)),
              child: Text(badge, style: textTheme.bodySmall?.copyWith(fontSize: 12, fontWeight: FontWeight.w500)),
            ),
          ],
        ),
      ),
    );
  }
}