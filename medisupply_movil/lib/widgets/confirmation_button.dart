import 'package:flutter/material.dart';

class ConfirmationButton extends StatefulWidget {
  const ConfirmationButton({
    super.key,
    required this.isLoading,
    required this.onTap,
    required this.idleLabel,
    required this.onTapLabel,
    this.isEnabled = true,
  });

  final bool isLoading;
  final bool isEnabled;
  final VoidCallback onTap;
  final String idleLabel;
  final String onTapLabel;

  @override
  State<ConfirmationButton> createState() => _ConfirmationButtonState();
}

class _ConfirmationButtonState extends State<ConfirmationButton> {
  @override
  Widget build(BuildContext context) {
    return FilledButton(
      style: ButtonStyle(
        shape: WidgetStateProperty.all<RoundedRectangleBorder>(
          RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8.0),
          ),
        ),
        backgroundColor: widget.isEnabled
            ? null
            : WidgetStateProperty.all<Color>(Color(0xFF4682B4).withValues(alpha: 0.5)),
      ),
      onPressed: widget.isLoading ? null : widget.onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 12.0),
        child: Text(widget.isLoading ? widget.onTapLabel : widget.idleLabel),
      ),
    );
  }
}