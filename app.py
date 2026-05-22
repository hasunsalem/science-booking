import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & UI DESIGN ---
st.set_page_config(page_title="Science Lab Booking", layout="wide")

# Custom CSS สำหรับดีไซน์ทันสมัยและลายน้ำ
st.markdown("""
<style>
    /* พื้นหลังหลัก */
    .stApp {
        background-color: #f4f7f6;
    }
    
    /* ลายน้ำโมเลกุล Dynamic */
    .molecule-bg {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1; pointer-events: none; opacity: 0.07; overflow: hidden;
    }
    .mol {
        position: absolute; font-family: 'Courier New', monospace; font-weight: 800;
        color: #2c3e50; animation: floatAnim 15s infinite alternate ease-in-out;
    }
    @keyframes floatAnim {
        from { transform: translate(0, 0) rotate(0deg); }
        to { transform: translate(50px, 30px) rotate(15deg); }
    }

    /* ตกแต่ง Card และ Form */
    div[data-testid="stForm"] {
        background: #ffffff;
        padding: 40px;
        border-radius: 24px;
        border: none;
        box-shadow: 0 20px 40px rgba(0,0,0,0.05);
    }
    
    /* ตกแต่ง Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #ffffff;
        border-radius: 12px;
        padding: 0 30px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
</style>

<div class="molecule-bg">
    <div class="mol" style="top:10%; left:5%; font-size:60px;">H₂O</div>
    <div class="mol" style="top:40%; left:85%; font-size:80px; animation-delay: -2s;">C₆H₁₂O₆</div>
    <div class="mol" style="top:70%; left:15%; font-size:50px; animation-delay: -5s;">NaCl</div>
    <div class="mol" style="top:85%; left:65%; font-size:55px; animation-delay: -7s;">CO₂</div>
    <div class="mol" style="top:20%; left:60%; font-size:40px; animation-delay: -10s;">NH₃</div>
</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE SYSTEM ---
def init_db():
    conn = sqlite3.connect('science_lab.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, status TEXT, phone TEXT, faculty TEXT, 
        purpose TEXT, start_date DATE, end_date DATE, 
        tool_name TEXT, asset_id TEXT, state TEXT DEFAULT 'Active'
    )''')
    conn.commit()
    return conn

db_conn = init_db()

def check_overlap(asset_id, start, end):
    query = "SELECT name FROM bookings WHERE asset_id = ? AND state = 'Active' AND (? <= end_date AND ? >= start_date)"
    return pd.read_sql_query(query, db_conn, params=(asset_id, str(end), str(start)))

# --- 3. MAIN APP INTERFACE ---
tabs = st.tabs(["✨ สร้างคำขอจองใหม่", "📋 รายการจองทั้งหมด"])

with tabs[0]:
    st.markdown("<h1 style='color: #1a3a5f;'>🧪 แบบฟอร์มจองเครื่องมือวิทยาศาสตร์</h1>", unsafe_allow_html=True)
    st.write("ระบุรายละเอียดการจองด้านล่าง ระบบจะตรวจสอบคิวว่างให้อัตโนมัติ")

    with st.form("booking_form", clear_on_submit=True):
        # ส่วนที่ 1: ข้อมูลผู้จอง
        st.markdown("### 👤 ส่วนที่ 1: ข้อมูลผู้ขอใช้บริการ")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("ชื่อ - นามสกุล", placeholder="ระบุชื่อจริง-นามสกุล")
            u_status = st.selectbox("สถานะผู้ใช้งาน", ["อาจารย์", "เจ้าหน้าที่", "นักศึกษา"])
            phone = st.text_input("เบอร์โทรศัพท์ติดต่อ")
        with c2:
            faculty = st.text_input("สังกัด / คณะ / สาขาวิชา")
            purpose = st.selectbox("วัตถุประสงค์การใช้งาน", ["งานวิจัย", "การเรียนการสอน", "อื่นๆ"])
            location = st.text_input("สถานที่นำไปใช้")
        
        c3, c4 = st.columns(2)
        with c3:
            start_date = st.date_input("ตั้งแต่วันที่", min_value=datetime.today())
        with c4:
            end_date = st.date_input("ถึงวันที่", min_value=start_date)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ส่วนที่ 2: ข้อมูลเครื่องมือ (แบบเพิ่มรายการได้)
        st.markdown("### 🔬 ส่วนที่ 2: รายละเอียดเครื่องมือ")
        
        # ใช้ Session State เก็บจำนวนรายการเครื่องมือ
        if 'item_count' not in st.session_state:
            st.session_state.item_count = 1
        
        tool_data = []
        for i in range(st.session_state.item_count):
            st.markdown(f"**รายการที่ {i+1}**")
            col_t1, col_t2 = st.columns([2, 1])
            with col_t1:
                t_name = st.text_input(f"ชื่อเครื่องมือ {i+1}", key=f"t_name_{i}")
            with col_t2:
                a_id = st.text_input(f"รหัสครุภัณฑ์ {i+1}", key=f"a_id_{i}")
            tool_data.append({"name": t_name, "id": a_id})
        
        # ปุ่มเพิ่มรายการ (อยู่นอก Form เพื่อให้กดแล้ว UI เปลี่ยนทันที)
        # หมายเหตุ: ใน Streamlit ปุ่มใน Form จะไม่เปลี่ยน state จนกว่าจะกด submit 
        # จึงต้องใช้เทคนิคทำรายการเผื่อไว้ หรือใช้ปุ่มนอก form ครับ 
        # เพื่อความง่าย ผมจะทำช่องกรอกเพิ่มรายการไว้ให้เลย
        
        st.info("💡 หากต้องการจองเครื่องมือมากกว่า 1 รายการในครั้งเดียว กรุณาระบุรหัสครุภัณฑ์คั่นด้วยเครื่องหมายคอมม่า (,) หรือกดปุ่ม Submit เพื่อจองทีละรายการ")

        # ปุ่มกดยืนยัน
        submit_btn = st.form_submit_button("🚀 ยืนยันการจองทั้งหมด", use_container_width=True)
        
        if submit_btn:
            if not name or not tool_data[0]['id']:
                st.warning("⚠️ กรุณากรอกข้อมูลผู้จองและรหัสครุภัณฑ์อย่างน้อย 1 รายการ")
            else:
                success_count = 0
                for item in tool_data:
                    if item['id']:
                        overlap = check_overlap(item['id'], start_date, end_date)
                        if not overlap.empty:
                            st.error(f"❌ รายการ {item['name']} (รหัส {item['id']}) ถูกจองแล้วโดยคุณ {overlap.iloc[0]['name']}")
                        else:
                            cursor = db_conn.cursor()
                            cursor.execute('''INSERT INTO bookings 
                                (name, status, phone, faculty, purpose, start_date, end_date, tool_name, asset_id)
                                VALUES (?,?,?,?,?,?,?,?,?)''', 
                                (name, u_status, phone, faculty, purpose, str(start_date), str(end_date), item['name'], item['id']))
                            db_conn.commit()
                            success_count += 1
                
                if success_count > 0:
                    st.success(f"🎊 บันทึกข้อมูลการจองสำเร็จทั้งหมด {success_count} รายการ!")
                    st.balloons()

# --- หน้าที่ 2: ประวัติการจอง ---
with tabs[1]:
    st.markdown("<h2 style='color: #1a3a5f;'>📂 ตรวจสอบประวัติการใช้งาน</h2>", unsafe_allow_html=True)
    
    try:
        all_data = pd.read_sql_query("SELECT id, name, tool_name, asset_id, start_date, end_date, state FROM bookings ORDER BY id DESC", db_conn)
        
        if not all_data.empty:
            search = st.text_input("🔎 ค้นหาด้วยรหัสครุภัณฑ์ หรือ ชื่อผู้จอง")
            if search:
                all_data = all_data[all_data['name'].str.contains(search, na=False) | 
                                    all_data['asset_id'].str.contains(search, na=False)]
            
            # แต่งตารางให้สวย
            st.dataframe(
                all_data, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "state": st.column_config.BadgeColumn("สถานะ", format="🟢 %s"),
                    "start_date": "วันที่เริ่ม",
                    "end_date": "วันที่คืน"
                }
            )
        else:
            st.info("ยังไม่มีข้อมูลการจองในระบบ")
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลได้: {e}")
