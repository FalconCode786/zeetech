import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/provider_provider.dart';
import '../../widgets/custom_app_bar.dart';

class ProviderBookingsScreen extends StatefulWidget {
  const ProviderBookingsScreen({super.key});

  @override
  State<ProviderBookingsScreen> createState() => _ProviderBookingsScreenState();
}

class _ProviderBookingsScreenState extends State<ProviderBookingsScreen> {
  String selectedFilter = 'all';

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<ProviderProvider>().fetchBookings();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: CustomAppBar(
        title: 'Manage Bookings',
        showBackButton: true,
        onBackPressed: () => context.pop(),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 600),
            child: Column(
              children: [
                // Filter Chips
                SizedBox(
                  height: 50.h,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    padding: EdgeInsets.symmetric(horizontal: 16.w),
                    children: [
                      _buildFilterChip('All', 'all'),
                      SizedBox(width: 8.w),
                      _buildFilterChip('Pending', 'assigned'),
                      SizedBox(width: 8.w),
                      _buildFilterChip('Confirmed', 'confirmed'),
                      SizedBox(width: 8.w),
                      _buildFilterChip('In Progress', 'in_progress'),
                      SizedBox(width: 8.w),
                      _buildFilterChip('Completed', 'completed'),
                    ],
                  ),
                ),
                SizedBox(height: 12.h),

                // Bookings List
                Expanded(
                  child: Consumer<ProviderProvider>(
                    builder: (context, provider, _) {
                      if (provider.isLoadingBookings &&
                          provider.bookings.isEmpty) {
                        return Center(
                          child: CircularProgressIndicator(
                            valueColor: AlwaysStoppedAnimation<Color>(
                              AppColors.primary,
                            ),
                          ),
                        );
                      }

                      List<dynamic> displayBookings = provider.bookings;

                      if (selectedFilter != 'all') {
                        displayBookings = provider.bookings
                            .where((b) => b.status == selectedFilter)
                            .toList();
                      }

                      if (displayBookings.isEmpty) {
                        return Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.inbox,
                                size: 64.w,
                                color: AppColors.textHint,
                              ),
                              SizedBox(height: 16.h),
                              Text(
                                'No bookings found',
                                style: TextStyle(
                                  fontSize: 16.sp,
                                  color: AppColors.textHint,
                                ),
                              ),
                            ],
                          ),
                        );
                      }

