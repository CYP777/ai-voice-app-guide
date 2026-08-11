import { useState, useRef, useEffect } from 'react';
import './App.css'; // นำเข้าไฟล์ CSS ที่เราแยกไว้

export default function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [text, setText] = useState('');
    
  const wsRef = useRef(null);
  const mediaRecorderRef = useRef(null);

  // 1. ตั้งค่าและเชื่อมต่อ WebSocket เมื่อเปิดหน้าเว็บ
  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL;
    wsRef.current = new WebSocket(wsUrl);
    wsRef.current.onopen = () => console.log('WebSocket Connected');
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.text) {
        setText(data.text);
        speakThai(data.text);
      }
    };
    wsRef.current.onclose = () => console.log('WebSocket Disconnected');

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // 2. ฟังก์ชันอ่านออกเสียง
  const speakThai = (textToSpeak) => {
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.lang = 'th-TH';
    utterance.rate = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  // 3. ฟังก์ชันจัดการปุ่มอัดเสียง
  // 3. ฟังก์ชันจัดการปุ่มอัดเสียง
  const toggleRecording = async () => {
    if (isRecording) {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop();
      }
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const options = { mimeType: 'audio/mp4' }; 
        const mediaRecorder = new MediaRecorder(stream, options);
        mediaRecorderRef.current = mediaRecorder;
        
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send("CLEAR");
        }

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(event.data);
          }
        };
        mediaRecorder.start(1000);
        setIsRecording(true);
        setText('กำลังฟัง...');
      } catch (err) {
        console.error("Error accessing microphone:", err);
        alert("กรุณาอนุญาตการใช้งานไมโครโฟนในเบราว์เซอร์");
      }
    }
  };

  return (
    <div className="app-container">
      <h2 className="header-title">AI Voice Interface</h2>
      <p className="subtitle">Real-time speech to text processing</p>
      <div className="controls-wrapper">
        <button 
          onClick={toggleRecording}
          className={`record-button ${isRecording ? 'recording' : 'idle'}`}
        >
        {isRecording ? 'หยุดอัดเสียง' : 'เริ่มการบันทึกเสียง'}
        </button>
      </div>
          
      <div className="result-container">
        <span className="result-label">Transcription Result</span>
        <p className="result-text">
          {text || ''}
        </p>
      </div>
    </div>
  );
}