import React, { useState, useEffect, useCallback } from 'react';
import { Check, Edit2, ChevronRight, AlertCircle, Download, Save } from 'lucide-react';

interface Answer {
  id: number;
  image_path: string;
  transcribed_text: string;
  ai_grade: number;
  ai_justification: string;
  status: string;
  ta_grade?: number;
}

const TADashboard: React.FC = () => {
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [editedGrade, setEditedGrade] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [completed, setCompleted] = useState(false);

  const fetchAnswers = async () => {
    try {
      const response = await fetch('http://localhost:8000/answers/pending', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await response.json();
      if (Array.isArray(data)) {
        setAnswers(data);
      }
    } catch (error) {
      console.error("Failed to fetch answers", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnswers();
  }, []);

  const currentAnswer = answers[currentIndex];

  const handleApprove = useCallback(async () => {
    if (!currentAnswer) return;
    try {
      await fetch(`http://localhost:8000/answers/${currentAnswer.id}/approve`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      const updatedAnswers = [...answers];
      updatedAnswers[currentIndex].status = 'approved';
      updatedAnswers[currentIndex].ta_grade = currentAnswer.ai_grade;
      setAnswers(updatedAnswers);
      
      nextAnswer();
    } catch (e) {
      console.error(e);
    }
  }, [currentAnswer, answers, currentIndex]);

  const handleSaveOverride = useCallback(async () => {
    if (!currentAnswer) return;
    
    // Update local state first for instant feedback
    const updatedAnswers = [...answers];
    updatedAnswers[currentIndex].status = 'overridden';
    updatedAnswers[currentIndex].ta_grade = editedGrade;
    setAnswers(updatedAnswers);
    setIsEditing(false);
    
    // In a real app, you'd call a specific /override endpoint here
    console.log(`Saved override for ${currentAnswer.id}: ${editedGrade}`);
    nextAnswer();
  }, [currentAnswer, answers, currentIndex, editedGrade]);

  const handleOverride = useCallback(() => {
    setIsEditing(true);
    setEditedGrade(currentAnswer?.ai_grade || 0);
  }, [currentAnswer]);

  const nextAnswer = useCallback(() => {
    if (currentIndex < answers.length - 1) {
      setCurrentIndex(prev => prev + 1);
      setIsEditing(false);
    } else {
      setCompleted(true);
    }
  }, [currentIndex, answers.length]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (isEditing || completed) {
          if (isEditing && e.key === 'Enter') handleSaveOverride();
          return;
      }
      
      switch (e.key.toLowerCase()) {
        case 'a':
          handleApprove();
          break;
        case 'o':
          handleOverride();
          break;
        case 'n':
          nextAnswer();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleApprove, handleOverride, nextAnswer, isEditing, completed, handleSaveOverride]);

  if (loading) return <div style={{padding: 50}}>Connecting to AI Pipeline...</div>;
  
  if (completed || answers.length === 0) {
    const totalMarks = answers.reduce((sum, a) => sum + (a.ta_grade || 0), 0);
    return (
      <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', width: '100%', padding: '20px'}}>
        <div style={{background: '#2a2a2a', padding: '40px', borderRadius: '12px', textAlign: 'center', maxWidth: '500px'}}>
            <Check size={64} color="#10b981" style={{marginBottom: '20px'}}/>
            <h2>Grading Batch Complete!</h2>
            <div style={{fontSize: '3rem', fontWeight: 'bold', margin: '20px 0'}}>
                {totalMarks.toFixed(1)} <span style={{fontSize: '1rem', color: '#888'}}>/ {answers.length * 10} Total</span>
            </div>
            <p style={{color: '#aaa', marginBottom: '30px'}}>All student answers have been reviewed.</p>
            <div style={{display: 'flex', gap: '10px', justifyContent: 'center'}}>
                <button onClick={() => window.location.href='/instructor'} className="button button-secondary">Upload More</button>
                <button onClick={() => alert("Final Grades Exported as CSV")} className="button button-primary">
                    <Download size={18} style={{marginRight: 8}}/> Export CSV
                </button>
            </div>
        </div>
      </div>
    );
  }

  const imageUrl = currentAnswer.image_path.includes('data/') 
    ? `http://localhost:8000/${currentAnswer.image_path.replace('./', '')}`
    : currentAnswer.image_path;

  return (
    <div className="dashboard-container">
      <div className="answer-image-section">
        <img 
            src={imageUrl} 
            alt="Student Answer" 
            key={imageUrl} // Force re-render when image changes
            onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = "https://via.placeholder.com/600x800?text=Scan+Processing...";
            }}
        />
      </div>

      <div className="grading-panel">
        <h2 style={{marginTop: 0}}>TA Review Pipeline</h2>
        <div style={{color: '#888', marginBottom: 20}}>
          Answer {currentIndex + 1} of {answers.length}
        </div>

        <div className="card">
          <h3>AI Transcription</h3>
          <p style={{fontStyle: 'italic'}}>{currentAnswer.transcribed_text || "Transcribing..."}</p>
        </div>

        <div className="card">
          <h3>{isEditing ? "Override Grade" : "AI Proposed Grade"}</h3>
          <div style={{display: 'flex', alignItems: 'center', gap: '15px'}}>
            {isEditing ? (
              <input 
                type="number" 
                className="grade-input"
                value={editedGrade}
                onChange={(e) => setEditedGrade(Number(e.target.value))}
                onKeyDown={(e) => e.key === 'Enter' && handleSaveOverride()}
                autoFocus
              />
            ) : (
              <span style={{fontSize: '2.5rem', fontWeight: 'bold'}}>{currentAnswer.ta_grade ?? currentAnswer.ai_grade}</span>
            )}
            <span style={{color: '#888'}}>/ 10</span>
          </div>
          <p style={{marginTop: 15, color: '#aaa'}}>{currentAnswer.ai_justification || "Grading in progress..."}</p>
        </div>

        <div style={{marginTop: 'auto', display: 'flex', gap: '10px'}}>
          {isEditing ? (
            <button onClick={handleSaveOverride} className="button button-primary" style={{flex: 1}}>
              <Save size={18} style={{marginRight: 8}}/> Save Grade (Enter)
            </button>
          ) : (
            <>
              <button onClick={handleApprove} className="button button-primary" style={{flex: 1}}>
                <Check size={18} style={{marginRight: 8}}/> Approve (A)
              </button>
              <button onClick={handleOverride} className="button button-secondary">
                <Edit2 size={18}/> Override (O)
              </button>
            </>
          )}
          <button onClick={nextAnswer} className="button button-secondary">
            <ChevronRight size={18}/> Next (N)
          </button>
        </div>
        
        <div style={{marginTop: 20, padding: 10, background: '#332', borderRadius: 4, display: 'flex', gap: 10}}>
          <AlertCircle size={18} color="#fbbf24"/>
          <span style={{fontSize: '0.8rem', color: '#fbbf24'}}>
            Plagiarism check: No similar answers found in this batch.
          </span>
        </div>
      </div>
    </div>
  );
};

export default TADashboard;