                      return ListView.builder(
                        padding: EdgeInsets.symmetric(horizontal: 16.w),
                        itemCount: displayBookings.length,
                        itemBuilder: (context, index) {
                          return _buildBookingCard(
                            context,
                            displayBookings[index],
                            provider,
                          );
                        },
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFilterChip(String label, String value) {
    return FilterChip(
      label: Text(
        label,
        style: TextStyle(
          fontSize: 12.sp,
          fontWeight: FontWeight.w600,
          color: selectedFilter == value
              ? Colors.white
              : AppColors.textSecondary,
        ),
      ),
      selected: selectedFilter == value,
      onSelected: (selected) {
        setState(() {
          selectedFilter = value;
        });
      },
      backgroundColor: AppColors.surface,
      selectedColor: AppColors.primary,
      side: BorderSide(
        color: selectedFilter == value ? AppColors.primary : Colors.transparent,
      ),
    );
  }

  Widget _buildBookingCard(
    BuildContext context,
    dynamic booking,
    ProviderProvider provider,
  ) {
    final statusColor = _getStatusColor(booking.status);
    final statusLabel = _getStatusLabel(booking.status);

    return GestureDetector(
      onTap: () => _showBookingDetailsDialog(context, booking, provider),
      child: Container(
        margin: EdgeInsets.only(bottom: 12.h),
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
        child: Padding(
          padding: EdgeInsets.all(12.w),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          booking.subcategoryName,
                          style: TextStyle(
                            fontSize: 14.sp,
                            fontWeight: FontWeight.bold,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        SizedBox(height: 4.h),
                        Text(
                          'Booking ID: ${booking.id.substring(0, 8)}...',
                          style: TextStyle(
                            fontSize: 11.sp,
                            color: AppColors.textHint,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: EdgeInsets.symmetric(
                      horizontal: 8.w,
                      vertical: 4.h,
                    ),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8.r),
                    ),
                    child: Text(
                      statusLabel,
                      style: TextStyle(
                        fontSize: 10.sp,
                        fontWeight: FontWeight.bold,
                        color: statusColor,
                      ),
                    ),
                  ),
                ],
              ),
              SizedBox(height: 8.h),
              Divider(color: AppColors.surface.withOpacity(0.5)),
              SizedBox(height: 8.h),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Schedule',
                        style: TextStyle(
                          fontSize: 11.sp,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      SizedBox(height: 2.h),
                      Text(
                        booking.preferredDate,
                        style: TextStyle(
                          fontSize: 12.sp,
                          fontWeight: FontWeight.w600,
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        'Amount',
                        style: TextStyle(
                          fontSize: 11.sp,
                          color: AppColors.textSecondary,
                        ),
                      ),
                      SizedBox(height: 2.h),
                      Text(
                        'Rs.${booking.totalAmount.toStringAsFixed(0)}',
                        style: TextStyle(
                          fontSize: 13.sp,
                          fontWeight: FontWeight.bold,
                          color: AppColors.primary,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              SizedBox(height: 12.h),
              _buildActionButtons(context, booking, provider),
            ],
          ),
        ),
      ),
    ).animate().fadeIn(duration: const Duration(milliseconds: 300));
  }

  Widget _buildActionButtons(
    BuildContext context,
    dynamic booking,
    ProviderProvider provider,
  ) {
    if (booking.status == 'assigned') {
      return Row(
        children: [
          Expanded(
            child: OutlinedButton(
              onPressed: () => _confirmBooking(context, booking, provider),
              child: Text('Confirm', style: TextStyle(fontSize: 12.sp)),
            ),
          ),
          SizedBox(width: 8.w),
          Expanded(
            child: OutlinedButton(
              onPressed: () => _rejectBooking(context, booking, provider),
              style: OutlinedButton.styleFrom(
                side: BorderSide(color: AppColors.error),
              ),
              child: Text(
                'Reject',
                style: TextStyle(fontSize: 12.sp, color: AppColors.error),
              ),
            ),
          ),
        ],
      );
    } else if (booking.status == 'confirmed') {
      return SizedBox(
        width: double.infinity,
        child: ElevatedButton(
          onPressed: () => _startBooking(context, booking, provider),
          child: Text('Start Work', style: TextStyle(fontSize: 12.sp)),
        ),
      );
    } else if (booking.status == 'in_progress') {
      return SizedBox(
        width: double.infinity,
        child: ElevatedButton(
          onPressed: () => _completeBooking(context, booking, provider),
          style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
          child: Text('Complete', style: TextStyle(fontSize: 12.sp)),
        ),
      );
    }
    return const SizedBox.shrink();
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'assigned':
        return Colors.orange;
      case 'confirmed':
        return Colors.blue;
      case 'in_progress':
        return Colors.purple;
      case 'completed':
        return Colors.green;
      default:
        return AppColors.textSecondary;
    }
  }

  String _getStatusLabel(String status) {
    switch (status) {
      case 'assigned':
        return 'PENDING';
      case 'confirmed':
        return 'CONFIRMED';
      case 'in_progress':
        return 'IN PROGRESS';
      case 'completed':
        return 'COMPLETED';
      default:
        return status.toUpperCase();
    }
  }

