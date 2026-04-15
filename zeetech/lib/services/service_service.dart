import 'api_service.dart';
import '../models/service_model.dart';

class ServiceService {
  final ApiService _apiService = ApiService();

  Future<List<ServiceCategory>> getCategories() async {
    final response = await _apiService.get('services/categories');
    final List<dynamic> data = response.data;
    return data.map((json) => ServiceCategory.fromJson(json)).toList();
  }

  Future<ServiceCategory> getCategoryById(int id) async {
    final response = await _apiService.get('services/categories/$id');
    return ServiceCategory.fromJson(response.data);
  }

  Future<List<ServiceSubCategory>> getSubcategories(int categoryId) async {
    final response = await _apiService.get(
      'services/categories/$categoryId/subcategories',
    );
    final List<dynamic> data = response.data;
    return data.map((json) => ServiceSubCategory.fromJson(json)).toList();
  }

  Future<ServiceSubCategory> getSubcategoryById(int id) async {
    // Note: Individual subcategory endpoint doesn't exist in backend
    // This would need to be fetched from the category subcategories list
    throw UnimplementedError('Use getSubcategories() instead to fetch subcategories for a category');
  }
}
