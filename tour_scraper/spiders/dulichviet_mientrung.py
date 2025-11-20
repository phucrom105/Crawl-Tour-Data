import scrapy
import re
from ..items import TourItem
from urllib.parse import urljoin

def extract_tour_name(url, title=None):
    """Trích xuất tên tour ngắn gọn từ URL hoặc title"""
    
    MIEN_BAC = {
    'mien-bac': 'Miền Bắc', 'ha-noi': 'Hà Nội', 'bac-kan': 'Bắc Kạn', 'bac-ninh': 'Bắc Ninh',
    'bong-bang': 'Bông Bằng', 'dien-bien': 'Điện Biên', 'ha-giang': 'Hà Giang', 'ha-long': 'Hạ Long',
    'hoa-binh': 'Hòa Bình', 'lai-chau': 'Lai Châu', 'lang-son': 'Lạng Sơn', 'lao-cai': 'Lào Cai',
    'mai-chau': 'Mai Châu', 'moc-chau': 'Mộc Châu', 'ninh-binh': 'Ninh Bình', 'phu-tho': 'Phú Thọ',
    'sapa': 'Sapa', 'tay-bac': 'Tây Bắc', 'tam-coc': 'Tam Cốc', 'trang-an': 'Tràng An',
    'dong-bac': 'Đông Bắc', 'cao-bang': 'Cao Bằng', 'cat-ba': 'Cát Bà', 'thanh-hoa': 'Thanh Hóa',
    }

    MIEN_TRUNG = {
        'mien-trung': 'Miền Trung', 'da-nang': 'Đà Nẵng', 'binh-thuan': 'Bình Thuận', 'buon-ma-thuot': 'Buôn Ma Thuột',
        'binh-dinh': 'Bình Định', 'da-lat': 'Đà Lạt', 'dao-binh-ba': 'Đảo Bình Ba', 'dao-binh-hung': 'Đảo Bình Hưng',
        'hoi-an': 'Hội An', 'hue': 'Huế', 'nha-trang': 'Nha Trang', 'ninh-chu': 'Ninh Chữ',
        'ninh-thuan': 'Ninh Thuận', 'phan-thiet': 'Phan Thiết', 'phu-yen': 'Phú Yên', 'quy-nhon': 'Quy Nhơn',
        'quang-binh': 'Quảng Bình', 'quang-nam': 'Quảng Nam', 'quang-ngai': 'Quảng Ngãi', 'binh-binh': 'Bình Bình',
        'tay-nguyen': 'Tây Nguyên', 'phong-nha': 'Phong Nha', 'mui-ne': 'Mũi Né', 'kon-tum': 'Kon Tum',
    }

    MIEN_NAM = {
        'mien-nam': 'Miền Nam', 'tay-ninh': 'Tây Ninh', 'phu-quoc': 'Phú Quốc', 'an-giang': 'An Giang',
        'bac-lieu': 'Bạc Liêu', 'ben-tre': 'Bến Tre', 'ca-mau': 'Cà Mau', 'can-tho': 'Cần Thơ',
        'con-dao': 'Côn Đảo', 'chau-doc': 'Châu Đốc', 'dao-ba-lua': 'Đảo Bà Lụa', 'ha-tien': 'Hà Tiên',
        'kien-giang': 'Kiên Giang', 'long-an': 'Long An', 'nam-du': 'Nam Du', 'mien-tay': 'Miền Tây',
        'soc-trang': 'Sóc Trăng', 'tien-giang': 'Tiền Giang', 'dong-thap': 'Đồng Tháp', 'vung-tau': 'Vũng Tàu',
        'sai-gon': 'Sài Gòn', 'ho-chi-minh': 'Hồ Chí Minh', 'phu-quy': 'Phú Quý',
    }
    
    ALL_LOCATIONS = {**MIEN_BAC, **MIEN_TRUNG, **MIEN_NAM}
    url_lower = url.lower()
    
    # Tìm trong URL
    found = []
    for key, name in ALL_LOCATIONS.items():
        if key in url_lower:
            found.append((name, url_lower.index(key)))
    
    if found:
        found.sort(key=lambda x: x[1])
        return found[0][0]
    
    # Fallback: extract từ URL pattern
    match = re.search(r'/(?:tour|du-lich)-([a-z-]+)', url_lower)
    if match:
        slug = match.group(1)
        if slug in ALL_LOCATIONS:
            return ALL_LOCATIONS[slug]
    
    return "Tour Việt Nam"


