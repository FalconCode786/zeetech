import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/provider_api_service.dart';

class ProviderModel {
  final String id;
  final String subcategoryName;
  final double price;
  final String? description;
  final String status;
  final DateTime createdAt;

  ProviderModel({
    required this.id,
    required this.subcategoryName,
    required this.price,
    this.description,
    required this.status,
    required this.createdAt,
  });

  factory ProviderModel.fromJson(Map<String, dynamic> json) {
    return ProviderModel(
      id: json['_id'] ?? '',
      subcategoryName:
          json['subcategoryName'] ?? json['subcategory_name'] ?? '',
      price: (json['price'] ?? 0).toDouble(),
      description: json['description'],
      status: json['status'] ?? 'active',
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'])
          : DateTime.now(),
    );
  }
}

class BookingModel {
  final String id;
  final String customerId;
  final String subcategoryName;
  final double baseAmount;
  final double additionalCharges;
  final double discountAmount;
  final String status;
  final String? problemDescription;
  final String preferredDate;
  final String? preferredTimeSlot;
  final Map<String, dynamic>? location;
  final DateTime createdAt;

  BookingModel({
    required this.id,
    required this.customerId,
    required this.subcategoryName,
    required this.baseAmount,
    required this.additionalCharges,
    required this.discountAmount,
    required this.status,
    this.problemDescription,
    required this.preferredDate,
    this.preferredTimeSlot,
    this.location,
    required this.createdAt,
  });

  double get totalAmount => baseAmount + additionalCharges - discountAmount;

  factory BookingModel.fromJson(Map<String, dynamic> json) {
    return BookingModel(
      id: json['_id'] ?? '',
      customerId: json['customerId'] ?? json['customer_id'] ?? '',
      subcategoryName:
          json['subcategoryName'] ?? json['subcategory_name'] ?? '',
      baseAmount: (json['baseAmount'] ?? json['base_amount'] ?? 0).toDouble(),
      additionalCharges:
          (json['additionalCharges'] ?? json['additional_charges'] ?? 0)
              .toDouble(),
      discountAmount: (json['discountAmount'] ?? json['discount_amount'] ?? 0)
          .toDouble(),
      status: json['status'] ?? 'pending',
      problemDescription:
          json['problemDescription'] ?? json['problem_description'],
      preferredDate: json['preferredDate'] ?? json['preferred_date'] ?? '',
      preferredTimeSlot:
          json['preferredTimeSlot'] ?? json['preferred_time_slot'],
      location: json['location'],
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'])
          : DateTime.now(),
    );
  }
}

class ProviderProvider extends ChangeNotifier {
  late ProviderApiService _providerApiService;
  final ApiService _apiService = ApiService();
  bool _initialized = false;

  List<ProviderModel> services = [];
  List<BookingModel> bookings = [];
  List<BookingModel> pendingBookings = [];
  List<BookingModel> confirmedBookings = [];
  List<BookingModel> inProgressBookings = [];
  List<BookingModel> completedBookings = [];

  Map<String, dynamic> stats = {
    'totalBookings': 0,
    'completedBookings': 0,
    'pendingBookings': 0,
    'inProgress': 0,
  };

  bool isLoadingServices = false;
  bool isLoadingBookings = false;
  bool isLoadingStats = false;
  String? errorMessage;

  ProviderProvider() {
    _initializeServices();
  }

  void _initializeServices() {
    if (_initialized) return;
    try {
      _providerApiService = ProviderApiService(_apiService.dio);
      _initialized = true;
    } catch (e) {
      errorMessage = 'Failed to initialize provider services: $e';
      notifyListeners();
    }
  }

  // ============ SERVICES MANAGEMENT ============

  Future<void> fetchServices() async {
    try {
      if (!_initialized) _initializeServices();
      isLoadingServices = true;
      errorMessage = null;
      notifyListeners();

      final response = await _providerApiService.getServices();

      if (response['data'] != null && response['data']['services'] != null) {
        services = (response['data']['services'] as List)
            .map((e) => ProviderModel.fromJson(e as Map<String, dynamic>))
            .toList();
      }

      notifyListeners();
    } catch (e) {
      errorMessage = e.toString();
      notifyListeners();
    } finally {
      isLoadingServices = false;
      notifyListeners();
    }
  }

