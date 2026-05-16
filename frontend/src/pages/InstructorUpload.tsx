import React, { useState } from 'react';
import { Upload, FileText, Send } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const InstructorUpload: React.FC = () => {
  const [title, setTitle] = useState('');
  const [rubric, setRubric] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !title || !rubric) return;
    
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('rubric', rubric);

    try {
      const response = await fetch(`http://localhost:8000/exams/upload?title=${encodeURIComponent(title)}&rubric=${encodeURIComponent(rubric)}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData 
      });

      if (response.ok) {
        alert("Exam uploaded successfully! AI pipeline started.");
        navigate('/ta'); 
      } else {
        const err = await response.json();
        alert(`Upload failed: ${err.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error("Upload error", error);
      alert("Connection error. Is the backend running?");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{maxWidth: '800px', margin: '50px auto', padding: '40px', background: '#2a2a2a', borderRadius: '12px'}}>
      <h1 style={{marginBottom: '30px', display: 'flex', alignItems: 'center', gap: '10px'}}>
        <Upload color="#3b82f6"/> Instructor Portal: Upload Exams
      </h1>

      <form onSubmit={handleUpload} style={{display: 'flex', flexDirection: 'column', gap: '20px'}}>
        <div>
          <label style={{display: 'block', marginBottom: '8px', fontWeight: 'bold'}}>Exam Title</label>
          <input 
            type="text" 
            placeholder="Midterm Biology 101"
            style={{width: '100%', padding: '12px', borderRadius: '6px', background: '#333', border: '1px solid #444', color: 'white'}}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div>
          <label style={{display: 'block', marginBottom: '8px', fontWeight: 'bold'}}>Grading Rubric (JSON)</label>
          <textarea 
            placeholder='[{"question": "Q1", "max_marks": 10, "criteria": "..."}]'
            style={{width: '100%', height: '150px', padding: '12px', borderRadius: '6px', background: '#333', border: '1px solid #444', color: 'white', fontFamily: 'monospace'}}
            value={rubric}
            onChange={(e) => setRubric(e.target.value)}
          />
        </div>

        <div style={{border: '2px dashed #444', padding: '40px', textAlign: 'center', borderRadius: '8px'}}>
          <input 
            type="file" 
            accept=".pdf" 
            id="file-upload" 
            style={{display: 'none'}} 
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <label htmlFor="file-upload" style={{cursor: 'pointer'}}>
            <FileText size={48} color="#888" style={{marginBottom: '10px'}}/>
            <p>{file ? file.name : 'Click to select bulk exam PDF'}</p>
          </label>
        </div>

        <button type="submit" disabled={uploading} className="button button-primary" style={{padding: '15px', fontSize: '1.1rem'}}>
          <Send size={18} style={{marginRight: 8}}/> {uploading ? 'Processing...' : 'Start Grading Pipeline'}
        </button>
      </form>
    </div>
  );
};

export default InstructorUpload;
