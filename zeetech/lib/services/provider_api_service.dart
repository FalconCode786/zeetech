import 'package:dio/dio.dart';

class ProviderApiService {
  final Dio _dio;
  static const String _baseUrl = 'provider';

  ProviderApiService(this._dio);

  // ============ PROVIDER SERVICES MANAGEMENT ============

  /// Get all services offered by the provider
  Future<Map<String, dynamic>> getServices({
    int page = 1,
    int limit = 10,
  }) async {
    try {
      final response = await _dio.get(
        '$_baseUrl/services',
        queryParameters: {'page': page, 'limit': limit},
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  /// Create a new service offering
  Future<Map<String, dynamic>> createService({
    required String subcategoryName,
    required double price,
    String? description,
  }) async {
    try {
      final response = await _dio.post(
        '$_baseUrl/services',
        data: {
          'subcategoryName': subcategoryName,
          'price': price,
          'description': description,
        },
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  /// Update a provider's service
  Future<Map<String, dynamic>> updateService({
    required String serviceId,
    String? subcategoryName,
    double? price,
    String? description,
    String? status,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (subcategoryName != null) data['subcategoryName'] = subcategoryName;
      if (price != null) data['price'] = price;
      if (description != null) data['description'] = description;
      if (status != null) data['status'] = status;

      final response = await _dio.put(
        '$_baseUrl/services/$serviceId',
        data: data,
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  /// Delete a provider's service
  Future<Map<String, dynamic>> deleteService(String serviceId) async {
    try {
      final response = await _dio.delete('$_baseUrl/services/$serviceId');
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  // ============ PROVIDER BOOKINGS MANAGEMENT ============

  /// Get all bookings for the provider
  Future<Map<String, dynamic>> getBookings({
    int page = 1,
    int limit = 10,
    String? status,
  }) async {
    try {
      final Map<String, dynamic> queryParams = {'page': page, 'limit': limit};
      if (status != null) queryParams['status'] = status;

      final response = await _dio.get(
        '$_baseUrl/bookings',
        queryParameters: queryParams,
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  /// Get specific booking details
  Future<Map<String, dynamic>> getBookingDetail(String bookingId) async {
    try {
      final response = await _dio.get('$_baseUrl/bookings/$bookingId');
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  /// Confirm/accept a booking
  Future<Map<String, dynamic>> confirmBooking(String bookingId) async {
    try {
      final response = await _dio.post('$_baseUrl/bookings/$bookingId/confirm');
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  /// Start work on a booking
  Future<Map<String, dynamic>> startBooking(String bookingId) async {
    try {
      final response = await _dio.post('$_baseUrl/bookings/$bookingId/start');
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  /// Complete a booking
  Future<Map<String, dynamic>> completeBooking({
    required String bookingId,
    double? additionalCharges,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (additionalCharges != null)
        data['additionalCharges'] = additionalCharges;

      final response = await _dio.post(
        '$_baseUrl/bookings/$bookingId/complete',
        data: data,
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  /// Cancel a booking
  Future<Map<String, dynamic>> cancelBooking({
    required String bookingId,
    String? reason,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (reason != null) data['reason'] = reason;

      final response = await _dio.post(
        '$_baseUrl/bookings/$bookingId/cancel',
        data: data,
      );
      return response.data;
    } catch (e) {
      rethrow;
    }
  }

  // ============ PROVIDER STATISTICS ============

  /// Get provider statistics
  Future<Map<String, dynamic>> getStats() async {
    try {
      final response = await _dio.get('$_baseUrl/stats');
      return response.data;
    } catch (e) {
      rethrow;
    }
  }
}
