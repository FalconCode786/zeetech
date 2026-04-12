import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../../core/constants/app_colors.dart';

class ServiceDetailScreen extends StatelessWidget {
  final int subcategoryId;

  const ServiceDetailScreen({super.key, required this.subcategoryId});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(
          'Service Details',
          style: TextStyle(fontSize: 20.sp, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        elevation: 0,
      ),
      body: Center(
        child: Text(
          'Service Detail - ID: $subcategoryId',
          style: TextStyle(fontSize: 18.sp),
        ),
      ),
    );
  }
}
