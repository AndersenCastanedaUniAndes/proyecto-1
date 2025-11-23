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

Future<http.Response> getSailes(String id, String token) async {
  final baseUrl = dotenv.env[userServiceURL];
  final url = Uri.parse('$baseUrl/vendedor/$id');

  try {
    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token'
      },
    );

    return response;
  } catch (e) {
    return http.Response('Error: $e', 500);
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

    await Future.delayed(const Duration(seconds: 1));

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

    await Future.delayed(const Duration(seconds: 1));

    final body = jsonDecode(response.body);
    final clients = body as List<dynamic>;

    return clients;
  } catch (e) {
    return [];
  }
}

Future<http.Response> getVisits(String id, String token) async {
  final baseUrl = dotenv.env[informesServiceURL];
  final visitas = Uri.parse('$baseUrl/ventas/visitas/vendedor/$id');

  try {
    final response = await http.get(
      visitas,
      headers: {
        'Authorization': 'Bearer $token'
      },
    );

    await Future.delayed(const Duration(seconds: 1));

    return response;
  } catch (e) {
    return http.Response('Error: $e', 500);
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
    final products = body as List<dynamic>;
    final List<Product> productList = products.map((p) => Product(
      id: p['id'],
      nombre: p['nombre'],
      precio: p['valor_unitario'],
      stock: p['stock_total'],
      categoria: p['categoria'],
    )).toList();

    await Future.delayed(const Duration(seconds: 1));

    return productList;

    // {
    //   "id": 1,
    //   "nombre": "Producto AAA",
    //   "lote": "2023A",
    //   "sku": "SNNE2RCQH2",
    //   "stock_total": 980,
    //   "stock_minimo": 200,
    //   "status": "disponible",
    //   "bodegas": [
    //       {
    //           "id": 1,
    //           "nombre": "Bodega Norte",
    //           "direccion": "Calle 112 #45-55",
    //           "cantidad_disponible": 300,
    //           "pasillo": "A",
    //           "estante": "A12"
    //       },
    //       {
    //           "id": 2,
    //           "nombre": "Bodega Sur",
    //           "direccion": "Calle 112 Sur #45A-55",
    //           "cantidad_disponible": 680,
    //           "pasillo": "A",
    //           "estante": "A12"
    //       }
    //   ],
    //   "fecha_ultima_actualizacion": "2025-11-23T21:11:00.325657",
    //   "proveedor": "Proveedor A",
    //   "categoria": "Hormonas",
    //   "valor_unitario": 2500.0
    // },


  } catch (e) {
    return [];
  }
}

Future<http.Response> getOrders(String id, String token) async {
  final baseUrl = dotenv.env[informesServiceURL];
  final url = Uri.parse('$baseUrl/ventas/vendedor/$id');

  try {
    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token'
      },
    );

    return response;
  } catch (e) {
    return http.Response('Error: $e', 500);
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