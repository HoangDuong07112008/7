import streamlit as st
import pandas as pd
import numpy as np

# Cấu hình trang
st.set_page_config(
    page_title="App Tính Lãi Suất & Tài Chính Toàn Diện",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Ứng Dụng Tính Toán Lãi Suất & Hoạch Định Tài Chính")
st.markdown("---")

# Thanh điều hướng sidebar
tab = st.sidebar.radio(
    "🧭 Chọn tính năng:",
    [
        "📈 Lãi kép, Lạm phát & Thuế đầu tư",
        "🧮 Lãi đơn truyền thống",
        "⚖️ So sánh Lãi đơn vs Lãi kép",
        "🏠 Tính khoản vay trả góp (EMI)",
        "🎯 Mục tiêu tài chính (Goal Seek)",
        "📉 Phân tích Lạm phát độc lập"
    ]
)

# ==========================================
# TAB 1: LÃI KÉP, LẠM PHÁT & THUẾ ĐẦU TƯ
# ==========================================
if tab == "📈 Lãi kép, Lạm phát & Thuế đầu tư":
    st.header("📈 Máy tính Lãi kép Tích hợp Lạm phát & Thuế")
    st.markdown("Tính toán tăng trưởng tài sản dài hạn có xét đến đóng góp định kỳ, khấu trừ lạm phát và thuế thu nhập từ đầu tư.")
    
    with st.form("compound_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            principal = st.number_input("Vốn ban đầu (VNĐ)", min_value=0.0, value=50000000.0, step=1000000.0, format="%f")
            rate = st.number_input("Lãi suất hằng năm (%/năm)", min_value=0.0, max_value=100.0, value=9.0, step=0.1)
        with c2:
            monthly_contrib = st.number_input("Đóng góp định kỳ hằng tháng (VNĐ)", min_value=0.0, value=3000000.0, step=500000.0, format="%f")
            years = st.slider("Thời gian đầu tư (Năm)", min_value=1, max_value=40, value=15)
        with c3:
            frequency = st.selectbox("Tần suất ghép lãi", ["Hằng tháng", "Hằng năm", "Hằng ngày"])
            inflation_rate = st.number_input("Tỷ lệ lạm phát kỳ vọng (%/năm)", min_value=0.0, max_value=20.0, value=4.0, step=0.1)
            tax_rate = st.number_input("Thuế thu nhập đầu tư / Lợi nhuận (%)", min_value=0.0, max_value=50.0, value=5.0, step=0.5)
            
        submitted = st.form_submit_button("🚀 Tính toán ngay")

    # Xử lý tính toán
    r = rate / 100.0
    inf = inflation_rate / 100.0
    tax = tax_rate / 100.0
    t = years
    
    schedule = []
    current_balance = principal
    total_contrib = principal
    
    months = t * 12
    monthly_rate = r / 12.0
    
    data_points = []
    for m in range(1, months + 1):
        interest_earned = current_balance * monthly_rate
        current_balance += interest_earned + monthly_contrib
        total_contrib += monthly_contrib
        
        if m % 12 == 0:
            yr = m // 12
            gross_interest = current_balance - total_contrib
            # Tính thuế trên tổng tiền lãi tích lũy đến năm thứ yr
            tax_amount = max(0, gross_interest * tax)
            net_balance = current_balance - tax_amount
            
            # Quy đổi sức mua thực tế sau lạm phát (tính trên số dư ròng sau thuế)
            real_value = net_balance / ((1 + inf) ** yr)
            
            schedule.append({
                "Năm": yr,
                "Vốn gốc tích lũy": total_contrib,
                "Lợi nhuận gộp": gross_interest,
                "Thuế phải nộp": tax_amount,
                "Tài sản ròng (Sau thuế)": net_balance,
                "Sức mua thực tế (Trừ lạm phát)": real_value
            })
            data_points.append({
                "Năm": yr, 
                "Tài sản ròng (Sau thuế)": net_balance, 
                "Sức mua thực tế": real_value,
                "Vốn gốc": total_contrib
            })

    df_schedule = pd.DataFrame(schedule)
    final_gross = current_balance
    final_gross_interest = final_gross - total_contrib
    final_tax = max(0, final_gross_interest * tax)
    final_net_balance = final_gross - final_tax
    final_real_value = final_net_balance / ((1 + inf) ** t)
    
    # Hiển thị kết quả tổng quan
    st.markdown("### 📊 Kết quả tổng quan")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tài sản ròng (Sau thuế)", f"{final_net_balance:,.0f} VNĐ")
    m2.metric("Sức mua thực tế (Hôm nay)", f"{final_real_value:,.0f} VNĐ")
    m3.metric("Tổng vốn gốc đã đóng", f"{total_contrib:,.0f} VNĐ")
    m4.metric("Tổng thuế thu nhập", f"{final_tax:,.0f} VNĐ")
    
    st.subheader("📈 Biểu đồ tăng trưởng tài sản ròng & Sức mua thực tế")
    if data_points:
        df_chart = pd.DataFrame(data_points).set_index("Năm")
        st.line_chart(df_chart[["Tài sản ròng (Sau thuế)", "Sức mua thực tế", "Vốn gốc"]])
        
    st.subheader("📋 Bảng chi tiết dòng tiền theo năm")
    st.dataframe(df_schedule.style.format({
        "Vốn gốc tích lũy": "{:,.0f} VNĐ",
        "Lợi nhuận gộp": "{:,.0f} VNĐ",
        "Thuế phải nộp": "{:,.0f} VNĐ",
        "Tài sản ròng (Sau thuế)": "{:,.0f} VNĐ",
        "Sức mua thực tế (Trừ lạm phát)": "{:,.0f} VNĐ"
    }), use_container_width=True)
    
    csv = df_schedule.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Tải xuống lịch trình chi tiết (CSV)",
        data=csv,
        file_name='lich_trinh_lai_kep_nang_cao.csv',
        mime='text/csv',
    )

# ==========================================
# TAB 2: LÃI ĐƠN TRUYỀN THỐNG
# ==========================================
elif tab == "🧮 Lãi đơn truyền thống":
    st.header("🧮 Máy tính Lãi đơn (Simple Interest)")
    col1, col2 = st.columns(2)
    with col1:
        p_simple = st.number_input("Số tiền gốc (VNĐ)", min_value=0.0, value=100000000.0, step=1000000.0)
        r_simple = st.number_input("Lãi suất (%/năm)", min_value=0.0, value=8.0, step=0.1)
        t_simple = st.number_input("Thời gian (Năm)", min_value=0.1, value=5.0, step=0.5)
    
    interest_simple = p_simple * (r_simple / 100.0) * t_simple
    total_simple = p_simple + interest_simple
    
    with col2:
        st.markdown("### Kết quả tính toán")
        st.metric("Tiền lãi thu được", f"{interest_simple:,.0f} VNĐ")
        st.metric("Tổng gốc + lãi cuối kỳ", f"{total_simple:,.0f} VNĐ")

# ==========================================
# TAB 3: SO SÁNH LÃI ĐƠN VS LÃI KÉP
# ==========================================
elif tab == "⚖️ So sánh Lãi đơn vs Lãi kép":
    st.header("⚖️ So sánh trực quan: Lãi đơn vs Lãi kép")
    c1, c2, c3 = st.columns(3)
    with c1:
        comp_p = st.number_input("Vốn gốc ban đầu (VNĐ)", value=100000000.0, step=1000000.0)
    with c2:
        comp_r = st.number_input("Lãi suất năm (%/năm)", value=9.0, step=0.5)
    with c3:
        comp_t = st.slider("Thời gian so sánh (Năm)", min_value=1, max_value=30, value=15)
        
    years_arr = list(range(1, comp_t + 1))
    comparison_data = []
    for y in years_arr:
        simple_val = comp_p + (comp_p * (comp_r/100.0) * y)
        compound_val = comp_p * ((1 + comp_r/100.0 / 12) ** (y * 12))
        comparison_data.append({
            "Năm": y,
            "Lãi đơn": simple_val,
            "Lãi kép": compound_val
        })
        
    df_comp = pd.DataFrame(comparison_data).set_index("Năm")
    st.line_chart(df_comp)
    
    final_s = df_comp.iloc[-1]["Lãi đơn"]
    final_c = df_comp.iloc[-1]["Lãi kép"]
    diff = final_c - final_s
    st.success(f"🔥 Sau {comp_t} năm, lãi kép tạo ra nhiều hơn lãi đơn **{diff:,.0f} VNĐ** (chênh lệch **{(diff/final_s)*100:.1f}%**).")
    st.dataframe(df_comp.style.format("{:,.0f} VNĐ"), use_container_width=True)

# ==========================================
# TAB 4: TÍNH KHOẢN VAY TRẢ GÓP (EMI)
# ==========================================
elif tab == "🏠 Tính khoản vay trả góp (EMI)":
    st.header("🏠 Tính toán khoản vay trả góp (Dư nợ giảm dần)")
    c1, c2 = st.columns(2)
    with c1:
        loan_amount = st.number_input("Số tiền vay (VNĐ)", value=500000000.0, step=10000000.0)
        loan_rate = st.number_input("Lãi suất vay (%/năm)", value=10.5, step=0.1)
    with c2:
        loan_years = st.number_input("Thời hạn vay (Năm)", value=20, min_value=1, max_value=35)
        
    months_loan = loan_years * 12
    monthly_r = loan_rate / 100.0 / 12.0
    
    if monthly_r > 0:
        emi = loan_amount * monthly_r * ((1 + monthly_r)**months_loan) / (((1 + monthly_r)**months_loan) - 1)
    else:
        emi = loan_amount / months_loan
        
    total_payment = emi * months_loan
    total_loan_interest = total_payment - loan_amount
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Trả hàng tháng (EMI)", f"{emi:,.0f} VNĐ")
    m2.metric("Tổng tiền lãi phải trả", f"{total_loan_interest:,.0f} VNĐ")
    m3.metric("Tổng gốc + lãi", f"{total_payment:,.0f} VNĐ")

# ==========================================
# TAB 5: MỤC TIÊU TÀI CHÍNH (GOAL SEEK)
# ==========================================
elif tab == "🎯 Mục tiêu tài chính (Goal Seek)":
    st.header("🎯 Máy tính Định hướng Mục tiêu Tài chính")
    c1, c2 = st.columns(2)
    with c1:
        target_amount = st.number_input("Mục tiêu số tiền mong muốn (VNĐ)", value=1000000000.0, step=10000000.0)
        initial_saving = st.number_input("Vốn ban đầu hiện có (VNĐ)", value=50000000.0, step=5000000.0)
    with c2:
        goal_rate = st.number_input("Lãi suất kỳ vọng (%/năm)", value=8.0, step=0.1)
        goal_years = st.number_input("Thời gian đạt mục tiêu (Năm)", value=5, min_value=1, max_value=30)
        
    months_g = goal_years * 12
    r_g = goal_rate / 100.0 / 12.0
    
    if r_g > 0:
        factor = ((1 + r_g)**months_g - 1) / r_g
        future_val_initial = initial_saving * ((1 + r_g)**months_g)
        required_pmt = max(0, (target_amount - future_val_initial) / factor)
    else:
        required_pmt = max(0, (target_amount - initial_saving) / months_g)
        
    st.success(f"💡 Để đạt mục tiêu **{target_amount:,.0f} VNĐ** sau {goal_years} năm với lãi suất {goal_rate}%/năm:")
    st.metric("Số tiền cần tiết kiệm định kỳ hằng tháng", f"{required_pmt:,.0f} VNĐ")

# ==========================================
# TAB 6: PHÂN TÍCH LẠM PHÁT ĐỘC LẬP
# ==========================================
elif tab == "📉 Phân tích Lạm phát độc lập":
    st.header("📉 Máy tính Tác động Lạm phát & Lãi suất thực tế")
    col1, col2 = st.columns(2)
    with col1:
        future_val = st.number_input("Số tiền trong tương lai (VNĐ)", value=1000000000.0, step=10000000.0)
        years_inf = st.number_input("Số năm sau (năm)", value=10, min_value=1, max_value=50)
        inflation_c = st.number_input("Tỷ lệ lạm phát hằng năm (%)", value=4.0, step=0.1)
    
    real_purchasing_power = future_val / ((1 + inflation_c / 100.0) ** years_inf)
    loss_value = future_val - real_purchasing_power
    
    with col2:
        st.markdown("### Kết quả quy đổi sức mua")
        st.metric("Sức mua thực tế tương đương", f"{real_purchasing_power:,.0f} VNĐ")
        st.metric("Giá trị hao hụt do lạm phát", f"{loss_value:,.0f} VNĐ", delta=f"-{loss_value/future_val*100:.1f}%")
