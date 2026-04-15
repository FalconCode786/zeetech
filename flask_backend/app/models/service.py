"""Service category and subcategory models"""

from app.models.database import get_categories_collection
from app.utils.helpers import get_timestamp, is_valid_object_id
from datetime import datetime


class ServiceSubCategory:
    """Service subcategory model"""

    def __init__(self, name, base_price, price_unit='per_hour', estimated_duration=None,
                 warranty_period=None, description=None, **kwargs):
        self.name = name  # English name
        self.name_urdu = kwargs.get('name_urdu')  # Urdu name
        self.base_price = base_price
        # 'per_hour', 'per_visit', 'per_unit', etc.
        self.price_unit = price_unit
        self.estimated_duration = estimated_duration  # in minutes
        self.warranty_period = warranty_period  # in days
        self.description = description
        self.description_urdu = kwargs.get('description_urdu')

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'name': self.name,
            'nameUrdu': self.name_urdu,
            'basePrice': self.base_price,
            'priceUnit': self.price_unit,
            'estimatedDuration': self.estimated_duration,
            'warrantyPeriod': self.warranty_period,
            'description': self.description,
            'descriptionUrdu': self.description_urdu,
        }

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            name=data.get('name'),
            base_price=data.get('basePrice'),
            price_unit=data.get('priceUnit', 'per_hour'),
            estimated_duration=data.get('estimatedDuration'),
            warranty_period=data.get('warrantyPeriod'),
            description=data.get('description'),
            name_urdu=data.get('nameUrdu'),
            description_urdu=data.get('descriptionUrdu'),
        )


class ServiceCategory:
    """Service category model"""

    def __init__(self, name, icon=None, image=None, display_order=0, **kwargs):
        self.id = kwargs.get('id')
        self.name = name  # English name
        self.name_urdu = kwargs.get('name_urdu')  # Urdu name
        self.icon = icon
        self.image = image
        self.display_order = display_order
        self.description = kwargs.get('description')
        self.description_urdu = kwargs.get('description_urdu')

        # Subcategories list
        self.subcategories = kwargs.get('subcategories', [])

        # Timestamps
        self.created_at = kwargs.get('created_at', get_timestamp())
        self.updated_at = kwargs.get('updated_at', get_timestamp())

    def add_subcategory(self, subcategory):
        """Add a subcategory"""
        if isinstance(subcategory, dict):
            subcategory = ServiceSubCategory.from_dict(subcategory)

        self.subcategories.append(subcategory.to_dict())

    def remove_subcategory(self, index):
        """Remove a subcategory by index"""
        if 0 <= index < len(self.subcategories):
            self.subcategories.pop(index)

    def to_dict(self, include_id=True):
        """Convert to dictionary"""
        data = {
            'name': self.name,
            'nameUrdu': self.name_urdu,
            'icon': self.icon,
            'image': self.image,
            'displayOrder': self.display_order,
            'description': self.description,
            'descriptionUrdu': self.description_urdu,
            'subcategories': self.subcategories,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }

        if include_id and self.id:
            data['id'] = self.id

        return data

    def save(self):
        """Save category to database via Supabase"""
        from app.models.database import supabase_client

        data = {
            'name': self.name,
            'nameUrdu': self.name_urdu,
            'icon': self.icon,
            'image': self.image,
            'displayOrder': self.display_order,
            'description': self.description,
            'descriptionUrdu': self.description_urdu,
            'subcategories': self.subcategories,
        }

        if self.id:
            # Update existing category
            response = supabase_client.table('serviceCategories').update(
                data).eq('id', self.id).execute()
            return response.data is not None
        else:
            # Insert new category
            data['createdAt'] = self.created_at
            response = supabase_client.table(
                'serviceCategories').insert(data).execute()
            if response.data:
                self.id = response.data[0]['id']
                return True
            return False

    @classmethod
    def find_by_id(cls, category_id):
        """Find category by ID"""
        from app.models.database import supabase_client

        try:
            response = supabase_client.table('serviceCategories').select(
                '*').eq('id', int(category_id)).execute()
            if response.data and len(response.data) > 0:
                doc = response.data[0]
                return cls._from_doc(doc)
            return None
        except Exception:
            return None

    @classmethod
    def find_by_name(cls, name):
        """Find category by name"""
        from app.models.database import supabase_client

        try:
            response = supabase_client.table('serviceCategories').select(
                '*').eq('name', name).execute()
            if response.data and len(response.data) > 0:
                doc = response.data[0]
                return cls._from_doc(doc)
            return None
        except Exception:
            return None

    @classmethod
    def find_all(cls, skip=0, limit=10):
        """Find all categories with pagination"""
        from app.models.database import supabase_client

        try:
            start = skip
            end = skip + limit - 1
            response = supabase_client.table('serviceCategories').select(
                '*').order('displayOrder', desc=False).range(start, end).execute()

            categories = []
            if response.data:
                for doc in response.data:
                    categories.append(cls._from_doc(doc))
            return categories
        except Exception:
            return []

    @classmethod
    def count_all(cls):
        """Count total categories"""
        from app.models.database import supabase_client

        try:
            response = supabase_client.table('serviceCategories').select(
                'id', count='exact').execute()
            return response.count if response.count else 0
        except Exception:
            return 0

    @classmethod
    def _from_doc(cls, doc):
        """Create CategoryService instance from Supabase record"""
        if not doc:
            return None

        return cls(
            name=doc.get('name'),
            icon=doc.get('icon'),
            image=doc.get('image'),
            display_order=doc.get('displayOrder', 0),
            id=doc.get('id'),
            name_urdu=doc.get('nameUrdu'),
            description=doc.get('description'),
            description_urdu=doc.get('descriptionUrdu'),
            subcategories=doc.get('subcategories', []),
            created_at=doc.get('createdAt', get_timestamp()),
            updated_at=doc.get('updatedAt', get_timestamp()),
        )

    @classmethod
    def search(cls, query, skip=0, limit=10):
        """Search categories by name"""
        from app.models.database import supabase_client

        try:
            start = skip
            end = skip + limit - 1
            # Note: Supabase doesn't support complex full-text search in the same way
            # We'll do a simple filter on name field
            response = supabase_client.table('serviceCategories').select(
                '*').ilike('name', f'%{query}%').range(start, end).execute()

            categories = []
            if response.data:
                for doc in response.data:
                    categories.append(cls._from_doc(doc))
            return categories
        except Exception:
            return []
