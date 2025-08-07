from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, relationship
from datetime import datetime, timezone, UTC

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(50), nullable = False)
    phone_number: Mapped[int] = mapped_column(Integer, nullable = False, default = "")
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    avatar: Mapped[str] = mapped_column(String(500), nullable=True)
    public_id: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False) 
    salt: Mapped[str] = mapped_column(String(80), nullable = False, default = 1 )

    farm_of_user: Mapped[list["Farm"]] = relationship(back_populates="farm_to_user")    # Mapped hace referencia a la clase con que me conecto

    def serialize(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "avatar": self.avatar,
            "public_id": self.public_id
            # do not serialize the password and salt, its a security breach
        }
    
class Farm(db.Model):
    __tablename__ = "farm"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    farm_location: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    farm_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    farm_to_user: Mapped["User"] = relationship(back_populates="farm_of_user")
    # ndvi_to_farm: Mapped[list["NDVI_images"]] = relationship(back_populates="ndvi_of_farm")
    # aerial_to_farm: Mapped[list["Aerial_images"]] = relationship(back_populates="aerial_of_farm")
    images: Mapped[list["Farm_images"]] = relationship(back_populates="images_table")

    def serialize(self):
        return {
            "id": self.id,
            "farm_location": self.farm_location,
            "farm_name": self.farm_name,
            "user_id": self.user_id,
        }
    
class Farm_images(db.Model):
    __tablename__ = "farm_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    image_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'NDVI' o 'AERIAL'
    upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    file_name: Mapped[str] = mapped_column(String(255), nullable=True)
    uploaded_by: Mapped[str] = mapped_column(String(100), nullable=True)  # Email o username del usuario (opcional)

    images_table: Mapped["Farm"] = relationship(back_populates="images")

    def serialize(self):
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "image_url": self.image_url,
            "image_type": self.image_type,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "file_name": self.file_name,
            "uploaded_by": self.uploaded_by,
        }
    
# class NDVI_images(db.Model):
#     __tablename__ = "ndvi_images"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"), nullable=False) 
#     ndvi_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)

#     file_name: Mapped[str] = mapped_column(String(255), nullable=True)
#     upload_date: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
#     geo_location: Mapped[str] = mapped_column(String(255), nullable=True)

#     ndvi_of_farm: Mapped["Farm"] = relationship(back_populates="ndvi_to_farm")

#     def serialize(self):
#         return {
#             "id": self.id,
#             "farm_id": self.farm_id,
#             "ndvi_url": self.ndvi_url,

#             "file_name": self.file_name,
#             "upload_date": self.upload_date.isoformat() if self.upload_date else None,
#             "geo_location": self.geo_location    
#         }

# class Aerial_images(db.Model):
#     __tablename__ = "aerial_images"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"), nullable=False)
#     aerial_url: Mapped[str] = mapped_column(String(500), unique=True, nullable=False)

#     file_name: Mapped[str] = mapped_column(String(255), nullable=True)
#     upload_date: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
#     geo_location: Mapped[str] = mapped_column(String(255), nullable=True)

#     aerial_of_farm: Mapped["Farm"] = relationship(back_populates="aerial_to_farm")

#     def serialize(self):
#         return {
#             "id": self.id,
#             "farm_id": self.farm_id,
#             "aerial_url": self.aerial_url,

#             "file_name": self.file_name,
#             "upload_date": self.upload_date.isoformat() if self.upload_date else None,
#             "geo_location": self.geo_location    
#         }
    