class Visita {
  final int id;
  final String cliente;
  final String fecha; // YYYY-MM-DD
  final String hora; // HH:mm
  final String direccion;
  final String hallazgos;
  final List<String> sugerencias;

  Visita({
    required this.id,
    required this.cliente,
    required this.fecha,
    required this.hora,
    required this.direccion,
    required this.hallazgos,
    required this.sugerencias,
  });
}