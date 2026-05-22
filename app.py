/* ลายน้ำในกล่อง: ปรับให้ดูเป็นละอองจางๆ */
.inner-molecule {
    position: absolute;
    color: rgba(217, 119, 6, 0.15); /* สีส้มทองจางๆ 15% */
    font-family: 'Courier New', monospace;
    font-weight: bold;
    z-index: 1; /* อยู่หลังข้อความหลัก */
    pointer-events: none;
    animation: innerFloat 12s infinite ease-in-out;
}

/* ชื่อระบบ: เน้นความหนาและเงาให้ดูเป็น 3D */
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
    filter: drop-shadow(0px 4px 4px rgba(0,0,0,0.1)); /* เพิ่มเงาให้นูนขึ้น */
    margin-bottom: 5px;
}

/* ชื่อหลักสูตร: ปรับให้ดูเป็นระเบียบ */
.sub-title {
    position: relative;
    z-index: 10;
    color: #92400e;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: 0.5px;
    opacity: 0.85;
}
