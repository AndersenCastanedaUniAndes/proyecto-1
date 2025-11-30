import 'package:flutter/material.dart';

class QuickStats extends StatelessWidget {
  const QuickStats({
    super.key,
    required this.stat1Title,
    required this.stat1Value,
    required this.stat1Color,
    required this.stat2Title,
    required this.stat2Value,
    required this.stat2Color,
  });

  final Color stat1Color;
  final String stat1Title;
  final String stat1Value;

  final Color stat2Color;
  final String stat2Title;
  final String stat2Value;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: CardStat(color: stat1Color, value: stat1Value, caption: stat1Title)
        ),
        SizedBox(width: 12),
        Expanded(child: CardStat(color: stat2Color, value: stat2Value, caption: stat2Title)),
      ],
    );
  }
}

class CardStat extends StatelessWidget {
  final Color color;
  final String value;
  final String caption;
  const CardStat({
    super.key,
    required this.color,
    required this.value,
    required this.caption
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Color(0x2A000000), width: 1)
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: color)),
            Text(caption, style: const TextStyle(fontSize: 12, color: Colors.black54)),
            const SizedBox(height: 4),
          ],
        ),
      ),
    );
  }
}