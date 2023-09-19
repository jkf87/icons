import openai
import streamlit as st
import time
import os
import platform
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from prompt import *
import pandas as pd
import plotly.express as px
import json

os.environ["OPENAI_API_KEY"] = os.environ['my_secret']
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        /* 애플 스타일 버튼 */
        .stButton > button {
            background-color: #ffffff;
            border: 1px solid #a9a9a9;
            color: black;
            padding: 12px 24px;
            text-align: center;
            font-size: 18px;
            border-radius: 8px;
            transition: background-color 0.3s, color 0.3s;
        }
        /* 호버 상태 */
        .stButton > button:hover {
            background-color: #007bff;
            color: white;
            border: 1px solid #007bff;
        }
        /* 클릭 시 */
        .stButton:active > button {
            background-color: #0056b3;
            border: 1px solid #0056b3;
        }
        .chat-row {
            display: flex;
        }
        .chat-icon {
            margin-right: 8px;
        }
        .chat-bubble {
            padding: 10px;
            border-radius: 10px;
        }
        .row-reverse {
            flex-direction: row-reverse;
        }
                
    </style>
    """, unsafe_allow_html=True)

#감정 분석을 위한 코드, 최근 대화
def analyze_emotion(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"이 상담사의 대화는 다음과 같습니다 : {text} 이 대화를 보고 [긍정, 공감, 정리] 중 하나로 분류하여 답하시오.",
        }],
        stream=False
    )
    
    return response['choices'][0]['message']['content'].strip()



# 감정에 따른 이미지 선택 함수
def select_icon_based_on_response(emotion):
    if emotion == "긍정":
        return "https://raw.githubusercontent.com/jkf87/icons/main/cheerup.png"
    elif emotion == "공감":
        return "https://raw.githubusercontent.com/jkf87/icons/main/listen.png"
    elif emotion == "정리":
        return "https://raw.githubusercontent.com/jkf87/icons/main/wrapup.png"
    else:
        return "https://raw.githubusercontent.com/jkf87/icons/main/idle.png"
    


# CSS 로딩
def load_css():
    css = """
    .chat-row {
        display: flex;
        margin-bottom: 8px;
    }p
    .chat-icon {
        margin-right: 8px;
    }
    .chat-bubble {
        padding: 10px;
        border-radius: 10px;
    }
    .row-reverse {
        flex-direction: row-reverse;
    }
    .ai-bubble {
        background-color: #f0f0f0;
        color: black;
    }
    .human-bubble {
        background-color: #4f8bf9;
        color: white;
    }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# finetune gpt를 사용하여 챗봇 응답 생성
def get_bot_response(user_input):
    # 대화 주제와 챗봇 역할을 설명하는 시스템 메시지
    system_message = """
You are a counselor who helps adolescents and adults with psychological counseling. Restate the problem and ask for more details. Empathize with your client and talk about your feelings. Speak warmly to help them feel like you are on the same page, rather than solving their problem. use only korean
"""

    messages = [{"role": "system", "content": system_message}]
    # 이전 대화 내용을 메시지로 추가
    
    for chat in st.session_state.chat_history[-30:]:  # 최근 30개의 대화만 고려
        origin = chat["origin"]
        message = chat["message"]
        role = "user" if origin == "human" else "assistant"
        messages.append({"role": role, "content": message})
    messages.append({"role": "user", "content": user_input}) # 사용자의 현재 입력 추가

    response = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0613:personal::7qyPLZzo",
        messages=messages,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    
    return response.choices[0].message['content']


#버튼들 모음을 함수로 만들기
#자주 사용하는 상담 주제를 선정하여 초기 입력으로 넣기

