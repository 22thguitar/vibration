import streamlit as st
import math

# --- 페이지 설정 ---
st.set_page_config(
    page_title="슬레드 진동저감장치 선정 계산기",
    page_icon="🔧",
    layout="centered"
)

# --- 스타일 커스텀 (CSS) ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stAppHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
    }
    .result-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 10px;
        color: #856404;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 5px solid #721c24;
        padding: 10px;
        color: #721c24;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 세션 상태 초기화 (도우미 값 연동용) ---
if 'frequency' not in st.session_state:
    st.session_state.frequency = 34.0

# --- 헤더 ---
st.title("🔧 슬레드 진동저감장치 선정")
st.markdown("### Vibration Isolator Selection Calculator")
st.markdown("---")

# --- 입력 섹션 ---
st.header("📋 시스템 제원 입력")

col1, col2 = st.columns(2)

with col1:
    load = st.number_input("진동저감장치 지탱하중 (kg)", value=500.0, step=10.0)
    
with col2:
    num_isolators = st.number_input("아이솔레이터 개수", value=4, step=1)

# --- 주파수 계산 도우미 (Expander) ---
with st.expander("⚡ 주파수 계산 도우미 (속도/간격으로 계산)"):
    h_col1, h_col2, h_col3 = st.columns([1, 1, 1])
    with h_col1:
        speed = st.number_input("주행 속도 (m/s)", value=340.0)
    with h_col2:
        pitch = st.number_input("주기/간격 (m)", value=10.0)
    with h_col3:
        st.write("") # 여백용
        st.write("") 
        if st.button("계산 및 적용"):
            if pitch > 0:
                calc_freq = speed / pitch
                st.session_state.frequency = calc_freq
                st.success(f"적용 완료: {calc_freq:.1f} Hz")
                st.rerun() # 화면 갱신
            else:
                st.error("간격은 0보다 커야 합니다.")

# --- 2열 입력 (주파수 등) ---
col3, col4 = st.columns(2)

with col3:
    # session_state 값을 기본값으로 사용
    excite_freq = st.number_input(
        "주 가진 주파수 (Hz)", 
        value=st.session_state.frequency, 
        step=1.0, 
        key="freq_input" # 키를 지정하여 state와 연동
    )
    # 입력값이 바뀌면 state 업데이트
    st.session_state.frequency = excite_freq

with col4:
    target_efficiency = st.number_input("목표 격리 효율 (%)", value=90.0, step=0.5, max_value=99.9)

# --- 추가 입력 (목표 고유 진동수) ---
target_natural_freq_input = st.number_input(
    "목표 고유 진동수 (Hz) - 비워두면 자동 계산 (0: 자동)", 
    value=0.0, 
    step=0.1,
    help="0으로 설정하면 주 가진 주파수의 35%로 자동 설정됩니다."
)

st.markdown("---")

