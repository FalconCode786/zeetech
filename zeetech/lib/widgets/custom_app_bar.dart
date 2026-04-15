import 'package:flutter/material.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final VoidCallback? onLeadingPressed;
  final VoidCallback? onBackPressed;
  final List<Widget>? actions;
  final Color? backgroundColor;
  final Color? textColor;
  final double? elevation;
  final Widget? leading;
  final bool showBackButton;
  final TextStyle? titleStyle;
  final EdgeInsets? contentPadding;

  const CustomAppBar({
    Key? key,
    required this.title,
    this.onLeadingPressed,
    this.onBackPressed,
    this.actions,
    this.backgroundColor,
    this.textColor,
    this.elevation = 2.0,
    this.leading,
    this.showBackButton = true,
    this.titleStyle,
    this.contentPadding,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      backgroundColor: backgroundColor ?? Color(0xFF1F77D2),
      elevation: elevation,
      leading:
          leading ??
          (showBackButton
              ? IconButton(
                  icon: Icon(
                    Icons.arrow_back_ios,
                    color: textColor ?? Colors.white,
                    size: 20,
                  ),
                  onPressed: onBackPressed ?? onLeadingPressed ?? () => Navigator.pop(context),
                )
              : null),
      title: Text(
        title,
        style:
            titleStyle ??
            TextStyle(
              color: textColor ?? Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
      ),
      centerTitle: true,
      actions: actions,
      iconTheme: IconThemeData(color: textColor ?? Colors.white),
      titleSpacing: 0,
    );
  }

  @override
  Size get preferredSize => Size.fromHeight(kToolbarHeight);
}