def button():

    col1, col2= st.columns(2)
    with col1:
        #우울증 사례 - 채팅입력에는 '요즘 우울해요'라고 입력
        
        if st.button('우울증'): 
            st.session_state.chat_history.append({
                "origin": "human",
                "message": "요즘 우울해요",
                "icon_url": "https://raw.githubusercontent.com/jkf87/icons/main/basic.png"  
            })
            response = get_bot_response("요즘 우울해요")
            emotion = analyze_emotion("요즘 우울해요")
            ai_icon_url = select_icon_based_on_response(emotion)
            st.session_state.chat_history.append({
                "origin": "ai",
                "message": response,
                "icon_url": ai_icon_url
            })
            st.experimental_rerun()

            
        #불안 장애 사례 - 채팅입력에는 '마음이 불안해요'라고 입력
        if st.button('불안 장애'):
            st.session_state.chat_history.append({
                "origin": "human",
                "message": "마음이 불안해요",
                "icon_url": "https://raw.githubusercontent.com/jkf87/icons/main/basic.png"  
            })
            response = get_bot_response("마음이 불안해요")
            emotion = analyze_emotion("마음이 불안해요")
            ai_icon_url = select_icon_based_on_response(emotion)
            st.session_state.chat_history.append({
                "origin": "ai",
                "message": response,
                "icon_url": ai_icon_url
            })
            st.experimental_rerun()
    with col2:
        #교권 침해 사례- 채팅입력에는 '교권 침해를 당했어요'라고 입력
        if st.button('교권 침해'):
            st.session_state.chat_history.append({
                "origin": "human",
                "message": "교권 침해를 당했어요",
                "icon_url": "https://raw.githubusercontent.com/jkf87/icons/main/basic.png"  
            })
            response = get_bot_response("교권 침해를 당했어요")
            emotion = analyze_emotion("교권 침해를 당했어요")
            ai_icon_url = select_icon_based_on_response(emotion)
            st.session_state.chat_history.append({
                "origin": "ai",
                "message": response,
                "icon_url": ai_icon_url
            })
            st.experimental_rerun()
        #학교 폭력 사례 - 채팅입력에는 '학교 폭력을 당했어요'라고 입력
        if st.button('학교 폭력'):
            st.session_state.chat_history.append({
                "origin": "human",
                "message": "학교 폭력을 당했어요",
                "icon_url": "https://raw.githubusercontent.com/jkf87/icons/main/basic.png"  
            })
            response = get_bot_response("학교 폭력을 당했어요")
            emotion = analyze_emotion("학교 폭력을 당했어요")
            ai_icon_url = select_icon_based_on_response(emotion)
            st.session_state.chat_history.append({
                "origin": "ai",
                "message": response,
                "icon_url": ai_icon_url
            })
            st.experimental_rerun()

        



#한글 폰트 등록
pdfmetrics.registerFont(TTFont('NanumGothic', 'NanumGothic.ttf'))


#챗봇 대화내용 pdf로 저장하는 함수 만들기
def save_pdf():
    pdf = SimpleDocTemplate("chatbot.pdf", pagesize=letter)
    
    # PDF 스타일 설정
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.fontName = 'NanumGothic'  # 폰트를 NanumGothic 설정
    styleH = styles["Heading1"]
    
    # 대화 내용을 담을 리스트 생성
    data = [["AI", "USER"]]
    
    for origin, message in st.session_state.chat_history[-30:]:
        if origin == 'human':
            data.append(["", Paragraph(message, styleN)])
        else:
            data.append([Paragraph(message, styleN), ""])
    
    # 테이블 생성
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # PDF에 테이블 추가
    global elements
    elements = []
    elements.append(table)
    pdf.build(elements)

#감정 분석을 위한 코드, 최근 대화
def analyze_emotion(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"이 상담사의 대화는 다음과 같습니다 : {text} 이 대화를 보고 [긍정, 공감, 정리] 중 하나로 분류하여 답하시오.",
        }],
        stream=False
    )
    
    return response['choices'][0]['message']['content'].strip()



# 감정에 따른 이미지 선택 함수
def select_icon_based_on_response(emotion):
    if emotion == "긍정":
        return "https://raw.githubusercontent.com/jkf87/icons/main/cheerup.png"
    elif emotion == "공감":
        return "https://raw.githubusercontent.com/jkf87/icons/main/listen.png"
    elif emotion == "정리":
        return "https://raw.githubusercontent.com/jkf87/icons/main/wrapup.png"
    else:
        return "https://raw.githubusercontent.com/jkf87/icons/main/idle.png"
    



###########################################main###########################################

#화면을 컬럼 두개로 나누기
col1, col2 = st.columns(2)

#컬럼에 컨텐츠 추가
with col1:
        # 챗봇 대화 히스토리 초기화
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 대화 기록 초기화 버튼
    if st.button('대화 기록 초기화'):
        st.session_state.chat_history = []
        st.experimental_rerun()

    # 초기 session_state 설정
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ''


    # 제목
    st.title('심리 상담 챗봇')

    # 사용자 입력
    user_input = st.text_input('AI상담사 파인힐러에게 속마음을 이야기해보세요.', '', key=st.session_state.user_input)
    #버튼을 추가하면 엔터 효과  한번만 입력하도록 버그 수정
    
    #입력이라는 버튼 추가
    if st.button('Enter'):
        st.session_state.chat_history.append({
            "origin": "human",
            "message": user_input,
            "icon_url": "https://raw.githubusercontent.com/jkf87/icons/main/basic.png"  
        })
        response = get_bot_response(user_input)
        emotion = analyze_emotion(user_input)
        ai_icon_url = select_icon_based_on_response(emotion)
        st.session_state.chat_history.append({
            "origin": "ai",
            "message": response,
            "icon_url": ai_icon_url
        })

       # 입력 상자 초기화
        st.session_state.user_input = ""
        st.experimental_rerun()


    # 사용자가 입력한 경우
    if user_input:
        # 챗봇 응답 및 감정 분석
        response = get_bot_response(user_input)
        emotion = analyze_emotion(user_input)
        ai_icon_url = select_icon_based_on_response(emotion)

        # 대화 히스토리에 추가
        st.session_state.chat_history.append({
            "origin": "human",
            "message": user_input,
            "icon_url": "https://raw.githubusercontent.com/jkf87/icons/main/basic.png"  
        })
        st.session_state.chat_history.append({
            "origin": "ai",
            "message": response,
            "icon_url": ai_icon_url
        })

    # 챗봇 대화 히스토리 표시
    for chat in st.session_state.chat_history[-30:]:  # 최근 30개의 대화만 표시
        origin = chat["origin"]
        message = chat["message"]
        icon_url = chat["icon_url"]

        bubble_class = "ai-bubble" if origin == "ai" else "human-bubble"
        row_reverse_class = "" if origin == "ai" else "row-reverse"

        st.markdown(f'<div class="chat-row {row_reverse_class}"><img class="chat-icon" src="{icon_url}" width=128 height=128><div class="chat-bubble {bubble_class}">&#8203;{message}</div></div>', unsafe_allow_html=True)
        
    

