import requests
from bs4 import BeautifulSoup
import time
import os
import re

# 설정
BASE_URL = "https://squid-game.fandom.com"
START_URL = f"{BASE_URL}/wiki/Special:AllPages"
SAVE_FOLDER = "squid_game_data2"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def clean_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title).strip()

def scrape_all_pages_fixed(start_url):
    current_list_url = start_url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    page_count = 0

    while current_list_url:
        print(f"\n--- 목록 페이지 탐색 중: {current_list_url} ---")
        response = requests.get(current_list_url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ 목록 페이지 접속 실패 (코드: {response.status_code})")
            break
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # [수정 포인트 1] 특정 클래스명을 찾지 않고, 'Special:AllPages' 내의 모든 위키 문서 링크를 다 찾음
        # 주소에 '/wiki/'가 포함되어 있고, 'Special:'이 포함되지 않은 모든 링크를 타겟팅합니다.
        all_links = soup.find_all("a", href=True)
        valid_links = []
        
        for l in all_links:
            href = l["href"]
            title = l.get_text(strip=True)
            # 위키 문서 링크 조건 필터링
            if href.startswith("/wiki/") and "Special:" not in href and "File:" not in href and "Category:" not in href:
                if title and l.find_parent("table") is None: # 메뉴 바 등에 있는 링크 제외
                    valid_links.append((title, href))
        
        # 중복 링크 제거
        valid_links = list(set(valid_links))
        print(f"👉 현재 페이지에서 발견된 하위 문서 수: {len(valid_links)}개")

        if not valid_links:
            print("❌ 하위 문서 링크를 찾지 못했습니다. 구조를 다시 확인해야 합니다.")
            break

        # 발견된 하위 문서 순회하며 크롤링
        for page_title, page_href in valid_links:
            full_page_url = BASE_URL + page_href
            try:
                print(f"[{page_count+1}] 수집 중: {page_title}")
                page_res = requests.get(full_page_url, headers=headers)
                page_soup = BeautifulSoup(page_res.text, "html.parser")
                
                # [수정 포인트 2] 본문 영역을 아주 넓게 잡음 (하나라도 걸리게)
                content_div = page_soup.find("div", class_="mw-parser-output")
                if not content_div:
                    content_div = page_soup.find("div", id="content")
                if not content_div:
                    content_div = page_soup.find("main")
                
                if content_div:
                    for noscript in content_div(["noscript", "style", "script"]):
                        noscript.decompose()
                        
                    text_content = content_div.get_text()
                    
                    safe_filename = clean_filename(page_title)
                    if not safe_filename:
                        continue
                        
                    file_path = os.path.join(SAVE_FOLDER, f"{safe_filename}.txt")
                    
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f"Title: {page_title}\n")
                        f.write(f"URL: {full_page_url}\n")
                        f.write("-" * 50 + "\n")
                        f.write(text_content.strip())
                        
                    page_count += 1
                
                time.sleep(0.5) # 안전 기어
                
            except Exception as e:
                print(f"❌ 에러 건너뜀 ({page_title}): {e}")
                continue
        
        # [수정 포인트 3] 다음 페이지 버튼 매칭 방식 개선
        next_url = None
        nav_links = soup.find_all("a")
        for nl in nav_links:
            text = nl.get_text()
            # "Next page" 혹은 ">" 모양의 링크가 있으면 다음 목록 주소로 지정
            if "Next page" in text or "Next" in text:
                next_url = BASE_URL + nl["href"]
                break
                
        current_list_url = next_url

    print(f"\n✨ 크롤링 완료! 총 {page_count}개의 문서가 '{SAVE_FOLDER}' 폴더에 저장되었습니다.")

# 실행
scrape_all_pages_fixed(START_URL)