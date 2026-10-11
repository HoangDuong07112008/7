
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO

# ==================================================
# 1. CẤU HÌNH ỨNG DỤNG
# ==================================================
st.set_page_config(
    page_title="Tính lãi tiết kiệm ngân hàng",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 ỨNG DỤNG TÍNH LÃI TIẾT KIỆM NGÂN HÀNG")
st.caption(
    "Tính lãi đơn, lãi kép, bảng tăng trưởng, "
    "biểu đồ và xuất báo cáo Excel."
)

st.divider()


# ==================================================
# 2. HÀM HỖ TRỢ
# ==================================================
def format_vnd(value):
    return f"{value:,.0f} VNĐ".replace(",", ".")


def simple_interest(principal, annual_rate, months):
    interest = principal * annual_rate * months / 12
    return interest, principal + interest


def compound_balance(principal, annual_rate, months, cycle_months):
    full_periods = months // cycle_months
    remaining_months = months % cycle_months

    period_rate = annual_rate * cycle_months / 12

    balance = principal * (1 + period_rate) ** full_periods

    # Tính lãi cho phần tháng lẻ chưa đủ một chu kỳ
    balance *= 1 + annual_rate * remaining_months / 12

    return balance


def make_excel_bytes(report_df, growth_df):
    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        report_df.to_excel(
            writer,
            sheet_name="Bao cao tong hop",
            index=False
        )

        growth_df.to_excel(
            writer,
            sheet_name="Bang tang truong",
            index=False
        )

        # Định dạng các sheet Excel
        for sheet in writer.sheets.values():
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions

            for cells in sheet.columns:
                max_length = max(
                    len(str(cell.value or ""))
                    for cell in cells
                )

                letter = cells[0].column_letter

                sheet.column_dimensions[letter].width = min(
                    max_length + 3, 40
                )

    return output.getvalue()


# ==================================================
# 3. THÔNG TIN KHÁCH HÀNG
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
            min_value=100000,
            max_value=1000000000000,
            value=10000000,
            step=1000000
        )

    with col2:
        annual_rate_percent = st.number_input(
            "Lãi suất năm (%/năm)",
            min_value=0.0,
            max_value=100.0,
            value=6.0,
            step=0.1
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
        list(term_options.keys()),
        index=4
    )

    term_months = term_options[term_label]

    start_date = st.date_input(
        "Ngày bắt đầu gửi",
        value=datetime.now().date()
    )

    st.caption(
        f"Kỳ hạn: {term_months} tháng."
    )


# ==================================================
# 4. PHƯƠNG PHÁP TÍNH LÃI
# ==================================================
st.header("2. Phương pháp tính lãi")

interest_method = st.radio(
    "Chọn phương pháp tính",
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
    list(cycle_options.keys()),
    disabled=(interest_method != "Lãi kép")
)

cycle_months = cycle_options[cycle_label]

st.info(
    "Lãi đơn tính lãi trên gốc ban đầu. "
    "Lãi kép nhập lãi vào gốc theo chu kỳ đã chọn. "
    "Kết quả là mô phỏng, có thể khác cách tính thực tế "
    "của từng ngân hàng."
)


# ==================================================
# 5. TÍNH TOÁN
# ==================================================
annual_rate = annual_rate_percent / 100

simple_interest_value, simple_total = simple_interest(
    principal,
    annual_rate,
    term_months
)

compound_total = compound_balance(
    principal,
    annual_rate,
    term_months,
    cycle_months
)

compound_interest_value = compound_total - principal

interest_difference = (
    compound_interest_value - simple_interest_value
)

total_difference = compound_total - simple_total

if interest_method == "Lãi đơn":
    selected_interest = simple_interest_value
    selected_total = simple_total
else:
    selected_interest = compound_interest_value
    selected_total = compound_total


# ==================================================
# 6. KẾT QUẢ TÍNH TOÁN
# ==================================================
st.header("3. Kết quả tính toán")

if not customer_name.strip():
    st.warning("Vui lòng nhập tên khách hàng.")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Tiền gốc ban đầu",
        format_vnd(principal)
    )

