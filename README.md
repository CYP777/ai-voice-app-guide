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
Backend (FastAPI)                            รับไฟล์เสียง —> เรียกใช้ AI Model
                                                        |
                                                ส่งผลลัพธ์กลับเป็นข้อความ
                                                        |
                                                Frontend แสดงผลลัพธ์
```
โปรเจกต์นี้เลือกใช้ FastAPI เป็น Backend ตัวเดียว 

### Tech Stack
---
| ส่วน | เทคโนโลยี |
| --- | --- |
| Frontend | React (vite) + JavaScript |
| Backend | FastAPI (Python) |
| อัดเสียง | MediaRecorder API (built-in browser) |
| รับไฟล์ | FastAPI |
| Deploy Frontend | Vercel |
| Deploy Backend | Render |

### Getting Started
---

#### สิ่งที่ต้องมีก่อน
* [Node.js] (https://nodejs.org/) (แนะนำใช้ v18 ขึ้นไป) — สำหรับรัน Frontend (Vite)
* [Python] (https://www.python.org/) (แนะนำใช้ 3.10 ขึ้นไป) — สำหรับรัน Backend (FastAPI)
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
   python -m venv venv
   source venv/bin/activate   # Windows ใช้ venv\Scripts\activate
   pip install fastapi uvicorn python-multipart python-dotenv
   ```
   > **อธิบายเพิ่ม**
   > - `fastapi` = framework สำหรับสร้างเซิร์ฟเวอร์
   > - `uvicorn` = ASGI server สำหรับรัน FastAPI
   > - `python-multipart` = จำเป็นสำหรับให้ FastAPI รับไฟล์ (เช่นไฟล์เสียง) ที่ส่งมาจาก Frontend
   > - `python-dotenv` = โหลดค่าลับ เช่น API Key จากไฟล์ .env

   สร้างไฟล์ `main.py` แล้ววางโค้ดนี้
   ```python
   from fastapi import FastAPI, UploadFile, File
   from fastapi.middleware.cors import CORSMiddleware
   from dotenv import load_dotenv
   import os
   
   load_dotenv()  # โหลดค่าจาก .env เข้ามาใช้ในโปรเจกต์
   
   app = FastAPI()
   
   # เปิดให้ Frontend เรียก API นี้ได้
   app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],  # ตอน production ควรระบุ origin ที่แน่นอน
      allow_methods=["*"],
      allow_headers=["*"],
   )
   
   # เส้นทางทดสอบ เข้าเว็บแล้วควรเห็นข้อความนี้
   @app.get("/")
   def read_root():
      return {"message": "Backend is running"}
   
   # เส้นทางหลัก: รับไฟล์เสียงจาก Frontend
   @app.post("/api/transcribe")
   async def transcribe(audio: UploadFile = File(...)):
      # TODO: ส่งไฟล์ไปให้ AI model แล้วส่งผลลัพธ์กลับ
      # หมายเหตุ: ปกติตรงนี้จะเรียกใช้ AI Speech-to-Text เช่น Whisper
      # แต่ในตัวอย่างนี้ยังไม่ได้เชื่อมต่อจริง เพื่อให้เห็นโครงสร้างของระบบก่อน
      return {"text": "placeholder result"}
   ```

   สร้างไฟล์ `.env.example` (ใส่ค่าที่จำเป็นเข้าไปที่นี่)
   ```bash
   PORT=8000
   MODEL_REPO_ID=your_model_repo_id_here
   MODEL_FILENAME=your_model_filename_here
   ```

   สร้างไฟล์ `.env` จาก `.env.example` แล้วใส่ค่าจริง
   ```bash
   cp .env.example .env
   ```

   รัน backend
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   เปิด Browser ไปที่ http://localhost:5000 (หรือ port ที่ตั้งค่าไว้ใน .env)

4. **สำคัญ**: ห้าม commit ไฟล์ `.env` ขึ้น GitHub เด็ดขาด เพราะจะทำให้ API Key หลุด
   > **ทำไมถึงห้าม?** ไฟล์ `.env` มี API Key ที่เป็นความลับอยู่ ถ้าใครเอา Key นี้ไปใช้ อาจทำให้เจ้าของ Key
   > ถูกเรียกเก็บเงินโดยไม่รู้ตัว หรือมีคนแอบใช้บริการในนามเรา วิธีป้องกันคือใส่ `.env` ไว้ในไฟล์ `.gitignore`
   > เพื่อให้ Git ข้ามไฟล์นี้ไปตอน commit เสมอ

   เช็คว่า setup สำเร็จ
   - Frontend รันที่ `http://localhost:5173` แล้วเห็นหน้าเว็บ
   - Backend รันที่ `http://localhost:8000` แล้วเห็นคำว่า `{ "message": "AI Voice App Backend is running!", "model_status": "loaded" }`
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