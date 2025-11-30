import 'package:flutter/material.dart';
import 'package:medisupply_movil/styles/styles.dart';

class NotFoundSection extends StatelessWidget {
  const NotFoundSection({
    super.key,
    required this.iconData,
    required this.label,
  });

  final IconData iconData;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: AppStyles.decoration,
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(iconData, size: 48, color: AppStyles.grey1),
            SizedBox(height: 8),
            Text(label, style: TextStyle(color: AppStyles.grey1)),
          ],
        ),
      ),
    );
  }
}