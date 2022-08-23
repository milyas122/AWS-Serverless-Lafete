from marshmallow import Schema, fields, validate, EXCLUDE


class ServicesSchema(Schema):
    service = fields.String(required=True, validate=validate.OneOf(["Hall", "Catering", "Farm House", "Event Organizer", "Morquee"]),
                                error_messages={"invalid": "Invalid Service Type", "required":"Service is required field"})
    location = fields.String(required=True, error_messages={"required":"Location is required field"})
    city = fields.String(required=True, error_messages={"required":"City is required field"})
    state = fields.String(required=True, error_messages={"required":"State is required field"})
    images = fields.Url(fields.List(validate=validate.Length(1,10)))
    about_service = fields.String() 

    class Meta:
        unknown = EXCLUDE

class HallSchema(ServicesSchema):
    name = fields.String(required=True, error_messages={"required":"Hall name is required field"})
    max_seating = fields.Integer(strict=True, validate=validate.Length(min=300))
    evening_slot = fields.String(required=True, error_messages={"required":"Evening slot is required field"})
    afternoon_slot = fields.String(required=True, error_messages={"required": "Afternoon slot is required field"})
    per_head = fields.Integer(strict=True, validate=validate.Length(min=100))


class MorqueeSchema(ServicesSchema):
    name = fields.String(required=True, error_messages={"required":"Hall name is required field"})
    decores = fields.Url(fields.List(validate=validate.Length(min = 1)), required=True, error_messages={"required":"Decores is required field"})
    per_head = fields.Integer(strict=True, validate=validate.Length(min=100))
    max_seating = fields.Integer(strict=True, validate=validate.Length(min=300))

class FarmHouseSchema(ServicesSchema):
    area = fields.String(required=True, error_messages={"required":"Area/Kanal is required field"})
    per_hour_rate = fields.Integer(strict=True, required=True, error_messages={"required":"Per hour rate is required field"}, validate=validate.Length(min=100))
