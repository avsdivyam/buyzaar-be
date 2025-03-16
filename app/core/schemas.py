"""
Schemas for request validation and serialization.
"""
from marshmallow import Schema, fields, validate, validates, ValidationError

class LoginSchema(Schema):
    """Schema for login requests."""
    
    username = fields.String(required=True)
    password = fields.String(required=True)


class RegisterSchema(Schema):
    """Schema for user registration."""
    
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=validate.Length(min=8, max=100)
    )
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    
    @validates('password')
    def validate_password(self, value):
        """Validate password complexity."""
        if not any(char.isdigit() for char in value):
            raise ValidationError('Password must contain at least one digit')
        
        if not any(char.isupper() for char in value):
            raise ValidationError('Password must contain at least one uppercase letter')


class UserSchema(Schema):
    """Schema for user serialization."""
    
    id = fields.Integer(dump_only=True)
    keycloak_id = fields.String(dump_only=True)
    email = fields.Email(dump_only=True)
    first_name = fields.String()
    last_name = fields.String()
    full_name = fields.String(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserUpdateSchema(Schema):
    """Schema for user updates."""
    
    first_name = fields.String()
    last_name = fields.String()


class ProductSchema(Schema):
    """Schema for product serialization and validation."""
    
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String()
    price = fields.Float(required=True, validate=validate.Range(min=0.01))
    image_url = fields.String(dump_only=True)
    stock = fields.Integer(validate=validate.Range(min=0))
    sku = fields.String()
    is_active = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class OrderItemSchema(Schema):
    """Schema for order item serialization."""
    
    id = fields.Integer(dump_only=True)
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    price = fields.Float(dump_only=True)
    subtotal = fields.Float(dump_only=True)


class OrderSchema(Schema):
    """Schema for order serialization."""
    
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    status = fields.String(dump_only=True)
    total_amount = fields.Float(dump_only=True)
    shipping_address = fields.String()
    tracking_number = fields.String(dump_only=True)
    notes = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    items = fields.List(fields.Nested(OrderItemSchema), dump_only=True)


class OrderCreateSchema(Schema):
    """Schema for order creation."""
    
    items = fields.List(
        fields.Nested(OrderItemSchema(only=('product_id', 'quantity'))),
        required=True,
        validate=validate.Length(min=1)
    )
    shipping_address = fields.String(required=True)
    notes = fields.String()