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

# Khởi tạo Session State lưu danh sách khách hàng chung cho toàn bộ app
if "customer_records" not in st.session_state:
    st.session_state.customer_records = []

# Hàm tiện ích hiển thị form nhập thông tin khách hàng chung cho các tab
def render_customer_input(tab_name):
    with st.expander(f"👤 Thông tin Khách hàng cho tính năng: [{tab_name}]", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            c_name = st.text_input("Họ và tên khách hàng", value="", placeholder="Ví dụ: Nguyễn Văn A", key=f"name_{tab_name}")
        with c2:
            c_phone = st.text_input("Số điện thoại khách hàng", value="", placeholder="Ví dụ: 0912345678", key=f"phone_{tab_name}")
    return c_name, c_phone

# Thanh điều hướng sidebar
tab = st.sidebar.radio(
    "🧭 Chọn tính năng:",
    [
        "📈 Lãi kép, Lạm phát & Thuế đầu tư",
        "🧮 Lãi đơn truyền thống",
        "⚖️ So sánh Lãi đơn vs Lãi kép",
        "🏠 Tính khoản vay trả góp (EMI)",
        "🎯 Mục tiêu tài chính (Goal Seek)",
        "📉 Phân tích Lạm phát độc lập",
        "👥 Quản lý & Lưu Khách Hàng"
    ]
)

# ==========================================
# TAB 1: LÃI KÉP, LẠM PHÁT & THUẾ ĐẦU TƯ
# ==========================================
if tab == "📈 Lãi kép, Lạm phát & Thuế đầu tư":
    st.header("📈 Máy tính Lãi kép Tích hợp Lạm phát & Thuế")
    st.markdown("Tính toán tăng trưởng tài sản dài hạn có xét đến đóng góp định kỳ, khấu trừ lạm phát và thuế thu nhập từ đầu tư.")
    
    cust_name, cust_phone = render_customer_input("Lãi kép")
    
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
            tax_amount = max(0, gross_interest * tax)
            net_balance = current_balance - tax_amount
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
    
    # Nút lưu kết quả vào danh sách khách hàng chung
    if st.button("💾 Lưu kết quả Lãi kép này vào hồ sơ khách hàng"):
        if not cust_name.strip():
            st.warning("⚠️ Vui lòng nhập tên khách hàng trước khi lưu!")
        else:
            new_record = {
                "Họ tên khách hàng": cust_name,
                "Số điện thoại": cust_phone if cust_phone else "Không có",
                "Tính năng": "Lãi kép & Đầu tư",
                "Chi tiết đầu tư": f"Vốn: {principal:,.0f}đ, Góp/tháng: {monthly_contrib:,.0f}đ, {years} năm, LS: {rate}%",
                "Kết quả chính (Tài sản ròng)": f"{final_net_balance:,.0f} VNĐ",
                "Thời gian lưu": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.customer_records.append(new_record)
            st.success(f"✅ Đã lưu hồ sơ cho khách hàng **{cust_name}** thành công!")

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
    
    cust_name, cust_phone = render_customer_input("Lãi đơn")
    
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
        
    if st.button("💾 Lưu kết quả Lãi đơn vào hồ sơ khách hàng"):
        if not cust_name.strip():
            st.warning("⚠️ Vui lòng nhập tên khách hàng trước khi lưu!")
        else:
            new_record = {
                "Họ tên khách hàng": cust_name,
                "Số điện thoại": cust_phone if cust_phone else "Không có",
                "Tính năng": "Lãi đơn truyền thống",
                "Chi tiết đầu tư": f"Gốc: {p_simple:,.0f}đ, {t_simple} năm, LS: {r_simple}%",
                "Kết quả chính (Tổng gốc+lãi)": f"{total_simple:,.0f} VNĐ",
                "Thời gian lưu": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.customer_records.append(new_record)
            st.success(f"✅ Đã lưu hồ sơ cho khách hàng **{cust_name}** thành công!")

# ==========================================
# TAB 3: SO SÁNH LÃI ĐƠN VS LÃI KÉP
# ==========================================
elif tab == "⚖️ So sánh Lãi đơn vs Lãi kép":
    st.header("⚖️ So sánh trực quan: Lãi đơn vs Lãi kép")
    
    cust_name, cust_phone = render_customer_input("So sánh Lãi đơn vs Lãi kép")
    
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

    if st.button("💾 Lưu kết quả So sánh vào hồ sơ khách hàng"):
        if not cust_name.strip():
            st.warning("⚠️ Vui lòng nhập tên khách hàng trước khi lưu!")
        else:
            new_record = {
                "Họ tên khách hàng": cust_name,
                "Số điện thoại": cust_phone if cust_phone else "Không có",
                "Tính năng": "So sánh Lãi đơn vs Lãi kép",
                "Chi tiết đầu tư": f"Gốc: {comp_p:,.0f}đ, {comp_t} năm, LS: {comp_r}%",
                "Kết quả chính (Lãi kép trội hơn)": f"{diff:,.0f} VNĐ",
                "Thời gian lưu": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.customer_records.append(new_record)
            st.success(f"✅ Đã lưu hồ sơ cho khách hàng **{cust_name}** thành công!")

# ==========================================
# TAB 4: TÍNH KHOẢN VAY TRẢ GÓP (EMI)
# ==========================================
elif tab == "🏠 Tính khoản vay trả góp (EMI)":
    st.header("🏠 Tính toán khoản vay trả góp (Dư nợ giảm dần)")
    
    cust_name, cust_phone = render_customer_input("Khoản vay trả góp")

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
    
    if st.button("💾 Lưu hồ sơ khoản vay này vào danh sách khách hàng"):
        if not cust_name.strip():
            st.warning("⚠️ Vui lòng nhập tên khách hàng trước khi lưu!")
        else:
            new_record = {
                "Họ tên khách hàng": cust_name,
                "Số điện thoại": cust_phone if cust_phone else "Không có",
                "Tính năng": "Khoản vay trả góp (EMI)",
                "Chi tiết đầu tư": f"Vay: {loan_amount:,.0f}đ, {loan_years} năm, LS: {loan_rate}%",
                "Kết quả chính (Trả hàng tháng)": f"{emi:,.0f} VNĐ",
                "Thời gian lưu": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.customer_records.append(new_record)
            st.success(f"✅ Đã lưu hồ sơ khoản vay cho khách hàng **{cust_name}** thành công!")

# ==========================================
# TAB 5: MỤC TIÊU TÀI CHÍNH (GOAL SEEK)
# ==========================================
elif tab == "🎯 Mục tiêu tài chính (Goal Seek)":
    st.header("🎯 Máy tính Định hướng Mục tiêu Tài chính")
    
    cust_name, cust_phone = render_customer_input("Mục tiêu tài chính")
    
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

    if st.button("💾 Lưu kết quả Mục tiêu tài chính vào hồ sơ khách hàng"):
        if not cust_name.strip():
            st.warning("⚠️ Vui lòng nhập tên khách hàng trước khi lưu!")
        else:
            new_record = {
                "Họ tên khách hàng": cust_name,
                "Số điện thoại": cust_phone if cust_phone else "Không có",
                "Tính năng": "Mục tiêu tài chính (Goal Seek)",
                "Chi tiết đầu tư": f"Mục tiêu: {target_amount:,.0f}đ, {goal_years} năm, LS: {goal_rate}%",
                "Kết quả chính (Cần góp/tháng)": f"{required_pmt:,.0f} VNĐ",
                "Thời gian lưu": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.customer_records.append(new_record)
            st.success(f"✅ Đã lưu hồ sơ cho khách hàng **{cust_name}** thành công!")

# ==========================================
# TAB 6: PHÂN TÍCH LẠM PHÁT ĐỘC LẬP
# ==========================================
elif tab == "📉 Phân tích Lạm phát độc lập":
    st.header("📉 Máy tính Tác động Lạm phát & Lãi suất thực tế")
    
    cust_name, cust_phone = render_customer_input("Phân tích Lạm phát")
    
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

    if st.button("💾 Lưu kết quả Lạm phát vào hồ sơ khách hàng"):
        if not cust_name.strip():
            st.warning("⚠️ Vui lòng nhập tên khách hàng trước khi lưu!")
        else:
            new_record = {
                "Họ tên khách hàng": cust_name,
                "Số điện thoại": cust_phone if cust_phone else "Không có",
                "Tính năng": "Phân tích Lạm phát",
                "Chi tiết đầu tư": f"Số tiền: {future_val:,.0f}đ, {years_inf} năm, Lạm phát: {inflation_c}%",
                "Kết quả chính (Sức mua thực tế)": f"{real_purchasing_power:,.0f} VNĐ",
                "Thời gian lưu": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.customer_records.append(new_record)
            st.success(f"✅ Đã lưu hồ sơ cho khách hàng **{cust_name}** thành công!")

# ==========================================
# TAB 7: QUẢN LÝ & LƯU KHÁCH HÀNG
# ==========================================
elif tab == "👥 Quản lý & Lưu Khách Hàng":
    st.header("👥 Danh sách Khách hàng & Hồ sơ đã lưu toàn hệ thống")
    st.markdown("Quản lý toàn bộ thông tin khách hàng đã được lưu từ bất kỳ tab tính toán nào. Bạn có thể xem bảng chi tiết hoặc tải xuống file Excel/CSV.")
    
    if len(st.session_state.customer_records) > 0:
        df_customers = pd.DataFrame(st.session_state.customer_records)
        st.dataframe(df_customers, use_container_width=True)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            csv_cust = df_customers.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Tải xuống toàn bộ danh sách khách hàng (CSV)",
                data=csv_cust,
                file_name=f"danh_sach_khach_hang_toan_bo_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        with col_b2:
            if st.button("🗑️ Xóa toàn bộ danh sách khách hàng"):
                st.session_state.customer_records = []
                st.rerun()
    else:
        st.info("💡 Chưa có hồ sơ khách hàng nào được lưu. Hãy sử dụng các tab tính năng phía trên, điền tên khách hàng và bấm **Lưu kết quả** để ghi nhận dữ liệu tại đây!")
