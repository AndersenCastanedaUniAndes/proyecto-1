import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:medisupply_movil/view_types.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:medisupply_movil/data/data.dart';

final userServiceURL = 'USER_SERVICE_URL';
final informesServiceURL = 'INFORMES_SERVICE_URL';
final inventoryServiceURL = 'INVENTORY_SERVICE_URL';

Future<http.Response> register(Object body) async {
  final baseUrl = dotenv.env[userServiceURL];
  final url = Uri.parse('$baseUrl/clients');

  try {
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    );

    return response;
  } catch (e) {
    return http.Response('Error: $e', 500);
  }
}

Future<http.Response> login(
  String email,
  String password,
  UserType userType) async {
  final baseUrl = dotenv.env[userServiceURL];

  final endpoint = switch (userType) {
    UserType.vendedor => '/token',
    UserType.cliente => '/clients/login',
  };

  final url = Uri.parse('$baseUrl$endpoint');

  try {
    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: Uri(queryParameters: {
        'username': email,
        'password': password,
      }).query,
    );

    return response;
  } catch (e) {
    return http.Response('Error: $e', 500);
  }
}

Future<List<SalesPlan>> getSalesPlans(String id, String token) async {
  final baseUrl = dotenv.env[userServiceURL];
  final url = Uri.parse('$baseUrl/planes_venta/vendedor/$id');

  try {
    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token'
      }
    );

    final decodedBody = jsonDecode(response.body);
    final list = decodedBody as List<dynamic>;

    final plans = list.map((p) => SalesPlan(
      id: p['id'],
      period: p['periodo'],
      totalSales: p['valor_ventas'],
      sellers: (p['vendedores_asignados'] as List<dynamic>).length,
      state: p['estado'],
    )).toList();

    return plans;
  } catch (e) {
    return [];
  }
}

Future<Map<int, String>> getClientsSmall(String id, String token) async {
  final baseUrl = dotenv.env[userServiceURL];
  final url = Uri.parse('$baseUrl/clients-small/$id');

  try {
    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token'
      },
    );

    // await Future.delayed(const Duration(seconds: 1));

    if (response.statusCode != 200) {
      return {};
    }

    final decodedBody = jsonDecode(response.body);

    final Map<int, String> data = {};
    for (var item in decodedBody) {
      data[item['id']] = item['empresa'];
    }

    return data;
  } catch (e) {
    return {};
  }
}

Future<List<dynamic>> getClients(String id, String token) async {
  final baseUrl = dotenv.env[userServiceURL];
  final url = Uri.parse('$baseUrl/clients/$id');

  try {
    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token'
      },
    );

    // await Future.delayed(const Duration(seconds: 1));

    final body = jsonDecode(response.body);
    final clients = body as List<dynamic>;

    return clients;
  } catch (e) {
    return [];
  }
}

Future<List<Visita>> getVisits(String id, String token) async {
  final baseUrl = dotenv.env[informesServiceURL];
  final visitas = Uri.parse('$baseUrl/ventas/visitas/vendedor/$id');

  try {
    final response = await http.get(
      visitas,
      headers: {
        'Authorization': 'Bearer $token'
      },
    );

    // await Future.delayed(const Duration(seconds: 1));

    final decodedBody = jsonDecode(response.body) as List<dynamic>;

    final List<Visita> list = [];
    for (var item in decodedBody) {
      var sugerencias = item['sugerencias'] as String;
      sugerencias.split(',');

      list.add(Visita(
        id: item['id'],
        cliente: item['cliente'],
        fecha: item['fecha'],
        hora: item['hora'],
        direccion: item['direccion'],
        hallazgos: item['hallazgos'],
        sugerencias: sugerencias.split(','),
      ));
    }

    list.sort((a, b) => b.fecha.compareTo(a.fecha));

    return list;
  } catch (e) {
    return [];
  }
}

Future<http.Response> createVisit(Object body, String id, String token) async {
  final baseUrl = dotenv.env[informesServiceURL];
  final url = Uri.parse('$baseUrl/ventas/visitas');

  try {
    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token'
      },
      body: jsonEncode(body),
    );

    return response;
  } catch (e) {
    return http.Response('Error: $e', 500);
  }
}

Future<List<Product>> getInventory(String id, String token) async {
  final baseUrl = dotenv.env[inventoryServiceURL];
  final url = Uri.parse('$baseUrl/inventario/productos');

  try {
    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token'
      },
    );

    final body = jsonDecode(response.body);
    final list = body as List<dynamic>;
    final products = list.map((p) => Product(
      id: p['id'],
      nombre: p['nombre'],
      precio: p['valor_unitario'],
      stock: p['stock_total'],
      categoria: p['categoria'],
    )).toList();

    // await Future.delayed(const Duration(seconds: 1));

    return products;
  } catch (e) {
    return [];
  }
}

Future<List<Order>> getVendorOrders(String id, String token) async {
  final baseUrl = dotenv.env[informesServiceURL];
  final url = Uri.parse('$baseUrl/ventas/vendedor/$id');

  try {
    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token'
      },
    );

    // await Future.delayed(const Duration(seconds: 1));

    final body = jsonDecode(response.body);
    final list = body as List<dynamic>;
    var orders = <Order>[];

    for (var item in list) {
      double total = 0;
      for (var product in item['productos']) {
        total += product['cantidad'] * product['valor_unitario'];
      }

      orders.add(Order(
        id: item['id'],
        cliente: item['cliente'],
        clienteId: item['cliente_id'],
        fecha: item['fecha'],
        estado: item['estado'],
        items: (item['productos'] as List<dynamic>).map((product) => OrderItem(
          id: product['producto_id'],
          nombre: product['producto'],
          cantidad: product['cantidad'],
          precio: product['valor_unitario'],
        )).toList(),
        total: total,
        fechaCreacion: item['fecha'],
      ));
    }

    orders.sort((a, b) => b.fecha.compareTo(a.fecha));

    return orders;
  } catch (e) {
    return [];
  }
}

Future<http.Response> createOrder(Object body, String id, String token) async {
  final baseUrl = dotenv.env[informesServiceURL];
  final url = Uri.parse('$baseUrl/ventas/');

  try {
    final response = await http.post(
      url,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token'
      },
      body: jsonEncode(body),
    );

    return response;
  } catch (e) {
    return http.Response('Error: $e', 500);
  }
}

Future<List<Order>> getClientOrders(String id, String token) async {
  final baseUrl = dotenv.env[informesServiceURL];
  final url = Uri.parse('$baseUrl/ventas/cliente/$id');

  try {
    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token'
      },
    );

    // await Future.delayed(const Duration(seconds: 1));

    final body = jsonDecode(response.body);
    final list = body as List<dynamic>;
    var orders = <Order>[];

    for (var item in list) {
      double total = 0;
      for (var product in item['productos']) {
        total += product['cantidad'] * product['valor_unitario'];
      }

      orders.add(Order(
        id: item['id'],
        cliente: item['cliente'],
        clienteId: item['cliente_id'],
        fecha: item['fecha'],
        estado: item['estado'],
        items: (item['productos'] as List<dynamic>).map((product) => OrderItem(
          id: product['producto_id'],
          nombre: product['producto'],
          cantidad: product['cantidad'],
          precio: product['valor_unitario'],
        )).toList(),
        total: total,
        fechaCreacion: item['fecha'],
      ));
    }

    orders.sort((a, b) => b.fecha.compareTo(a.fecha));

    return orders;
  } catch (e) {
    return [];
  }
}