import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:dio_cookie_manager/dio_cookie_manager.dart';
import 'package:cookie_jar/cookie_jar.dart';

import '../core/constants/app_constants.dart';
import 'storage_service.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  late Dio _dio;
  final StorageService _storageService = StorageService();

  Dio get dio => _dio;

  Future<void> initialize() async {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConstants.baseUrl,
        connectTimeout: const Duration(milliseconds: AppConstants.apiTimeout),
        receiveTimeout: const Duration(milliseconds: AppConstants.apiTimeout),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        validateStatus: (status) {
          // Don't throw for any status code, let app handle it
          return status != null && status < 500;
        },
      ),
    );

    // Configure for web platform - include credentials for cookie-based auth
    // Note: withCredentials must be true for cookies to work in CORS requests
    if (kIsWeb) {
      // For web platform, we need to ensure credentials are included
      // This is handled through the request-level options and headers
      if (kDebugMode) {
        print('[API] Configured for web - Authorization header will be used');
      }
    }

    // Add cookie manager for session management
    // Use in-memory for web, persistent for mobile
    await _initializeCookieManager();

    // Add Authorization header interceptor
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          // Add token to Authorization header if available
          try {
            final token = await _storageService.getToken();
            if (token != null && token.isNotEmpty) {
              options.headers['Authorization'] = 'Bearer $token';
              if (kDebugMode) {
                print('[API] Added Authorization header with token');
              }
            }
          } catch (e) {
            if (kDebugMode) {
              print('[API] Failed to get token for Authorization header: $e');
            }
          }

          // On web platform, ensure credentials are included for CORS
          if (kIsWeb) {
            // This helps with cross-origin cookie/credential handling
            // Note: backend must have proper CORS headers set
          }

          return handler.next(options);
        },
      ),
    );

    // Add logging and error handling interceptor
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          if (kDebugMode) {
            print(
              '[API] ${options.method} ${AppConstants.baseUrl}${options.path}',
            );
            print('[API] Headers: ${options.headers}');
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          if (kDebugMode) {
            print(
              '[API] Error: ${error.response?.statusCode} - ${error.message}',
            );
            print('[API] Response: ${error.response?.data}');
          }
          return handler.next(error);
        },
        onResponse: (response, handler) async {
          if (kDebugMode) {
            print('[API] Response Status: ${response.statusCode}');
          }
          return handler.next(response);
        },
      ),
    );
  }

  Future<Response> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      if (kDebugMode) {
        print('[API] GET: ${AppConstants.baseUrl}$path');
      }
      final response = await _dio.get(path, queryParameters: queryParameters);
      if (kDebugMode) {
        print('[API] Response: ${response.statusCode}');
      }
      return response;
    } catch (e) {
      if (kDebugMode) {
        print('[API] Error: $e');
      }
      rethrow;
    }
  }

  Future<Response> post(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      if (kDebugMode) {
        print('[API] POST: ${AppConstants.baseUrl}$path');
        print('[API] Data: $data');
      }
      final response = await _dio.post(path, data: data);
      if (kDebugMode) {
        print('[API] Response: ${response.statusCode}');
      }
      return response;
    } catch (e) {
      if (kDebugMode) {
        print('[API] Error: $e');
      }
      rethrow;
    }
  }

  Future<Response> put(
    String path, {
    required Map<String, dynamic> data,
  }) async {
    try {
      if (kDebugMode) {
        print('[API] PUT: ${AppConstants.baseUrl}$path');
        print('[API] Data: $data');
      }
      final response = await _dio.put(path, data: data);
      if (kDebugMode) {
        print('[API] Response: ${response.statusCode}');
      }
      return response;
    } catch (e) {
      if (kDebugMode) {
        print('[API] Error: $e');
      }
      rethrow;
    }
  }

  Future<Response> delete(String path, {Map<String, dynamic>? data}) async {
    try {
      if (kDebugMode) {
        print('[API] DELETE: ${AppConstants.baseUrl}$path');
      }
      final response = await _dio.delete(path, data: data);
      if (kDebugMode) {
        print('[API] Response: ${response.statusCode}');
      }
      return response;
    } catch (e) {
      if (kDebugMode) {
        print('[API] Error: $e');
      }
      rethrow;
    }
  }

  Future<void> _initializeCookieManager() async {
    try {
      if (kIsWeb) {
        // Web platform: do NOT use CookieManager (not supported on web)
        // Dio handles cookies automatically in web environments
        if (kDebugMode) {
          print(
            '[API] Web environment detected - using native cookie handling',
          );
        }
      } else {
        // Mobile/desktop: use CookieManager with persistent storage
        try {
          final cookieJar = PersistCookieJar(ignoreExpires: true);
          _dio.interceptors.add(CookieManager(cookieJar));
          if (kDebugMode) {
            print('[API] Using persistent cookie storage');
          }
          return;
        } catch (e) {
          if (kDebugMode) {
            print('[API] Failed to load persistent storage: $e');
          }
        }

        // Fallback to in-memory CookieManager
        try {
          _dio.interceptors.add(CookieManager(CookieJar()));
          if (kDebugMode) {
            print('[API] Using in-memory cookie storage');
          }
        } catch (e) {
          if (kDebugMode) {
            print('[API] Failed to add in-memory cookie manager: $e');
          }
        }
      }
    } catch (e) {
      if (kDebugMode) {
        print('[API] Cookie manager initialization failed: $e');
      }
    }
  }
}
