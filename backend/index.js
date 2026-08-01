    require('dotenv').config(); // โหลดค่าจาก .env เข้ามาใช้ในโปรเจกต์
    const express = require('express');
    const cors = require('cors');
    const multer = require('multer');
    
    const app = express();
    const upload = multer({ limits: { fileSize: 10 * 1024 * 1024 } }); // จำกัดไฟล์ไม่เกิน 10MB
    
    app.use(cors()); // เปิดให้ Frontend เรียก API นี้ได้
    
    // เส้นทางทดสอบ เข้าเว็บแล้วควรเห็นข้อความนี้
    app.get('/', (req, res) => res.send('Backend is running'));
    
    // เส้นทางหลัก: รับไฟล์เสียงจาก Frontend (field ชื่อ 'audio')
    app.post('/api/transcribe', upload.single('audio'), (req, res) => {
        // TODO: ส่งไฟล์ไปให้ AI model แล้วส่งผลลัพธ์กลับ
        // หมายเหตุ: ปกติตรงนี้จะเรียกใช้ AI Speech-to-Text เช่น OpenAI Whisper API
        // แต่ในตัวอย่างนี้ยังไม่ได้เชื่อมต่อจริง เพื่อให้เห็นโครงสร้างของระบบก่อน
        res.json({ text: 'placeholder result' });
    });
    
    const PORT = process.env.PORT;
    app.listen(PORT, () => console.log(`Server running on port ${PORT}`));