"""Service catalog business logic"""

from app.models.service import ServiceCategory, ServiceSubCategory
from app.utils.errors import ValidationError, NotFoundError


class ServiceService:
    """Service for managing service categories and subcategories"""

    @staticmethod
    def create_category(data):
        """
        Create a new service category

        Args:
            data: Dictionary with category data

        Returns:
            ServiceCategory: Created category
        """
        name = data.get('name')
        if not name or not name.strip():
            raise ValidationError('Category name is required')

        # Check if category already exists
        existing = ServiceCategory.find_by_name(name)
        if existing:
            raise ValidationError('Category already exists')

        category = ServiceCategory(
            name=name,
            icon=data.get('icon'),
            image=data.get('image'),
            display_order=data.get('displayOrder', 0),
            name_urdu=data.get('nameUrdu'),
            description=data.get('description'),
            description_urdu=data.get('descriptionUrdu'),
        )

        # Add subcategories if provided
        subcategories = data.get('subcategories', [])
        for sub_data in subcategories:
            category.add_subcategory(sub_data)

        if category.save():
            return category

        raise Exception('Failed to create category')

    @staticmethod
    def update_category(category_id, data):
        """
        Update a service category

        Args:
            category_id: ID of category to update
            data: Dictionary with updated data

        Returns:
            ServiceCategory: Updated category
        """
        category = ServiceCategory.find_by_id(category_id)
        if not category:
            raise NotFoundError('Category not found')

        # Update fields
        if 'name' in data and data['name']:
            # Check if new name already exists
            existing = ServiceCategory.find_by_name(data['name'])
            if existing and existing._id != category._id:
                raise ValidationError('Category name already exists')

            category.name = data['name']

        if 'nameUrdu' in data:
            category.name_urdu = data['nameUrdu']

        if 'icon' in data:
            category.icon = data['icon']

        if 'image' in data:
            category.image = data['image']

        if 'displayOrder' in data:
            category.display_order = data['displayOrder']

        if 'description' in data:
            category.description = data['description']

        if 'descriptionUrdu' in data:
            category.description_urdu = data['descriptionUrdu']

        # Update subcategories if provided
        if 'subcategories' in data:
            category.subcategories = data['subcategories']

        if category.save():
            return category

        raise Exception('Failed to update category')

    @staticmethod
    def delete_category(category_id):
        """
        Delete a service category

        Args:
            category_id: ID of category to delete

        Returns:
            bool: Success status
        """
        from app.models.database import supabase_client

        category = ServiceCategory.find_by_id(category_id)
        if not category:
            raise NotFoundError('Category not found')

        try:
            response = supabase_client.table('serviceCategories').delete().eq(
                'id', int(category_id)).execute()
            return response.count > 0 if hasattr(response, 'count') else True
        except Exception as e:
            print(f"Error deleting category: {e}")
            raise Exception('Failed to delete category')

    @staticmethod
    def get_category(category_id):
        """
        Get a service category by ID

        Args:
            category_id: Category ID

        Returns:
            ServiceCategory: Category instance
        """
        category = ServiceCategory.find_by_id(category_id)
        if not category:
            raise NotFoundError('Category not found')

        return category

    @staticmethod
    def list_categories(skip=0, limit=10):
        """
        List all service categories

        Args:
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            tuple: (categories list, total count)
        """
        categories = ServiceCategory.find_all(skip=skip, limit=limit)
        total = ServiceCategory.count_all()

        return categories, total

    @staticmethod
    def search_categories(query, skip=0, limit=10):
        """
        Search service categories

        Args:
            query: Search query
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            tuple: (categories list, total count)
        """
        if not query or not query.strip():
            return ServiceService.list_categories(skip, limit)

        categories = ServiceCategory.search(query, skip=skip, limit=limit)

        # Get total count for search results
        from app.models.database import get_categories_collection
        search_filter = {
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'nameUrdu': {'$regex': query, '$options': 'i'}},
            ]
        }
        total = get_categories_collection().count_documents(search_filter)

        return categories, total

    @staticmethod
    def get_subcategories(category_id):
        """
        Get subcategories for a category

        Args:
            category_id: Category ID

        Returns:
            list: Subcategories
        """
        category = ServiceCategory.find_by_id(category_id)
        if not category:
            raise NotFoundError('Category not found')

        return category.subcategories
