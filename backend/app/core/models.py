"""
Database models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Review(Base):
    """Code review record"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, index=True)
    language = Column(String)
    code_content = Column(Text)
    review_results = Column(JSON)
    model_used = Column(String)
    overall_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=True)
    repository = Column(String, nullable=True)
    commit_hash = Column(String, nullable=True)
    
    # Relationships
    issues = relationship("Issue", back_populates="review", cascade="all, delete-orphan")
    history_entries = relationship("ReviewHistory", back_populates="review")

class Issue(Base):
    """Individual issue found in review"""
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    issue_type = Column(String)  # bug, security, style, documentation
    severity = Column(String)  # critical, high, medium, low
    line = Column(Integer)
    column = Column(Integer, nullable=True)
    description = Column(Text)
    suggestion = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    status = Column(String, default="open")  # open, resolved, ignored
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    review = relationship("Review", back_populates="issues")
    comments = relationship("IssueComment", back_populates="issue")

class IssueComment(Base):
    """Comments on issues (collaboration)"""
    __tablename__ = "issue_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))
    user_id = Column(String)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    issue = relationship("Issue", back_populates="comments")

class ReviewHistory(Base):
    """Review history tracking"""
    __tablename__ = "review_history"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"))
    action = Column(String)  # created, updated, resolved, etc.
    user_id = Column(String)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    review = relationship("Review", back_populates="history_entries")

class Configuration(Base):
    """User/team configuration"""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    user_id = Column(String, nullable=True)
    team_id = Column(String, nullable=True)
    config_data = Column(JSON)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class APIAudit(Base):
    """API usage audit log"""
    __tablename__ = "api_audit"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True)
    model_used = Column(String)
    tokens_used = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

