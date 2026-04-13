import 'api_service.dart';
import '../models/service_model.dart';

class ServiceService {
  final ApiService _apiService = ApiService();

  Future<List<ServiceCategory>> getCategories() async {
    final response = await _apiService.get('/services/categories');
    final List<dynamic> data = response.data;
    return data.map((json) => ServiceCategory.fromJson(json)).toList();
  }

  Future<ServiceCategory> getCategoryById(int id) async {
    final response = await _apiService.get('/services/categories/$id');
    return ServiceCategory.fromJson(response.data);
  }

  Future<List<ServiceSubCategory>> getSubcategories(int categoryId) async {
    final response = await _apiService.get(
      '/services/category/$categoryId/subcategories',
    );
    final List<dynamic> data = response.data;
    return data.map((json) => ServiceSubCategory.fromJson(json)).toList();
  }

  Future<ServiceSubCategory> getSubcategoryById(int id) async {
    final response = await _apiService.get('/services/subcategories/$id');
    return ServiceSubCategory.fromJson(response.data);
  }
}
