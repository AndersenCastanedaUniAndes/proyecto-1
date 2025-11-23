import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:medisupply_movil/state/app_state.dart';
import 'package:medisupply_movil/styles/styles.dart';
import 'package:medisupply_movil/utils/utils.dart';
import 'package:medisupply_movil/widgets/widgets.dart';
import 'package:provider/provider.dart';

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
  bool _isCreatingVisit = false;
  bool _isLoadingClients = false;
  bool _isLoadingVisits = false;

  // Filters
  final _filtroFechaCtrl = TextEditingController();
  final _filtroClienteCtrl = TextEditingController();

  late Map<int, String> _clientes = const {};

  late final List<Visita> _visitasBase = [];

  List<Visita> get _visitasFiltradas {
    final fFecha = _filtroFechaCtrl.text.trim();
    final fCli = _filtroClienteCtrl.text.trim().toLowerCase();
    return _visitasBase.where((v) {
      final fechaOk = fFecha.isEmpty || v.fecha.contains(fFecha);
      final clienteOk = fCli.isEmpty || v.cliente.toLowerCase().contains(fCli);
      return fechaOk && clienteOk;
    }).toList();
  }

  @override
  void initState() {
    super.initState();
    _loadClients();
    _loadHistory();
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

  Future<void> _loadClients() async {
    setState(() => _isLoadingClients = true);

    final state = context.read<AppState>();

    final response = await getClientsSmall(state.id, state.token);
    setState(() => _isLoadingClients = false);

    try {
      _clientes = response;
    } catch (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al cargar los clientes: $error'),
        ),
      );
    }
  }

  Future<void> _loadHistory() async {
    setState(() => _isLoadingVisits = true);
    final state = context.read<AppState>();

    final response = await getVisits(state.id, state.token);

    try {
      final decodedBody = jsonDecode(response.body);

      final List<Visita> visitas = [];
      for (var item in decodedBody) {
        var sugerencias = item['sugerencias'] as String;
        sugerencias.split(',');

        visitas.add(Visita(
          id: item['id'],
          cliente: item['cliente'],
          fecha: item['fecha'],
          hora: item['hora'],
          direccion: item['direccion'],
          hallazgos: item['hallazgos'],
          sugerencias: sugerencias.split(','),
        ));
      }

      setState(() {
        _visitasBase.clear();
        _visitasBase.addAll(visitas);
      });
    } catch (error) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error $error'),
        ),
      );
    }

    setState(() => _isLoadingVisits = false);
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: now,
      firstDate: DateTime(now.year - 1),
      lastDate: now,
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
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() => _isCreatingVisit = true);

    final state = context.read<AppState>();

    final response = await createVisit({
      'cliente': _clienteSel,
      'cliente_id': _clientes.entries.firstWhere((e) => e.value == _clienteSel).key,
      'vendedor': state.userName,
      'vendedor_id': state.id,
      'fecha': _fechaCtrl.text.trim(),
      'hora': _horaCtrl.text.trim(),
      'direccion': _localizacionCtrl.text.trim(),
      'hallazgos': _hallazgosCtrl.text.trim(),
      'sugerencias': _sugerenciasCtrl.text.trim()
    }, state.id, state.token);

    setState(() => _isCreatingVisit = false);

    if (response.statusCode != 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error ${response.statusCode}: ${response.body}'),
        ),
      );
      return;
    }

    _loadHistory();

    setState(() {
      _clienteSel = null;
      _fechaCtrl.clear();
      _horaCtrl.clear();
      _localizacionCtrl.clear();
      _hallazgosCtrl.clear();
      _sugerenciasCtrl.clear();
      _isCreatingVisit = false;
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
                  style: textTheme.titleMedium?.copyWith(fontSize: 16),
                ),
                const SizedBox(height: 18),

                // Dropdown
                Text('Cliente', style: textTheme.titleMedium),
                const SizedBox(height: 2),

                DropdownButtonFormField<String>(
                  dropdownColor: Colors.white,
                  menuMaxHeight: 300,
                  isExpanded: true,
                  icon: const SizedBox.shrink(),
                  value: _clienteSel,
                  items: _clientes.values.map((v) => DropdownMenuItem(
                    value: v,
                    child: Text(v, style: textTheme.bodySmall),
                  )).toList(),
                  onChanged: (v) => setState(() => _clienteSel = v),
                  decoration: _baseInputDecoration().copyWith(
                    hintText: _isLoadingClients ? 'Cargando...' : 'Selecciona un cliente',
                    suffixIcon: Icon(AppIcons.chevronDown, size: 16),
                  ),
                  validator: (v) => (v == null || v.isEmpty) ? 'Selecciona un cliente' : null,
                ),
                const SizedBox(height: 12),

                // Date and Time
                Row(
                  spacing: 12,
                  children: [
                    Expanded(child: Text('Fecha', style: textTheme.titleMedium)),
                    Expanded(child: Text('Hora', style: textTheme.titleMedium))
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
                        controller: _horaCtrl,
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
                Text('Localización', style: textTheme.titleMedium),
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
                Text('Hallazgos Técnicos o Clínicos', style: textTheme.titleMedium),
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
                Text('Sugerencias de Producto', style: textTheme.titleMedium),
                const SizedBox(height: 4),
                // Crea un TextFormField: El input debe crecer en altura según el contenido
                TextFormField(
                  controller: _sugerenciasCtrl,
                  maxLines: null,
                  decoration: _baseInputDecoration(useConstraints: false).copyWith(
                    counterText: '',
                    hintText: 'Lista los productos recomendados (separados por comas)...',
                    hintStyle: textTheme.bodySmall?.copyWith(height: 1.8),
                    labelStyle: textTheme.bodySmall?.copyWith(height: 1.8),
                  ),
                  maxLength: 500,
                  maxLengthEnforcement: MaxLengthEnforcement.enforced,
                  validator: (v) => (v == null || v.isEmpty) ? 'Requerido' : null,
                ),
                const SizedBox(height: 18),

                ConfirmationButton(
                  isEnabled: !_isLoadingClients,
                  isLoading: _isCreatingVisit,
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
    final textTheme = Theme.of(context).textTheme;
    final visits = _visitasFiltradas;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Date and Time
        Row(
          spacing: 12,
          children: [
            Expanded(child: Text('Filtrar por fecha', style: textTheme.titleSmall?.copyWith(fontSize: 13))),
            Expanded(child: Text('Filtrar por cliente', style: textTheme.titleSmall?.copyWith(fontSize: 13)))
          ],
        ),
        const SizedBox(height: 2),

        Row(
          spacing: 12,
          children: [
            Expanded(
              child: TextField(
                controller: _filtroFechaCtrl,
                decoration: _baseInputDecoration().copyWith(
                  hintText: 'mm/dd/yyyy',
                  suffixIcon: Icon(AppIcons.calendar, size: 16, color: Colors.white),
                ),
                onChanged: (_) => setState(() {}),
              ),
            ),
            Expanded(
              child: TextField(
                controller: _filtroClienteCtrl,
                decoration: _baseInputDecoration().copyWith(
                  hintText: 'Cliente...',
                  prefixIcon: Icon(AppIcons.search, size: 16),
                ),
                onChanged: (_) => setState(() {}),
              ),
            ),
          ]
        ),
        const SizedBox(height: 12),

        _isLoadingVisits ? Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: CircularProgressIndicator(),
          ),
        )
        : visits.isEmpty ? Container(
          decoration: AppStyles.decoration,
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(AppIcons.calendar, size: 48, color: AppStyles.grey1),
                SizedBox(height: 8),
                Text('No se encontraron visitas', style: TextStyle(color: AppStyles.grey1)),
              ],
            ),
          ),
        )
        : Expanded(
          child: ListView.separated(
            itemCount: visits.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, i) {
              final v = visits[i];
              return Container(
                decoration: AppStyles.decoration,
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            v.cliente,
                            style: textTheme.titleSmall?.copyWith(fontSize: 15)
                          ),
                          _idBadge('ID: ${v.id}', textTheme),
                        ],
                      ),
                      const SizedBox(height: 8),

                      Row(
                        children: [
                          Icon(AppIcons.calendar, size: 14, color: AppStyles.grey1),
                          const SizedBox(width: 4),

                          Text(
                            v.fecha,
                            style: textTheme.bodySmall?.copyWith(fontSize: 12.5, color: AppStyles.grey1),
                          ),
                          const SizedBox(width: 16),

                          Icon(AppIcons.clock, size: 14, color: AppStyles.grey1),
                          const SizedBox(width: 4),

                          Text(
                            v.hora,
                            style: textTheme.bodySmall?.copyWith(fontSize: 12.5, color: AppStyles.grey1),
                          ),
                        ]
                      ),
                      const SizedBox(height: 8),

                      Row(
                        spacing: 4,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(AppIcons.pin, size: 14, color: AppStyles.grey1),
                          Expanded(
                            child: Text(
                              v.direccion,
                              style: textTheme.bodySmall?.copyWith(fontSize: 12.5, color: AppStyles.grey1, height: 1),
                            )
                          ),
                        ]
                      ),
                      const SizedBox(height: 12),

                      Row(
                        spacing: 4,
                        children: [
                        Icon(Icons.description_outlined, size: 14),
                        Text(
                          'Hallazgos',
                          style: textTheme.bodySmall?.copyWith(fontSize: 12, fontWeight: FontWeight.w600),
                        ),
                      ]),
                      const SizedBox(height: 2),

                      Text(
                        v.hallazgos,
                        style: textTheme.bodySmall?.copyWith(fontSize: 12, color: AppStyles.grey1),
                      ),

                      if (v.sugerencias.isNotEmpty) ...[
                        const SizedBox(height: 8),

                        Row(
                          children: const [
                            Icon(Icons.lightbulb_outline, size: 14),
                            SizedBox(width: 4),
                            Text('Sugerencias', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                          ]
                        ),
                        const SizedBox(height: 4),

                        Wrap(
                          spacing: 6,
                          runSpacing: 6,
                          children: v.sugerencias.map((s) => Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: AppStyles.decoration,
                            child: Text(
                              s,
                              style: textTheme.bodySmall?.copyWith(fontSize: 11, fontWeight: FontWeight.w600),
                            ),
                          )).toList(),
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

  Widget _idBadge(String text, TextTheme textTheme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: AppStyles.grey1.withAlpha(30), borderRadius: BorderRadius.circular(12)),
      child: Text(text, style: textTheme.bodySmall?.copyWith(fontSize: 12, fontWeight: FontWeight.w500)),
    );
  }

  InputDecoration _baseInputDecoration({bool useConstraints = true}) {
    return InputDecoration(
      constraints: useConstraints ? BoxConstraints.expand(height: 36) : null,
      filled: true,
      fillColor: AppStyles.grey1.withAlpha(25),
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