# --- 계산 로직 ---
if st.button("결과 계산하기", type="primary", use_container_width=True):
    
    # 2단계: 목표 고유진동수 선정
    max_natural_freq = excite_freq / math.sqrt(2)
    min_rec_freq = 0.3 * excite_freq
    max_rec_freq = 0.4 * excite_freq

    is_manual = False
    if target_natural_freq_input > 0:
        selected_natural_freq = target_natural_freq_input
        is_manual = True
    else:
        selected_natural_freq = 0.35 * excite_freq

    # 3단계: 강성(k) 계산
    # k = (2 * pi * fn)^2 * m
    total_stiffness = math.pow(2 * math.pi * selected_natural_freq, 2) * load
    each_stiffness = total_stiffness / num_isolators
    each_load = load / num_isolators

    # 4단계: 처짐량(Deflection)
    # d approx 250 / fn^2
    deflection = 250 / math.pow(selected_natural_freq, 2)

    # 5단계: 격리 효율(Efficiency)
    freq_ratio = excite_freq / selected_natural_freq
    
    in_resonance = False
    transmissibility = 0.0
    isolation_eff = 0.0

    if freq_ratio <= 1.414:
        in_resonance = True
        transmissibility = 1 / abs(1 - math.pow(freq_ratio, 2))
        isolation_eff = 0 # 증폭됨
    else:
        transmissibility = 1 / (math.pow(freq_ratio, 2) - 1)
        isolation_eff = (1 - transmissibility) * 100

    # --- 결과 출력 화면 ---
    
    st.header("📊 분석 결과")

    # 1. 주파수 분석 결과
    st.subheader("1. 주파수 및 선정 제원")
    r_col1, r_col2, r_col3 = st.columns(3)
    r_col1.metric("가진 주파수", f"{excite_freq:.2f} Hz")
    r_col2.metric("최대 허용 고유진동수", f"{max_natural_freq:.2f} Hz", delta="이하 유지 필요", delta_color="inverse")
    
    selection_desc = " (사용자 지정)" if is_manual else " (자동: 35%)"
    r_col3.metric("선정 고유진동수", f"{selected_natural_freq:.2f} Hz", selection_desc)

    # 2. 물리적 제원
    st.divider()
    st.subheader("2. 필요 스프링/방진재 제원")
    
    k_col1, k_col2, k_col3 = st.columns(3)
    k_col1.metric("개별 지지 하중", f"{each_load:.1f} kg")
    k_col2.metric("개별 필요 강성", f"{each_stiffness:.0f} N/m")
    
    # 처짐량 평가
    defl_status = ""
    if deflection < 3:
        defl_status = "⚠️ 너무 작음 (방진고무)"
    elif 3 <= deflection <= 50:
        defl_status = "✅ 적절함"
    else:
        defl_status = "⚠️ 너무 큼 (조정 필요)"
        
    k_col3.metric("요구 정적 처짐", f"{deflection:.2f} mm", defl_status)

    # 3. 효율 검증
    st.divider()
    st.subheader("3. 격리 성능 검증")
    
    if in_resonance:
        st.error(f"### ⚠️ 공진 위험 (증폭 영역)")
        st.write(f"주파수 비: **{freq_ratio:.2f}** (√2 = 1.414 이하)")
        st.write(f"전달률: **{transmissibility:.2f}** (진동이 증폭되어 전달됨)")
    else:
        # 효율 달성 여부
        if isolation_eff >= target_efficiency:
            st.success(f"### 🎯 목표 달성: {isolation_eff:.2f}%")
        elif isolation_eff >= target_efficiency - 5:
            st.warning(f"### ⚠️ 보통: {isolation_eff:.2f}% (목표: {target_efficiency}%)")
        else:
            st.error(f"### ❌ 미달: {isolation_eff:.2f}% (목표: {target_efficiency}%)")
            
        st.write(f"주파수 비: **{freq_ratio:.2f}** (> 1.414 안전)")
        st.write(f"전달률: **{transmissibility:.4f}**")

    # 4. 추천 가이드
    st.divider()
    with st.expander("💡 제품 선정 가이드 및 조치 사항", expanded=True):
        if in_resonance:
            st.markdown(f"- 🔴 **[위험]** 현재 설정은 공진 영역입니다. 고유 진동수를 **{max_natural_freq:.1f} Hz 미만**으로 낮추십시오.")
        else:
            if selected_natural_freq < 10:
                st.markdown("- **[제품]** 낮은 고유진동수가 필요하므로 **스프링 마운트/행거**를 권장합니다.")
            else:
                st.markdown("- **[제품]** **방진 고무** 또는 **방진 패드** 사용이 가능할 수 있습니다.")
            
            st.markdown(f"- **[스펙]** 개당 하중 **{(each_load * 1.2):.1f} kg 이상** (안전율 20% 적용) 제품을 선정하세요.")
            st.markdown(f"- **[스펙]** 하중 작용 시 **약 {deflection:.1f} mm**가 눌리는(처지는) 제품이어야 합니다.")

        if is_manual and selected_natural_freq > max_natural_freq:
            st.markdown("- ⚠️ **[주의]** 입력한 목표 고유 진동수가 너무 높습니다. 격리 효율이 떨어질 수 있습니다.")
        
        if excite_freq < 5:
            st.markdown("- ⚠️ **[초저주파]** 매우 낮은 주파수 가진입니다. **공기 스프링(Air Spring)** 등 특수 장치를 검토하세요.")