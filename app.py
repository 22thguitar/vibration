import streamlit as st
import math

# 페이지 설정
st.set_page_config(
    page_title="진동 격리기 선정 계산기",
    page_icon="🔧",
    layout="wide"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .formula-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        margin: 15px 0;
        border-radius: 5px;
        font-family: monospace;
        font-size: 13px;
    }
    .calculation-box {
        background: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        font-family: monospace;
        font-size: 13px;
    }
    .status-good {
        background: #d4edda;
        color: #155724;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .status-warning {
        background: #fff3cd;
        color: #856404;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .status-bad {
        background: #f8d7da;
        color: #721c24;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .recommendation-box {
        background: #e7f3ff;
        border-left: 4px solid #2196F3;
        padding: 15px;
        margin-top: 20px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown("""
<div class="main-header">
    <h1>🔧 진동 격리기 선정 계산기</h1>
    <p>Vibration Isolator Selection Calculator</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 - 입력 섹션
st.sidebar.header("📋 입력 파라미터")

# 기본 입력
load = st.sidebar.number_input("진동저감장치 지탱하중 (kg)", min_value=0.0, value=500.0, step=10.0)
num_isolators = st.sidebar.number_input("아이솔레이터 개수", min_value=1, value=4, step=1)

# 주파수 계산 도우미
with st.sidebar.expander("⚡ 주파수 계산 도우미"):
    helper_speed = st.number_input("주행 속도 (m/s)", min_value=0.0, value=340.0, step=10.0)
    helper_pitch = st.number_input("주기/간격 (m)", min_value=0.1, value=10.0, step=0.1)
    
    if st.button("계산 및 적용"):
        calculated_freq = helper_speed / helper_pitch
        st.session_state['calculated_freq'] = calculated_freq
        st.success(f"계산된 주파수: {calculated_freq:.2f} Hz")
    
    st.info("예시: 340m/s ÷ 10m = 34Hz\n\n간격 예시: 레일 이음매(10~25m), 체결구(0.6m)")

# 주파수 입력 (계산된 값이 있으면 사용)
if 'calculated_freq' in st.session_state:
    default_freq = st.session_state['calculated_freq']
else:
    default_freq = 34.0

excite_freq = st.sidebar.number_input("주 가진 주파수 (Hz)", min_value=0.1, value=default_freq, step=0.1)

target_efficiency = st.sidebar.number_input("목표 격리 효율 (%)", min_value=0.0, max_value=99.9, value=90.0, step=0.1)

target_natural_freq = st.sidebar.number_input(
    "목표 고유 진동수 (Hz)", 
    min_value=0.0, 
    value=0.0, 
    step=0.1,
    help="0으로 두면 자동 계산 (0.35 × 가진 주파수)"
)

# 계산 버튼
calculate_button = st.sidebar.button("🔍 계산하기", type="primary", use_container_width=True)

# 메인 영역 - 결과 표시
if calculate_button:
    # 입력 검증
    if load <= 0 or num_isolators <= 0 or excite_freq <= 0:
        st.error("⚠️ 모든 입력값은 0보다 커야 합니다.")
    else:
        # 계산 시작
        st.success("✅ 계산 완료!")
        
        # 탭으로 구성
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🎯 1단계: 가진주파수", 
            "📊 2단계: 고유진동수", 
            "⚙️ 3단계: 스프링강성",
            "📏 4단계: 처짐량",
            "✅ 5단계: 격리성능",
            "💡 제품선정"
        ])
        
        # 1단계: 가진 주파수
        with tab1:
            st.subheader("🎯 가진 주파수 분석")
            
            st.markdown(f"""
            <div class="formula-box">
            f<sub>excite</sub> = 입력값 (Hz)
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="calculation-box">
            입력값: f<sub>excite</sub> = {excite_freq:.2f} Hz
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("가진 주파수", f"{excite_freq:.2f} Hz")
        
        # 2단계: 목표 고유진동수
        with tab2:
            st.subheader("📊 목표 고유진동수 계산")
            
            max_natural_freq = excite_freq / math.sqrt(2)
            min_recommended_freq = 0.3 * excite_freq
            max_recommended_freq = 0.4 * excite_freq
            
            if target_natural_freq > 0:
                selected_natural_freq = target_natural_freq
                is_manual = True
            else:
                selected_natural_freq = 0.35 * excite_freq
                is_manual = False
            
            st.markdown(f"""
            <div class="formula-box">
            f<sub>n</sub> = 사용자 입력값 또는 자동 계산 (0.35 × f<sub>excite</sub>)<br>
            최대 허용: f<sub>n,max</sub> = f<sub>excite</sub> / √2<br>
            권장 범위: 0.3 × f<sub>excite</sub> ~ 0.4 × f<sub>excite</sub>
            </div>
            """, unsafe_allow_html=True)
            
            calc_text = f"""
            <div class="calculation-box">
            최대 허용: f<sub>n,max</sub> = {excite_freq:.2f} / √2 = {excite_freq:.2f} / 1.414 = {max_natural_freq:.2f} Hz<br>
            권장 최소: 0.3 × {excite_freq:.2f} = {min_recommended_freq:.2f} Hz<br>
            권장 최대: 0.4 × {excite_freq:.2f} = {max_recommended_freq:.2f} Hz<br>
            선정값: f<sub>n</sub> = {selected_natural_freq:.2f} Hz {'(사용자 지정)' if is_manual else f'(0.35 × {excite_freq:.2f})'}
            </div>
            """
            st.markdown(calc_text, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("최대 허용 고유진동수", f"{max_natural_freq:.2f} Hz")
            with col2:
                st.metric("권장 범위", f"{min_recommended_freq:.2f} ~ {max_recommended_freq:.2f} Hz")
            with col3:
                selection_text = "사용자 지정" if is_manual else "자동 계산"
                st.metric("선정 고유진동수", f"{selected_natural_freq:.2f} Hz", delta=selection_text)
        
        # 3단계: 스프링 강성
        with tab3:
            st.subheader("⚙️ 스프링 강성 계산")
            
            omega = 2 * math.pi * selected_natural_freq
            total_stiffness = omega**2 * load
            each_stiffness = total_stiffness / num_isolators
            each_load = load / num_isolators
            
            st.markdown(f"""
            <div class="formula-box">
            f<sub>n</sub> = (1/2π) × √(k/m)<br>
            k<sub>total</sub> = (2π × f<sub>n</sub>)² × m (N/m)<br>
            k<sub>each</sub> = k<sub>total</sub> / n (개별 강성)
            </div>
            """, unsafe_allow_html=True)
            
            calc_text = f"""
            <div class="calculation-box">
            ω = 2π × f<sub>n</sub> = 2π × {selected_natural_freq:.2f} = {omega:.2f} rad/s<br>
            k<sub>total</sub> = ω² × m = ({omega:.2f})² × {load:.1f} = {total_stiffness:.0f} N/m<br>
            k<sub>each</sub> = k<sub>total</sub> / n = {total_stiffness:.0f} / {num_isolators} = {each_stiffness:.0f} N/m<br>
            개별 하중 = {load:.1f} / {num_isolators} = {each_load:.1f} kg
            </div>
            """
            st.markdown(calc_text, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("전체 시스템 강성", f"{total_stiffness:.0f} N/m")
            with col2:
                st.metric("개별 아이솔레이터 강성", f"{each_stiffness:.0f} N/m")
            with col3:
                st.metric("개별 아이솔레이터 하중", f"{each_load:.1f} kg")
        
        # 4단계: 처짐량
        with tab4:
            st.subheader("📏 처짐량 계산")
            
            deflection = 250 / (selected_natural_freq**2)
            
            st.markdown(f"""
            <div class="formula-box">
            δ = mg / k = g / (2πf<sub>n</sub>)² × 1000 ≈ 250 / f<sub>n</sub>² (mm)
            </div>
            """, unsafe_allow_html=True)
            
            calc_text = f"""
            <div class="calculation-box">
            δ = 250 / f<sub>n</sub>² = 250 / ({selected_natural_freq:.2f})²<br>
            δ = 250 / {selected_natural_freq**2:.2f} = {deflection:.2f} mm
            </div>
            """
            st.markdown(calc_text, unsafe_allow_html=True)
            
            # 처짐 평가
            if deflection < 3:
                deflection_status = "너무 작음 (방진고무 검토)"
                deflection_class = "status-warning"
            elif deflection >= 3 and deflection <= 50:
                deflection_status = "적절함"
                deflection_class = "status-good"
            else:
                deflection_status = "너무 큼 (스프링 상수 조정 필요)"
                deflection_class = "status-warning"
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("정적 처짐", f"{deflection:.2f} mm")
            with col2:
                st.markdown(f'<span class="{deflection_class}">{deflection_status}</span>', unsafe_allow_html=True)
        
        # 5단계: 격리 성능
        with tab5:
            st.subheader("✅ 격리 성능 검증")
            
            freq_ratio = excite_freq / selected_natural_freq
            
            st.markdown(f"""
            <div class="formula-box">
            주파수 비율: r = f<sub>excite</sub> / f<sub>n</sub><br>
            전달률: T = 1 / (r² - 1) (r > √2일 때)<br>
            격리율: η = (1 - T) × 100 (%)
            </div>
            """, unsafe_allow_html=True)
            
            if freq_ratio <= 1.414:
                # 공진 영역
                transmissibility = 1 / abs(1 - freq_ratio**2)
                isolation_efficiency = 0
                
                calc_text = f"""
                <div class="calculation-box" style="border-left-color: #c62828;">
                <b style="color: #c62828;">⚠️ 공진 영역 감지!</b><br>
                r = f<sub>excite</sub> / f<sub>n</sub> = {excite_freq:.2f} / {selected_natural_freq:.2f} = {freq_ratio:.2f}<br>
                r ≤ √2 (1.414) 이므로 공진/증폭 발생<br>
                증폭률 = 1 / |1 - r²| = 1 / |1 - {freq_ratio**2:.2f}| = {transmissibility:.2f}
                </div>
                """
                st.markdown(calc_text, unsafe_allow_html=True)
                
                st.error(f"⚠️ 경고: 주파수 비율 {freq_ratio:.2f}는 공진 영역입니다!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("주파수 비율", f"{freq_ratio:.2f}", delta="공진 영역")
                with col2:
                    st.metric("전달률", f"증폭 ({transmissibility:.2f})")
                with col3:
                    st.markdown('<span class="status-bad">격리 불가 (증폭)</span>', unsafe_allow_html=True)
            else:
                # 격리 영역
                transmissibility = 1 / (freq_ratio**2 - 1)
                isolation_efficiency = (1 - transmissibility) * 100
                
                calc_text = f"""
                <div class="calculation-box">
                r = f<sub>excite</sub> / f<sub>n</sub> = {excite_freq:.2f} / {selected_natural_freq:.2f} = {freq_ratio:.2f}<br>
                r² = ({freq_ratio:.2f})² = {freq_ratio**2:.2f}<br>
                T = 1 / (r² - 1) = 1 / ({freq_ratio**2:.2f} - 1) = {transmissibility:.4f}<br>
                η = (1 - T) × 100 = (1 - {transmissibility:.4f}) × 100 = {isolation_efficiency:.2f}%
                </div>
                """
                st.markdown(calc_text, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("주파수 비율", f"{freq_ratio:.2f}", delta="격리 영역 ✓")
                with col2:
                    st.metric("전달률", f"{transmissibility:.4f}")
                with col3:
                    if isolation_efficiency >= target_efficiency:
                        st.metric("실제 격리 효율", f"{isolation_efficiency:.2f}%", 
                                 delta=f"목표: {target_efficiency}%", delta_color="normal")
                    else:
                        st.metric("실제 격리 효율", f"{isolation_efficiency:.2f}%", 
                                 delta=f"목표: {target_efficiency}% (미달)", delta_color="inverse")
        
        # 6단계: 제품 선정 가이드
        with tab6:
            st.subheader("💡 제품 선정 가이드")
            
            recommendations = []
            
            if freq_ratio <= 1.414:
                recommendations.append(f"⚠️ **경고**: 현재 설정은 공진 영역에 있습니다. 고유 진동수를 {max_natural_freq:.1f} Hz 미만으로 낮추십시오.")
            else:
                if selected_natural_freq < 10:
                    recommendations.append(f"✅ 스프링 마운트/행거 권장 (고유진동수 {selected_natural_freq:.1f} Hz)")
                else:
                    recommendations.append(f"✅ 방진 고무 또는 패드 검토 가능 (고유진동수 {selected_natural_freq:.1f} Hz)")
                
                recommendations.append(f"📦 개당 하중 용량: **{each_load * 1.2:.1f} kg 이상** (안전율 20%)")
                recommendations.append(f"📏 요구 정적 처짐: 약 **{deflection:.1f} mm**")
            
            if is_manual and selected_natural_freq > max_natural_freq:
                recommendations.append(f"⚠️ **주의**: 입력한 목표 고유 진동수가 너무 높습니다. 격리 효율이 떨어질 수 있습니다.")
            
            if excite_freq < 5:
                recommendations.append("🌀 초저주파 가진: 공기 스프링(Air Spring) 등 특수 제진 장치 검토 필요")
            
            st.markdown('<div class="recommendation-box">', unsafe_allow_html=True)
            for rec in recommendations:
                st.markdown(f"- {rec}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 요약 테이블
            st.subheader("📋 설계 요약")
            summary_data = {
                "항목": [
                    "가진 주파수",
                    "선정 고유진동수",
                    "주파수 비율",
                    "전체 시스템 강성",
                    "개별 강성",
                    "개별 하중",
                    "정적 처짐",
                    "격리 효율"
                ],
                "값": [
                    f"{excite_freq:.2f} Hz",
                    f"{selected_natural_freq:.2f} Hz",
                    f"{freq_ratio:.2f}",
                    f"{total_stiffness:.0f} N/m",
                    f"{each_stiffness:.0f} N/m",
                    f"{each_load:.1f} kg",
                    f"{deflection:.2f} mm",
                    f"{isolation_efficiency:.2f}%" if freq_ratio > 1.414 else "격리 불가"
                ]
            }
            st.table(summary_data)

else:
    st.info("👈 좌측 사이드바에서 파라미터를 입력하고 '계산하기' 버튼을 클릭하세요.")
    
    # 사용 안내
    with st.expander("📖 사용 방법"):
        st.markdown("""
        ### 입력 파라미터
        1. **지탱하중**: 진동 격리기가 지탱해야 할 총 하중 (kg)
        2. **아이솔레이터 개수**: 사용할 진동 격리기의 개수
        3. **가진 주파수**: 시스템에 가해지는 진동의 주파수 (Hz)
           - 주파수 계산 도우미를 사용하여 속도와 간격으로 계산 가능
        4. **목표 격리 효율**: 원하는 진동 격리 효율 (%)
        5. **목표 고유 진동수**: 직접 지정하거나 0으로 두면 자동 계산
        
        ### 계산 결과
        - **1단계**: 입력된 가진 주파수 확인
        - **2단계**: 최적 고유 진동수 계산
        - **3단계**: 필요한 스프링 강성 계산
        - **4단계**: 예상 처짐량 계산
        - **5단계**: 격리 성능 검증
        - **6단계**: 제품 선정 가이드 제공
        
        ### 주의사항
        - 주파수 비율이 √2 (1.414) 이하면 공진 발생
        - 처짐량이 3~50mm 범위가 적절
        - 개별 하중에 안전율 20% 이상 적용 권장
        """)
    
    with st.expander("📐 이론 배경"):
        st.markdown("""
        ### 진동 격리 원리
        
        진동 격리기는 **공진 주파수보다 높은 가진 주파수**에서 효과적으로 작동합니다.
        
        **주요 공식:**
        - 고유 진동수: `fn = (1/2π) × √(k/m)`
        - 주파수 비율: `r = f_excite / f_n`
        - 전달률: `T = 1 / (r² - 1)` (r > √2일 때)
        - 격리율: `η = (1 - T) × 100%`
        
        **설계 기준:**
        - r > √2 (1.414): 격리 영역
        - r = 1: 공진 (최대 증폭)
        - r < √2: 증폭 영역
        
        **권장 고유진동수:**
        - 가진 주파수의 30~40% (일반적으로 35%)
        - 최대 허용: 가진 주파수 / √2
        """)
