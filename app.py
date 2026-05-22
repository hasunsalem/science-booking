/* เอฟเฟกต์สำหรับชื่อระบบ */
.animated-title {
    position: relative;
    z-index: 10;
    font-size: 3rem;
    font-weight: 900;
    /* ไล่เฉดสีทอง-น้ำตาลเข้ม */
    background: linear-gradient(90deg, #b45309, #f59e0b, #d97706, #b45309);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    /* แอนิเมชันแสงวิ่งผ่าน และ ลอยขึ้นลง */
    animation: shine 5s linear infinite, floatTitle 4s ease-in-out infinite;
    margin-bottom: 8px;
    display: inline-block;
    filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.1));
}

/* แสงวิ่งผ่านตัวอักษร */
@keyframes shine {
    to { background-position: 200% center; }
}

/* ลอยขึ้นลงอย่างนุ่มนวล */
@keyframes floatTitle {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-12px); }
}

/* เพิ่มเอฟเฟกต์ตัวอักษรของหลักสูตรให้ดูเด่นขึ้น */
.sub-title-style {
    position: relative;
    z-index: 10;
    color: #92400e;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 1px;
    opacity: 0.9;
}
