# analyze_reviews 함수 부분만 수정합니다
def analyze_reviews(api_key, reviews_text, product_name):
    if not api_key:
        st.error("OpenAI API 키가 필요합니다.")
        return None, None, None
   
    try:
        # OpenAI 모듈 가져오기 및 클라이언트 초기화 (새 버전 방식)
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
       
        # 리뷰 텍스트가 너무 긴 경우 줄이기
        max_chars = 15000
        if len(reviews_text) > max_chars:
            st.warning(f"리뷰 텍스트가 너무 깁니다. 처음 {max_chars} 문자만 분석합니다.")
            reviews_text = reviews_text[:max_chars] + "... (이하 생략)"
       
        # 리뷰 분석을 위한 프롬프트 (기존 코드와 동일)
        prompt = f"""
다음은 '{product_name}'에 대한 네이버 블로그 포스트입니다. 해당 콘텐츠를 철저히 분석하여 아래 요청사항에 따라 응답해주세요:

1. 광고성 콘텐츠 식별:
   - 먼저 제공된 글이 광고성 콘텐츠인지 객관적으로 판단해주세요.
   - 판단 기준: 협찬/광고 문구 명시, 지나치게 긍정적인 어조, 구매 링크 다수 포함, 상품 홍보에 치중된 내용 등
   - 광고성 콘텐츠로 판단되면 해당 내용은 의견 분석에서 제외하거나 비중을 낮춰주세요.

2. 긍정적 의견 분석:
   - 실제 사용자가 직접 경험한 구체적인 장점을 중심으로 분석해주세요.
   - 객관적 사실과 주관적 만족도를 구분하여 서술해주세요.
   - 가장 자주 언급되는 긍정적 특징을 우선적으로 포함해주세요.
   - 5-7줄로 간결하게 요약해주세요.

3. 부정적 의견 분석:
   - 실제 사용자의 불만사항과 개선점을 중심으로 분석해주세요.
   - 단순한 불평이 아닌 구체적인 단점과 문제점에 초점을 맞춰주세요.
   - 가장 자주 언급되는 부정적 특징을 우선적으로 포함해주세요.
   - 5-7줄로 간결하게 요약해주세요.
   - 부정적 의견이 거의 없는 경우, 그 이유(광고성 글이 많은지, 제품이 실제로 만족도가 높은지 등)를 분석해주세요.

4. 종합 평가:
   - 긍정/부정 의견의 비율과 신뢰도를 고려한 균형 잡힌 총평을 제공해주세요.
   - 광고성 콘텐츠의 비중을 고려하여 실제 사용자 의견이 얼마나 반영되었는지 언급해주세요.
   - 제품의 주요 특징과 사용자 만족도를 객관적으로 평가해주세요.
   - 5-7줄로 간결하게 요약해주세요.

블로그 내용:
{reviews_text}

응답은 JSON 형식으로 제공하되 Markdown출력은 사용하지 말아주세요:
{{
  "ad_analysis": "광고성 콘텐츠 분석 결과 (광고성 콘텐츠 비율 추정치 포함)",
  "positive": "구체적인 긍정적 의견 요약 (실제 사용자 경험 중심)",
  "negative": "구체적인 부정적 의견 요약 (실제 사용자 경험 중심)",
  "summary": "객관적인 전체 요약 및 종합 평가"
}}
"""

        # API 호출 (새 버전 방식)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 제품 리뷰 분석 전문가입니다. 제공된 콘텐츠를 철저히 분석하여 광고성 글을 식별하고, 실제 사용자 경험에 기반한 정보를 추출하는 능력이 있습니다. 분석 시 객관적 근거를 바탕으로 추론하고, 긍정/부정 의견의 패턴을 파악하여 명확하게 구분합니다. 단순 요약이 아닌 심층적 분석을 제공하며, 신뢰할 수 있는 종합 평가를 제시합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2048
        )
       
        # 결과 파싱 (새 버전 방식)
        content = response.choices[0].message.content.strip()

        if not content:
            st.error("ChatGPT 응답이 비어 있습니다.")
            return None, None, None

        try:
            result = json.loads(content)
            return result["positive"], result["negative"], result["summary"]
        except json.JSONDecodeError as e:
            st.error(f"JSON 파싱 오류 발생: {str(e)}")
            st.text_area("응답 원문 보기", content, height=300)
            return None, None, None
   
    except Exception as e:
        st.error(f"ChatGPT API 호출 중 오류 발생: {str(e)}")
        return None, None, None
