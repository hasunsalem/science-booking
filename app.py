import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & UI DESIGN ---
st.set_page_config(page_title="Chem Booking - วท.บ.เคมี", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #fcfdfe !important; }
    
    /* ลายน้ำพื้นหลัง */
    .molecule-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0; pointer-events: none; overflow: hidden; opacity: 0.1;
    }
    .molecule {
        position: absolute; font-family: 'Courier New', monospace; font-weight: 900;
        color: #856404; animation: floatWave 25s infinite alternate ease-in-out;
    }
    @keyframes floatWave {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(120px, 60px) rotate(360deg); }
    }

    /* กล่องหน้าปก 3 มิติ */
    .glass-header {
        position: relative;
        background: rgba(255, 251, 235, 0.85); 
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 2px solid rgba(251, 191, 36, 0.4);
        border-radius: 35px;
        padding: 60px 45px;
        text-align: center;
        box-shadow: 0 25px 50px rgba(251, 191, 36, 0.2), inset 0 0 30px rgba(255, 255, 255, 0.8);
        margin-bottom: 45px;
        transform: perspective(1000px) rotateX(1deg);
        overflow: hidden;
    }
    
    /* ตัวการ์ตูนนักวิทยาศาสตร์น้อย */
    .mascot {
        position: absolute;
        bottom: 10px;
        right: 40px;
        font-size: 80px;
        z-index: 5;
        animation: mascotFloat 4s ease-in-out infinite;
        filter: drop-shadow(2px 4px 8px rgba(0,0,0,0.1));
    }
    @keyframes mascotFloat {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(5deg); }
    }

    /* ลายน้ำในกล่อง */
    .inner-molecule {
        position: absolute;
        color: rgba(217, 119, 6, 0.12);
        font-family: 'Courier New', monospace;
        font-weight: bold;
        z-index: 1;
        pointer-events: none;
        animation: innerFloat 10s infinite linear;
    }
    @keyframes innerFloat {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        50% { transform: translate(20px, -20px) rotate(15deg); }
    }

    /* ชื่อระบบเคลื่อนไหว */
    .animated-title {
        position: relative;
        z-index: 10;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #b45309, #f59e0b, #d97706, #b45309);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 5s linear infinite, floatTitle 4s ease-in-out infinite;
        margin-bottom: 8px;
        display: inline-block;
    }
    @keyframes shine { to { background-position: 200% center; } }
    @keyframes floatTitle {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-12px); }
    }

    /* กล่องข้อมูล */
    .section-1-container { border-radius: 22px; overflow: hidden; margin-bottom: 25px; border: 1px solid #fde68a; }
    .header-1 { background: #d97706; color: white; padding: 18px 25px; font-weight: bold; }
    .body-1 { background: #fffbeb; padding: 28px; }

    .section-2-container { border-radius: 22px; overflow: hidden; margin-bottom: 25px; border: 1px solid #fde68a; }
    .header-2 { background: #b45309; color: white; padding: 18px 25px; font-weight: bold; }
    .body-2 { background: #fef3c7; padding: 28px; }

    .busy-box { background: #fef3c7; color: #92400e; padding: 15px; border-radius: 12px; border-left: 6px solid #fbbf24; }
</style>

<div class="molecule-bg">
    <div class="molecule" style="top:15%; left:10%; font-size:50px;">H₂O</div>
    <div class="molecule" style="top:70%; left:25%; font-size:55px; animation-delay: -10s;">NaCl</div>
</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('chem_lab_final_v2.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, status TEXT, phone TEXT, faculty TEXT, supervisor TEXT,
        purpose TEXT, start_date DATE, end_date DATE, tool_name TEXT, 
        asset_id TEXT, approval_status TEXT DEFAULT 'รออนุมัติ'
    )''')
    conn.commit()
    return conn
db_conn = init_db()

# --- 3. APP INTERFACE ---
# หน้าปกพร้อม "นักวิทยาศาสตร์น้อย" (Mascot) และลายน้ำ
st.markdown("""
<div class="glass-header">
    <!-- ตัวการ์ตูนนักวิทยาศาสตร์ (Mascot) -->
    <div class="mascot">🧑‍🔬</div>
    
    <!-- ลายน้ำโมเลกุลในกล่อง -->
    <div class="inner-molecule" style="top:10%; left:5%; font-size:30px;">C₂H₅OH</div>
    <div class="inner-molecule" style="top:60%; left:75%; font-size:25px; animation-delay: -2s;">H₂SO₄</div>
    <div class="inner-molecule" style="top:20%; left:85%; font-size:22px; animation-delay: -4s;">CH₄</div>
    
    <div class="animated-title">ระบบขอใช้เครื่องมือวิทยาศาสตร์</div>
    <div style="position: relative; z-index: 10; color: #92400e; font-size: 1.3rem; font-weight: 700;">
        หลักสูตร วท.บ. สาขาวิชาเคมี
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✍️ ลงทะเบียนจอง", "🔍 ตรวจสอบสถานะ"])

with tab1:
    st.markdown('<div class="section-1-container"><div class="header-1">👤 ส่วนที่ 1: รายละเอียดผู้ขอใช้บริการ</div><div class="body-1">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        u_name = st.text_input("ชื่อ - นามสกุล", key="user_n")
        u_phone = st.text_input("เบอร์โทรศัพท์", key="user_p")
    with c2:
        u_fac = st.text_input("คณะ/สังกัด", value="วท.บ.เคมี", key="user_f")
        u_purp = st.text_input("วัตถุประสงค์การใช้งาน", key="user_pu")
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-2-container"><div class="header-2">🔬 ส่วนที่ 2: รายละเอียดเครื่องมือ</div><div class="body-2">', unsafe_allow_html=True)
    ct1, ct2 = st.columns([2, 1])
    with ct1: t_name = st.text_input("ชื่อเครื่องมือ", key="tool_n")
    with ct2: a_id = st.text_input("รหัสครุภัณฑ์", key="asset_i")
    
    if t_name and a_id:
        busy_df = pd.read_sql_query("SELECT start_date, end_date FROM bookings WHERE tool_name = ? AND asset_id = ? AND approval_status != 'ไม่นุมัติ'", db_conn, params=(t_name, a_id))
        if not busy_df.empty:
            busy_txt = "<br>".join([f"📅 {r['start_date']} ถึง {r['end_date']}" for _, r in busy_df.iterrows()])
            st.markdown(f'<div class="busy-box"><b>⚠️ พบประวัติการจอง:</b><br>{busy_txt}</div>', unsafe_allow_html=True)

    st.divider()
    cd1, cd2 = st.columns(2)
    with cd1: s_date = st.date_input("วันที่เริ่มใช้", min_value=datetime.today(), key="sd")
    with cd2: e_date = st.date_input("วันที่คืน", min_value=s_date, key="ed")
    st.markdown('</div></div>', unsafe_allow_html=True)

    if st.button("🚀 ยืนยันการจอง", use_container_width=True, type="primary"):
        if not u_name or not a_id:
            st.error("⚠️ ข้อมูลไม่ครบ")
        else:
            cur = db_conn.cursor()
            cur.execute("INSERT INTO bookings (name, start_date, end_date, tool_name, asset_id) VALUES (?,?,?,?,?)", 
                        (u_name, str(s_date), str(e_date), t_name, a_id))
            db_conn.commit()
            st.success("บันทึกสำเร็จ!")
            st.balloons()

with tab2:
    st.markdown("### 📊 รายการตรวจสอบสถานะ")
    df = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", db_conn)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("ไม่มีข้อมูล")
