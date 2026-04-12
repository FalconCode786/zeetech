import 'package:flutter/material.dart';
import '../models/booking_model.dart';
import '../services/booking_service.dart';

class BookingProvider extends ChangeNotifier {
  final BookingService _bookingService = BookingService();

  List<BookingModel> _bookings = [];
  BookingModel? _currentBooking;
  bool _isLoading = false;
  String? _error;
  int _currentPage = 1;
  bool _hasMore = true;

  List<BookingModel> get bookings => _bookings;
  BookingModel? get currentBooking => _currentBooking;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasMore => _hasMore;

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  void _setError(String? value) {
    _error = value;
    notifyListeners();
  }

  Future<bool> createBooking({
    required int subcategoryId,
    required String address,
    required String city,
    required String area,
    String? landmark,
    required DateTime preferredDate,
    required String preferredTimeSlot,
    String? problemDescription,
    String? specialInstructions,
  }) async {
    try {
      _setLoading(true);
      _setError(null);

      final booking = await _bookingService.createBooking(
        subcategoryId: subcategoryId,
        address: address,
        city: city,
        area: area,
        landmark: landmark,
        preferredDate: preferredDate,
        preferredTimeSlot: preferredTimeSlot,
        problemDescription: problemDescription,
        specialInstructions: specialInstructions,
      );

      _currentBooking = booking;
      _bookings.insert(0, booking);

      _setLoading(false);
      notifyListeners();
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  Future<void> loadMyBookings({
    String? status,
    bool refresh = false,
  }) async {
    try {
      if (refresh) {
        _currentPage = 1;
        _bookings = [];
        _hasMore = true;
      }

      if (!_hasMore && !refresh) return;

      _setLoading(true);
      _setError(null);

      final newBookings = await _bookingService.getMyBookings(
        status: status,
        page: _currentPage,
      );

      if (newBookings.isEmpty) {
        _hasMore = false;
      } else {
        _bookings.addAll(newBookings);
        _currentPage++;
      }

      _setLoading(false);
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
    }
  }

  Future<void> getBookingDetail(int bookingId) async {
    try {
      _setLoading(true);
      _setError(null);

      _currentBooking = await _bookingService.getBookingDetail(bookingId);

      _setLoading(false);
      notifyListeners();
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
    }
  }

  Future<bool> cancelBooking(int bookingId) async {
    try {
      _setLoading(true);
      _setError(null);

      final updatedBooking = await _bookingService.cancelBooking(bookingId);

      // Update in list
      final index = _bookings.indexWhere((b) => b.id == bookingId);
      if (index != -1) {
        _bookings[index] = updatedBooking;
      }

      _currentBooking = updatedBooking;

      _setLoading(false);
      notifyListeners();
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  List<BookingModel> getBookingsByStatus(String status) {
    return _bookings.where((b) => b.status == status).toList();
  }

  void clearCurrentBooking() {
    _currentBooking = null;
    notifyListeners();
  }
}
