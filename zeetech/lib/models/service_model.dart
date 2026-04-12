class ServiceCategory {
  final int id;
  final String name;
  final String? nameUrdu;
  final String? description;
  final String? icon;
  final String? image;
  final int displayOrder;
  final bool isActive;
  final List<ServiceSubCategory> subcategories;

  ServiceCategory({
    required this.id,
    required this.name,
    this.nameUrdu,
    this.description,
    this.icon,
    this.image,
    required this.displayOrder,
    required this.isActive,
    this.subcategories = const [],
  });

  factory ServiceCategory.fromJson(Map<String, dynamic> json) {
    return ServiceCategory(
      id: json['id'],
      name: json['name'],
      nameUrdu: json['name_urdu'],
      description: json['description'],
      icon: json['icon'],
      image: json['image'],
      displayOrder: json['display_order'] ?? 0,
      isActive: json['is_active'] ?? true,
      subcategories: (json['subcategories'] as List?)
          ?.map((e) => ServiceSubCategory.fromJson(e))
          .toList() ?? [],
    );
  }
}

class ServiceSubCategory {
  final int id;
  final int categoryId;
  final String name;
  final String? nameUrdu;
  final String? description;
  final String? image;
  final double basePrice;
  final String priceUnit;
  final String? estimatedDuration;
  final String? warrantyPeriod;
  final int displayOrder;
  final bool isActive;

  ServiceSubCategory({
    required this.id,
    required this.categoryId,
    required this.name,
    this.nameUrdu,
    this.description,
    this.image,
    required this.basePrice,
    required this.priceUnit,
    this.estimatedDuration,
    this.warrantyPeriod,
    required this.displayOrder,
    required this.isActive,
  });

  factory ServiceSubCategory.fromJson(Map<String, dynamic> json) {
    return ServiceSubCategory(
      id: json['id'],
      categoryId: json['category_id'],
      name: json['name'],
      nameUrdu: json['name_urdu'],
      description: json['description'],
      image: json['image'],
      basePrice: (json['base_price'] ?? 0).toDouble(),
      priceUnit: json['price_unit'] ?? 'fixed',
      estimatedDuration: json['estimated_duration'],
      warrantyPeriod: json['warranty_period'],
      displayOrder: json['display_order'] ?? 0,
      isActive: json['is_active'] ?? true,
    );
  }
}