with col2:
    #버튼모음 넣기
    response = button()
    #pdf저장 버튼 넣기
    if st.button('대화내용 pdf로 저장'):
        save_pdf()  # PDF 저장 함수 (이미 정의되어 있다고 가정)
        st.success('저장되었습니다.')
        time.sleep(1)
        if platform.system() == 'Windows':
            os.startfile('chatbot.pdf')
        elif platform.system() == 'Darwin':  # macOS
            os.system(f'open chatbot.pdf')
        elif platform.system() == 'Linux':
            os.system(f'xdg-open chatbot.pdf')
            


    if st.button('대화 내용 분석'):
        with st.spinner("대화 내용을 분석하고 있습니다..."):
            chat_history_json_str = json.dumps(st.session_state.chat_history, ensure_ascii=False, indent=4)
            user_history_prompt= """상담사(AI)와 내담자(USER)간의 대화 내용은 다음과 같다: \n{chat_history_json_str}\n 이 대화 내용을 보고 다음에 대해 점수를 매길 것이다.  
0~100점 사이로 제공해라. 정확하지 않을 수 있지만 가능성을 기반으로 객관적으로 점수를 매기면 된다. 기준은 사회활동을 하는 일반적인 성인을 기준으로 둔다. 아래 순서대로 점수를 제공하고 그에 대한 설명을 사용자에게 제공해라.
- 정서적 안정성
- 대인관계 능력
- 자기 인식도
- 스트레스 관리 능력
- 적응력
- 의사소통 능력
출력 포맷은 코드에서 활용할 수 있도록 json 형식으로 출력해라. 아래의 형식을 따라라. 출력은 Python json.loads() 사용해서 파싱할 수 있어야 한다.
```{score : [- 정서적 안정성 점수, 대인관계 능력, 자기 인식도점수, 스트레스 관리 능력 점수, 적응력 점수, 의사소통 능력 점수], 
description: 각각에 대한 설명을 하나의 string으로 unordered list with dash 형태로
}```
따라야할 결과물 예시는 다음과 같다.
```{
  "score": [70, 60, 75, 40, 85, 50],
  "description": "- 정서적 안정성: 70점으로, 내담자가 일상생활에서 상당한 정서적 불안을 겪고 있을 수 있습니다.\\n- 대인관계 능력: 60점으로, 사회적 상황에서 불편함을 느끼고 대인관계에 어려움을 겪을 가능성이 있습니다.\\n- 자기 인식도: 75점으로, 내담자가 자신의 감정과 생각을 어느 정도 잘 알고 있으나, 아직 개선의 여지가 있습니다.\\n- 스트레스 관리 능력: 40점으로, 스트레스 상황에서 적절히 대처하기 어렵다고 판단됩니다.\\n- 적응력: 85점으로, 일반적인 생활 변화나 어려움에는 잘 적응하는 편입니다.\\n- 의사소통 능력: 50점으로, 내담자가 자신의 생각과 감정을 표현하는 능력이 일부 제한적일 수 있습니다."
}
```
"""
            # st.write(type(user_history_prompt))
            gpt_response2 = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": user_history_prompt}],
                stream=False)
            
            gpt_response2 = gpt_response2["choices"][0]["message"]["content"]
        
            start_keyword = "{"
            end_keyword = "}"

            if start_keyword in gpt_response2 and end_keyword in gpt_response2:
                list_start = gpt_response2.find(start_keyword) + len(start_keyword)
                list_end = gpt_response2.find(end_keyword, list_start)
                list_content = gpt_response2[list_start-1:list_end+1].strip()
            else:
                st.markdown(f"No python list found in the response: \n\n ```{gpt_response2}```")

            print(list_content)

            list_content = json.loads(list_content)

            df = pd.DataFrame(dict(
                r=list_content["score"],
                theta=["정서적 안정성","대인관계 능력","자기 인식도","스트레스 관리 능력","적응력","의사소통 능력"]))
            fig = px.line_polar(df, r="r", theta="theta", line_close=True)
            fig.update_traces(fill='toself')
            st.write(fig)
            st.markdown(list_content["description"])
            