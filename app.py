import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- การตั้งค่าฐานข้อมูล ---
def init_db():
    conn = sqlite3.connect('science_booking_v2.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, status TEXT, phone TEXT, course TEXT, 
            faculty TEXT, supervisor TEXT, purpose TEXT, 
            location TEXT, start_date DATE, end_date DATE, 
            tool_name TEXT, asset_id TEXT, booking_status TEXT DEFAULT 'Active'
        )
    ''')
    conn.commit()
    conn.close()

def check_overlap(asset_id, start_date, end_date):
    conn = sqlite3.connect('science_booking_v2.db')
    c = conn.cursor()
    c.execute('''
        SELECT * FROM bookings 
        WHERE asset_id = ? 
        AND booking_status = 'Active'
        AND (? <= end_date AND ? >= start_date)
    ''', (asset_id, str(start_date), str(end_date)))
    result = c.fetchone()
    conn.close()
    return result

# --- ฟังก์ชันหลักของระบบ ---
def main():
    st.set_page_config(page_title="ระบบจัดการเครื่องมือวิทยาศาสตร์", layout="wide")
    init_db()

    # Sidebar สำหรับการเปลี่ยนหน้า
    menu = ["หน้าจองเครื่องมือ", "เจ้าหน้าที่ (Login)"]
    choice = st.sidebar.selectbox("เมนูหลัก", menu)

    # --- หน้าจองเครื่องมือ (สำหรับบุคคลทั่วไป) ---
    if choice == "หน้าจองเครื่องมือ":
        st.title("🧪 ระบบจองเครื่องมือวิทยาศาสตร์")
        
        with st.form("booking_form"):
            st.subheader("ส่วนที่ 1: รายละเอียดผู้จอง")
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("ชื่อ - นามสกุล")
                status = st.selectbox("สถานะ", ["อาจารย์", "เจ้าหน้าที่", "นักศึกษา"])
                phone = st.text_input("เบอร์โทรศัพท์")
            with col2:
                course = st.text_input("หลักสูตรวิชา")
                faculty = st.text_input("สังกัด/คณะ")
                supervisor = st.text_input("อาจารย์ผู้ควบคุม")
            
            purpose = st.radio("วัตถุประสงค์", ["งานวิจัย", "การเรียนการสอน", "อื่นๆ"], horizontal=True)
            location = st.text_input("สถานที่นำไปใช้")
            
            col3, col4 = st.columns(2)
            with col3:
                start_date = st.date_input("ตั้งแต่วันที่", min_value=datetime.today())
            with col4:
                end_date = st.date_input("ถึงวันที่", min_value=start_date)

            st.divider()
            st.subheader("ส่วนที่ 2: รายละเอียดเครื่องมือ")
            tool_name = st.text_input("ชื่อเครื่องมือวิทยาศาสตร์")
            asset_id = st.text_input("รหัสครุภัณฑ์")

            submit = st.form_submit_button("ยืนยันการจอง")
            
            if submit:
                if not name or not asset_id:
                    st.error("กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน")
                else:
                    overlap = check_overlap(asset_id, start_date, end_date)
                    if overlap:
                        st.error(f"❌ ไม่สามารถจองได้: รหัส {asset_id} มีการจองแล้ว ({overlap[9]} ถึง {overlap[10]})")
                    else:
                        conn = sqlite3.connect('science_booking_v2.db')
                        c = conn.cursor()
                        c.execute('''INSERT INTO bookings (name, status, phone, course, faculty, supervisor, purpose, location, start_date, end_date, tool_name, asset_id) 
                                     VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', 
                                  (name, status, phone, course, faculty, supervisor, purpose, location, str(start_date), str(end_date), tool_name, asset_id))
                        conn.commit()
                        conn.close()
                        st.success("✅ บันทึกการจองสำเร็จ!")

    # --- หน้าเจ้าหน้าที่ (Admin Dashboard) ---
    elif choice == "เจ้าหน้าที่ (Login)":
        st.title("🔐 ส่วนสำหรับเจ้าหน้าที่")
        
        # ระบบ Login แบบง่าย
        if 'logged_in' not in st.session_state:
            st.session_state['logged_in'] = False

        if not st.session_state['logged_in']:
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                if user == "admin" and password == "1234": # สามารถเปลี่ยนรหัสตรงนี้ได้
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        else:
            if st.sidebar.button("Logout"):
                st.session_state['logged_in'] = False
                st.rerun()

            st.subheader("📋 รายการจองทั้งหมด")
            conn = sqlite3.connect('science_booking_v2.db')
            df = pd.read_sql_query("SELECT * FROM bookings", conn)
            st.dataframe(df, use_container_width=True)

            st.divider()
            st.subheader("🚫 ยกเลิกการจอง")
            booking_id = st.number_input("ระบุ ID ของรายการที่ต้องการยกเลิก", min_value=1, step=1)
            if st.button("ยกเลิกรายการนี้"):
                c = conn.cursor()
                c.execute("UPDATE bookings SET booking_status = 'Cancelled' WHERE id = ?", (booking_id,))
                conn.commit()
                st.warning(f"ยกเลิกรายการจอง ID: {booking_id} เรียบร้อยแล้ว")
                st.rerun()
            conn.close()

if __name__ == "__main__":
    main()
