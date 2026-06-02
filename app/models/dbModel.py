import enum
import os
from sqlalchemy import String, Integer, ForeignKey, Enum, URL
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from app.extensions import db
from typing import List
from dotenv import load_dotenv




class RolesEnum(enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    guest = 'guest'

class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    phone_no: Mapped[str] = mapped_column(String(15), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(600), nullable=False)
    
    org: Mapped[List[Organisation]] = relationship(back_populates="user", cascade='all, delete-orphan')
    members: Mapped[List[Members]] = relationship(back_populates="user", cascade='all, delete-orphan')
    
    
class Organisation(db.Model):
    __tablename__ = "org"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(25), nullable=True)
    description: Mapped[str] = mapped_column(String(5000), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    
    user: Mapped[User] = relationship(back_populates="org")
    members: Mapped[List[Members]] = relationship(back_populates="org", cascade='all, delete-orphan')
    
class Members(db.Model):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[RolesEnum] = mapped_column(Enum(RolesEnum))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    org_id: Mapped[int] = mapped_column(Integer, ForeignKey("org.id"))
    
    user: Mapped[User] = relationship(back_populates="members")
    org: Mapped[Organisation] = relationship(back_populates="members")
    
    
#class Workspace(db.Model):
 #   __tablename__ = 'workspace'
  #  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   # name: Mapped[str] = mapped_column(String(60), nullable=False)
    #description: Mapped[str] = mapped_column(String(1200), nullable=True)
    #org_id: Mapped[int] = mapped_column(Integer, ForeignKey("org.id"))
    
    #org: Mapped[Organisation] = relationship(back_populates='org')

    
    



