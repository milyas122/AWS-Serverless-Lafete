from marshmallow import Schema, fields, EXCLUDE

class CompleteProfileSchema(Schema):
    business_name = fields.String(required=True, error_messages={"required":"Business Name is required field"})
    phone_no = fields.String(required=True, error_messages={"required":"Phone No is required field"})
    landline_no = fields.String()
   
    class Meta:
        unknown = EXCLUDE

        