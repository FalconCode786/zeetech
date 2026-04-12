import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_constants.dart';
import '../../core/routes/app_router.dart';
import '../../providers/booking_provider.dart';
import '../../widgets/custom_text_field.dart';
import '../../widgets/custom_button.dart';
import '../../widgets/loading_overlay.dart';

class BookingScreen extends StatefulWidget {
  final int subcategoryId;
  final String subcategoryName;
  final double basePrice;

  const BookingScreen({
    super.key,
    required this.subcategoryId,
    required this.subcategoryName,
    required this.basePrice,
  });

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  final _formKey = GlobalKey<FormState>();
  final _addressController = TextEditingController();
  final _landmarkController = TextEditingController();
  final _problemController = TextEditingController();
  final _instructionsController = TextEditingController();

  String? _selectedCity;
  String? _selectedArea;
  DateTime? _selectedDate;
  String? _selectedTimeSlot;

  final List<String> _islamabadAreas = [
    'Sector F-6',
    'Sector F-7',
    'Sector F-8',
    'Sector F-10',
    'Sector F-11',
    'Sector G-6',
    'Sector G-7',
    'Sector G-8',
    'Sector G-9',
    'Sector G-10',
    'Sector G-11',
    'Sector G-13',
    'Sector H-8',
    'Sector H-9',
    'Sector H-11',
    'Sector H-12',
    'Sector I-8',
    'Sector I-9',
    'Sector I-10',
    'Sector I-11',
    'Bahria Town',
    'DHA',
    'PWD',
    'Media Town',
    'Soan Garden',
  ];

  final List<String> _rawalpindiAreas = [
    'Saddar',
    'Commercial Market',
    'Murree Road',
    'Chaklala',
    'Westridge',
    'Satellite Town',
    'Allama Iqbal Colony',
    'Dhoke Kala Khan',
    'Lalkurti',
    'Tench Bhata',
    'People\'s Colony',
    'Afshan Colony',
    'Shamsabad',
  ];

  final List<String> _peshawarAreas = [
    'Cantt',
    'Saddar',
    'University Town',
    'Hayatabad',
    'Defence Colony',
    'Gulberg',
    'Regi Model Town',
    'DHA Peshawar',
    'Board Bazar',
  ];

  List<String> get _areas {
    switch (_selectedCity) {
      case 'Islamabad':
        return _islamabadAreas;
      case 'Rawalpindi':
        return _rawalpindiAreas;
      case 'Peshawar':
        return _peshawarAreas;
      default:
        return [];
    }
  }

