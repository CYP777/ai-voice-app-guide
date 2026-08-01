import { useState, useRef } from 'react';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const apiUrl = import.meta.env.VITE_API_URL;

  // เริ่มอัดเสียง
  const startRecording = async () => {
    // ขอ permission ใช้ไมโครโฟน
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;
    chunksRef.current = [];

    // ทุกครั้งที่มีข้อมูลเสียงเข้ามา เก็บใส่ chunks
    mediaRecorder.ondataavailable = (e) => {
      chunksRef.current.push(e.data);
    };

    // เมื่อหยุดอัด รวม chunks เป็นไฟล์แล้วส่งไป backend
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
      await sendAudio(audioBlob);
      // ปิดไมค์หลังใช้เสร็จ
      stream.getTracks().forEach((track) => track.stop());
    };

    mediaRecorder.start();
    setIsRecording(true);
  };

  // หยุดอัดเสียง
  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setIsRecording(false);
  };

  // ส่งไฟล์เสียงไป backend
  const sendAudio = async (audioBlob) => {
    setLoading(true);
    setResult('');

    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    try {
      const response = await fetch(`${apiUrl}/api/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Request failed');

      const data = await response.json();
      setResult(data.text);
    } catch (err) {
      setResult('เกิดข้อผิดพลาด: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'kanit, sans-serif' }}>
      <h1>AI Voice to Text</h1>

      <button onClick={isRecording ? stopRecording : startRecording}>
        {isRecording ? '⏹ หยุดอัด' : '🎙 เริ่มอัดเสียง'}
      </button>

      {loading && <p>กำลังประมวลผล...</p>}

      {result && (
        <div style={{ marginTop: '1rem' }}>
          <strong>ผลลัพธ์:</strong>
          <p>{result}</p>
        </div>
      )}
    </div>
  );
}

export default App;