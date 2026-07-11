import os
import re

# PDF 생성을 위한 리포트랩 라이브러리
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# [설정]
TXT_FOLDER = "./squid_game_data"  # 수집된 텍스트 파일들이 있는 폴더
OUTPUT_PDF_NAME = "Merged_Squid_Game_Wiki.pdf"  # 새로 만들 PDF 이름

# ★ 중요: 한글이나 특수문자가 깨지지 않도록 시스템 기본 폰트 등록 (Windows 기준 맑은고딕)
# Mac 사용자라면 '/System/Library/Fonts/Supplemental/AppleGothic.ttf' 등으로 변경하세요.
font_path = "C:\\Windows\\Fonts\\malgun.ttf"
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont("MalgunGothic", font_path))
    FONT_NAME = "MalgunGothic"
else:
    FONT_NAME = "Helvetica"  # 폰트가 없을 경우 기본 영문 폰트 사용

def convert_txt_to_pdf(folder_path, output_pdf):
    # 1. 폴더 내 모든 .txt 파일 목록 가져와서 정렬
    if not os.path.exists(folder_path):
        print(f"❌ '{folder_path}' 폴더를 찾을 수 없습니다. 경로를 확인해 주세요.")
        return
        
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    files.sort()  # 알파벳 순 정렬
    
    print(f"👉 총 {len(files)}개의 텍스트 파일을 찾았습니다. PDF 병합을 시작합니다.")

    # 2. PDF 스타일 정의
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'FandomTitle',
        parent=styles['Heading1'],
        fontName=FONT_NAME,
        fontSize=22,
        leading=26,
        spaceAfter=15,
        textColor='black'
    )
    
    body_style = ParagraphStyle(
        'FandomBody',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        leading=15,
        spaceAfter=8
    )

    story = []
    file_count = 0

    # 3. 각 텍스트 파일을 읽어서 PDF 'story'에 추가
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            if not lines:
                continue
                
            print(f"[{file_count+1}] 병합 중: {filename}")
            
            # 첫 번째 줄(Title)과 두 번째 줄(URL) 분리 처리 시도
            # 크롤러가 상단에 Title과 URL을 적어두었기 때문에 이를 이쁘게 구분합니다.
            doc_title = filename.replace('.txt', '')
            
            # 문서 제목을 상단에 크게 배치
            story.append(Paragraph(doc_title, title_style))
            
            # 본문 내용 한 줄씩 읽어서 추가
            for line in lines:
                line_text = line.strip()
                if not line_text:
                    continue
                
                # 리포트랩 XML 에러 방지를 위해 특수문자 치환
                line_text = line_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                # 이미 텍스트에 Title이나 URL 표시가 있으면 작게 표현되거나 그냥 들어감
                story.append(Paragraph(line_text, body_style))
            
            # 한 문서가 끝나면 다음 장으로 넘기기 (책처럼 분리)
            story.append(PageBreak())
            file_count += 1
            
        except Exception as e:
            print(f"❌ 파일 읽기 실패 ({filename}): {e}")
            continue

    # 4. 하나의 거대한 PDF 파일로 빌드
    if story:
        print("\n PDF 파일 빌드 중... 잠시만 기다려주세요.")
        doc = SimpleDocTemplate(output_pdf, pagesize=letter)
        doc.build(story)
        print(f"✨ PDF 생성 완료! 파일명: {output_pdf} (총 {file_count}개 문서 합쳐짐)")
    else:
        print("❌ PDF로 변환할 내용이 없습니다.")

# 실행
convert_txt_to_pdf(TXT_FOLDER, OUTPUT_PDF_NAME)