import 'package:flutter/material.dart';

class UserTypeWidget extends StatefulWidget {
  const UserTypeWidget({
    super.key,
    required this.onTap,
    required this.selectedType,
    required this.iconData,
    required this.label,
  });

  final bool selectedType;
  final VoidCallback onTap;
  final IconData iconData;
  final String label;

  @override
  State<UserTypeWidget> createState() => _UserTypeWidgetState();
}

class _UserTypeWidgetState extends State<UserTypeWidget> {
  final unSelectedBoderColor = const Color(0xFFA1A1A1);
  final unSelectedColor = const Color(0xFF717182);

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final textTheme = Theme.of(context).textTheme;

    return InkWell(
      borderRadius: BorderRadius.circular(10),
      onTap: widget.onTap,
      highlightColor: Colors.transparent,
      focusColor: Colors.transparent,
      splashColor: Colors.transparent,
      child: Container(
        padding: const EdgeInsets.all(8),
        width: 157,
        height: 87,
        decoration: BoxDecoration(
          color: widget.selectedType ? colorScheme.primary.withAlpha(13) : Colors.white,
          border: Border.all(
            color: widget.selectedType ? colorScheme.primary : unSelectedBoderColor,
            width: 2,
          ),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: 16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              Icon(
                widget.iconData,
                color: widget.selectedType ? colorScheme.primary : unSelectedColor,
                size: 24,
              ),
              Text(
                widget.label,
                style: textTheme.labelLarge?.copyWith(
                  color: widget.selectedType ? colorScheme.primary : unSelectedColor
                )
              ),
            ],
          ),
        ),
      ),
    );
  }
}
