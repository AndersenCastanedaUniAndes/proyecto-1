import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:medisupply_movil/styles/styles.dart';

class _Visita {
  final int id;
  final String cliente;
  final String fecha; // YYYY-MM-DD
  final String hora; // HH:mm
  final String direccion;
  final String hallazgos;
  final List<String> sugerencias;
  final String fechaCreacion; // YYYY-MM-DD
  _Visita({
    required this.id,
    required this.cliente,
    required this.fecha,
    required this.hora,
    required this.direccion,
    required this.hallazgos,
    required this.sugerencias,
    required this.fechaCreacion,
  });
}

class VendorVisitsScreen extends StatefulWidget {
  final VoidCallback onBack;
  const VendorVisitsScreen({super.key, required this.onBack});

  @override
  State<VendorVisitsScreen> createState() => _VendorVisitsScreenState();
}

class _VendorVisitsScreenState extends State<VendorVisitsScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController = TabController(length: 2, vsync: this);

  // Form state
  final _formKey = GlobalKey<FormState>();
  String? _clienteSel;
  final _fechaCtrl = TextEditingController();
  final _horaCtrl = TextEditingController();
  final _localizacionCtrl = TextEditingController();
  final _hallazgosCtrl = TextEditingController();
  final _sugerenciasCtrl = TextEditingController();
  bool _isLoading = false;

  // Filters
  final _filtroFechaCtrl = TextEditingController();
  final _filtroClienteCtrl = TextEditingController();

  final List<String> _clientes = const [
    'Farmacia Central',
    'Droguería La Salud',
    'Hospital Nacional',
    'Red Farmacias Unidos',
    'Clínica San Juan',
  ];

  late final List<_Visita> _visitasBase = [
    _Visita(
      id: 1,
      cliente: 'Farmacia Central',
      fecha: '2024-03-20',
      hora: '09:30',
      direccion: 'Av. Principal 123, Centro',
      hallazgos:
          'Cliente requiere mayor stock de analgésicos para temporada de gripe. Inventario actual bajo en paracetamol y ibuprofeno.',
      sugerencias: const ['Paracetamol 500mg x 500 unidades', 'Ibuprofeno 600mg x 300 unidades', 'Antigripales variados'],
      fechaCreacion: '2024-03-20',
    ),
    _Visita(
      id: 2,
      cliente: 'Hospital Nacional',
      fecha: '2024-03-19',
      hora: '14:15',
      direccion: 'Carrera 30 #45-67, Sur',
      hallazgos:
          'Necesidad urgente de antibióticos para área de emergencias. Personal médico reporta escasez en tratamientos post-quirúrgicos.',
      sugerencias: const ['Amoxicilina 875mg', 'Cefalexina 500mg', 'Material quirúrgico estéril'],
      fechaCreacion: '2024-03-19',
    ),
  ];

  List<_Visita> get _visitasFiltradas {
    final fFecha = _filtroFechaCtrl.text.trim();
    final fCli = _filtroClienteCtrl.text.trim().toLowerCase();
    return _visitasBase.where((v) {
      final fechaOk = fFecha.isEmpty || v.fecha.contains(fFecha);
      final clienteOk = fCli.isEmpty || v.cliente.toLowerCase().contains(fCli);
      return fechaOk && clienteOk;
    }).toList();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _fechaCtrl.dispose();
    _horaCtrl.dispose();
    _localizacionCtrl.dispose();
    _hallazgosCtrl.dispose();
    _sugerenciasCtrl.dispose();
    _filtroFechaCtrl.dispose();
    _filtroClienteCtrl.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: now,
      firstDate: DateTime(now.year - 1),
      lastDate: DateTime(now.year + 2),
    );
    if (picked != null) {
      _fechaCtrl.text = picked.toIso8601String().substring(0, 10);
      setState(() {});
    }
  }

  Future<void> _pickTime() async {
    final now = TimeOfDay.now();
    final picked = await showTimePicker(context: context, initialTime: now);
    if (picked != null) {
      _horaCtrl.text = picked.format(context);
      setState(() {});
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 1));
    // Simular guardado en _visitasBase (inmutable en runtime, pero aquí recreamos)
    final nueva = _Visita(
      id: _visitasBase.length + 1,
      cliente: _clienteSel!,
      fecha: _fechaCtrl.text.trim(),
      hora: _horaCtrl.text.trim(),
      direccion: _localizacionCtrl.text.trim(),
      hallazgos: _hallazgosCtrl.text.trim(),
      sugerencias: _sugerenciasCtrl.text
          .split('\n')
          .map((e) => e.trim())
          .where((e) => e.isNotEmpty)
          .toList(),
      fechaCreacion: DateTime.now().toIso8601String().substring(0, 10),
    );
    setState(() {
      _visitasBase.add(nueva);
      _clienteSel = null;
      _fechaCtrl.clear();
      _horaCtrl.clear();
      _localizacionCtrl.clear();
      _hallazgosCtrl.clear();
      _sugerenciasCtrl.clear();
      _isLoading = false;
      _tabController.index = 1; // Ir al historial
    });
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        ScreenTitleAndBackNavigation(
          title: 'Visitas',
          subtitle: '${_visitasFiltradas.length} registros',
          textTheme: textTheme,
          onBack: widget.onBack,
        ),
        const SizedBox(height: 18),

        Container(
          height: 36,
          decoration: BoxDecoration(
            color: const Color(0xFFF1F1F4), // light gray background
            borderRadius: BorderRadius.circular(20),
          ),
          padding: const EdgeInsets.all(3),
          child: TabBar(
            controller: _tabController,
            indicator: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
            ),
            labelColor: Colors.black,
            unselectedLabelColor: Colors.black54,
            indicatorSize: TabBarIndicatorSize.tab,
            dividerColor: Colors.transparent,
            overlayColor: WidgetStateProperty.all(Colors.transparent),
            tabs: [
              Tab(
                iconMargin: EdgeInsets.only(bottom: 2),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  spacing: 8,
                  children: [
                    Icon(AppIcons.add, size: 16, color: Colors.black),
                    Text(
                      "Registrar",
                      style: textTheme.labelMedium?.copyWith(fontSize: 13),
                    ),
                  ],
                ),
              ),
              Tab(
                iconMargin: EdgeInsets.only(bottom: 2),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  spacing: 8,
                  children: [
                    Icon(AppIcons.historyList, size: 16, color: Colors.black),
                    Text("Historial", style: textTheme.labelMedium),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),

        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildRegistrar(context),
              _buildHistorial(context),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRegistrar(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;

    return SingleChildScrollView(
      child: Container(
        decoration: AppStyles.decoration,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Title
                Text(
                  'Nueva Visita',
                  style: Theme.of(
                    context,
                  ).textTheme.titleMedium?.copyWith(fontSize: 16),
                ),
                const SizedBox(height: 18),

                // Dropdown
                Text('Cliente', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 2),

                DropdownButtonFormField<String>(
                  isExpanded: true,
                  icon: const SizedBox.shrink(),
                  value: _clienteSel,
                  items: _clientes.map((c) => DropdownMenuItem(value: c, child: Text(c)),).toList(),
                  onChanged: (v) => setState(() => _clienteSel = v),
                  decoration: _baseInputDecoration().copyWith(
                    hintText: 'Selecciona un cliente',
                    suffixIcon: Icon(AppIcons.chevronDown, size: 16),
                  ),
                  validator: (v) => (v == null || v.isEmpty) ? 'Selecciona un cliente' : null,
                ),
                const SizedBox(height: 12),

                // Date and Time
                Row(
                  spacing: 12,
                  children: [
                    Expanded(child: Text('Fecha', style: Theme.of(context).textTheme.titleMedium)),
                    Expanded(child: Text('Hora', style: Theme.of(context).textTheme.titleMedium))
                  ],
                ),
                const SizedBox(height: 2),

                Row(
                  spacing: 12,
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _fechaCtrl,
                        readOnly: true,
                        decoration: _baseInputDecoration().copyWith(
                          hintText: 'mm/dd/yyyy',
                          suffixIcon: Icon(AppIcons.calendar, size: 16, color: Colors.white),
                        ),
                        onTap: _pickDate,
                        validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                      ),
                    ),

                    Expanded(
                      child: TextFormField(
                        controller: _fechaCtrl,
                        readOnly: true,
                        decoration: _baseInputDecoration().copyWith(
                          hintText: _horaCtrl.text.isEmpty ? '--:-- --' : _horaCtrl.text,
                          suffixIcon: Icon(AppIcons.clock, size: 16, color: Colors.white,)
                        ),
                        onTap: _pickTime,
                        validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),

                // Location
                Text('Localización', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 2),
                TextFormField(
                  controller: _localizacionCtrl,
                  decoration: _baseInputDecoration(useConstraints: false).copyWith(
                    counterText: '',
                    hintText: 'Dirección del cliente',
                    hintStyle: textTheme.bodySmall?.copyWith(height: 1.3),
                    prefixIcon: Icon(AppIcons.pin, size: 18, color: AppStyles.grey1),
                  ),
                  maxLength: 300,
                  validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: 12),

                // Findings
                Text('Hallazgos Técnicos o Clínicos', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 4),
                // Crea un TextFormField: El input debe crecer en altura según el contenido
                TextFormField(
                  controller: _hallazgosCtrl,
                  maxLines: null,
                  decoration: _baseInputDecoration(useConstraints: false).copyWith(
                    counterText: '',
                    hintText: 'Describe los hallazgos encontrados durante la visita...',
                    hintStyle: textTheme.bodySmall?.copyWith(height: 1.8),
                    labelStyle: textTheme.bodySmall?.copyWith(height: 1.8),
                  ),
                  maxLength: 500,
                  maxLengthEnforcement: MaxLengthEnforcement.enforced,
                  validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: 12),

                // Suggestions
                Text('Sugerencias de Producto', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 4),
                // Crea un TextFormField: El input debe crecer en altura según el contenido
                TextFormField(
                  controller: _sugerenciasCtrl,
                  maxLines: null,
                  decoration: _baseInputDecoration(useConstraints: false).copyWith(
                    counterText: '',
                    hintText: 'Lista los productos recomendados (uno por línea)...',
                    hintStyle: textTheme.bodySmall?.copyWith(height: 1.8),
                    labelStyle: textTheme.bodySmall?.copyWith(height: 1.8),
                  ),
                  maxLength: 500,
                  maxLengthEnforcement: MaxLengthEnforcement.enforced,
                  validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: 18),

                ConfirmationButton(
                  isLoading: _isLoading,
                  onTap: _submit,
                  idleLabel: 'Registrar Visita',
                  onTapLabel: 'Registrando...'
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHistorial(BuildContext context) {
    final visits = _visitasFiltradas;
    return Column(
      children: [
        Row(children: [
          Expanded(
            child: TextField(
              controller: _filtroFechaCtrl,
              decoration: const InputDecoration(labelText: 'Filtrar por fecha (YYYY-MM-DD)', prefixIcon: Icon(Icons.calendar_today)),
              onChanged: (_) => setState(() {}),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: TextField(
              controller: _filtroClienteCtrl,
              decoration: const InputDecoration(labelText: 'Filtrar por cliente', prefixIcon: Icon(Icons.search)),
              onChanged: (_) => setState(() {}),
            ),
          ),
        ]),
        const SizedBox(height: 12),
        Expanded(
          child: visits.isEmpty
              ? Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: const [
                        Icon(Icons.event_busy, size: 48, color: Colors.grey),
                        SizedBox(height: 8),
                        Text('No se encontraron visitas', style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  ),
                )
              : ListView.separated(
                  itemCount: visits.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, i) {
                    final v = visits[i];
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(12.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(v.cliente, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                                _idBadge('ID: ${v.id}')
                              ],
                            ),
                            const SizedBox(height: 8),
                            Row(children: [
                              const Icon(Icons.calendar_today, size: 14, color: Colors.grey),
                              const SizedBox(width: 4),
                              Text(v.fecha, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                              const SizedBox(width: 16),
                              const Icon(Icons.access_time, size: 14, color: Colors.grey),
                              const SizedBox(width: 4),
                              Text(v.hora, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                            ]),
                            const SizedBox(height: 8),
                            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                              const Icon(Icons.place_outlined, size: 14, color: Colors.grey),
                              const SizedBox(width: 4),
                              Expanded(child: Text(v.direccion, style: const TextStyle(fontSize: 12, color: Colors.grey))),
                            ]),
                            const SizedBox(height: 12),
                            Row(children: const [
                              Icon(Icons.description_outlined, size: 14),
                              SizedBox(width: 4),
                              Text('Hallazgos', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                            ]),
                            Text(v.hallazgos, style: const TextStyle(fontSize: 12, color: Colors.black87)),
                            if (v.sugerencias.isNotEmpty) ...[
                              const SizedBox(height: 8),
                              Row(children: const [
                                Icon(Icons.lightbulb_outline, size: 14),
                                SizedBox(width: 4),
                                Text('Sugerencias', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                              ]),
                              const SizedBox(height: 4),
                              Wrap(
                                spacing: 6,
                                runSpacing: 6,
                                children: v.sugerencias
                                    .map((s) => Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                          decoration: BoxDecoration(
                                            color: Colors.grey.shade200,
                                            borderRadius: BorderRadius.circular(12),
                                          ),
                                          child: Text(s, style: const TextStyle(fontSize: 11)),
                                        ))
                                    .toList(),
                              ),
                            ]
                          ],
                        ),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }

  Widget _idBadge(String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: Colors.grey.shade200, borderRadius: BorderRadius.circular(12)),
      child: Text(text, style: const TextStyle(fontSize: 11)),
    );
  }

  InputDecoration _baseInputDecoration({bool useConstraints = true}) {
    return InputDecoration(
      constraints: useConstraints ? BoxConstraints.expand(height: 36) : null,
      filled: true,
      fillColor: AppStyles.grey1.withAlpha(30),
      contentPadding: const EdgeInsets.symmetric(
        vertical: 12,
        horizontal: 12,
      ),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8.0),
        borderSide: BorderSide.none,
      ),
    );
  }
}