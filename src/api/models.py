from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, relationship

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
    ndvi_to_farm: Mapped[list["NDVI_images"]] = relationship(back_populates="ndvi_of_farm")
    aereal_to_farm: Mapped[list["Aereal_images"]] = relationship(back_populates="aereal_of_farm")

    def serialize(self):
        return {
            "id": self.id,
            "farm_location": self.farm_location,
            "farm_name": self.farm_name,
            "user_id": self.user_id,
        }
    
class NDVI_images(db.Model):
    __tablename__ = "ndvi_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"), nullable=False) 
    ndvi_url: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

    ndvi_of_farm: Mapped["Farm"] = relationship(back_populates="ndvi_to_farm")

    def serialize(self):
        return {
            "id": self.id,
            "ndvi_url": self.ndvi_url    
        }

class Aereal_images(db.Model):
    __tablename__ = "aereal_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"), nullable=False)
    aereal_url: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

    aereal_of_farm: Mapped["Farm"] = relationship(back_populates="aereal_to_farm")

    def serialize(self):
        return {
            "id": self.id,
            "aereal_url": self.aereal_url,    
        }