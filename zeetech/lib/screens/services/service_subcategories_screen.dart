import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../core/routes/app_router.dart';
import '../../providers/service_provider.dart';
import '../../widgets/service_subcategory_card.dart';
import '../../widgets/shimmer_loading.dart';
import '../../widgets/custom_app_bar.dart';

class ServiceSubcategoriesScreen extends StatefulWidget {
  final int categoryId;
  final String categoryName;

  const ServiceSubcategoriesScreen({
    super.key,
    required this.categoryId,
    required this.categoryName,
  });

  @override
  State<ServiceSubcategoriesScreen> createState() =>
      _ServiceSubcategoriesScreenState();
}

class _ServiceSubcategoriesScreenState
    extends State<ServiceSubcategoriesScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ServiceProvider>().loadSubcategories(widget.categoryId);
    });
  }

  @override
  Widget build(BuildContext context) {
    final serviceProvider = context.watch<ServiceProvider>();

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: CustomAppBar(
        title: widget.categoryName,
        showBackButton: true,
        onBackPressed: () => context.pop(),
      ),
      body: SafeArea(
        child: Padding(
          padding: EdgeInsets.all(16.w),
          child: serviceProvider.isLoading
              ? _buildShimmerList()
              : _buildSubcategoriesList(serviceProvider),
        ),
      ),
    );
  }

  Widget _buildSubcategoriesList(ServiceProvider serviceProvider) {
    if (serviceProvider.subcategories.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.construction, size: 64.w, color: AppColors.textHint),
            SizedBox(height: 16.h),
            Text(
              'No services available',
              style: TextStyle(fontSize: 18.sp, color: AppColors.textSecondary),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      itemCount: serviceProvider.subcategories.length,
      itemBuilder: (context, index) {
        final subcategory = serviceProvider.subcategories[index];
        return ServiceSubcategoryCard(
              subcategory: subcategory,
              onTap: () {
                context.push(
                  AppRoutes.booking,
                  extra: {
                    'subcategoryId': subcategory.id,
                    'subcategoryName': subcategory.name,
                    'basePrice': subcategory.basePrice,
                  },
                );
              },
            )
            .animate()
            .fadeIn(delay: Duration(milliseconds: index * 100))
            .slideX(begin: 0.3, end: 0);
      },
    );
  }

  Widget _buildShimmerList() {
    return ListView.builder(
      itemCount: 4,
      itemBuilder: (context, index) {
        return Padding(
          padding: EdgeInsets.only(bottom: 16.h),
          child: ShimmerLoading(
            child: Container(
              height: 120.h,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16.r),
              ),
            ),
          ),
        );
      },
    );
  }
}
