class BookingModel {
  final int id;
  final String bookingNumber;
  final int customerId;
  final int subcategoryId;
  final int? providerId;
  final String status;
  final String paymentStatus;
  final String address;
  final String city;
  final String area;
  final String? landmark;
  final DateTime preferredDate;
  final String preferredTimeSlot;
  final double baseAmount;
  final double additionalCharges;
  final double discountAmount;
  final double totalAmount;
  final String? problemDescription;
  final String? specialInstructions;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final DateTime? confirmedAt;
  final DateTime? completedAt;
  final int? customerRating;
  final String? customerReview;

  BookingModel({
    required this.id,
    required this.bookingNumber,
    required this.customerId,
    required this.subcategoryId,
    this.providerId,
    required this.status,
    required this.paymentStatus,
    required this.address,
    required this.city,
    required this.area,
    this.landmark,
    required this.preferredDate,
    required this.preferredTimeSlot,
    required this.baseAmount,
    required this.additionalCharges,
    required this.discountAmount,
    required this.totalAmount,
    this.problemDescription,
    this.specialInstructions,
    required this.createdAt,
    this.updatedAt,
    this.confirmedAt,
    this.completedAt,
    this.customerRating,
    this.customerReview,
  });

  factory BookingModel.fromJson(Map<String, dynamic> json) {
    return BookingModel(
      id: json['id'],
      bookingNumber: json['booking_number'],
      customerId: json['customer_id'],
      subcategoryId: json['subcategory_id'],
      providerId: json['provider_id'],
      status: json['status'],
      paymentStatus: json['payment_status'],
      address: json['address'],
      city: json['city'],
      area: json['area'],
      landmark: json['landmark'],
      preferredDate: DateTime.parse(json['preferred_date']),
      preferredTimeSlot: json['preferred_time_slot'],
      baseAmount: (json['base_amount'] ?? 0).toDouble(),
      additionalCharges: (json['additional_charges'] ?? 0).toDouble(),
      discountAmount: (json['discount_amount'] ?? 0).toDouble(),
      totalAmount: (json['total_amount'] ?? 0).toDouble(),
      problemDescription: json['problem_description'],
      specialInstructions: json['special_instructions'],
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: json['updated_at'] != null ? DateTime.parse(json['updated_at']) : null,
      confirmedAt: json['confirmed_at'] != null ? DateTime.parse(json['confirmed_at']) : null,
      completedAt: json['completed_at'] != null ? DateTime.parse(json['completed_at']) : null,
      customerRating: json['customer_rating'],
      customerReview: json['customer_review'],
    );
  }

  String get statusDisplay {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'confirmed':
        return 'Confirmed';
      case 'assigned':
        return 'Assigned';
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  String get paymentStatusDisplay {
    switch (paymentStatus) {
      case 'pending':
        return 'Pending';
      case 'paid':
        return 'Paid';
      case 'failed':
        return 'Failed';
      case 'refunded':
        return 'Refunded';
      default:
        return paymentStatus;
    }
  }
}
