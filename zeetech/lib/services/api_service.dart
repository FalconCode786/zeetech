import 'package:dio/dio.dart';
import '../core/constants/app_constants.dart';
import 'storage_service.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  late Dio _dio;
  final StorageService _storageService = StorageService();

  void initialize() {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.baseUrl,
        connectTimeout: const Duration(milliseconds: AppConstants.apiTimeout),
        receiveTimeout: const Duration(milliseconds: AppConstants.apiTimeout),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storageService.getToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401) {
            // Handle token refresh or logout
            await _storageService.clearAll();
          }
          return handler.next(error);
        },
      ),
    );
  }

  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      return await _dio.get(path, queryParameters: queryParameters);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Response> post(String path, {dynamic data}) async {
    try {
      print('[API] POST: ${AppConstants.baseUrl}$path');
      print('[API] Data: $data');
      final response = await _dio.post(path, data: data);
      print('[API] Response: ${response.statusCode} - ${response.data}');
      return response;
    } catch (e) {
      print('[API] Error: $e');
      throw _handleError(e);
    }
  }

  Future<Response> put(String path, {dynamic data}) async {
    try {
      return await _dio.put(path, data: data);
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Response> delete(String path) async {
    try {
      return await _dio.delete(path);
    } catch (e) {
      throw _handleError(e);
    }
  }

  String _handleError(dynamic error) {
    if (error is DioException) {
      print('[API Error] Type: ${error.type}, Message: ${error.message}');
      print('[API Error] Response status: ${error.response?.statusCode}');
      print('[API Error] Response data: ${error.response?.data}');

      if (error.response != null) {
        final data = error.response?.data;
        if (data is Map) {
          if (data.containsKey('error')) {
            return data['error'] as String;
          }
          if (data.containsKey('detail')) {
            return data['detail'] as String;
          }
        }
        return 'Server error: ${error.response?.statusCode}';
      }

      if (error.type == DioExceptionType.connectionTimeout) {
        return 'Connection timeout. Please check your internet and ensure the backend is running.';
      }
      if (error.type == DioExceptionType.receiveTimeout) {
        return 'Server took too long to respond.';
      }

      return 'Network error: ${error.message}. Please check your connection and ensure the backend is running on ${AppConstants.baseUrl}';
    }
    return error.toString();
  }
}