class DuLichVietMienTrungSpider(scrapy.Spider):
    name = "dulichviet_mientrung"
    mien = "Miền Trung"
    allowed_domains = ["dulichviet.com.vn"]

    # Chỉ bắt đầu từ đúng trang này
    start_urls = ["https://dulichviet.com.vn/du-lich-mien-trung"]

    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'CONCURRENT_REQUESTS': 10,
        'DEPTH_LIMIT': 10,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': False,
    }

    def parse(self, response):
        self.logger.info(f"Đang crawl: {response.url}")

        # Lấy tất cả các tour boxes
        tour_boxes = response.xpath('//div[contains(@class, "mda-box-item")]')
        
        self.logger.info(f"Tìm thấy {len(tour_boxes)} tour boxes trên trang này")

        for box in tour_boxes:
            # Lấy link tour
            tour_link = box.xpath('.//a/@href').get()
            
            if not tour_link:
                continue
            
            tour_url = response.urljoin(tour_link)
            
            # Kiểm tra xem có thuộc miền Trung không
            if not self.is_still_in_mientrung_scope(tour_url):
                continue
            
            # Lấy hình ảnh từ tour box
            hinh_anh = box.xpath('.//img/@data-src').get()
            if not hinh_anh:
                hinh_anh = box.xpath('.//img/@src').get()
            
            # Xử lý URL hình ảnh
            if hinh_anh:
                if 'data:image' in hinh_anh or 'nophoto.jpg' in hinh_anh:
                    hinh_anh = None
                else:
                    if hinh_anh.startswith('//'):
                        hinh_anh = 'https:' + hinh_anh
                    elif not hinh_anh.startswith('http'):
                        hinh_anh = response.urljoin(hinh_anh)
            
            self.logger.info(f"Tour: {tour_url}")
            self.logger.info(f"Hình ảnh: {hinh_anh}")
            
            # Gửi request với metadata chứa hình ảnh
            yield scrapy.Request(
                tour_url, 
                callback=self.parse_tour_detail,
                meta={'hinh_anh_chinh': hinh_anh}
            )

        # Phân trang
        next_page = response.xpath('//a[@rel="next"]/@href | //a[contains(text(),"Sau")]/@href').get()
        if next_page:
            yield scrapy.Request(response.urljoin(next_page), callback=self.parse)

    def is_still_in_mientrung_scope(self, url):
        """Chỉ cho phép các URL thuộc phạm vi Miền Trung"""
        url_lower = url.lower()
        
        # Cấm nhảy sang miền khác
        forbidden = [
        '/du-lich-mien-bac', '/du-lich-mien-nam',
        '/du-lich-ha-noi', '/du-lich-ha-long', '/du-lich-sapa',
        '/du-lich-ninh-binh', '/du-lich-ha-giang', '/du-lich-mai-chau',
        '/du-lich-phu-quoc', '/du-lich-can-tho', '/du-lich-con-dao',
        '/du-lich-tay-ninh', '/du-lich-vung-tau', '/du-lich-ben-tre',
        '/du-lich-sai-gon', '/du-lich-ho-chi-minh'
    ]
        if any(bad in url_lower for bad in forbidden):
            return False

        # Ưu tiên các từ khóa chắc chắn là Miền Trung
        good_keywords = [
        # Miền Trung Bắc (Bắc Trung Bộ)
        'hue', 'quang-binh', 'quang-tri', 'quang-nam', 'quang-ngai',
        'phong-nha', 'ke-bang', 'dong-hoi', 'lang-co', 'bach-ma',
        
        # Miền Trung Duyên hải (Nam Trung Bộ)
        'da-nang', 'hoi-an', 'binh-dinh', 'phu-yen', 'quy-nhon',
        'khanh-hoa', 'nha-trang', 'ninh-thuan', 'binh-thuan',
        'cam-ranh', 'vinh-hy', 'ninh-chu', 'dao-binh-ba', 'dao-binh-hung',
        
        # Tây Nguyên
        'tay-nguyen', 'da-lat', 'lam-dong', 'gia-lai', 'kon-tum',
        'dak-lak', 'dak-nong', 'buon-ma-thuot', 'pleiku',
        
        # Các địa danh nổi tiếng Miền Trung
        'ba-na', 'son-tra', 'cham', 'my-son', 'cua-dai',
        'an-bang', 'tra-que', 'thanh-ha', 'cu-lao-cham',
        'eo-gio', 'ghenh-rang', 'ki-co', 'bai-xep',
        'vung-ro', 'ganh-da-dia', 'mui-dien', 'hang-son-doong',
        
        # Biển Miền Trung
        'phan-thiet', 'mui-ne', 'hon-rom', 'phan-rang',
        
        # Từ khóa tổng quát
        'mien-trung', 'du-lich-mien-trung'
    ]
        if any(kw in url_lower for kw in good_keywords):
            return True

        # Nếu URL vẫn nằm trong cây /du-lich-mien-trung
        if 'dulichviet.com.vn/du-lich-mien-trung' in url_lower:
            return True
        if '/du-lich-' in url_lower and not any(bad in url_lower for bad in forbidden):
            return True

        return False

    def parse_tour_detail(self, response):
        # Bảo vệ cuối cùng
        if not self.is_still_in_mientrung_scope(response.url):
            self.logger.warning(f"Bỏ qua tour ngoài miền Trung: {response.url}")
            return

        self.logger.info(f"Đang parse tour MIỀN TRUNG: {response.url}")
        
        item = TourItem()
        item['url'] = response.url
        
        # Lấy hình ảnh từ metadata (đã lấy từ trang danh sách)
        item['hinh_anh_chinh'] = response.meta.get('hinh_anh_chinh')
        self.logger.info(f"Hình ảnh chính: {item['hinh_anh_chinh']}")


        # 0. TÊN TOUR (TITLE)
        title = response.xpath('//div[@class="name"]/text()').get()
        if not title:
            # Fallback: thử lấy từ h1 hoặc title tag
            title = response.xpath('//h1/text()').get()
        if not title:
            title = response.xpath('//title/text()').get()
        
        item['title'] = title.strip() if title else None
        self.logger.info(f"Tên tour: {item['title']}")
        
        # 1. Tour name
        item['tour_name'] = extract_tour_name(response.url, item['title'])
        self.logger.info(f"Tour name: {item['tour_name']}") 

        # 2. MÃ TOUR
        ma_tour = response.xpath('//div[@class="at" and contains(text(), "Mã tour")]/following-sibling::div[@class="as"]/text()').get()
        item['ma_tour'] = ma_tour.strip() if ma_tour else None
        self.logger.info(f"Mã tour: {item['ma_tour']}")
        
        # 3. THỜI GIAN
        thoi_gian = response.xpath('//div[@class="at" and contains(text(), "Thời gian")]/following-sibling::div[@class="as"]/text()').get()
        item['thoi_gian'] = thoi_gian.strip() if thoi_gian else None
        self.logger.info(f"Thời gian: {item['thoi_gian']}")
        
        # 4. KHỞI HÀNH
        khoi_hanh_texts = response.xpath('//div[@class="at" and contains(text(), "Khởi hành")]/following-sibling::div[@class="as"]//text()').getall()
        if khoi_hanh_texts:
            khoi_hanh = ' '.join([t.strip() for t in khoi_hanh_texts if t.strip()])
            item['khoi_hanh'] = khoi_hanh.strip() if khoi_hanh else None
        else:
            item['khoi_hanh'] = None
        self.logger.info(f"Khởi hành: {item['khoi_hanh']}")
        
        # 5. VẬN CHUYỂN
        van_chuyen_texts = response.xpath('//div[@class="at" and contains(text(), "Vận Chuyển")]/following-sibling::div[@class="as"]//text()').getall()
        if van_chuyen_texts:
            van_chuyen = ' '.join([t.strip() for t in van_chuyen_texts if t.strip()])
            item['van_chuyen'] = van_chuyen.strip() if van_chuyen else None
        else:
            item['van_chuyen'] = None
        self.logger.info(f"Vận chuyển: {item['van_chuyen']}")
        
        # 6. XUẤT PHÁT
        xuat_phat_texts = response.xpath('//div[@class="at" and contains(text(), "Xuất phát")]/following-sibling::div[@class="as"]//text()').getall()
        if xuat_phat_texts:
            # Clean từng đoạn text
            cleaned_texts = [t.strip() for t in xuat_phat_texts if t.strip() and t.strip() != 'Từ']
            # Join lại và clean thêm lần nữa
            xuat_phat = ' '.join(cleaned_texts)
            # Remove extra whitespace và newlines
            xuat_phat = re.sub(r'\s+', ' ', xuat_phat).strip()
            item['xuat_phat'] = xuat_phat if xuat_phat else None
        else:
            item['xuat_phat'] = None
        self.logger.info(f"Xuất phát: {item['xuat_phat']}")
        
        # 7. GIÁ TỪ
        gia_tu = response.xpath('//span[contains(text(), "Giá từ")]/following-sibling::*/text()').get()
        if not gia_tu:
            gia_tu = response.xpath('//*[contains(text(), "Giá từ")]/following::text()[normalize-space()][1]').get()
        if not gia_tu:
            gia_tu = response.xpath('//div[@class="red" and @id="giactt"]/text()').get()
        
        item['gia_tu'] = gia_tu.strip() if gia_tu else None
        self.logger.info(f"Giá từ: {item['gia_tu']}")
        
        # 8. TRẢI NGHIỆM
        trai_nghiem = []
        
        # Strategy 1: Tìm trong các div class="attr" hoặc boxPrice
        attr_sections = response.xpath('//div[contains(@class, "attr") or contains(@class, "boxPrice")]//p[contains(., "Trải nghiệm") or contains(., "trải nghiệm")]')
        
        for p_elem in attr_sections:
            # Lấy tất cả text nodes bên trong <p>
            full_text = ''.join(p_elem.xpath('.//text()').getall())
            
            # Tách theo <br/> hoặc newline
            lines = re.split(r'<br\s*/?>', p_elem.get())
            if not lines or len(lines) == 1:
                lines = full_text.split('\n')
            
            for line in lines:
                cleaned = self.clean_text(line).strip()
                
                # Bỏ qua dòng chứa "Trải nghiệm:"
                if not cleaned or 'trải nghiệm' in cleaned.lower() and len(cleaned) < 20:
                    continue
                
                # Tìm các items có ✔️ hoặc ☑️
                if '✔️' in cleaned or '☑️' in cleaned:
                    # Tách nếu có nhiều items trên cùng 1 dòng
                    for prefix in ['✔️', '☑️']:
                        if prefix in cleaned:
                            parts = cleaned.split(prefix)
                            for part in parts[1:]:  # Skip phần trước prefix đầu tiên
                                experience = part.strip()
                                # Clean thêm các ký tự không cần thiết
                                experience = experience.strip('.,;:')
                                if experience and len(experience) > 10:
                                    trai_nghiem.append(experience)
                                    self.logger.info(f"  [TRẢI NGHIỆM] Strategy 1: {experience[:60]}...")
        
        # Strategy 2: Nếu chưa tìm thấy, tìm trong toàn bộ trang
        if not trai_nghiem:
            self.logger.info("Strategy 1 failed, trying Strategy 2...")
            
            # Tìm tất cả các đoạn văn bản có chứa "Trải nghiệm" và checkmarks
            all_text_blocks = response.xpath('//*[contains(., "Trải nghiệm") or contains(., "trải nghiệm")]')
            
            for block in all_text_blocks:
                text_content = ''.join(block.xpath('.//text()').getall())
                
                # Tách theo các checkmarks
                for prefix in ['✔️', '☑️']:
                    if prefix in text_content:
                        parts = text_content.split(prefix)
                        for part in parts[1:]:
                            # Lấy đến khi gặp checkmark tiếp theo hoặc newline
                            experience = part.split('\n')[0].strip()
                            experience = experience.split('✔️')[0].split('☑️')[0].strip()
                            experience = experience.strip('.,;:<br/>')
                            
                            if experience and len(experience) > 10:
                                # Kiểm tra không trùng
                                if experience not in trai_nghiem:
                                    trai_nghiem.append(experience)
                                    self.logger.info(f"  [TRẢI NGHIỆM] Strategy 2: {experience[:60]}...")
        
        # Strategy 3: Regex pattern matching
        if not trai_nghiem:
            self.logger.info("Strategy 2 failed, trying Strategy 3 (regex)...")
            
            # Lấy toàn bộ HTML
            html_text = response.text
            
            # Pattern: tìm các dòng có ✔️ hoặc ☑️ theo sau là text
            patterns = [
                r'[✔☑]️\s*([^✔☑<\n]{10,150})',
                r'[✔☑]️?\s*([^✔☑<\n]{10,150})',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html_text)
                for match in matches:
                    experience = self.clean_text(match).strip()
                    if experience and len(experience) > 10:
                        if experience not in trai_nghiem:
                            trai_nghiem.append(experience)
                            self.logger.info(f"  [TRẢI NGHIỆM] Strategy 3: {experience[:60]}...")

        item['trai_nghiem'] = trai_nghiem if trai_nghiem else None
        self.logger.info(f"Trải nghiệm: {len(trai_nghiem)} items found")
        
        # 9. LỊCH TRÌNH 
        lich_trinh = []
        flag2 = response.xpath('//div[@id="flag2"]')
        
        if flag2:
            self.logger.info("Found flag2 section, starting lich_trinh parsing")
            day_sections = flag2.xpath('.//div[@class="day active"] | .//div[contains(@class, "day active")]')
            self.logger.info(f"Found {len(day_sections)} day sections")

            for idx, day in enumerate(day_sections, 1):
                # Extract day title
                title_parts = day.xpath('.//div[@class="titDay"]//h2//text()').getall()
                day_title_full = ' '.join([t.strip() for t in title_parts if t.strip()])
                
                day_match = re.search(r'NGÀY\s+(\d+)', day_title_full, re.IGNORECASE)
                day_number = day_match.group(1) if day_match else str(idx)
                location = re.sub(r'NGÀY\s+\d+\s*\|?\s*', '', day_title_full, flags=re.IGNORECASE).strip()
                
                if not location:
                    location = day_title_full.strip()
                
                day_title = f"NGÀY {day_number}: {location}" if location else f"NGÀY {day_number}"
                self.logger.info(f"Processing {day_title}")

                # Extract content theo cấu trúc HTML
                contday = day.xpath('.//div[@class="contDay"]//div[@class="the-content desc"]')
                activities = []
                
                if contday:
                    # Parse từng element để giữ nguyên format
                    for elem in contday.xpath('.//*[self::p or self::div or self::ul]'):
                        elem_html = elem.get()
                        
                        # Xử lý <p> tags
                        if elem.xpath('name()').get() == 'p':
                            # Lấy HTML và convert <br/> thành \n
                            p_html = elem.get()
                            # Split by <br/> tags
                            parts = re.split(r'<br\s*/?>', p_html)
                            
                            full_text = ''
                            for part in parts:
                                # Clean HTML tags but keep text
                                text = re.sub(r'<[^>]+>', '', part)
                                text = self.clean_text(text)
                                if text:
                                    full_text += text + '\n'
                            
                            full_text = full_text.rstrip('\n')
                            
                            # Kiểm tra xem có phải time marker không
                            if re.match(r'^(Sáng|Trưa|Chiều|Tối|Buổi|\d{2}h\d{2})\s*:', full_text, re.IGNORECASE):
                                # Time marker - giữ nguyên không xuống dòng
                                if full_text:
                                    activities.append(full_text)
                                    self.logger.debug(f"    [TIME SECTION] {full_text[:60]}...")
                            elif full_text and len(full_text) > 20:
                                activities.append(full_text)
                        
                        # Xử lý <ul> tags
                        elif elem.xpath('name()').get() == 'ul':
                            li_items = elem.xpath('.//li')
                            ul_text = ''
                            for li in li_items:
                                li_texts = li.xpath('.//text()').getall()
                                li_text = ' '.join([self.clean_text(t) for t in li_texts if self.clean_text(t)])
                                if li_text:
                                    ul_text += f"• {li_text}\n"
                            
                            if ul_text:
                                activities.append(ul_text.rstrip('\n'))
                        
                        # Xử lý <div> tags (thường chứa time markers)
                        elif elem.xpath('name()').get() == 'div':
                            div_texts = elem.xpath('.//text()').getall()
                            div_text = ' '.join([self.clean_text(t) for t in div_texts if self.clean_text(t)])
                            if div_text and re.match(r'^(Sáng|Trưa|Chiều|Tối|Buổi|\d{2}h\d{2})', div_text, re.IGNORECASE):
                                activities.append(div_text)
                                self.logger.debug(f"    [TIME MARKER] {div_text}")
                
                if day_title and activities:
                    lich_trinh.append({
                        'ngay': day_title,
                        'hoat_dong': activities
                    })
                    self.logger.info(f"  ✓ {day_title} - {len(activities)} sections")

        item['lich_trinh'] = lich_trinh if lich_trinh else None
        self.logger.info(f"========== LỊCH TRÌNH: {len(lich_trinh)} days ==========")
        
        # 10. DỊCH VỤ - DICH VỤ BAO GỒM & KHÔNG BAO GỒM 
        dich_vu_bao_gom = []
        dich_vu_khong_bao_gom = []
        flag3 = response.xpath('//div[@id="flag3"]')
        if flag3:
            # Lấy toàn bộ text từ div the-content, clean và split lines
            full_text = ' '.join(flag3.xpath('.//div[contains(@class, "the-content") or contains(@class, "desc")]//text()').getall())
            full_text = re.sub(r'\s+', ' ', full_text).strip()  # Clean extra spaces
            
            # Normalize headers (ignore case, remove accents for matching)
            def normalize(text):
                text = text.lower()
                text = re.sub(r'[áàảãạăắằẳẵặâấầẩẫậ]', 'a', text)
                text = re.sub(r'[éèẻẽẹêếềểễệ]', 'e', text)
                text = re.sub(r'[íìỉĩị]', 'i', text)
                text = re.sub(r'[óòỏõọôốồổỗộơớờởỡợ]', 'o', text)
                text = re.sub(r'[úùủũụưứừửữự]', 'u', text)
                text = re.sub(r'[ýỳỷỹỵ]', 'y', text)
                text = re.sub(r'đ', 'd', text)
                return text
            
            normalized_full = normalize(full_text)
            
            # Tìm vị trí headers
            bao_gom_patterns = [
                'gia tour bao gom', 'dich vu bao gom', 'bao gom', 
                'gia tour bao gom:', 'dich vu bao gom:', 'bao gom:'
            ]
            khong_bao_gom_patterns = [
                'khong bao gom', 'kh ong bao gom', 'khong bao gom:', 
                'kh ong bao gom:', 'khong bao gom'
            ]
            
            bao_gom_start = None
            khong_bao_gom_start = None
            
            for pattern in bao_gom_patterns:
                match = normalized_full.find(pattern)
                if match != -1:
                    bao_gom_start = match + len(pattern)
                    self.logger.info(f">>> Found included header at {match}: {pattern}")
                    break
            
            for pattern in khong_bao_gom_patterns:
                match = normalized_full.find(pattern)
                if match != -1:
                    khong_bao_gom_start = match + len(pattern)
                    self.logger.info(f">>> Found excluded header at {match}: {pattern}")
                    break
            
            # Extract content between headers
            if bao_gom_start is not None:
                end = khong_bao_gom_start if khong_bao_gom_start else len(full_text)
                bao_gom_text = full_text[bao_gom_start:end].strip()
                # Split into items by bullets or sentences
                items = re.split(r'(?<=[\.\?!;])\s+|\n+|- |\• |\* |;', bao_gom_text)
                for service_item in items:  # Changed 'item' to 'service_item'
                    cleaned = self.clean_text(service_item).strip()
                    if cleaned and len(cleaned) > 10 and not any(p in normalize(cleaned) for p in khong_bao_gom_patterns + ['ghi chu', 'luu y']):
                        dich_vu_bao_gom.append(cleaned)
                        self.logger.debug(f"  [BAO GỒM] + {cleaned[:50]}...")
            
            if khong_bao_gom_start is not None:
                khong_bao_gom_text = full_text[khong_bao_gom_start:].strip()
                # Stop at unrelated sections
                stop_patterns = ['ghi chu', 'luu y', 'quy dinh', 'dieu kien', 'gia ve danh cho tre em', 'cac quy dinh', 'thu tuc']
                stop_pos = len(khong_bao_gom_text)
                for pattern in stop_patterns:
                    match = normalized_full[khong_bao_gom_start:].find(pattern)
                    if match != -1 and match < stop_pos:
                        stop_pos = match
                khong_bao_gom_text = khong_bao_gom_text[:stop_pos].strip()
                
                items = re.split(r'(?<=[\.\?!;])\s+|\n+|- |\• |\* |;', khong_bao_gom_text)
                for service_item in items:  # Changed 'item' to 'service_item'
                    cleaned = self.clean_text(service_item).strip()
                    if cleaned and len(cleaned) > 10:
                        dich_vu_khong_bao_gom.append(cleaned)
                        self.logger.debug(f"  [KHÔNG BAO GỒM] + {cleaned[:50]}...")

            # Fallback: if no patterns found, try extracting from <li>
            if not dich_vu_bao_gom and not dich_vu_khong_bao_gom:
                lis = flag3.xpath('.//li')
                for li in lis:
                    text = ' '.join(li.xpath('.//text()').getall())
                    cleaned = self.clean_text(text)
                    if cleaned and len(cleaned) > 10:
                        dich_vu_bao_gom.append(cleaned)

        item['dich_vu_bao_gom'] = dich_vu_bao_gom if dich_vu_bao_gom else None
        item['dich_vu_khong_bao_gom'] = dich_vu_khong_bao_gom if dich_vu_khong_bao_gom else None
        self.logger.info(f"Dịch vụ bao gồm: {len(dich_vu_bao_gom)} items")
        self.logger.info(f"Dịch vụ không bao gồm: {len(dich_vu_khong_bao_gom)} items")
        
        # 10. GHI CHÚ - FIXED
        ghi_chu = []
        flag4 = response.xpath('//div[@id="flag4"]')
        
        if flag4:
            # Lấy toàn bộ content trong div.the-content
            content_div = flag4.xpath('.//div[contains(@class, "the-content") or contains(@class, "desc")]')
            
            if content_div:
                # Parse theo thứ tự các elements (p, ul)
                for elem in content_div.xpath('.//*[self::p or self::ul]'):
                    elem_name = elem.xpath('name()').get()
                    
                    if elem_name == 'p':
                        # Đây có thể là tiêu đề (có <strong><u>) hoặc nội dung text thường
                        p_texts = elem.xpath('.//text()').getall()
                        p_text = ' '.join([t.strip() for t in p_texts if t.strip()])
                        p_text = self.clean_text(p_text)
                        
                        # Kiểm tra xem có phải tiêu đề không (có <strong> và <u>)
                        has_strong_u = elem.xpath('.//strong//u') or elem.xpath('.//u//strong')
                        
                        if p_text:
                            if has_strong_u:
                                # Là tiêu đề - thêm format đặc biệt
                                ghi_chu.append(f"__{p_text}__")
                                self.logger.debug(f"  [GHI CHÚ - HEADER] {p_text[:60]}...")
                            elif len(p_text) > 20:
                                # Là đoạn text thường
                                ghi_chu.append(p_text)
                                self.logger.debug(f"  [GHI CHÚ - TEXT] {p_text[:60]}...")
                    
                    elif elem_name == 'ul':
                        # Parse các <li> items
                        li_items = elem.xpath('.//li')
                        for li in li_items:
                            li_texts = li.xpath('.//text()').getall()
                            li_text = ' '.join([t.strip() for t in li_texts if t.strip()])
                            li_text = self.clean_text(li_text)
                            
                            if li_text and len(li_text) > 10:
                                # Thêm bullet point
                                ghi_chu.append(f"* {li_text}")
                                self.logger.debug(f"  [GHI CHÚ - ITEM] {li_text[:60]}...")
        
        item['ghi_chu'] = ghi_chu if ghi_chu else None
        self.logger.info(f"Ghi chú: {len(ghi_chu)} items")

        yield item

    def clean_text(self, text):
        """Clean text - remove HTML entities, extra spaces"""
        if not text:
            return None
        
        # Remove HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('\xa0', ' ')
        text = text.replace('&ndash;', '–')
        text = text.replace('&mdash;', '—')
        text = text.replace('&ldquo;', '"')
        text = text.replace('&rdquo;', '"')
        text = text.replace('&hellip;', '...')
        text = re.sub(r'&[a-z]+;', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        text = text.strip(':').strip()
        
        return text if text else None 