  Future<bool> createService({
    required String subcategoryName,
    required double price,
    String? description,
  }) async {
    try {
      if (!_initialized) _initializeServices();
      isLoadingServices = true;
      errorMessage = null;
      notifyListeners();

      final response = await _providerApiService.createService(
        subcategoryName: subcategoryName,
        price: price,
        description: description,
      );

      if (response['data'] != null && response['data']['service'] != null) {
        final newService = ProviderModel.fromJson(response['data']['service']);
        services.add(newService);
        notifyListeners();
        return true;
      }
      return false;
    } catch (e) {
      errorMessage = e.toString();
      notifyListeners();
      return false;
    } finally {
      isLoadingServices = false;
      notifyListeners();
    }
  }

  Future<bool> updateService({
    required String serviceId,
    String? subcategoryName,
    double? price,
    String? description,
    String? status,
  }) async {
    try {
      if (!_initialized) _initializeServices();
      isLoadingServices = true;
      errorMessage = null;
      notifyListeners();

      await _providerApiService.updateService(
        serviceId: serviceId,
        subcategoryName: subcategoryName,
        price: price,
        description: description,
        status: status,
      );

      await fetchServices();
      return true;
    } catch (e) {
      errorMessage = e.toString();
      notifyListeners();
      return false;
    } finally {
      isLoadingServices = false;
      notifyListeners();
    }
  }

  Future<bool> deleteService(String serviceId) async {
    try {
      if (!_initialized) _initializeServices();
      isLoadingServices = true;
      errorMessage = null;
      notifyListeners();

      await _providerApiService.deleteService(serviceId);
      services.removeWhere((s) => s.id == serviceId);
      notifyListeners();
      return true;
    } catch (e) {
      errorMessage = e.toString();
      notifyListeners();
      return false;
    } finally {
      isLoadingServices = false;
      notifyListeners();
    }
  }

  // ============ BOOKINGS MANAGEMENT ============

  Future<void> fetchBookings({String? status}) async {
    try {
      if (!_initialized) _initializeServices();
      isLoadingBookings = true;
      errorMessage = null;
      notifyListeners();

      final response = await _providerApiService.getBookings(status: status);

      if (response['data'] != null && response['data']['bookings'] != null) {
        bookings = (response['data']['bookings'] as List)
            .map((e) => BookingModel.fromJson(e as Map<String, dynamic>))
            .toList();

        // Separate bookings by status
        pendingBookings = bookings
            .where((b) => b.status == 'assigned')
            .toList();
        confirmedBookings = bookings
            .where((b) => b.status == 'confirmed')
            .toList();
        inProgressBookings = bookings
            .where((b) => b.status == 'in_progress')
            .toList();
        completedBookings = bookings
            .where((b) => b.status == 'completed')
            .toList();
      }

      notifyListeners();
    } catch (e) {
      errorMessage = e.toString();
      notifyListeners();
    } finally {
      isLoadingBookings = false;
      notifyListeners();
    }
  }

  Future<bool> confirmBooking(String bookingId) async {
    try {
      if (!_initialized) _initializeServices();
      errorMessage = null;
      await _providerApiService.confirmBooking(bookingId);
      await fetchBookings();
      return true;
    } catch (e) {
      errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> startBooking(String bookingId) async {
    try {
      if (!_initialized) _initializeServices();
      errorMessage = null;
      await _providerApiService.startBooking(bookingId);
      await fetchBookings();
      return true;
    } catch (e) {
      errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> completeBooking(
    String bookingId, {
    double? additionalCharges,
  }) async {
    try {
      if (!_initialized) _initializeServices();
      errorMessage = null;
      await _providerApiService.completeBooking(
        bookingId: bookingId,
        additionalCharges: additionalCharges,
      );
      await fetchBookings();
      return true;
    } catch (e) {
      errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> cancelBooking(String bookingId, {String? reason}) async {
    try {
      if (!_initialized) _initializeServices();
      errorMessage = null;
      await _providerApiService.cancelBooking(
        bookingId: bookingId,
        reason: reason,
      );
      await fetchBookings();
      return true;
    } catch (e) {
      errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }

  // ============ STATISTICS ============

  Future<void> fetchStats() async {
    try {
      if (!_initialized) _initializeServices();
      isLoadingStats = true;
      errorMessage = null;
      notifyListeners();

      final response = await _providerApiService.getStats();

      if (response['data'] != null) {
        stats = response['data'];
      }

      notifyListeners();
    } catch (e) {
      errorMessage = e.toString();
      notifyListeners();
    } finally {
      isLoadingStats = false;
      notifyListeners();
    }
  }
}
