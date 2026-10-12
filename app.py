
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

# ==================================================
# 1. CẤU HÌNH GIAO DIỆN
# ==================================================
st.set_page_config(
    page_title="Tính lãi tiết kiệm ngân hàng",
    page_icon="🏦",
    layout="wide"
)

st.image("banner.jpg", use_container_width=True)
st.title("🏦 ỨNG DỤNG TÍNH LÃI TIẾT KIỆM NGÂN HÀNG")
st.caption(
    "Tính toán lãi đơn, lãi kép, so sánh lợi nhuận "
    "và xuất báo cáo tiền gửi tiết kiệm."
)

st.divider()


# ==================================================
# 2. CÁC HÀM HỖ TRỢ
# ==================================================
def format_vnd(value):
    """Định dạng số tiền theo kiểu Việt Nam."""
    return f"{value:,.0f} VNĐ".replace(",", ".")


def simple_interest(principal, annual_rate, months):
    """Tính lãi đơn theo lãi suất năm."""
    interest = principal * annual_rate * months / 12
    return interest, principal + interest


def compound_balance(principal, annual_rate, months, cycle_months):
    """
    Tính số dư lãi kép tại một thời điểm.
    Lãi được nhập gốc theo chu kỳ đã chọn.
    Phần thời gian chưa đủ một chu kỳ được tính
    lãi theo tỷ lệ số tháng còn lại.
    """
    full_periods = months // cycle_months
    remaining_months = months % cycle_months

    period_rate = annual_rate * cycle_months / 12
    balance = principal * (1 + period_rate) ** full_periods

    # Lãi tích lũy trong chu kỳ chưa hoàn tất
    balance *= 1 + annual_rate * remaining_months / 12

    return balance



def make_excel_bytes(dataframe):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Bang tang truong"
        )
    return output.getvalue()


# ==================================================
# 3. NHẬP THÔNG TIN KHÁCH HÀNG
# ==================================================
st.header("1. Thông tin khách hàng")

with st.container(border=True):
    customer_name = st.text_input(
        "Tên khách hàng",
        placeholder="Ví dụ: Nguyễn Văn A"
    )

    col1, col2 = st.columns(2)

    with col1:
        principal = st.number_input(
            "Số tiền gửi ban đầu (VNĐ)",
            min_value=100000.0,
            max_value=1000000000000.0,
            value=10000000.0,
            step=1000000.0,
            format="%.0f"
        )

    with col2:
        annual_rate_percent = st.number_input(
            "Lãi suất năm (%)",
            min_value=0.0,
            max_value=100.0,
            value=6.0,
            step=0.1,
            format="%.2f"
        )

    term_options = {
        "1 tháng": 1,
        "3 tháng": 3,
        "6 tháng": 6,
        "9 tháng": 9,
        "12 tháng": 12,
        "18 tháng": 18,
        "24 tháng": 24,
        "36 tháng": 36,
        "48 tháng": 48,
        "60 tháng": 60
    }

    term_label = st.selectbox(
        "Kỳ hạn gửi tiết kiệm",
        options=list(term_options.keys()),
        index=4
    )

    term_months = term_options[term_label]

    st.caption(
        f"Kỳ hạn được chọn: {term_months} tháng "
        f"({term_months / 12:g} năm)."
    )


# ==================================================
# 4. CHỌN PHƯƠNG PHÁP TÍNH LÃI
# ==================================================
st.header("2. Phương pháp tính lãi")

interest_method = st.radio(
    "Chọn phương pháp chính muốn sử dụng",
    ["Lãi đơn", "Lãi kép"],
    horizontal=True
)

cycle_options = {
    "Hàng tháng": 1,
    "Hàng quý (3 tháng)": 3,
    "Nửa năm (6 tháng)": 6,
    "Hàng năm (12 tháng)": 12
}

cycle_label = st.selectbox(
    "Chu kỳ nhập lãi vào gốc (dùng cho lãi kép)",
    options=list(cycle_options.keys()),
    index=0,
    disabled=(interest_method != "Lãi kép")
)

cycle_months = cycle_options[cycle_label]

st.info(
    "Lãi đơn: tiền lãi tính trên số tiền gốc ban đầu. "
    "Lãi kép: tiền lãi được cộng vào gốc theo chu kỳ, "
    "sau đó tiếp tục sinh lãi."
)


# ==================================================
# 5. TÍNH TOÁN
# ==================================================
annual_rate = annual_rate_percent / 100

simple_interest_value, simple_total = simple_interest(
    principal, annual_rate, term_months
)

compound_total = compound_balance(
    principal, annual_rate, term_months, cycle_months
)

compound_interest_value = compound_total - principal

interest_difference = compound_interest_value - simple_interest_value
total_difference = compound_total - simple_total

selected_interest = (
    simple_interest_value
    if interest_method == "Lãi đơn"
    else compound_interest_value
)

selected_total = (
    simple_total
    if interest_method == "Lãi đơn"
    else compound_total
)


# ==================================================
# 6. HIỂN THỊ KẾT QUẢ
# ==================================================
st.header("3. Kết quả tính toán")

if not customer_name.strip():
    st.warning(
        "Bạn chưa nhập tên khách hàng. "
        "Hãy nhập tên để hoàn thiện báo cáo."
    )

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Tiền gửi ban đầu",
        format_vnd(principal)
    )

with col2:
    st.metric(
        "Tiền lãi theo phương pháp đã chọn",
        format_vnd(selected_interest)
    )

with col3:
    st.metric(
        "Tổng tiền cuối kỳ",
        format_vnd(selected_total)
    )

st.subheader("So sánh lãi đơn và lãi kép")

compare1, compare2 = st.columns(2)

