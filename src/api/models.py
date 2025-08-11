from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, relationship
from datetime import datetime, timezone, UTC

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(50), nullable = False)
    phone_number: Mapped[int] = mapped_column(String(30), nullable = False, default = "")
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    avatar: Mapped[str] = mapped_column(String(500), nullable=True)
    is_admin: Mapped[str] = mapped_column(String(20), nullable=False, default='user')       # user o admin
    public_id: Mapped[str] = mapped_column(String(255), nullable=True)
    password: Mapped[str] = mapped_column(String(500), nullable=False) 
    salt: Mapped[str] = mapped_column(String(80), nullable = False, default = 1 )


    # farm_of_user: Mapped[list["Farm"]] = relationship(back_populates="farm_to_user")    # Mapped hace referencia a la clase con que me conecto

    # user_diagnostic_reports: Mapped[list["DiagnosticReport"]] = relationship(back_populates="user_report", cascade="all, delete-orphan")



    farm_of_user: Mapped[list["Farm"]] = relationship(back_populates="farm_to_user")    

    user_diagnostic_reports: Mapped[list["DiagnosticReport"]] = relationship(back_populates="user_report", cascade="all, delete-orphan")
    email_diagnostic_reports: Mapped[list["DiagnosticReport"]] = relationship(back_populates="email_report", cascade="all, delete-orphan")
    
    def serialize(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "avatar": self.avatar,
            'is_admin': self.is_admin,
            "public_id": self.public_id
            # do not serialize the password and salt, its a security breach
        }
    
    # NUEVO MÉTODO: Para verificar si es admin
    def is_administrator(self):
        return self.is_admin == 'admin'
    
class Farm(db.Model):
    __tablename__ = "farm"
    __table_args__ = (
        UniqueConstraint('user_id', 'farm_location', name='uix_user_farm_location'),
        UniqueConstraint('user_id', 'farm_name', name='uix_user_farm_name'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    farm_location: Mapped[str] = mapped_column(String(100), nullable=False)
    farm_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    farm_to_user: Mapped["User"] = relationship(back_populates="farm_of_user")
    images: Mapped[list["Farm_images"]] = relationship(back_populates="images_table")

    # analyses: Mapped[list["ImageAnalysis"]] = relationship(back_populates="farm")
    diagnostic_reports: Mapped[list["DiagnosticReport"]] = relationship(back_populates="farm_report", cascade="all, delete-orphan")

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
    uploaded_by: Mapped[str] = mapped_column(String(100), nullable=True) 
    # uploaded_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)  # FK a User
    # public_id: Mapped[str] = mapped_column(String(255), nullable=True)  # para Cloudinary

    images_table: Mapped["Farm"] = relationship(back_populates="images")

    # uploader_user: Mapped["User"] = relationship("User")  # relacion con usuario que subió

    def serialize(self):
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "image_url": self.image_url,
            "image_type": self.image_type,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "file_name": self.file_name,
            "uploaded_by": self.uploaded_by,
            # "uploaded_by_user_id": self.uploaded_by_user_id,
            # "public_id": self.public_id
        }


# 1) Alternativa Avanzada version simple:

# class ImageAnalysis(db.Model):
#     __tablename__ = "image_analysis"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     farm_image_id: Mapped[int] = mapped_column(ForeignKey("farm_images.id"), nullable=False)
#     analysis_result: Mapped[str] = mapped_column(db.Text, nullable=False)  # puede ser JSON o texto plano
#     analysis_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

#     image: Mapped["Farm_images"] = relationship()  # relación simple con farm_images

#     def serialize(self):
#         return {
#             "id": self.id,
#             "farm_image_id": self.farm_image_id,
#             "analysis_result": self.analysis_result,
#             "analysis_date": self.analysis_date.isoformat(),
#         }

# 2) Alternativa Avanzada version compleja:
   
# class ImageAnalysis(db.Model):
#     __tablename__ = "image_analysis"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     image_id: Mapped[int] = mapped_column(ForeignKey("farm_images.id"), nullable=False)
#     farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"), nullable=False)
#     analysis_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    
#     ndvi_mean: Mapped[float] = mapped_column(Float, nullable=True)
#     ndvi_min: Mapped[float] = mapped_column(Float, nullable=True)
#     ndvi_max: Mapped[float] = mapped_column(Float, nullable=True)
    
#     stress_index: Mapped[float] = mapped_column(Float, nullable=True)  # ejemplo índice de estrés hídrico
#     pest_probability: Mapped[float] = mapped_column(Float, nullable=True)  # predicción de plagas
    
#     notes: Mapped[str] = mapped_column(String(500), nullable=True)  # Observaciones libres

#     farm: Mapped["Farm"] = relationship(back_populates="analyses")
#     image: Mapped["Farm_images"] = relationship(back_populates="analyses")

#     def serialize(self):
#         return {
#             "id": self.id,
#             "image_id": self.image_id,
#             "farm_id": self.farm_id,
#             "analysis_date": self.analysis_date.isoformat(),
#             "ndvi_mean": self.ndvi_mean,
#             "ndvi_min": self.ndvi_min,
#             "ndvi_max": self.ndvi_max,
#             "stress_index": self.stress_index,
#             "pest_probability": self.pest_probability,
#             "notes": self.notes,
#         };

class DiagnosticReport(db.Model):
    __tablename__ = 'diagnostic_reports'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey('farm.id'), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(255), nullable=False)
    uploaded_at: Mapped[str] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    uploaded_by: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)                  # Para distinguir reportes de usuarios vs diagnósticos de admin
    is_diagnostic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user_report : Mapped['User'] = relationship(back_populates='user_diagnostic_reports')
    farm_report : Mapped['Farm'] = relationship(back_populates='diagnostic_reports')
    email_report : Mapped['User'] = relationship(back_populates='email_diagnostic_reports')

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "farm_id": self.farm_id,
            "file_name": self.file_name,
            "file_url": self.file_url,
            "uploaded_at": self.uploaded_at.isoformat() if hasattr(self.uploaded_at, 'isoformat') else str(self.uploaded_at),
            "uploaded_by": self.uploaded_by,
            'is_diagnostic': self.is_diagnostic,
            "description": self.description,
        }