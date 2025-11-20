from .models import SessionLocal, Tour
from sqlalchemy.exc import IntegrityError
import json

class TourScraperPipeline:
    def open_spider(self, spider):
        self.session = SessionLocal()
        spider.logger.info("Database session opened")

    def close_spider(self, spider):
        self.session.commit()
        self.session.close()
        spider.logger.info("Database session closed")

    def process_item(self, item, spider):
        try:
            # Helper function để chuyển list/dict sang JSON
            def to_json(data):
                if data is None:
                    return None
                return json.dumps(data, ensure_ascii=False)
            
            # Tạo tour object
            tour = Tour(
                url=item.get("url"),
                ma_tour=item.get("ma_tour"),
                thoi_gian=item.get("thoi_gian"),
                khoi_hanh=item.get("khoi_hanh"),
                van_chuyen=item.get("van_chuyen"),
                xuat_phat=item.get("xuat_phat"),
                gia_tu=item.get("gia_tu"),
                trai_nghiem=to_json(item.get("trai_nghiem")),
                diem_nhan_hanh_trinh=to_json(item.get("diem_nhan_hanh_trinh")),
                lich_trinh=to_json(item.get("lich_trinh")),
                dich_vu_bao_gom=to_json(item.get("dich_vu_bao_gom")),
                dich_vu_khong_bao_gom=to_json(item.get("dich_vu_khong_bao_gom")),
                ghi_chu=to_json(item.get("ghi_chu"))
            )
            
            self.session.add(tour)
            self.session.commit()
            spider.logger.info(f"Saved tour: {item.get('ma_tour')}")
            
        except IntegrityError:
            self.session.rollback()
            spider.logger.warning(f"Duplicate tour URL: {item.get('url')}")
        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"Error saving tour: {e}")
        
        return item