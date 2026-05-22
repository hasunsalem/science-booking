import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & UI DESIGN (ห้ามแก้ไขตัวเลขในนี้หากไม่ชำนาญ) ---
st.set_page_config(page_title="Chem Booking - วท.บ.เคมี", layout="wide")

# ส่วนนี้คือ CSS ต้องอยู่ในเครื่องหมายคำพูด 3 อันเสมอ
st.markdown("""
<style>
    .stApp { background-color: #fcfdfe !important; }
    
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

    /* นักวิทยาศาสตร์น้อย */
    .mascot {
        position: absolute;
        bottom: 15px;
        right: 40px;
        font-size: 85px;
        z-index: 5;
        animation: mascotFloat 4s ease-in-out infinite;
    }

    /* ลายน้ำโมเลกุลในกล่อง */
    .inner-molecule {
        position: absolute;
        color: rgba(217, 119, 6, 0.12);
        font-family: 'Courier New', monospace;
        z-index: 1;
        animation: innerFloat 12s infinite ease-in-out;
    }

    @keyframes shine { to { background-position: 200% center; } }
    @keyframes floatTitle { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-12px); } }
    @keyframes mascotFloat { 0%, 100% { transform: translateY(0) rotate(0deg); } 50% { transform: translateY(-20px) rotate(8deg); } }
    @keyframes innerFloat { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(30px, -20px); } }

    /* กล่องข้อมูลส่วนที่ 1 และ 2 */
    .section-container { border-radius: 22px; overflow: hidden; margin-bottom: 25px; border: 1px solid #fde68a; }
    .header-box { background: #d97706; color: white; padding: 15px 25px; font-weight: bold; }
    .body-box { background: #fffbeb; padding: 25px; }
</style>
""", unsafe_allow_html=True)

# --- 2. MAIN PAGE ---
st.markdown("""
<div class="glass-header">
    <div class="mascot">🧑‍🔬</div>
    <div class="inner-molecule" style="top:10%; left:5%; font-size:30px;">C₂H₅OH</div>
    <div class="inner-molecule" style="top:60%; left:80%; font-size:25px;">H₂SO₄</div>
    
    <div class="animated-title">ระบบขอใช้เครื่องมือวิทยาศาสตร์</div>
    <div style="position: relative; z-index: 10; color: #92400e; font-size: 1.3rem; font-weight: 700;">
        หลักสูตร วท.บ. สาขาวิชาเคมี
    </div>
</div>
""", unsafe_allow_html=True)

# ส่วนของเนื้อหาแอป (Tabs)
tab1, tab2 = st.tabs(["✍️ ลงทะเบียนจอง", "🔍 ตรวจสอบสถานะ"])

with tab1:
    st.info("กรอกข้อมูลการจองด้านล่างนี้")
    # ใส่ฟอร์มของคุณตรงนี้...

with tab2:
    st.write("ตรวจสอบสถานะที่นี่")
