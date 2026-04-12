"""Service category and subcategory models"""

from bson.objectid import ObjectId
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
        self._id = kwargs.get('_id')
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
            'createdAt': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updatedAt': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }

        if include_id and self._id:
            data['_id'] = str(self._id)

        return data

    def save(self):
        """Save category to database"""
        categories_collection = get_categories_collection()

        mongo_data = {
            'name': self.name,
            'nameUrdu': self.name_urdu,
            'icon': self.icon,
            'image': self.image,
            'displayOrder': self.display_order,
            'description': self.description,
            'descriptionUrdu': self.description_urdu,
            'subcategories': self.subcategories,
            'updatedAt': get_timestamp(),
        }

        if self._id:
            result = categories_collection.update_one(
                {'_id': self._id},
                {'$set': mongo_data}
            )
            return result.modified_count > 0
        else:
            mongo_data['createdAt'] = get_timestamp()
            result = categories_collection.insert_one(mongo_data)
            self._id = result.inserted_id
            return True

    @classmethod
    def find_by_id(cls, category_id):
        """Find category by ID"""
        if not is_valid_object_id(category_id):
            return None

        categories_collection = get_categories_collection()
        doc = categories_collection.find_one({'_id': ObjectId(category_id)})

        if not doc:
            return None

        return cls._from_doc(doc)

    @classmethod
    def find_by_name(cls, name):
        """Find category by name"""
        categories_collection = get_categories_collection()
        doc = categories_collection.find_one({'name': name})

        if not doc:
            return None

        return cls._from_doc(doc)

    @classmethod
    def find_all(cls, skip=0, limit=10):
        """Find all categories with pagination"""
        categories_collection = get_categories_collection()
        cursor = categories_collection.find().sort(
            'displayOrder', 1).skip(skip).limit(limit)

        categories = []
        for doc in cursor:
            categories.append(cls._from_doc(doc))

        return categories

    @classmethod
    def count_all(cls):
        """Count total categories"""
        categories_collection = get_categories_collection()
        return categories_collection.count_documents({})

    @classmethod
    def _from_doc(cls, doc):
        """Create CategoryService instance from MongoDB document"""
        if not doc:
            return None

        return cls(
            name=doc.get('name'),
            icon=doc.get('icon'),
            image=doc.get('image'),
            display_order=doc.get('displayOrder', 0),
            _id=doc.get('_id'),
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
        categories_collection = get_categories_collection()
        search_filter = {
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'nameUrdu': {'$regex': query, '$options': 'i'}},
            ]
        }
        cursor = categories_collection.find(
            search_filter).skip(skip).limit(limit)

        categories = []
        for doc in cursor:
            categories.append(cls._from_doc(doc))

        return categories
