from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///tours.db"  # Có thể đổi sang MySQL/PostgreSQL sau

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Tour(Base):
    __tablename__ = "tours"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mien = Column(String(50), nullable=False, index=True)
    
    # Thông tin cơ bản
    url = Column(String(1000), unique=True)
    ma_tour = Column(String(100))
    thoi_gian = Column(String(100))
    khoi_hanh = Column(String(300))
    van_chuyen = Column(String(200))
    xuat_phat = Column(String(200))
    gia_tu = Column(String(100))
    
    # Nội dung tour
    trai_nghiem = Column(JSON)  # list
    diem_nhan_hanh_trinh = Column(JSON)  # list
    lich_trinh = Column(JSON)  # list of dicts
    
    # Dịch vụ
    dich_vu_bao_gom = Column(JSON)  # list
    dich_vu_khong_bao_gom = Column(JSON)  # list
    
    # Ghi chú
    ghi_chu = Column(JSON)  # list
    
    # Metadata
    created_at = Column(DateTime, default=datetime.now)

# Tạo bảng
Base.metadata.create_all(engine)