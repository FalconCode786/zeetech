import 'api_service.dart';
import '../models/booking_model.dart';

class BookingService {
  final ApiService _apiService = ApiService();

  Future<BookingModel> createBooking({
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
    final response = await _apiService.post('/bookings/', data: {
      'subcategory_id': subcategoryId,
      'address': address,
      'city': city,
      'area': area,
      'landmark': landmark,
      'preferred_date': preferredDate.toIso8601String(),
      'preferred_time_slot': preferredTimeSlot,
      'problem_description': problemDescription,
      'special_instructions': specialInstructions,
    });
    return BookingModel.fromJson(response.data);
  }

  Future<List<BookingModel>> getMyBookings({
    String? status,
    int page = 1,
    int perPage = 10,
  }) async {
    final response = await _apiService.get(
      '/bookings/my-bookings',
      queryParameters: {
        if (status != null) 'status': status,
        'page': page,
        'per_page': perPage,
      },
    );
    final List<dynamic> data = response.data;
    return data.map((json) => BookingModel.fromJson(json)).toList();
  }

  Future<BookingModel> getBookingDetail(int bookingId) async {
    final response = await _apiService.get('/bookings/$bookingId');
    return BookingModel.fromJson(response.data);
  }

  Future<BookingModel> cancelBooking(int bookingId) async {
    final response = await _apiService.put('/bookings/$bookingId/cancel');
    return BookingModel.fromJson(response.data);
  }
}