with compare1:
    st.markdown("**Lãi đơn**")
    st.metric(
        "Tiền lãi",
        format_vnd(simple_interest_value)
    )
    st.metric(
        "Tổng tiền cuối kỳ",
        format_vnd(simple_total)
    )

with compare2:
    st.markdown(f"**Lãi kép — {cycle_label}**")
    st.metric(
        "Tiền lãi",
        format_vnd(compound_interest_value),
        delta=format_vnd(interest_difference)
    )
    st.metric(
        "Tổng tiền cuối kỳ",
        format_vnd(compound_total),
        delta=format_vnd(total_difference)
    )

if total_difference > 0:
    st.success(
        f"Trong mô hình này, lãi kép tạo ra tổng tiền cao hơn "
        f"lãi đơn {format_vnd(total_difference)}."
    )
elif total_difference < 0:
    st.warning(
        f"Lãi đơn cao hơn lãi kép "
        f"{format_vnd(abs(total_difference))}."
    )
else:
    st.info("Hai phương pháp cho kết quả bằng nhau.")


# ==================================================
# 7. LẬP BẢNG TĂNG TRƯỞNG THEO THÁNG
# ==================================================
st.header("4. Bảng tăng trưởng tiền gửi")

rows = []

for month in range(term_months + 1):
    simple_interest_month = (
        principal * annual_rate * month / 12
    )
    simple_balance_month = (
        principal + simple_interest_month
    )

    compound_balance_month = compound_balance(
        principal,
        annual_rate,
        month,
        cycle_months
    )

    rows.append({
        "Tháng": month,
        "Tiền gốc ban đầu (VNĐ)": round(principal, 2),
        "Lãi đơn tích lũy (VNĐ)": round(
            simple_interest_month, 2
        ),
        "Tổng tiền theo lãi đơn (VNĐ)": round(
            simple_balance_month, 2
        ),
        "Lãi kép tích lũy (VNĐ)": round(
            compound_balance_month - principal, 2
        ),
        "Tổng tiền theo lãi kép (VNĐ)": round(
            compound_balance_month, 2
        )
    })

growth_df = pd.DataFrame(rows)

display_df = growth_df.copy()

money_columns = [
    col for col in display_df.columns
    if "(VNĐ)" in col
]

for col in money_columns:
    display_df[col] = display_df[col].map(format_vnd)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ==================================================
# 8. BIỂU ĐỒ TĂNG TRƯỞNG
# ==================================================
st.header("5. Biểu đồ tăng trưởng tiền gửi")

chart_df = growth_df.set_index("Tháng")[
    [
        "Tổng tiền theo lãi đơn (VNĐ)",
        "Tổng tiền theo lãi kép (VNĐ)"
    ]
]

st.line_chart(chart_df)

st.caption(
    "Biểu đồ so sánh tổng tiền tích lũy theo từng tháng "
    "với cùng số vốn, lãi suất và kỳ hạn."
)


# ==================================================
# 9. BÁO CÁO TỔNG HỢP
# ==================================================
st.header("6. Xuất báo cáo")

report_df = pd.DataFrame([
    {"Thông tin": "Tên khách hàng",
     "Giá trị": customer_name.strip() or "Chưa nhập"},
    {"Thông tin": "Ngày lập báo cáo",
     "Giá trị": datetime.now().strftime("%d/%m/%Y %H:%M")},
    {"Thông tin": "Số tiền gửi ban đầu (VNĐ)",
     "Giá trị": round(principal, 2)},
    {"Thông tin": "Lãi suất năm (%)",
     "Giá trị": annual_rate_percent},
    {"Thông tin": "Kỳ hạn",
     "Giá trị": term_label},
    {"Thông tin": "Phương pháp được chọn",
     "Giá trị": interest_method},
    {"Thông tin": "Chu kỳ nhập lãi vào gốc",
     "Giá trị": cycle_label},
    {"Thông tin": "Tiền lãi theo lãi đơn (VNĐ)",
     "Giá trị": round(simple_interest_value, 2)},
    {"Thông tin": "Tổng tiền theo lãi đơn (VNĐ)",
     "Giá trị": round(simple_total, 2)},
    {"Thông tin": "Tiền lãi theo lãi kép (VNĐ)",
     "Giá trị": round(compound_interest_value, 2)},
    {"Thông tin": "Tổng tiền theo lãi kép (VNĐ)",
     "Giá trị": round(compound_total, 2)},
    {"Thông tin": "Chênh lệch tổng tiền lãi kép - lãi đơn (VNĐ)",
     "Giá trị": round(total_difference, 2)},
    {"Thông tin": "Tổng tiền theo phương pháp đã chọn (VNĐ)",
     "Giá trị": round(selected_total, 2)}
])

st.subheader("Xem trước báo cáo tổng hợp")
st.dataframe(
    report_df,
    use_container_width=True,
    hide_index=True
)

col_download1, col_download2 = st.columns(2)

with col_download1:
        st.download_button(
    label="📗 Tải báo cáo tổng hợp Excel",
    data=make_excel_bytes(report_df),
    file_name="bao_cao_truong_tiet_kiem.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
    )

with col_download2:
    st.download_button(
    label="📗 Tải bảng tăng trưởng Excel",
    data=make_excel_bytes(growth_df),
    file_name="bang_tang_truong_tiet_kiem.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

st.divider()

st.caption(
    "Lưu ý: Đây là công cụ mô phỏng tài chính. "
    "Kết quả được tính theo lãi suất năm do người dùng nhập, "
    "không đại diện cho cam kết của bất kỳ ngân hàng nào. "
    "Sản phẩm tiền gửi thực tế có thể áp dụng quy tắc tính lãi "
    "và làm tròn khác."
)
