import uuid 
from marshmallow import Schema, fields, validate, EXCLUDE, post_load


class ServicesSchema(Schema):
    service = fields.String(required=True, validate=validate.OneOf(["Hall", "Catering", "Farm House", "Event Organizer", "Marquee"]),
                                error_messages={"invalid": "Invalid Service Type", "required":"Service is required field"})
    name = fields.String(required=True, error_messages={"required":"Name is required field"})
    location = fields.String(required=True, error_messages={"required":"Location is required field"})
    city = fields.String(required=True, error_messages={"required":"City is required field"})
    state = fields.String(required=True, error_messages={"required":"State is required field"})
    images = fields.List(fields.Url(),validate=validate.Length(1,10))
    about_service = fields.String() 

    class Meta:
        unknown = EXCLUDE

class HallSchema(ServicesSchema):
    max_seating = fields.Integer(required=True, error_messages={"required":" Max Seating is required field"})
    slot = fields.List(
                fields.String(
                    ), 
                required=True,
                validate=validate.Length(1,2),
                error_messages={"invalid": "Invalid Service Type", "required":"Slot is required field"})

    per_head = fields.Integer(required=True, error_messages={"required":" Per head is required field"})


class MarqueeSchema(HallSchema):
    decores = fields.List(fields.Url(),validate=validate.Length(1,10), required=True, error_messages={"required":"Decores images is required"})

class FarmHouseSchema(ServicesSchema):
    per_hour_rate = fields.Integer(required=True, error_messages={"required":"Per hour rate is required field"})

# class RatingSchema(Schema):
#     communication = fields.Integer(strict=True, require )

class PortfolioSchema(Schema):
    image = fields.Url(required=True, error_messages={"required":"Portfolio Image is required field"})
    about = fields.String() 

class EventOrganizer(ServicesSchema):
    about_service = fields.String(required=True, error_messages={"required":"About Service is reuqired field"})
    portfolio = fields.List(fields.Nested(PortfolioSchema))

    @post_load
    def remove_images(self,data: dict,**kwargs) -> dict:
        if data.get("images"):
            data.pop("images")
        return data

    class Meta:
        unknown = EXCLUDE

class CateringService(Schema):
    id = fields.UUID(load_default=str(uuid.uuid4()))
    service = fields.String(required=True, error_messages={"required":"Catering Service is required field"})
    images = fields.List(fields.Url(),validate=validate.Length(1,3))
    about_service = fields.String(required=True, error_messages={"required":"About service is reuqired field"})


class CateringSchema(ServicesSchema):
    services = fields.List(fields.Nested(CateringService))
    
    class Meta:
        unknown = EXCLUDE