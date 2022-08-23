from marshmallow import Schema, fields, EXCLUDE

class CompleteProfileSchema(Schema):
    buisness_name = fields.String(required=True, error_messages={"required":"Buisness Name is required field"})
    phone_no = fields.String(required=True, error_messages={"required":"Phone No is required field"})
    landline_no = fields.String(required=True, error_messages={"required":"Landline No is required field"})
   
    class Meta:
        unknown = EXCLUDE

        