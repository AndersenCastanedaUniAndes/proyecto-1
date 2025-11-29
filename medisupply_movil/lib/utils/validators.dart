final reg = RegExp(r'\B(?=(\d{3})+(?!\d))');

String toMoneyFormat(double amount) {
  return amount.toStringAsFixed(0).replaceAllMapped(reg, (match) => ',');
}
