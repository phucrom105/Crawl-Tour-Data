import scrapy

class TourItem(scrapy.Item):
    # Thông tin cơ bản
    url = scrapy.Field()  # URL tour
    hinh_anh_chinh = scrapy.Field() # Hình ảnh
    tour_name = scrapy.Field() 
    title = scrapy.Field() # Tên tour 
    ma_tour = scrapy.Field()  # Mã tour
    thoi_gian = scrapy.Field()  # Thời gian (VD: 6 ngày 5 đêm)
    khoi_hanh = scrapy.Field()  # Ngày khởi hành
    van_chuyen = scrapy.Field()  # Vận chuyển (xe, máy bay...)
    xuat_phat = scrapy.Field()  # Xuất phát từ (VD: Hồ Chí Minh)
    gia_tu = scrapy.Field()  # Giá từ (VD: 11,599,000 đ)
    
    # Nội dung tour
    trai_nghiem = scrapy.Field()  # Trải nghiệm (list)
    diem_nhan_hanh_trinh = scrapy.Field()  # Điểm nhấn hành trình (list)
    lich_trinh = scrapy.Field()  # Lịch trình từng ngày (list of dicts)
    
    # Dịch vụ
    dich_vu_bao_gom = scrapy.Field()  # Dịch vụ bao gồm (list)
    dich_vu_khong_bao_gom = scrapy.Field()  # Dịch vụ không bao gồm (list)
    
    # Ghi chú
    ghi_chu = scrapy.Field()  # Ghi chú (list)

    