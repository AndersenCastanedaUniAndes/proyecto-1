import 'package:flutter/material.dart';

class AppTitleAndSubtitle extends StatelessWidget {
  const AppTitleAndSubtitle({
    super.key,
    required this.titleLabel,
    required this.subtitleLabel,
    required this.textTheme,
  });

  final String titleLabel;
  final String subtitleLabel;
  final TextTheme textTheme;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          titleLabel,
          textAlign: TextAlign.center,
          style: textTheme.titleLarge
        ),
        const SizedBox(height: 4),

        // Subtítulo
        Text(
          subtitleLabel,
          textAlign: TextAlign.center,
          style: textTheme.bodyMedium
        ),
      ],
    );
  }
}