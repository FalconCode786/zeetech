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

  // --- CRUD Operations added below ---

  // CREATE Category
  Future<bool> createCategory(ServiceCategory category) async {
    try {
      _setLoading(true);
      // await _serviceService.createCategory(category); // Call to service if implemented
      _categories.add(category);
      _setLoading(false);
      notifyListeners();
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  // UPDATE Category
  Future<bool> updateCategory(int id, ServiceCategory updatedCategory) async {
    try {
      _setLoading(true);
      // await _serviceService.updateCategory(id, updatedCategory); // Call to service if implemented
      final index = _categories.indexWhere((c) => c.id == id);
      if (index != -1) {
        _categories[index] = updatedCategory;
      }
      _setLoading(false);
      notifyListeners();
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  // DELETE Category
  Future<bool> deleteCategory(int id) async {
    try {
      _setLoading(true);
      // await _serviceService.deleteCategory(id); // Call to service if implemented
      _categories.removeWhere((c) => c.id == id);
      _setLoading(false);
      notifyListeners();
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  // CREATE SubCategory
  Future<bool> createSubcategory(ServiceSubCategory subcategory) async {
    try {
      _setLoading(true);
      // await _serviceService.createSubcategory(subcategory); // Call to service if implemented
      _subcategories.add(subcategory);
      _setLoading(false);
      notifyListeners();
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  // UPDATE SubCategory
  Future<bool> updateSubcategory(
    int id,
    ServiceSubCategory updatedSubcategory,
  ) async {
    try {
      _setLoading(true);
      // await _serviceService.updateSubcategory(id, updatedSubcategory); // Call to service if implemented
      final index = _subcategories.indexWhere((s) => s.id == id);
      if (index != -1) {
        _subcategories[index] = updatedSubcategory;
      }
      _setLoading(false);
      notifyListeners();
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }

  // DELETE SubCategory
  Future<bool> deleteSubcategory(int id) async {
    try {
      _setLoading(true);
      // await _serviceService.deleteSubcategory(id); // Call to service if implemented
      _subcategories.removeWhere((s) => s.id == id);
      _setLoading(false);
      notifyListeners();
      return true;
    } catch (e) {
      _setLoading(false);
      _setError(e.toString());
      return false;
    }
  }
}
