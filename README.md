# Ai-Voice-App-Guide
 แอปพลิเคชันแปลงเสียงพูดเป็นข้อความด้วย AI (Speech-to-Text) บันทึกเสียงจาก Browser ส่งให้ AI ประมวลผลแล้วแสดงผลลัพธ์เป็นข้อความถอดเสียงแบบ Real-Time

### Process Demo
---
> (Add a Screenshot / DEMO (.gif))

### Architecture
---
```
Frontend (React + Vite)                     อัดเสียงด้วย MediaRecorderAPI
                                                        |
                                              ส่งไฟล์เสียงแบบ Multipart
                                                        |
Backend (Node.js + Express + Multer)                 รับไฟล์เสียง —> เรียกใช้ AI Model
                                                        |
                                                ส่งผลลัพธ์กลับเป็นข้อความ
                                                        |
                                                Frontend แสดงผลลัพธ์
```

### Tech Stack
---
| ส่วน | เทคโนโลยี |
| --- | --- |
| Frontend | React (vite) + JavaScript |
| Backend | Node.js + Express |
| อัดเสียง | MediaRecorder API (built-in browser) |
| รับไฟล์ | Multer |
| Deploy Frontend | Vercel |
| Deploy Backend | Render |

### Getting Started
---

#### สิ่งที่ต้องมีก่อน
* [Node.js] (https://nodejs.org/) (แนะนำใช้ v18 ขึ้นไป)
* Git
* Editor (แนะนำให้ใช้ VS Code)

#### ขั้นตอนติดตั้ง
1. สร้าง Repository สำหรับ Project แล้วทำการ Clone ลงไปที่เครื่องของตัวเอง
   ``` bash
   git clone https://github.com/[username]/[repo-name].git
   cd [repo-name]
   ```
2. ติดตั้ง Frontend (path /[repo-name])
   ``` bash
   npm create vite@latest [frontend-folder-name] -- --template react
   cd [frontend-folder-name]
   npm install # or npm i
   ```
   สร้างไฟล์ `.env` จาก `.env.example`
   ```bash
   cp .env.example .env
   ```

   รัน frontend

   ```bash
   npm run dev
   ```

   เปิด Browser ไปที่ http://localhost:5173 (หรือ port ที่ Vite แจ้ง)
3. ติดตั้ง Backend (path /[repo-name])
   ``` bash
   mkdir backend
   cd backend
   npm init -y # create package.json
   npm install express multer cors dotenv # install library
   npm install -D nodemon
   ```
   > **อธิบายเพิ่ม**
   > - `express` = framework สำหรับสร้างเซิร์ฟเวอร์
   > - `multer` = ตัวช่วยรับไฟล์ (เช่นไฟล์เสียง) ที่ส่งมาจาก Frontend
   > - `cors` = อนุญาตให้ Frontend (คนละ port/domain) เรียก Backend ได้
   > - `dotenv` = โหลดค่าลับ เช่น API Key จากไฟล์ `.env`
   > - `nodemon` = รัน server แล้ว auto-restart ทุกครั้งที่แก้โค้ด (ใช้ตอน dev เท่านั้น)

   เปิดไฟล์ `package.json` แล้วเพิ่ม script `dev`
   ```json
   "scripts": {
      "dev": "nodemon index.js"
   }
   ```
   สร้างไฟล์ `index.js` แล้ววางโค้ดนี้
   ```js
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
 
   const PORT = process.env.PORT || 5000;
   app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
   ```

   สร้างไฟล์ `.env.example` (ใส่ค่าที่จำเป็นเข้าไปที่นี่)
   ```bash
   PORT=5000
   API_KEY=your_ai_model_api_key_here
   ```

   สร้างไฟล์ `.env` จาก `.env.example` แล้วใส่ค่าจริง
   ```bash
   cp .env.example .env
   ```

   รัน backend
   ```bash
   npm run dev
   ```
   เปิด Browser ไปที่ http://localhost:5000 (หรือ port ที่ตั้งค่าไว้ใน .env)

4. **สำคัญ**: ห้าม commit ไฟล์ `.env` ขึ้น GitHub เด็ดขาด เพราะจะทำให้ API Key หลุด
   > **ทำไมถึงห้าม?** ไฟล์ `.env` มี API Key ที่เป็นความลับอยู่ ถ้าใครเอา Key นี้ไปใช้ อาจทำให้เจ้าของ Key
   > ถูกเรียกเก็บเงินโดยไม่รู้ตัว หรือมีคนแอบใช้บริการในนามเรา วิธีป้องกันคือใส่ `.env` ไว้ในไฟล์ `.gitignore`
   > เพื่อให้ Git ข้ามไฟล์นี้ไปตอน commit เสมอ

   เช็คว่า setup สำเร็จ
   - Frontend รันที่ `http://localhost:5173` แล้วเห็นหน้าเว็บ
   - Backend รันที่ `http://localhost:5000` แล้วเห็นคำว่า `Backend is running`
   - ทั้งสอง terminal รันพร้อมกันได้โดยไม่มี error

#### คู่มือแบบละเอียด
อยากเข้าใจทีละขั้นตอน อ่านต่อได้ที่ [`docs/`](./docs)
1. [Setup เบื้องต้น](./docs/01-setup.md)
2. [ทำความเข้าใจ Frontend](./docs/02-frontend.md)
3. [ทำความเข้าใจ Backend](./docs/03-backend.md)
4. [วิธี Deploy ขึ้นจริง](./docs/04-deploy.md)

### Environment Variables
---
ดูตัวอย่างที่ `.env.example` ในแต่ละโฟลเดอร์ **ห้าม commit ไฟล์ `.env` จริงขึ้น GitHub เด็ดขาด**

| ตัวแปร | คำอธิบาย |
|---|---|
| `API_KEY` | Key สำหรับเรียกใช้ AI Model |
| `PORT` | พอร์ตที่ backend รัน |

### Roadmap
* [x] อัดเสียงและส่งไฟล์ได้
* [x] เชื่อมต่อ AI Model แปลงเสียงเป็นข้อความ
* [ ] เพิ่มระบบ Login
* [ ] เก็บ History การแปลง (ต้องมี Database)