"""
Xe-Bot Database Models for Neon PostgreSQL
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, ForeignKey, Enum as SQLEnum, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import enum

from src.config import config

Base = declarative_base()


class ProcessingStatus(enum.Enum):
    """Status of paper processing"""
    PENDING = "pending"
    FETCHING = "fetching"
    EXTRACTING = "extracting"
    SEGMENTING = "segmenting"
    ANIMATING = "animating"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchPaper(Base):
    """Research paper model"""
    __tablename__ = "research_papers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    arxiv_id = Column(String(50), unique=True, nullable=True)
    title = Column(String(500), nullable=False)
    authors = Column(JSON, default=list)
    abstract = Column(Text, nullable=True)
    pdf_url = Column(String(500), nullable=True)
    source = Column(String(100), default="arxiv")
    status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    introduction = relationship("PaperIntroduction", back_populates="paper", uselist=False)
    segments = relationship("IntroSegment", back_populates="paper")
    animations = relationship("Animation", back_populates="paper")
    
    def __repr__(self):
        return f"<ResearchPaper(id={self.id}, title='{self.title[:50]}...')>"


class PaperIntroduction(Base):
    """Extracted introduction from a paper"""
    __tablename__ = "paper_introductions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("research_papers.id"), nullable=False)
    content = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    extraction_method = Column(String(50), default="llm")
    
    # Relationship
    paper = relationship("ResearchPaper", back_populates="introduction")
    
    def __repr__(self):
        return f"<PaperIntroduction(paper_id={self.paper_id}, words={self.word_count})>"


class IntroSegment(Base):
    """Segmented parts of the introduction"""
    __tablename__ = "intro_segments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("research_papers.id"), nullable=False)
    segment_order = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    topic = Column(String(200), nullable=True)
    topic_category = Column(String(100), nullable=True)
    key_concepts = Column(JSON, default=list)
    animation_hints = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    paper = relationship("ResearchPaper", back_populates="segments")
    
    def __repr__(self):
        return f"<IntroSegment(paper_id={self.paper_id}, order={self.segment_order}, topic='{self.topic}')>"


class Animation(Base):
    """Generated animations"""
    __tablename__ = "animations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("research_papers.id"), nullable=False)
    segment_id = Column(Integer, ForeignKey("intro_segments.id"), nullable=True)
    animation_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=True)
    video_url = Column(String(1000), nullable=True)  # URL to access the video
    download_url = Column(String(1000), nullable=True)  # URL to download the video
    manim_code = Column(Text, nullable=True)
    duration_seconds = Column(Integer, default=0)
    file_size_bytes = Column(Integer, default=0)  # Video file size
    status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    paper = relationship("ResearchPaper", back_populates="animations")
    
    def __repr__(self):
        return f"<Animation(id={self.id}, paper_id={self.paper_id}, type='{self.animation_type}')>"
    
    def to_dict(self):
        """Convert to dictionary with URLs"""
        return {
            "id": self.id,
            "paper_id": self.paper_id,
            "animation_type": self.animation_type,
            "file_path": self.file_path,
            "video_url": self.video_url,
            "download_url": self.download_url,
            "duration_seconds": self.duration_seconds,
            "file_size_bytes": self.file_size_bytes,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AgentLog(Base):
    """Agentic workflow logs"""
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("research_papers.id"), nullable=True)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(200), nullable=False)
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    status = Column(String(50), default="success")
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AgentLog(agent='{self.agent_name}', action='{self.action}')>"


class DatabaseManager:
    """Database connection manager for Neon PostgreSQL"""
    
    def __init__(self):
        self.database_url = config.database.database_url
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def init_sync_engine(self):
        """Initialize synchronous engine with connection pooling for Neon"""
        if not self.database_url:
            print("⚠ No DATABASE_URL configured - running without database")
            return None
        
        # Neon-optimized settings: handle connection drops gracefully
        self.engine = create_engine(
            self.database_url, 
            echo=False,
            pool_pre_ping=True,  # Check connection before use
            pool_recycle=300,    # Recycle connections every 5 minutes
            pool_size=5,         # Small pool for serverless
            max_overflow=10,     # Allow some overflow
            connect_args={
                "connect_timeout": 10,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            }
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        return self.engine
    
    def create_tables(self):
        """Create all tables"""
        if not self.database_url:
            print("⚠ Skipping table creation - no database configured")
            return
        if not self.engine:
            self.init_sync_engine()
        Base.metadata.create_all(self.engine)
        print("✓ Database tables created successfully")
    
    def get_session(self):
        """Get a database session with auto-reconnect"""
        if not self.database_url:
            return None
        if not self.SessionLocal:
            self.init_sync_engine()
        try:
            session = self.SessionLocal()
            # Test connection
            session.execute(text("SELECT 1"))
            return session
        except Exception as e:
            # Reconnect on failure
            print(f"Database connection lost, reconnecting... ({e})")
            self.init_sync_engine()
            return self.SessionLocal()
    
    def drop_tables(self):
        """Drop all tables (use with caution)"""
        if not self.engine:
            self.init_sync_engine()
        Base.metadata.drop_all(self.engine)
        print("✓ All tables dropped")


# Global database manager instance
db_manager = DatabaseManager()


def get_db_session():
    """Get a database session context manager"""
    session = db_manager.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
