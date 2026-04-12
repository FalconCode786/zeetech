import 'package:flutter/material.dart';
import '../models/service_model.dart';
import '../services/service_service.dart';

class ServiceProvider extends ChangeNotifier {
  final ServiceService _serviceService = ServiceService();

  List<ServiceCategory> _categories = [];
  List<ServiceSubCategory> _subcategories = [];
  ServiceCategory? _selectedCategory;
  ServiceSubCategory? _selectedSubcategory;
  bool _isLoading = false;
  String? _error;

  List<ServiceCategory> get categories => _categories;
  List<ServiceSubCategory> get subcategories => _subcategories;
  ServiceCategory? get selectedCategory => _selectedCategory;
  ServiceSubCategory? get selectedSubcategory => _selectedSubcategory;
  bool get isLoading => _isLoading;
  String? get error => _error;

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  void _setError(String? value) {
    _error = value;
    notifyListeners();
  }

  Future<void> loadCategories() async {
    try {
      _setLoading(true);
      _setError(null);

      _categories = await _serviceService.getCategories();

      _setLoading(false);
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
    }
  }

  Future<void> loadSubcategories(int categoryId) async {
    try {
      _setLoading(true);
      _setError(null);

      _subcategories = await _serviceService.getSubcategories(categoryId);

      _setLoading(false);
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
    }
  }

  void selectCategory(ServiceCategory category) {
    _selectedCategory = category;
    notifyListeners();
  }

  void selectSubcategory(ServiceSubCategory subcategory) {
    _selectedSubcategory = subcategory;
    notifyListeners();
  }

  void clearSelection() {
    _selectedCategory = null;
    _selectedSubcategory = null;
    notifyListeners();
  }

  ServiceCategory? getCategoryById(int id) {
    try {
      return _categories.firstWhere((c) => c.id == id);
    } catch (e) {
      return null;
    }
  }

  ServiceSubCategory? getSubcategoryById(int id) {
    try {
      return _subcategories.firstWhere((s) => s.id == id);
    } catch (e) {
      return null;
    }
  }
}
