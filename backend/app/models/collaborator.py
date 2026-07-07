"""SQLAlchemy models for collaborator profiles and related entities."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from app.database.session import Base


# Association table for profile-skill many-to-many relationship
profile_skills = Table(
    'profile_skills',
    Base.metadata,
    Column('profile_id', Integer, ForeignKey('collaborator_profiles.id', ondelete='CASCADE'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id', ondelete='CASCADE'), primary_key=True),
    Column('proficiency_level', String(20), default='intermediate')  # beginner, intermediate, advanced, expert
)


# Association table for profile-interest many-to-many relationship
profile_interests = Table(
    'profile_interests',
    Base.metadata,
    Column('profile_id', Integer, ForeignKey('collaborator_profiles.id', ondelete='CASCADE'), primary_key=True),
    Column('interest_id', Integer, ForeignKey('project_interests.id', ondelete='CASCADE'), primary_key=True)
)


class CollaboratorProfile(Base):
    """Represents a collaborator profile in the system."""
    
    __tablename__ = 'collaborator_profiles'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    professional_title = Column(String(200), nullable=False)
    bio = Column(Text, nullable=False)
    experience_level = Column(String(50), nullable=False)  # junior, mid-level, senior, lead
    years_of_experience = Column(Integer, nullable=False)
    weekly_availability_hours = Column(Integer, nullable=False)
    timezone = Column(String(50), nullable=False)
    collaboration_style = Column(String(50), nullable=False)  # collaborative, independent, flexible
    communication_preference = Column(String(50), nullable=False)  # async, sync, hybrid
    preferred_team_size = Column(String(50), nullable=False)  # small (2-3), medium (4-6), large (7+)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    skills = relationship('Skill', secondary=profile_skills, back_populates='profiles')
    interests = relationship('ProjectInterest', secondary=profile_interests, back_populates='profiles')
    
    def __repr__(self):
        return f"<CollaboratorProfile(id={self.id}, name='{self.name}', title='{self.professional_title}')>"


class Skill(Base):
    """Represents a technical or professional skill."""
    
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=False)  # frontend, backend, devops, design, data, etc.
    
    # Relationships
    profiles = relationship('CollaboratorProfile', secondary=profile_skills, back_populates='skills')
    
    def __repr__(self):
        return f"<Skill(id={self.id}, name='{self.name}', category='{self.category}')>"


class ProjectInterest(Base):
    """Represents a project domain or interest area."""
    
    __tablename__ = 'project_interests'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Relationships
    profiles = relationship('CollaboratorProfile', secondary=profile_interests, back_populates='interests')
    
    def __repr__(self):
        return f"<ProjectInterest(id={self.id}, name='{self.name}')>"
