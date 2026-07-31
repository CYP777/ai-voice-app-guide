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
   cp .env.example .env
   npm run dev
   ```
3. ติดตั้ง Backend (path /[repo-name])
   ``` bash
   mkdir backend
   cd backend
   npm init -y # create package.json
   npm install express multer cors dotenv # install library
   npm install -D nodemon
   cp .env.example .env
   npm run dev
   ```
4. เปิด Browser ไปที่ http://localhost:5173 (หรือ port ที่ Vite แจ้ง)

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
