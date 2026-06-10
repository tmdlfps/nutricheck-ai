import base64
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from google import genai
from PIL import Image


# -----------------------------
# 페이지 기본 설정
# -----------------------------
st.set_page_config(
    page_title="NutriCheck AI",
    page_icon="💊",
    layout="centered"
)


# -----------------------------
# 페이지 상태 관리
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"


# -----------------------------
# 공통 UI 스타일
# -----------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3 {
    letter-spacing: -0.03em;
}

[data-testid="stMetric"] {
    background-color: #f8fafc;
    border: 1px solid #e5e7eb;
    padding: 12px;
    border-radius: 12px;
}

.stAlert {
    border-radius: 12px;
}

div[data-testid="stFileUploader"] {
    border: 1px dashed #cbd5e1;
    border-radius: 12px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# 이미지 파일을 base64로 변환
# -----------------------------
def get_base64_of_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# -----------------------------
# 첫 화면
# -----------------------------
def show_home_page():
    hero_path = Path("hero.png")

    if hero_path.exists():
        hero_base64 = get_base64_of_image(hero_path)

        st.markdown(
            f"""
            <style>
            .hero-container {{
                position: relative;
                height: 82vh;
                border-radius: 28px;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-top: 10px;
                margin-bottom: 24px;
                background-image: url("data:image/png;base64,{hero_base64}");
                background-size: cover;
                background-position: center;
                box-shadow: 0 20px 60px rgba(15, 23, 42, 0.16);
            }}

            .hero-container::before {{
                content: "";
                position: absolute;
                inset: 0;
                background: rgba(255, 255, 255, 0.18);
                backdrop-filter: blur(2px);
            }}

            .hero-card {{
                position: relative;
                z-index: 2;
                text-align: center;
                max-width: 780px;
                padding: 42px 46px;
                border-radius: 28px;
                background: rgba(255, 255, 255, 0.55);
                border: 1px solid rgba(255, 255, 255, 0.7);
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
                backdrop-filter: blur(12px);
            }}

            .hero-badge {{
                display: inline-block;
                background: rgba(14, 165, 233, 0.13);
                border: 1px solid rgba(14, 165, 233, 0.22);
                color: #075985;
                padding: 8px 15px;
                border-radius: 999px;
                font-size: 0.92rem;
                font-weight: 700;
                margin-bottom: 18px;
            }}

            .hero-title {{
                font-size: 3.3rem;
                font-weight: 900;
                color: #0f172a;
                margin-bottom: 14px;
                letter-spacing: -0.06em;
            }}

            .hero-subtitle {{
                font-size: 1.13rem;
                line-height: 1.75;
                color: #334155;
                margin-bottom: 4px;
            }}

            .hero-highlight {{
                color: #0369a1;
                font-weight: 800;
            }}
            </style>

            <div class="hero-container">
                <div class="hero-card">
                    <div class="hero-badge">AI 기반 맞춤형 영양제 분석 서비스</div>
                    <div class="hero-title">💊 NutriCheck AI</div>
                    <div class="hero-subtitle">
                        영양제 성분표와 사용자 생활 습관 데이터를 함께 분석하여<br>
                        <span class="hero-highlight">핵심 성분, 위험도, 복용 시 주의사항</span>을 직관적으로 안내합니다.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown("""
        <div style="
            height: 70vh;
            border-radius: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            background: linear-gradient(135deg, #e0f2fe, #f8fafc);
            color: #0f172a;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(15, 23, 42, 0.12);
            ">
            <div>
                <div style="font-size: 3.2rem; font-weight: 900; margin-bottom: 12px;">💊 NutriCheck AI</div>
                <div style="font-size: 1.1rem; line-height: 1.7;">
                    영양제 성분표와 생활 습관을 함께 분석하여<br>
                    맞춤형 복용 주의사항을 안내하는 AI 웹앱입니다.
                </div>
                <div style="margin-top: 18px; color: #64748b;">
                    ※ hero.png 파일을 프로젝트 폴더에 넣으면 배경 이미지가 표시됩니다.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 1.25, 1])

    with center_col:
        if st.button("🚀 분석 시작하기", use_container_width=True, type="primary"):
            st.session_state.page = "analyzer"
            st.rerun()

    st.markdown("### 주요 기능")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("📷 **성분표 이미지 분석**\n\n영양제 라벨과 성분표 이미지를 업로드하여 핵심 성분을 추출합니다.")

    with col2:
        st.info("📊 **데이터 시각화**\n\n생활 습관 점수와 성분 함량 비율을 그래프로 확인할 수 있습니다.")

    with col3:
        st.info("💡 **맞춤형 주의사항**\n\n사용자 정보와 설문을 반영하여 안전/주의/위험 결과를 제공합니다.")


# -----------------------------
# 생활 습관 점수 계산
# -----------------------------
def get_lifestyle_scores(sleep, coffee, sunlight, meal, fatigue, supplement_count):
    sleep_score = {
        "6시간 미만": 3,
        "6~8시간": 1,
        "8시간 이상": 1
    }[sleep]

    coffee_score = {
        "거의 안 마심": 1,
        "하루 1잔": 1,
        "하루 2잔 이상": 2
    }[coffee]

    sunlight_score = {
        "적음": 3,
        "보통": 2,
        "많음": 1
    }[sunlight]

    meal_score = {
        "불규칙": 3,
        "보통": 2,
        "규칙적": 1
    }[meal]

    fatigue_score = {
        "낮음": 1,
        "보통": 2,
        "높음": 3
    }[fatigue]

    supplement_score = {
        "없음": 1,
        "1개": 1,
        "2~3개": 2,
        "4개 이상": 3
    }[supplement_count]

    return {
        "수면": sleep_score,
        "카페인": coffee_score,
        "햇빛 노출": sunlight_score,
        "식사 규칙성": meal_score,
        "피로감": fatigue_score,
        "영양제 개수": supplement_score
    }


# -----------------------------
# 프롬프트 생성
# -----------------------------
def make_prompt(
    gender, age, height, weight, blood_pressure, blood_sugar, medicine,
    sleep, coffee, sunlight, meal, fatigue, supplement_count, purpose,
    lifestyle_scores, average_score, max_factor
):
    return f"""
너는 영양제 성분표를 분석하는 AI 안전 정보 도우미이다.
의학적 진단이나 처방은 하지 말고, 참고용 정보와 주의사항만 제공해야 한다.

[사용자 정보]
- 성별: {gender}
- 나이: {age}
- 키: {height}cm
- 몸무게: {weight}kg
- 혈압 상태: {blood_pressure}
- 혈당 상태: {blood_sugar}
- 복용 중인 약 또는 질환: {medicine}

[생활 습관]
- 수면 시간: {sleep}
- 카페인 섭취: {coffee}
- 햇빛 노출: {sunlight}
- 식사 규칙성: {meal}
- 피로감: {fatigue}
- 현재 복용 중인 영양제 개수: {supplement_count}
- 영양제 복용 목적: {purpose}

[생활 습관 주의 점수]
- 수면: {lifestyle_scores["수면"]}점
- 카페인: {lifestyle_scores["카페인"]}점
- 햇빛 노출: {lifestyle_scores["햇빛 노출"]}점
- 식사 규칙성: {lifestyle_scores["식사 규칙성"]}점
- 피로감: {lifestyle_scores["피로감"]}점
- 영양제 개수: {lifestyle_scores["영양제 개수"]}점
- 평균 주의 점수: {average_score:.1f}점
- 가장 주의할 생활 습관 항목: {max_factor}

[분석 대상 핵심 성분]
- 비타민 D
- 비타민 C
- 아연
- 철분
- 칼슘
- 마그네슘

[데이터 처리 조건]
1. 성분표에 없는 성분은 절대 추측하지 말고 반드시 "검출되지 않음"이라고 표시한다.
2. 성분명은 보이지만 함량이 명확하지 않으면 "함량 정보 부족"이라고 표시한다.
3. 확인된 성분만 위험도 분석에 사용한다.
4. 동일 성분이 여러 이름으로 표시될 경우 하나로 통합한다.
   예: Vitamin D3, Colecalciferol은 비타민 D로 통합한다.
   예: Zinc, zinc oxide는 아연으로 통합한다.
   예: Calcium carbonate, calcium phosphate는 칼슘으로 통합한다.
5. 함량이 일반적인 영양제 범위를 크게 벗어나거나 단위가 불명확하면 "확인 필요"라고 표시한다.
6. 분석 대상 6대 성분 외의 성분이 보이면 "기타 확인 성분"에 따로 적되, 핵심 위험도 판단은 6대 성분 중심으로 한다.
7. 여러 장의 이미지가 입력된 경우, 각 이미지를 서로 다른 영양제 제품으로 보고 전체 복용 조합 관점에서 중복 성분과 주의 조합을 분석한다.

[중요 조건]
1. 단일 성분 제품일 경우 "단일 성분 중심 제품"이라고 설명한다.
2. 여러 성분이 포함된 제품일 경우 "복합 영양제 또는 멀티 영양제"라고 설명한다.
3. 위험도는 반드시 "안전", "주의", "위험" 중 하나로 분류한다.
4. 생활 습관 설문은 질병 진단이 아니라 참고용 맞춤 분석 자료로만 사용한다.
5. 복용 중인 약이나 질환 정보가 있으면 단정하지 말고 전문가 상담 필요성을 강조한다.
6. 인사말, 자기소개, 불필요한 서론 없이 바로 "0. 입력 제품 요약"부터 출력한다.
7. "복용해도 무방하다", "반드시 효과가 있다"처럼 단정적인 표현은 피하고, 참고용 표현을 사용한다.

[분석 지시]
1. 입력된 영양제 라벨 이미지 또는 텍스트에서 성분 정보를 읽는다.
2. 비타민 D, 비타민 C, 아연, 철분, 칼슘, 마그네슘이 포함되어 있는지 확인한다.
3. 포함된 성분의 함량을 정리한다.
4. 과다 섭취 가능성, 성분 간 주의 조합, 생활 습관과 관련된 주의사항을 분석한다.
5. 사용자가 이해하기 쉬운 한국어로 설명한다.
6. 의학적 진단이 아니며 전문가 상담이 필요할 수 있다는 문구를 포함한다.

[출력 제한]
반드시 "0. 입력 제품 요약"으로 시작한다.
"안녕하세요", "분석을 진행하겠습니다", "참고용 정보입니다" 같은 서론 문장은 쓰지 않는다.

[출력 형식]
아래 형식을 반드시 지켜라.

0. 입력 제품 요약
- 분석한 제품 수:
- 제품별 주요 성분:

1. 인식된 제품 유형
- 제품 유형:
- 판단 이유:

2. 6대 핵심 성분 탐지 결과
- 비타민 D:
- 비타민 C:
- 아연:
- 철분:
- 칼슘:
- 마그네슘:

3. 기타 확인 성분
- 기타 성분:
- 설명:

4. 확인된 성분 중심 분석
- 확인된 주요 성분:
- 함량:
- 관련 설명:

5. 생활 습관 데이터 해석
- 평균 주의 점수:
- 가장 주의할 생활 습관 항목:
- 해석:

6. 개인 맞춤형 분석
- 수면:
- 카페인:
- 햇빛 노출:
- 식사 습관:
- 피로감:
- 복용 중인 영양제 개수:
- 복용 목적:

7. 성분 간 주의 조합
- 주의할 조합:
- 이유:
- 확인된 성분만으로 뚜렷한 주의 조합이 없으면 "확인된 성분만으로는 뚜렷한 주의 조합이 발견되지 않음"이라고 표시:

8. 종합 위험도
- 안전 / 주의 / 위험 중 하나:
- 판단 이유:

9. 복용 조언
- 추천 행동:
- 피해야 할 행동:

10. 주의 문구
- 본 결과는 의학적 진단이 아니며, 질환이 있거나 약을 복용 중인 경우 의사 또는 약사와 상담해야 합니다.

11. 시각화용 함량 데이터(mg 기준)
VISUALIZATION_DATA_START
비타민 D: 숫자 mg
비타민 C: 숫자 mg
아연: 숫자 mg
철분: 숫자 mg
칼슘: 숫자 mg
마그네슘: 숫자 mg
기타: 숫자 mg
VISUALIZATION_DATA_END

[시각화용 함량 데이터 작성 규칙]
1. 위 11번 항목은 그래프 생성을 위한 데이터이므로 반드시 작성한다.
2. 가능하면 모든 함량을 mg 기준으로 환산한다.
3. 검출되지 않은 성분은 0 mg으로 표시한다.
4. 함량을 알 수 없는 성분은 0 mg으로 표시한다.
5. 기타는 6대 핵심 성분 외에 확인된 성분들의 대략적인 총합을 mg 기준으로 적는다.
6. 정확한 환산이 어려운 경우에도 성분표를 바탕으로 가능한 범위에서 숫자만 작성한다.
7. 숫자와 mg 단위 외의 설명을 VISUALIZATION_DATA_START와 VISUALIZATION_DATA_END 사이에 넣지 않는다.
"""


# -----------------------------
# Gemini 분석 함수
# -----------------------------
def analyze_with_gemini(api_key, prompt, image_files=None, text_input=None):
    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.5-flash"

    if image_files:
        contents = [prompt]

        for idx, image_file in enumerate(image_files, start=1):
            image_file.seek(0)
            image = Image.open(image_file)
            contents.append(f"\n[영양제 성분표 이미지 {idx}]")
            contents.append(image)

        response = client.models.generate_content(
            model=model_name,
            contents=contents
        )

    else:
        full_prompt = prompt + f"""

[사용자가 직접 입력한 영양제 정보]
{text_input}
"""
        response = client.models.generate_content(
            model=model_name,
            contents=full_prompt
        )

    return response.text


# -----------------------------
# AI 결과에서 6대 성분 탐지 상태 추출
# -----------------------------
def extract_nutrient_status(ai_text):
    nutrients = ["비타민 D", "비타민 C", "아연", "철분", "칼슘", "마그네슘"]
    result = []

    for nutrient in nutrients:
        pattern = rf"{re.escape(nutrient)}\s*:\s*(.*)"
        match = re.search(pattern, ai_text)

        if match:
            content = match.group(1).strip()

            if "검출되지 않음" in content or "없음" in content or "포함되어 있지" in content:
                status = "미검출"
                score = 0
            elif "함량 정보 부족" in content or "불명확" in content:
                status = "함량 정보 부족"
                score = 0.5
            elif "확인 필요" in content:
                status = "확인 필요"
                score = 0.5
            else:
                status = "검출"
                score = 1
        else:
            content = "결과에서 항목을 찾지 못함"
            status = "확인 필요"
            score = 0.5

        result.append({
            "성분": nutrient,
            "상태": status,
            "점수": score,
            "내용": content
        })

    return pd.DataFrame(result)


# -----------------------------
# AI 결과에서 시각화용 함량 데이터 추출
# -----------------------------
def extract_composition_data(ai_text):
    labels = ["비타민 D", "비타민 C", "아연", "철분", "칼슘", "마그네슘", "기타"]
    data = []

    section_match = re.search(
        r"VISUALIZATION_DATA_START(.*?)VISUALIZATION_DATA_END",
        ai_text,
        re.DOTALL
    )

    if section_match:
        target_text = section_match.group(1)
    else:
        target_text = ai_text

    for label in labels:
        pattern = rf"{re.escape(label)}\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*mg"
        match = re.search(pattern, target_text)

        if match:
            value = float(match.group(1))
        else:
            value = 0.0

        data.append({
            "성분": label,
            "함량(mg)": value
        })

    df = pd.DataFrame(data)
    df = df[df["함량(mg)"] > 0].copy()

    if not df.empty:
        total = df["함량(mg)"].sum()
        df["비율(%)"] = (df["함량(mg)"] / total * 100).round(1)

    return df


# -----------------------------
# 시각화용 데이터 구간 제거
# -----------------------------
def remove_visualization_section(ai_text):
    return re.sub(
        r"11\. 시각화용 함량 데이터\(mg 기준\).*?VISUALIZATION_DATA_END",
        "",
        ai_text,
        flags=re.DOTALL
    ).strip()


# -----------------------------
# 분석기 화면
# -----------------------------
def show_analyzer_page():
    st.title("💊 NutriCheck AI")
    st.subheader("AI 기반 맞춤형 영양제 성분 위험 분석기")

    if st.button("← 처음 화면으로 돌아가기"):
        st.session_state.page = "home"
        st.rerun()

    st.warning(
        "본 서비스는 의학적 진단이나 처방이 아닌 참고용 정보입니다. "
        "복용 중인 약물이 있거나 질환이 있는 경우 반드시 의사 또는 약사와 상담하세요."
    )

    # API Key 설정
st.sidebar.header("API 설정")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.sidebar.success("Gemini API Key가 Streamlit Secrets에 설정되어 있습니다.")
except Exception:
    api_key = st.sidebar.text_input("Gemini API Key 입력", type="password")
    st.sidebar.caption("Streamlit Secrets가 없을 때만 직접 입력합니다.")

if not api_key:
    st.info("Streamlit Secrets 또는 왼쪽 사이드바에 Gemini API Key를 설정하면 분석을 시작할 수 있습니다.")

    # 사용자 기본 정보
    st.header("1. 사용자 건강 정보 입력")

    col1, col2 = st.columns(2)

    with col1:
        gender = st.selectbox("성별", ["선택 안 함", "남성", "여성", "기타"])
        age = st.number_input("나이", min_value=1, max_value=120, value=20)
        height = st.number_input("키(cm)", min_value=50, max_value=250, value=170)

    with col2:
        weight = st.number_input("몸무게(kg)", min_value=10, max_value=250, value=60)
        blood_pressure = st.selectbox("혈압 상태", ["모름", "정상", "낮음", "높음"])
        blood_sugar = st.selectbox("혈당 상태", ["모름", "정상", "낮음", "높음"])

    medicine = st.text_area(
        "현재 복용 중인 약 또는 질환이 있다면 입력하세요",
        placeholder="예: 고혈압약 복용 중, 빈혈 있음, 특별한 질환 없음"
    )

    # 생활 습관 설문
    st.header("2. 생활 습관 설문")

    sleep = st.selectbox(
        "평소 수면 시간은 어느 정도인가요?",
        ["6시간 미만", "6~8시간", "8시간 이상"]
    )

    coffee = st.selectbox(
        "커피 또는 카페인은 하루에 얼마나 섭취하나요?",
        ["거의 안 마심", "하루 1잔", "하루 2잔 이상"]
    )

    sunlight = st.selectbox(
        "평소 외출 또는 햇빛 노출이 많은 편인가요?",
        ["적음", "보통", "많음"]
    )

    meal = st.selectbox(
        "식사는 규칙적으로 하는 편인가요?",
        ["불규칙", "보통", "규칙적"]
    )

    fatigue = st.selectbox(
        "평소 피로감을 자주 느끼나요?",
        ["낮음", "보통", "높음"]
    )

    supplement_count = st.selectbox(
        "현재 복용 중인 영양제는 몇 개인가요?",
        ["없음", "1개", "2~3개", "4개 이상"]
    )

    purpose = st.selectbox(
        "영양제를 복용하려는 주된 목적은 무엇인가요?",
        ["피로 개선", "면역 관리", "뼈 건강", "피부 건강", "식사 보충", "기타"]
    )

    # 영양제 입력
    st.header("3. 영양제 정보 입력")

    input_method = st.radio(
        "입력 방식을 선택하세요",
        ["이미지 업로드", "카메라 촬영", "직접 텍스트 입력"]
    )

    uploaded_images = []
    direct_text = ""

    if input_method == "이미지 업로드":
        uploaded_images = st.file_uploader(
            "영양제 성분표 사진을 여러 장 업로드할 수 있습니다",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=True
        )

    elif input_method == "카메라 촬영":
        camera_image = st.camera_input("영양제 라벨 또는 성분표를 촬영하세요")
        if camera_image is not None:
            uploaded_images = [camera_image]

    else:
        direct_text = st.text_area(
            "영양제 이름 또는 성분표를 직접 입력하세요",
            placeholder=(
                "예시 1: 비타민 D 1000IU\n"
                "예시 2: 센트룸 멀티비타민 - 비타민 C 180mg, 아연 11mg, 철분 6mg, 칼슘 300mg"
            )
        )

    if uploaded_images:
        st.write(f"업로드된 이미지 수: {len(uploaded_images)}장")

        preview_cols = st.columns(min(len(uploaded_images), 3))

        for idx, img_file in enumerate(uploaded_images):
            with preview_cols[idx % len(preview_cols)]:
                img_file.seek(0)
                st.image(
                    img_file,
                    caption=f"성분표 이미지 {idx + 1}",
                    use_container_width=True
                )

    # 분석 실행
    st.header("4. AI 분석 결과")

    if st.button("AI로 영양제 분석하기", type="primary"):
        if not api_key:
            st.error("Gemini API Key를 먼저 입력하세요.")

        elif input_method in ["이미지 업로드", "카메라 촬영"] and not uploaded_images:
            st.error("분석할 이미지를 업로드하거나 촬영하세요.")

        elif input_method == "직접 텍스트 입력" and not direct_text.strip():
            st.error("영양제 정보를 직접 입력하세요.")

        else:
            with st.spinner("AI가 영양제 성분을 분석하는 중입니다..."):
                try:
                    lifestyle_scores = get_lifestyle_scores(
                        sleep, coffee, sunlight, meal, fatigue, supplement_count
                    )

                    average_score = sum(lifestyle_scores.values()) / len(lifestyle_scores)
                    max_factor = max(lifestyle_scores, key=lifestyle_scores.get)
                    max_score = lifestyle_scores[max_factor]

                    prompt = make_prompt(
                        gender, age, height, weight, blood_pressure, blood_sugar, medicine,
                        sleep, coffee, sunlight, meal, fatigue, supplement_count, purpose,
                        lifestyle_scores, average_score, max_factor
                    )

                    if input_method in ["이미지 업로드", "카메라 촬영"]:
                        result = analyze_with_gemini(
                            api_key=api_key,
                            prompt=prompt,
                            image_files=uploaded_images
                        )
                    else:
                        result = analyze_with_gemini(
                            api_key=api_key,
                            prompt=prompt,
                            text_input=direct_text
                        )

                    st.success("분석이 완료되었습니다.")

                    # 그래프 1: 생활 습관 데이터 시각화
                    st.subheader("📊 데이터 특성 및 통계량 분석 1: 생활 습관 주의 점수")

                    lifestyle_df = pd.DataFrame({
                        "항목": list(lifestyle_scores.keys()),
                        "주의 점수": list(lifestyle_scores.values())
                    })

                    st.caption("점수 기준: 1점 = 낮은 주의, 2점 = 보통, 3점 = 높은 주의")
                    st.bar_chart(lifestyle_df.set_index("항목"))

                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("평균 주의 점수", f"{average_score:.1f} / 3")
                    col_b.metric("가장 주의할 항목", max_factor)
                    col_c.metric("해당 항목 점수", f"{max_score}점")

                    if average_score >= 2.5:
                        st.info("생활 습관 주의 점수가 높은 편입니다. AI 분석에서는 생활 습관 개선 필요성을 함께 반영합니다.")
                    elif average_score >= 1.7:
                        st.info("생활 습관 주의 점수가 보통 수준입니다. 일부 항목에 대한 주의사항을 함께 확인할 수 있습니다.")
                    else:
                        st.info("생활 습관 주의 점수가 낮은 편입니다. 영양제 성분 자체의 구성과 함량을 중심으로 분석합니다.")

                    # 그래프 2: 핵심 성분 + 기타 함량 구성 비율
                    st.subheader("📊 데이터 특성 및 통계량 분석 2: 핵심 성분 함량 구성 비율")

                    nutrient_df = extract_nutrient_status(result)
                    composition_df = extract_composition_data(result)

                    detected_count = len(nutrient_df[nutrient_df["상태"] == "검출"])
                    missing_count = len(nutrient_df[nutrient_df["상태"] == "미검출"])
                    unclear_count = len(nutrient_df[nutrient_df["상태"].isin(["함량 정보 부족", "확인 필요"])])

                    col1, col2, col3 = st.columns(3)
                    col1.metric("검출 성분 수", f"{detected_count}개")
                    col2.metric("미검출 성분 수", f"{missing_count}개")
                    col3.metric("확인 필요", f"{unclear_count}개")

                    if composition_df.empty:
                        st.warning("시각화용 함량 데이터를 읽지 못했습니다. Gemini 상세 분석 결과를 확인해 주세요.")
                    else:
                        fig = px.pie(
                            composition_df,
                            names="성분",
                            values="함량(mg)",
                            hole=0.45
                        )

                        fig.update_traces(
                            textposition="inside",
                            textinfo="percent+label"
                        )

                        fig.update_layout(
                            showlegend=True,
                            margin=dict(t=20, b=20, l=20, r=20)
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        total_amount = composition_df["함량(mg)"].sum()
                        top_component = composition_df.sort_values("함량(mg)", ascending=False).iloc[0]

                        col4, col5, col6 = st.columns(3)
                        col4.metric("시각화 성분 수", f"{len(composition_df)}개")
                        col5.metric("총 함량", f"{total_amount:.2f} mg")
                        col6.metric("가장 큰 비중", f"{top_component['성분']} {top_component['비율(%)']}%")

                        st.info(
                            "이 도넛 차트는 6대 핵심 성분과 기타 성분이 전체 함량에서 차지하는 비율을 시각화한 것입니다. "
                            "단위 환산이 어려운 성분은 AI가 성분표를 바탕으로 대략적인 mg 기준 수치로 정리합니다."
                        )

                        st.dataframe(
                            composition_df,
                            use_container_width=True
                        )

                    with st.expander("🔎 6대 핵심 성분 탐지 상세표 보기"):
                        st.dataframe(
                            nutrient_df[["성분", "상태", "내용"]],
                            use_container_width=True
                        )

                    st.markdown("---")

                    clean_result = remove_visualization_section(result)

                    with st.expander("📝 Gemini 상세 분석 결과 보기", expanded=True):
                        st.markdown(clean_result)

                except Exception as e:
                    st.error("오류가 발생했습니다.")
                    st.write(e)


# -----------------------------
# 페이지 라우팅
# -----------------------------
if st.session_state.page == "home":
    show_home_page()
else:
    show_analyzer_page()
