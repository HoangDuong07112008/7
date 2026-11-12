import streamlit as st
import pandas as pd
from datetime import datetime

# --- Cấu hình trang Streamlit ---
st.set_page_config(
    page_title="Ứng dụng Tính Lãi Suất & Quản Lý Khách Hàng",
    page_icon="💰",
    layout="wide"
)

st.title("📊 Quản lý Tính Lãi Suất Khách Hàng & Khoản Vay")
st.write("Hỗ trợ tính toán theo 2 hình thức: **Lãi phẳng (Cố định)** và **Dư nợ giảm dần**.")

# --- Khởi tạo Session State ---
if "danh_sach_kh" not in st.session_state:
    st.session_state.danh_sach_kh = pd.DataFrame(columns=[
        "Mã KH", "Tên khách hàng", "Phương thức", "Số tiền vay (VNĐ)", 
        "Lãi suất (%/tháng)", "Thời hạn (tháng)", "Tổng tiền lãi (VNĐ)", "Tổng tiền phải trả (VNĐ)"
    ])

# --- Form nhập liệu ---
with st.form("form_tinh_lai"):
    st.subheader("📝 Nhập thông tin khoản vay")
    
    col1, col2 = st.columns(2)
    with col1:
        ten_kh = st.text_input("Họ và tên khách hàng", placeholder="Ví dụ: Nguyễn Văn A")
        sdt_kh = st.text_input("Số điện thoại", placeholder="Ví dụ: 0912345678")
        so_tien_vay = st.number_input("Số tiền vay (VNĐ)", min_value=0.0, step=1000000.0, format="%.0f")
        
    with col2:
        phuong_thuc = st.selectbox(
            "Phương thức tính lãi", 
            ["Lãi phẳng (Cố định hàng tháng)", "Dư nợ giảm dần (Gốc đều hàng tháng)"]
        )
        lai_suat = st.number_input("Lãi suất (% / tháng)", min_value=0.0, step=0.1, value=1.5)
        thoi_han = st.number_input("Thời hạn vay (tháng)", min_value=1, step=1, value=12)
        
    submitted = st.form_submit_button("➕ Thêm & Tính toán cho khách hàng")
    
    if submitted:
        if not ten_kh.strip():
            st.error("⚠️ Vui lòng nhập tên khách hàng!")
        elif so_tien_vay <= 0:
            st.error("⚠️ Số tiền vay phải lớn hơn 0!")
        else:
            # --- XỬ LÝ TÍNH TOÁN ---
            if phuong_thuc == "Lãi phẳng (Cố định hàng tháng)":
                # Lãi tính trên tổng vốn ban đầu suốt thời gian vay
                tien_lai_thang = so_tien_vay * (lai_suat / 100)
                tong_tien_lai = tien_lai_thang * thoi_han
                tong_tien_phai_tra = so_tien_vay + tong_tien_lai
            else:
                # Dư nợ giảm dần: Gốc trả đều, lãi tính theo số dư nợ còn lại
                goc_hang_thang = so_tien_vay / thoi_han
                tong_tien_lai = 0
                du_no = so_tien_vay
                
                for _ in range(int(thoi_han)):
                    lai_thang = du_no * (lai_suat / 100)
                    tong_tien_lai += lai_thang
                    du_no -= goc_hang_thang
                    
                tong_tien_phai_tra = so_tien_vay + tong_tien_lai
            
            # Tạo mã khách hàng tự động
            ma_kh = f"KH_{datetime.now().strftime('%H%M%S')}"
            
            # Lưu vào danh sách
            new_row = {
                "Mã KH": ma_kh,
                "Tên khách hàng": ten_kh,
                "Phương thức": phuong_thuc,
                "Số tiền vay (VNĐ)": so_tien_vay,
                "Lãi suất (%/tháng)": lai_suat,
                "Thời hạn (tháng)": thoi_han,
                "Tổng tiền lãi (VNĐ)": tong_tien_lai,
                "Tổng tiền phải trả (VNĐ)": tong_tien_phai_tra
            }
            
            st.session_state.danh_sach_kh = pd.concat(
                [st.session_state.danh_sach_kh, pd.DataFrame([new_row])], 
                ignore_index=True
            )
            st.success(f"✅ Đã thêm khoản vay cho khách hàng **{ten_kh}** thành công!")

# --- Hiển thị danh sách ---
st.markdown("---")
st.subheader("📋 Danh sách khách hàng & Khoản vay")

if not st.session_state.danh_sach_kh.empty:
    st.dataframe(st.session_state.danh_sach_kh, use_container_width=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        csv_data = st.session_state.danh_sach_kh.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Tải xuống danh sách (CSV)",
            data=csv_data,
            file_name=f"danh_sach_khach_hang_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    with col_btn2:
        if st.button("🗑️ Xóa toàn bộ danh sách"):
            st.session_state.danh_sach_kh = pd.DataFrame(columns=[
                "Mã KH", "Tên khách hàng", "Phương thức", "Số tiền vay (VNĐ)", 
                "Lãi suất (%/tháng)", "Thời hạn (tháng)", "Tổng tiền lãi (VNĐ)", "Tổng tiền phải trả (VNĐ)"
            ])
            st.rerun()
else:
    st.info("Chưa có khách hàng nào trong hệ thống.")