with col2:
    st.metric(
        "Tiền lãi dự kiến",
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
    st.markdown("### Lãi đơn")

    st.metric(
        "Tiền lãi",
        format_vnd(simple_interest_value)
    )

    st.metric(
        "Tổng tiền cuối kỳ",
        format_vnd(simple_total)
    )

with compare2:
    st.markdown(f"### Lãi kép — {cycle_label}")

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


# ==================================================
# 7. BẢNG TĂNG TRƯỞNG TIỀN GỬI
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

# Hiển thị tiền theo định dạng Việt Nam
display_df = growth_df.copy()

money_columns = [
    column for column in display_df.columns
    if "(VNĐ)" in column
]

for column in money_columns:
    display_df[column] = display_df[column].map(format_vnd)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ==================================================
# 8. BIỂU ĐỒ TĂNG TRƯỞNG TIỀN GỬI
# ==================================================
st.header("5. Biểu đồ tăng trưởng tiền gửi")

chart_df = growth_df[
    [
        "Tháng",
        "Tổng tiền theo lãi đơn (VNĐ)",
        "Tổng tiền theo lãi kép (VNĐ)"
    ]
].melt(
    id_vars="Tháng",
    var_name="Phương pháp",
    value_name="Tổng tiền (VNĐ)"
)

fig = px.line(
    chart_df,
    x="Tháng",
    y="Tổng tiền (VNĐ)",
    color="Phương pháp",
    markers=True,
    title="So sánh tăng trưởng tiền gửi theo tháng",
    labels={
        "Tháng": "Tháng gửi",
        "Tổng tiền (VNĐ)": "Tổng tiền (VNĐ)",
        "Phương pháp": "Phương pháp tính"
    }
)

fig.update_layout(
    hovermode="x unified",
    legend_title_text="Phương pháp tính",
    xaxis=dict(dtick=1)
)

fig.update_yaxes(
    tickformat=",.0f"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.caption(
    "Biểu đồ tự động cập nhật theo số tiền gốc, "
    "lãi suất, kỳ hạn và chu kỳ nhập lãi đã chọn."
)


# ==================================================
# 9. BÁO CÁO TỔNG HỢP
# ==================================================
st.header("6. Báo cáo tổng hợp")

report_df = pd.DataFrame([
    {
        "Thông tin": "Tên khách hàng",
        "Giá trị": customer_name.strip() or "Chưa nhập"
    },
    {
        "Thông tin": "Ngày lập báo cáo",
        "Giá trị": datetime.now().strftime("%d/%m/%Y %H:%M")
    },
    {
        "Thông tin": "Ngày bắt đầu gửi",
        "Giá trị": start_date.strftime("%d/%m/%Y")
    },
    {
        "Thông tin": "Ngày đáo hạn dự kiến",
        "Giá trị": (
            start_date + pd.DateOffset(months=term_months)
        ).strftime("%d/%m/%Y")
    },
    {
        "Thông tin": "Tiền gốc ban đầu (VNĐ)",
        "Giá trị": round(principal, 2)
    },
    {
        "Thông tin": "Lãi suất năm (%)",
        "Giá trị": annual_rate_percent
    },
    {
        "Thông tin": "Kỳ hạn",
        "Giá trị": term_label
    },
    {
        "Thông tin": "Phương pháp được chọn",
        "Giá trị": interest_method
    },
    {
        "Thông tin": "Chu kỳ nhập lãi vào gốc",
        "Giá trị": cycle_label if interest_method == "Lãi kép" else "Không áp dụng"
    },
    {
        "Thông tin": "Tiền lãi theo lãi đơn (VNĐ)",
        "Giá trị": round(simple_interest_value, 2)
    },
    {
        "Thông tin": "Tổng tiền theo lãi đơn (VNĐ)",
        "Giá trị": round(simple_total, 2)
    },
    {
        "Thông tin": "Tiền lãi theo lãi kép (VNĐ)",
        "Giá trị": round(compound_interest_value, 2)
    },
    {
        "Thông tin": "Tổng tiền theo lãi kép (VNĐ)",
        "Giá trị": round(compound_total, 2)
    },
    {
        "Thông tin": "Tổng tiền theo phương pháp đã chọn (VNĐ)",
        "Giá trị": round(selected_total, 2)
    }
])

st.dataframe(
    report_df,
    use_container_width=True,
    hide_index=True
)


# ==================================================
# 10. XUẤT BÁO CÁO EXCEL
# ==================================================
st.header("7. Tải báo cáo")

excel_data = make_excel_bytes(
    report_df,
    growth_df
)

st.download_button(
    label="📊 TẢI BÁO CÁO EXCEL (.xlsx)",
    data=excel_data,
    file_name="bao_cao_tiet_kiem.xlsx",
    mime=(
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    ),
    use_container_width=True
)


# ==================================================
# 11. GHI CHÚ
# ==================================================
st.divider()

st.caption(
    "Lưu ý: Đây là công cụ mô phỏng tài chính. "
    "Lãi suất do người dùng nhập, không phải cam kết "
    "của bất kỳ ngân hàng nào. Kết quả thực tế có thể "
    "khác do quy tắc tính lãi, ngày gửi, ngày đáo hạn, "
    "làm tròn và điều kiện rút trước hạn."
)
