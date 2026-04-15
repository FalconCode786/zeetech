import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../widgets/custom_app_bar.dart';

class MyAddressesScreen extends StatefulWidget {
  const MyAddressesScreen({super.key});

  @override
  State<MyAddressesScreen> createState() => _MyAddressesScreenState();
}

class _MyAddressesScreenState extends State<MyAddressesScreen> {
  List<Map<String, String>> addresses = [
    {
      'title': 'Home',
      'address': 'G-12 Ghazali Road, Islamabad',
      'phone': '03005518622',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: CustomAppBar(
        title: 'My Addresses',
        onBackPressed: () => context.pop(),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddAddressDialog(),
        child: const Icon(Icons.add),
      ),
      body: SafeArea(
        child: addresses.isEmpty
            ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      Icons.location_off,
                      size: 64.w,
                      color: AppColors.textHint,
                    ),
                    SizedBox(height: 16.h),
                    Text(
                      'No Addresses',
                      style: TextStyle(
                        fontSize: 18.sp,
                        fontWeight: FontWeight.bold,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    SizedBox(height: 24.h),
                    ElevatedButton.icon(
                      onPressed: () => _showAddAddressDialog(),
                      icon: const Icon(Icons.add),
                      label: const Text('Add Address'),
                    ),
                  ],
                ),
              )
            : ListView.builder(
                padding: EdgeInsets.all(16.w),
                itemCount: addresses.length,
                itemBuilder: (context, index) {
                  final address = addresses[index];
                  return _buildAddressCard(address, index);
                },
              ),
      ),
    );
  }

  Widget _buildAddressCard(Map<String, String> address, int index) {
    return Container(
      margin: EdgeInsets.only(bottom: 12.h),
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12.r),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                address['title'] ?? '',
                style: TextStyle(
                  fontSize: 16.sp,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              PopupMenuButton(
                itemBuilder: (context) => [
                  PopupMenuItem(
                    child: const Text('Edit'),
                    onTap: () => _showAddAddressDialog(address: address),
                  ),
                  PopupMenuItem(
                    child: const Text('Delete'),
                    onTap: () {
                      setState(() => addresses.removeAt(index));
                    },
                  ),
                ],
              ),
            ],
          ),
          SizedBox(height: 8.h),
          Text(
            address['address'] ?? '',
            style: TextStyle(fontSize: 13.sp, color: AppColors.textSecondary),
          ),
          SizedBox(height: 8.h),
          Text(
            address['phone'] ?? '',
            style: TextStyle(fontSize: 13.sp, color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }

  void _showAddAddressDialog({Map<String, String>? address}) {
    final titleController = TextEditingController(text: address?['title']);
    final addressController = TextEditingController(text: address?['address']);
    final phoneController = TextEditingController(text: address?['phone']);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          address != null ? 'Edit Address' : 'Add New Address',
          style: TextStyle(fontSize: 18.sp, fontWeight: FontWeight.bold),
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: titleController,
                decoration: InputDecoration(
                  labelText: 'Title (e.g., Home)',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                ),
              ),
              SizedBox(height: 12.h),
              TextField(
                controller: addressController,
                decoration: InputDecoration(
                  labelText: 'Address',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                ),
                maxLines: 2,
              ),
              SizedBox(height: 12.h),
              TextField(
                controller: phoneController,
                decoration: InputDecoration(
                  labelText: 'Phone Number',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8.r),
                  ),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => context.pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              if (titleController.text.isNotEmpty &&
                  addressController.text.isNotEmpty) {
                setState(() {
                  final newAddress = {
                    'title': titleController.text,
                    'address': addressController.text,
                    'phone': phoneController.text,
                  };
                  if (address != null) {
                    final index = addresses.indexOf(address);
                    addresses[index] = newAddress;
                  } else {
                    addresses.add(newAddress);
                  }
                });
                context.pop();
              }
            },
            child: Text(address != null ? 'Update' : 'Add'),
          ),
        ],
      ),
    );
  }
}