  Future<void> _selectDate() async {
    final date = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 30)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: ColorScheme.light(
              primary: AppColors.primary,
              onPrimary: Colors.white,
              surface: AppColors.surface,
              onSurface: AppColors.textPrimary,
            ),
          ),
          child: child!,
        );
      },
    );

    if (date != null) {
      setState(() {
        _selectedDate = date;
      });
    }
  }

  Future<void> _submitBooking() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedDate == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select a date'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }
    if (_selectedTimeSlot == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select a time slot'),
          backgroundColor: AppColors.error,
        ),
      );
      return;
    }

    final bookingProvider = context.read<BookingProvider>();

    final success = await bookingProvider.createBooking(
      subcategoryId: widget.subcategoryId,
      address: _addressController.text,
      city: _selectedCity!,
      area: _selectedArea!,
      landmark: _landmarkController.text.isEmpty
          ? null
          : _landmarkController.text,
      preferredDate: _selectedDate!,
      preferredTimeSlot: _selectedTimeSlot!,
      problemDescription: _problemController.text.isEmpty
          ? null
          : _problemController.text,
      specialInstructions: _instructionsController.text.isEmpty
          ? null
          : _instructionsController.text,
    );

    if (success && mounted) {
      context.push(
        AppRoutes.bookingConfirmation,
        extra: {
          'bookingNumber': bookingProvider.currentBooking?.bookingNumber ?? '',
        },
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final bookingProvider = context.watch<BookingProvider>();

    return LoadingOverlay(
      isLoading: bookingProvider.isLoading,
      child: Scaffold(
        backgroundColor: AppColors.background,
        appBar: AppBar(
          title: Text(
            'Book Service',
            style: TextStyle(fontSize: 20.sp, fontWeight: FontWeight.bold),
          ),
          centerTitle: true,
          elevation: 0,
        ),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: EdgeInsets.all(16.w),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Service Info Card
                  _buildServiceInfoCard().animate().fadeIn(),

                  SizedBox(height: 24.h),

                  // Location Section
                  _buildSectionTitle(
                    'Location Details',
                  ).animate().fadeIn(delay: const Duration(milliseconds: 100)),

                  SizedBox(height: 16.h),

                  // City Dropdown
                  _buildCityDropdown().animate().fadeIn(
                    delay: const Duration(milliseconds: 200),
                  ),

                  SizedBox(height: 16.h),

                  // Area Dropdown
                  if (_selectedCity != null)
                    _buildAreaDropdown().animate().fadeIn(
                      delay: const Duration(milliseconds: 250),
                    ),

                  if (_selectedCity != null) SizedBox(height: 16.h),

                  // Address
                  CustomTextField(
                    controller: _addressController,
                    label: 'Complete Address',
                    hint: 'Enter your complete address',
                    prefixIcon: Icon(Icons.home_outlined),
                    maxLines: 2,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter your address';
                      }
                      return null;
                    },
                  ).animate().fadeIn(delay: const Duration(milliseconds: 300)),

                  SizedBox(height: 16.h),

                  // Landmark
                  CustomTextField(
                    controller: _landmarkController,
                    label: 'Landmark (Optional)',
                    hint: 'Nearby landmark',
                    prefixIcon: Icon(Icons.location_on_outlined),
                  ).animate().fadeIn(delay: const Duration(milliseconds: 350)),

                  SizedBox(height: 24.h),

                  // Schedule Section
                  _buildSectionTitle(
                    'Schedule',
                  ).animate().fadeIn(delay: const Duration(milliseconds: 400)),

                  SizedBox(height: 16.h),

                  // Date Picker
                  _buildDatePicker().animate().fadeIn(
                    delay: const Duration(milliseconds: 500),
                  ),

                  SizedBox(height: 16.h),

                  // Time Slot
                  _buildTimeSlotSelector().animate().fadeIn(
                    delay: const Duration(milliseconds: 600),
                  ),

                  SizedBox(height: 24.h),

                  // Additional Info Section
                  _buildSectionTitle(
                    'Additional Information',
                  ).animate().fadeIn(delay: const Duration(milliseconds: 700)),

                  SizedBox(height: 16.h),

                  // Problem Description
                  CustomTextField(
                    controller: _problemController,
                    label: 'Problem Description (Optional)',
                    hint: 'Describe the issue you\'re facing',
                    prefixIcon: Icon(Icons.description_outlined),
                    maxLines: 3,
                  ).animate().fadeIn(delay: const Duration(milliseconds: 800)),

                  SizedBox(height: 16.h),

                  // Special Instructions
                  CustomTextField(
                    controller: _instructionsController,
                    label: 'Special Instructions (Optional)',
                    hint: 'Any special instructions for the technician',
                    prefixIcon: Icon(Icons.notes_outlined),
                    maxLines: 2,
                  ).animate().fadeIn(delay: const Duration(milliseconds: 900)),

                  SizedBox(height: 32.h),

                  // Submit Button
                  CustomButton(
                    text: 'Confirm Booking',
                    onPressed: _submitBooking,
                  ).animate().fadeIn(delay: const Duration(milliseconds: 1000)),

                  SizedBox(height: 24.h),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildServiceInfoCard() {
    return Container(
      padding: EdgeInsets.all(16.w),
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: AppColors.primaryGradient),
        borderRadius: BorderRadius.circular(16.r),
      ),
      child: Row(
        children: [
          Container(
            width: 60.w,
            height: 60.w,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12.r),
            ),
            child: Icon(
              Icons.home_repair_service,
              color: Colors.white,
              size: 32.w,
            ),
          ),
          SizedBox(width: 16.w),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.subcategoryName,
                  style: TextStyle(
                    fontSize: 18.sp,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                SizedBox(height: 4.h),
                Text(
                  'Starting from',
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: Colors.white.withOpacity(0.8),
                  ),
                ),
                Text(
                  'PKR ${widget.basePrice.toStringAsFixed(0)}',
                  style: TextStyle(
                    fontSize: 20.sp,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: TextStyle(
        fontSize: 18.sp,
        fontWeight: FontWeight.bold,
        color: AppColors.textPrimary,
      ),
    );
  }

  Widget _buildCityDropdown() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 16.w),
      decoration: BoxDecoration(
        color: AppColors.inputBackground,
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButtonFormField<String>(
          value: _selectedCity,
          decoration: const InputDecoration(border: InputBorder.none),
          hint: Text(
            'Select City',
            style: TextStyle(color: AppColors.textHint),
          ),
          icon: Icon(Icons.location_city, color: AppColors.primary),
          validator: (value) {
            if (value == null) {
              return 'Please select a city';
            }
            return null;
          },
          items: AppConstants.supportedCities.map((city) {
            return DropdownMenuItem(value: city, child: Text(city));
          }).toList(),
          onChanged: (value) {
            setState(() {
              _selectedCity = value;
              _selectedArea = null;
            });
          },
        ),
      ),
    );
  }

  Widget _buildAreaDropdown() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 16.w),
      decoration: BoxDecoration(
        color: AppColors.inputBackground,
        borderRadius: BorderRadius.circular(12.r),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButtonFormField<String>(
          value: _selectedArea,
          decoration: const InputDecoration(border: InputBorder.none),
          hint: Text(
            'Select Area',
            style: TextStyle(color: AppColors.textHint),
          ),
          icon: Icon(Icons.map, color: AppColors.primary),
          validator: (value) {
            if (value == null) {
              return 'Please select an area';
            }
            return null;
          },
          items: _areas.map((area) {
            return DropdownMenuItem(value: area, child: Text(area));
          }).toList(),
          onChanged: (value) {
            setState(() {
              _selectedArea = value;
            });
          },
        ),
      ),
    );
  }

  Widget _buildDatePicker() {
    return GestureDetector(
      onTap: _selectDate,
      child: Container(
        padding: EdgeInsets.all(16.w),
        decoration: BoxDecoration(
          color: AppColors.inputBackground,
          borderRadius: BorderRadius.circular(12.r),
        ),
        child: Row(
          children: [
            Icon(Icons.calendar_today, color: AppColors.primary, size: 24.w),
            SizedBox(width: 12.w),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Preferred Date',
                    style: TextStyle(
                      fontSize: 12.sp,
                      color: AppColors.textSecondary,
                    ),
                  ),
                  SizedBox(height: 4.h),
                  Text(
                    _selectedDate != null
                        ? DateFormat(
                            'EEEE, MMM dd, yyyy',
                          ).format(_selectedDate!)
                        : 'Select Date',
                    style: TextStyle(
                      fontSize: 16.sp,
                      fontWeight: FontWeight.w500,
                      color: _selectedDate != null
                          ? AppColors.textPrimary
                          : AppColors.textHint,
                    ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              color: AppColors.textHint,
              size: 16.w,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeSlotSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Preferred Time Slot',
          style: TextStyle(fontSize: 14.sp, color: AppColors.textSecondary),
        ),
        SizedBox(height: 12.h),
        Wrap(
          spacing: 8.w,
          runSpacing: 8.h,
          children: AppConstants.timeSlots.map((slot) {
            final isSelected = _selectedTimeSlot == slot;
            return GestureDetector(
              onTap: () {
                setState(() {
                  _selectedTimeSlot = slot;
                });
              },
              child: Container(
                padding: EdgeInsets.symmetric(horizontal: 16.w, vertical: 12.h),
                decoration: BoxDecoration(
                  color: isSelected
                      ? AppColors.primary
                      : AppColors.inputBackground,
                  borderRadius: BorderRadius.circular(8.r),
                  border: Border.all(
                    color: isSelected ? AppColors.primary : Colors.transparent,
                  ),
                ),
                child: Text(
                  slot,
                  style: TextStyle(
                    fontSize: 14.sp,
                    fontWeight: isSelected
                        ? FontWeight.w600
                        : FontWeight.normal,
                    color: isSelected ? Colors.white : AppColors.textPrimary,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ],
    );
  }
}
