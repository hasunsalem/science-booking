import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & ADVANCED UI DESIGN ---
st.set_page_config(page_title="Chem Booking - วท.บ.เคมี", layout="wide")

st.markdown("""
<style>
    /* พื้นหลังหลัก */
    .stApp { background-color: #fcfdfe !important; }
    
    /* ลายน้ำโมเลกุล Dynamic */
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
        100% { transform: translate(100px, 50px) rotate(360deg); }
    }

    /* กล่องหน้าปก 3 มิติ สีเหลืองอ่อน */
    .glass-header {
        background: rgba(255, 251, 235, 0.85); 
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 2px solid rgba(251, 191, 36, 0.4);
        border-radius: 30px;
        padding: 45px;
        text-align: center;
        box-shadow: 0 15px 35px rgba(251, 191, 36, 0.15), inset 0 0 20px rgba(255, 255, 255, 0.6);
        margin-bottom: 45px;
        transform: perspective(1000px) rotateX(1deg);
    }
    
    .animated-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #b45309, #d97706, #b45309);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 5s linear infinite, floatTitle 3.5s ease-in-out infinite;
        margin-bottom: 8px;
        display: inline-block;
    }

    @keyframes shine { to { background-position: 200% center; } }
    @keyframes floatTitle {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    /* กล่องข้อมูลส่วนที่ 1 และ 2 */
    .section-1-container { border-radius: 22px; overflow: hidden; margin-bottom: 25px; box-shadow: 0 10px 25px rgba(180, 83, 9, 0.08); border: 1px solid #fde68a; }
    .header-1 { background: #d97706; color: white; padding: 18px 25px; font-weight: bold; font-size: 1.15rem; }
    .body-1 { background: #fffbeb; padding: 28px; }

    .section-2-container { border-radius: 22px; overflow: hidden; margin-bottom: 25px; box-shadow: 0 10px 25px rgba(180, 83, 9, 0.08); border: 1px solid #fde68a; }
    .header-2 { background: #b45309; color: white; padding: 18px 25px; font-weight: bold; font-size: 1.15rem; }
    .body-2 { background: #fef3c7; padding: 28px; }
    
    .block-container { position: relative; z-index: 10; padding-top: 2rem; }
    .busy-box { background: #fef3c7; color: #92400e; padding: 15px; border-radius: 12px; border-left: 6px solid #fbbf24; }
</style>

<div class="molecule-bg">
    <div class="molecule" style="top:15%; left:10%; font-size:50px;">H₂O</div>
    <div class="molecule" style="top:40%; left:80%; font-size:70px; animation-delay: -5s;">C₆H₁₂O₆</div>
    <div class="molecule" style="top:70%; left:25%; font-size:55px; animation-delay: -10s;">NaCl</div>
</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE SYSTEM ---
def init_db():
    conn = sqlite3.connect('chem_lab_v_final.db', check_same_thread=False)
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
st.markdown("""
<div class="glass-header">
    <div class="animated-title">ระบบขอใช้เครื่องมือวิทยาศาสตร์</div>
    <div style="color: #92400e; font-size: 1.25rem; font-weight: 600; letter-spacing: 0.5px;">
        หลักสูตร วท.บ. สาขาวิชาเคมี
    </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✍️ ลงทะเบียนจอง", "🔍 ตรวจสอบสถานะ"])

with tab1:
    # --- ส่วนที่ 1 ---
    st.markdown('<div class="section-1-container"><div class="header-1">👤 ส่วนที่ 1: รายละเอียดผู้ขอใช้บริการ</div><div class="body-1">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("ชื่อ - นามสกุล", placeholder="กรอกชื่อผู้จอง")
        u_status = st.selectbox("สถานะ", ["นักศึกษา", "อาจารย์", "เจ้าหน้าที่"])
        phone = st.text_input("เบอร์โทรศัพท์")
    with c2:
        faculty = st.text_input("คณะ/สาขาวิชา", value="วท.บ.เคมี")
        supervisor = st.text_input("อาจารย์ผู้ควบคุม")
        purpose = st.text_input("วัตถุประสงค์")
    st.markdown('</div></div>', unsafe_allow_html=True)

    # --- ส่วนที่ 2 ---
    st.markdown('<div class="section-2-container"><div class="header-2">🔬 ส่วนที่ 2: รายละเอียดเครื่องมือ และปฏิทินวันว่าง</div><div class="body-2">', unsafe_allow_html=True)
    col_t, col_i = st.columns([2, 1])
    with col_t:
        tool_name = st.text_input("ชื่อเครื่องมือวิทยาศาสตร์")
    with col_i:
        # แก้ไขจุดที่เกิด Error: แยกตัวแปรออกมาปกติ
        asset_id = st.text_input("รหัสครุภัณฑ์")
    
    if tool_name and asset_id:
        q_busy = "SELECT start_date, end_date FROM bookings WHERE tool_name = ? AND asset_id = ? AND approval_status != 'ไม่นุมัติ'"
        df_busy = pd.read_sql_query(q_busy, db_conn, params=(tool_name, asset_id))
        if not df_busy.empty:
            busy_txt = "<br>".join([f"📅 {r['start_date']} ถึง {r['end_date']}" for _, r in df_busy.iterrows()])
            st.markdown(f'<div class="busy-box"><b>⚠️ พบประวัติการจองเครื่องมือนี้:</b><br>{busy_txt}</div>', unsafe_allow_html=True)

    st.divider()
    cd1, cd2 = st.columns(2)
    with cd1: start_date = st.date_input("วันที่เริ่มใช้", min_value=datetime.today())
    with cd2: end_date = st.date_input("วันที่คืน", min_value=start_date)
    st.markdown('</div></div>', unsafe_allow_html=True)

    if st.button("🚀 ยืนยันคำขอจอง", use_container_width=True, type="primary"):
        if not name or not asset_id:
            st.error("⚠️ กรุณากรอกข้อมูลสำคัญให้ครบถ้วน")
        else:
            check_q = "SELECT id FROM bookings WHERE tool_name = ? AND asset_id = ? AND approval_status != 'ไม่นุมัติ' AND (? <= end_date AND ? >= start_date)"
            res = pd.read_sql_query(check_q, db_conn, params=(tool_name, asset_id, str(end_date), str(start_date)))
            if not res.empty:
                st.error("❌ ช่วงวันที่เลือกมีการจองอยู่แล้ว")
            else:
                cur = db_conn.cursor()
                cur.execute("INSERT INTO bookings (name, status, phone, faculty, supervisor, purpose, start_date, end_date, tool_name, asset_id) VALUES (?,?,?,?,?,?,?,?,?,?)", 
                            (name, u_status, phone, faculty, supervisor, purpose, str(start_date), str(end_date), tool_name, asset_id))
                db_conn.commit()
                st.success("🎉 บันทึกคำขอสำเร็จ!")
                st.balloons()

with tab2:
    st.markdown("### 📊 รายการตรวจสอบสถานะการจอง (วท.บ.เคมี)")
    is_admin = st.sidebar.checkbox("โหมดเจ้าหน้าที่ (Admin)")
    df = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", db_conn)
    if not df.empty:
        def style_status(row):
            s = row['approval_status']
            if s == 'อนุมัติแล้ว': return ['background-color: #d1fae5; color: #065f46'] * len(row)
            elif s == 'ไม่นุมัติ': return ['background-color: #fee2e2; color: #991b1b'] * len(row)
            return ['background-color: #fef3c7; color: #92400e'] * len(row)
        
        st.dataframe(df.style.apply(style_status, axis=1), use_container_width=True, hide_index=True)
        
        if is_admin:
            st.sidebar.divider()
            target_id = st.sidebar.number_input("จัดการสถานะ ID:", min_value=1, step=1)
            if st.sidebar.button("✅ อนุมัติ"):
                db_conn.cursor().execute("UPDATE bookings SET approval_status = 'อนุมัติแล้ว' WHERE id = ?", (target_id,))
                db_conn.commit()
                st.rerun()
            if st.sidebar.button("❌ ปฏิเสธ"):
                db_conn.cursor().execute("UPDATE bookings SET approval_status = 'ไม่นุมัติ' WHERE id = ?", (target_id,))
                db_conn.commit()
                st.rerun()
    else:
        st.info("ยังไม่มีข้อมูล")
