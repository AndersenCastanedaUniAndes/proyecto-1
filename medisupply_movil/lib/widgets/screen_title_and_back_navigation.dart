import 'package:flutter/material.dart';

class ScreenTitleAndBackNavigation extends StatelessWidget {
  const ScreenTitleAndBackNavigation({
    super.key,
    required this.title,
    required this.subtitle,
    this.onBack,
    this.textTheme = const TextTheme(),
  });

  final String title;
  final String subtitle;

  final VoidCallback? onBack;
  final TextTheme textTheme;

  @override
  Widget build(BuildContext context) {
    return Row(
      spacing: 12,
      children: [
        IconButton(
          onPressed: onBack,
          icon: const Icon(Icons.arrow_back, size: 18),
        ),
        Flexible(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: textTheme.titleMedium?.copyWith(
                  fontSize: 17,
                  fontWeight: FontWeight.w600,
                ),
              ),
              Text(
                subtitle,
                style: textTheme.bodySmall?.copyWith(fontSize: 13, color: Color(0xFF717182)),
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ],
    );
  }
}