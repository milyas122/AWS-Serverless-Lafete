from marshmallow import Schema, fields, validate, EXCLUDE

class SingleMenuSchema(Schema):
    curry = fields.String(required=True, error_messages={"required":"Curry is required field"})
    rice = fields.String(required=True, error_messages={"required":"Rice name is required field"})
    bread = fields.String(required=True, error_messages={"required":"Bread name is required field"})
    yogurt = fields.String(required=True, error_messages={"required":"yogurt name is required field"})
    salad = fields.String(required=True, error_messages={"required":"Salad name is required field"})
    desserts = fields.String(required=True, error_messages={"required":"Dessert name is required field"}) 
    per_head = fields.Integer(strict=True, validate=validate.Length(min=100), required=True, error_messages={"required":"Per head is required field"})

    class Meta:
        unknown = EXCLUDE

class AddOnSchema(Schema):
    add_on = fields.String(required=True, error_messages={"required":"Add On is required field"})
    per_head = fields.Integer(strict=True, validate=validate.Length(min=100), required=True, error_messages={"required":"Per head is required field"})

    class Meta:
        unknown = EXCLUDE

class MenuSchema(Schema):
    menu = fields.List(fields.Nested(SingleMenuSchema))
    add_on = fields.List(fields.Nested(AddOnSchema))
    
    class Meta:
        unknown = EXCLUDE
        