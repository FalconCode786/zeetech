class UserModel {
  final String id;
  final String email;
  final String phone;
  final String fullName;
  final String role;
  final String status;
  final bool isEmailVerified;
  final bool isPhoneVerified;
  final String? profileImage;
  final String? address;
  final String? city;
  final String? area;
  final num rating;
  final int totalReviews;
  final DateTime createdAt;

  UserModel({
    required this.id,
    required this.email,
    required this.phone,
    required this.fullName,
    required this.role,
    required this.status,
    required this.isEmailVerified,
    required this.isPhoneVerified,
    this.profileImage,
    this.address,
    this.city,
    this.area,
    required this.rating,
    required this.totalReviews,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['_id'] ?? json['id'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      fullName: json['fullName'] ?? json['full_name'] ?? '',
      role: json['role'] ?? 'customer',
      status: json['status'] ?? 'active',
      isEmailVerified:
          json['emailVerified'] ?? json['is_email_verified'] ?? false,
      isPhoneVerified:
          json['phoneVerified'] ?? json['is_phone_verified'] ?? false,
      profileImage: json['profileImage'] ?? json['profile_image'],
      address: json['address'],
      city: json['city'],
      area: json['area'],
      rating: json['rating'] ?? 0,
      totalReviews: json['totalReviews'] ?? json['total_reviews'] ?? 0,
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'])
          : (json['created_at'] != null
                ? DateTime.parse(json['created_at'])
                : DateTime.now()),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'phone': phone,
      'fullName': fullName,
      'role': role,
      'status': status,
      'emailVerified': isEmailVerified,
      'phoneVerified': isPhoneVerified,
      'profileImage': profileImage,
      'address': address,
      'city': city,
      'area': area,
      'rating': rating,
      'totalReviews': totalReviews,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  UserModel copyWith({
    String? id,
    String? email,
    String? phone,
    String? fullName,
    String? role,
    String? status,
    bool? isEmailVerified,
    bool? isPhoneVerified,
    String? profileImage,
    String? address,
    String? city,
    String? area,
    int? rating,
    int? totalReviews,
    DateTime? createdAt,
  }) {
    return UserModel(
      id: id ?? this.id,
      email: email ?? this.email,
      phone: phone ?? this.phone,
      fullName: fullName ?? this.fullName,
      role: role ?? this.role,
      status: status ?? this.status,
      isEmailVerified: isEmailVerified ?? this.isEmailVerified,
      isPhoneVerified: isPhoneVerified ?? this.isPhoneVerified,
      profileImage: profileImage ?? this.profileImage,
      address: address ?? this.address,
      city: city ?? this.city,
      area: area ?? this.area,
      rating: rating ?? this.rating,
      totalReviews: totalReviews ?? this.totalReviews,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