  void _showBookingDetailsDialog(
    BuildContext context,
    dynamic booking,
    ProviderProvider provider,
  ) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Booking Details',
          style: TextStyle(
            fontSize: 18.sp,
            fontWeight: FontWeight.bold,
            color: AppColors.textPrimary,
          ),
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _detailRow('Service', booking.subcategoryName),
              _detailRow('Status', _getStatusLabel(booking.status)),
              _detailRow('Date', booking.preferredDate),
              if (booking.preferredTimeSlot != null)
                _detailRow('Time', booking.preferredTimeSlot),
              _detailRow(
                'Base Amount',
                'Rs.${booking.baseAmount.toStringAsFixed(0)}',
              ),
              if (booking.additionalCharges > 0)
                _detailRow(
                  'Additional Charges',
                  'Rs.${booking.additionalCharges.toStringAsFixed(0)}',
                ),
              if (booking.discountAmount > 0)
                _detailRow(
                  'Discount',
                  '-Rs.${booking.discountAmount.toStringAsFixed(0)}',
                ),
              Divider(),
              _detailRow(
                'Total Amount',
                'Rs.${booking.totalAmount.toStringAsFixed(0)}',
                isBold: true,
              ),
              if (booking.problemDescription != null) ...[
                SizedBox(height: 12.h),
                Text(
                  'Problem Description',
                  style: TextStyle(
                    fontSize: 12.sp,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textSecondary,
                  ),
                ),
                SizedBox(height: 4.h),
                Text(
                  booking.problemDescription,
                  style: TextStyle(
                    fontSize: 12.sp,
                    color: AppColors.textPrimary,
                  ),
                ),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => context.pop(),
            child: Text('Close', style: TextStyle(fontSize: 14.sp)),
          ),
        ],
      ),
    );
  }

  Widget _detailRow(String label, String value, {bool isBold = false}) {
    return Padding(
      padding: EdgeInsets.symmetric(vertical: 4.h),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 12.sp,
              color: AppColors.textSecondary,
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 12.sp,
              fontWeight: isBold ? FontWeight.bold : FontWeight.w600,
              color: isBold ? AppColors.primary : AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }

  void _confirmBooking(
    BuildContext context,
    dynamic booking,
    ProviderProvider provider,
  ) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Confirm Booking',
          style: TextStyle(fontSize: 16.sp, fontWeight: FontWeight.bold),
        ),
        content: Text(
          'Are you sure you want to confirm this booking?',
          style: TextStyle(fontSize: 14.sp),
        ),
        actions: [
          TextButton(
            onPressed: () => context.pop(),
            child: Text('Cancel', style: TextStyle(fontSize: 14.sp)),
          ),
          ElevatedButton(
            onPressed: () async {
              final success = await provider.confirmBooking(booking.id);
              if (success) {
                if (!context.mounted) return;
                context.pop();
                context.pop();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Booking confirmed')),
                );
              } else {
                if (!context.mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'Error: ${provider.errorMessage ?? "Failed to confirm booking"}',
                    ),
                  ),
                );
              }
            },
            child: Text('Confirm', style: TextStyle(fontSize: 14.sp)),
          ),
        ],
      ),
    );
  }

  void _startBooking(
    BuildContext context,
    dynamic booking,
    ProviderProvider provider,
  ) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Start Work',
          style: TextStyle(fontSize: 16.sp, fontWeight: FontWeight.bold),
        ),
        content: Text(
          'Start work on this booking?',
          style: TextStyle(fontSize: 14.sp),
        ),
        actions: [
          TextButton(
            onPressed: () => context.pop(),
            child: Text('Cancel', style: TextStyle(fontSize: 14.sp)),
          ),
          ElevatedButton(
            onPressed: () async {
              final success = await provider.startBooking(booking.id);
              if (success) {
                if (!context.mounted) return;
                context.pop();
                context.pop();
                ScaffoldMessenger.of(
                  context,
                ).showSnackBar(const SnackBar(content: Text('Work started')));
              } else {
                if (!context.mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'Error: ${provider.errorMessage ?? "Failed to start booking"}',
                    ),
                  ),
                );
              }
            },
            child: Text('Start', style: TextStyle(fontSize: 14.sp)),
          ),
        ],
      ),
    );
  }

  void _completeBooking(
    BuildContext context,
    dynamic booking,
    ProviderProvider provider,
  ) {
    final chargesController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Complete Booking',
          style: TextStyle(fontSize: 16.sp, fontWeight: FontWeight.bold),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Mark this booking as complete?',
              style: TextStyle(fontSize: 14.sp),
            ),
            SizedBox(height: 12.h),
            TextField(
              controller: chargesController,
              keyboardType: const TextInputType.numberWithOptions(
                decimal: true,
              ),
              decoration: InputDecoration(
                hintText: 'Additional charges (optional)',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.r),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => context.pop(),
            child: Text('Cancel', style: TextStyle(fontSize: 14.sp)),
          ),
          ElevatedButton(
            onPressed: () async {
              final charges = chargesController.text.isEmpty
                  ? null
                  : double.tryParse(chargesController.text);
              final success = await provider.completeBooking(
                booking.id,
                additionalCharges: charges,
              );
              if (success) {
                if (!context.mounted) return;
                context.pop();
                context.pop();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Booking completed')),
                );
              } else {
                if (!context.mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'Error: ${provider.errorMessage ?? "Failed to complete booking"}',
                    ),
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            child: Text('Complete', style: TextStyle(fontSize: 14.sp)),
          ),
        ],
      ),
    );
  }

  void _rejectBooking(
    BuildContext context,
    dynamic booking,
    ProviderProvider provider,
  ) {
    final reasonController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Reject Booking',
          style: TextStyle(fontSize: 16.sp, fontWeight: FontWeight.bold),
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Are you sure you want to reject this booking?',
              style: TextStyle(fontSize: 14.sp),
            ),
            SizedBox(height: 12.h),
            TextField(
              controller: reasonController,
              maxLines: 3,
              decoration: InputDecoration(
                hintText: 'Reason (optional)',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.r),
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => context.pop(),
            child: Text('Keep', style: TextStyle(fontSize: 14.sp)),
          ),
          ElevatedButton(
            onPressed: () async {
              final success = await provider.cancelBooking(
                booking.id,
                reason: reasonController.text.isEmpty
                    ? null
                    : reasonController.text,
              );
              if (success) {
                if (!context.mounted) return;
                context.pop();
                context.pop();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Booking rejected')),
                );
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.error),
            child: Text('Reject', style: TextStyle(fontSize: 14.sp)),
          ),
        ],
      ),
    );
  }
}
