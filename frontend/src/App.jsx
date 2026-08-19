import { useState } from "react";
import "./App.css";

function App() {

  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [history, setHistory] = useState([]);
  const [activeRecordId, setActiveRecordId] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setAnalysis(null);
      setActiveRecordId(null);
      setError("");
    }
  };

  const handleSelectRecord = (record) => {
    setActiveRecordId(record.id);
    setAnalysis({
      ...record.analysis,
      ai_detection: record.ai_detection,
      manipulation_detection: record.manipulation_detection,
      forensic_assessment: record.forensic_assessment
    });
    setFile(null);
  };


  const analyzeMedia = async () => {

    if (!file) {

      setError("Please select an image first.");

      return;

    }

    setLoading(true);
    setError("");
    setAnalysis(null);


    const formData = new FormData();

    formData.append("file", file);


    try {

      const response = await fetch(
        "http://127.0.0.1:8000/upload",
        {
          method: "POST",
          body: formData
        }
      );


      if (!response.ok) {

        throw new Error(
          "Server returned an error."
        );

      }


      const data = await response.json();
      console.log("API RESPONSE:", data);

      if (data.analysis) {
        const record = {
          id: Date.now().toString(),
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          filename: data.analysis.filename,
          sizeBytes: data.analysis.size,
          analysis: data.analysis,
          ai_detection: data.ai_detection,
          manipulation_detection: data.manipulation_detection,
          forensic_assessment: data.forensic_assessment
        };

        setHistory(prev => [record, ...prev]);
        setActiveRecordId(record.id);

        setAnalysis({ 
          ...data.analysis, 
          ai_detection: data.ai_detection,
          manipulation_detection: data.manipulation_detection,
          forensic_assessment: data.forensic_assessment
        });

      } else {

        setError(
          data.error || "Analysis failed."
        );

      }

    }

    catch (error) {

      console.error(error);

      setError(
        "Could not connect to the forensic server."
      );

    }

    finally {

      setLoading(false);

    }

  };


  return (

    <div className="app">

      <div className="container">

        {/* HEADER */}

        <header>

          <h1>
            Media Forensics Dashboard
          </h1>

          <p className="subtitle">
            Detect • Analyze • Trace
          </p>

          <p className="description">
            Aggregated digital forensics command center. Upload media to evaluate authenticity indicators and localized tampering.
          </p>

        </header>


        {/* DASHBOARD LAYOUT */}
        <div className="dashboard-layout">
          
          {/* SIDEBAR PANEL */}
          <aside className="dashboard-sidebar">
            <div className="sidebar-header">
              <h3>Investigation Scans</h3>
              <span className="scans-count">{history.length} total</span>
            </div>
            {history.length === 0 ? (
              <div className="history-empty">
                <p>No scans in this session.</p>
                <span className="hint">Uploaded files will appear here for quick switching.</span>
              </div>
            ) : (
              <div className="history-list">
                {history.map((record) => {
                  const isFlagged = record.forensic_assessment.verdict === "Suspicious / Manipulated" || 
                                    record.forensic_assessment.verdict === "Likely AI-generated";
                  return (
                    <div 
                      key={record.id}
                      className={`history-item ${activeRecordId === record.id ? 'active' : ''} ${isFlagged ? 'flagged' : ''}`}
                      onClick={() => handleSelectRecord(record)}
                    >
                      <div className="history-item-header">
                        <span className="history-time">{record.timestamp}</span>
                        <span className={`history-status-tag ${isFlagged ? 'warning' : 'success'}`}>
                          {isFlagged ? 'FLAGGED' : 'CLEAN'}
                        </span>
                      </div>
                      <div className="history-filename" title={record.filename}>
                        {record.filename}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </aside>

          {/* MAIN DASHBOARD PANEL */}
          <main className="dashboard-main">
            {/* KPI STATS ROW */}
            {history.length > 0 && (
              <div className="kpi-grid">
                <div className="kpi-card">
                  <span className="kpi-label">Files Scanned</span>
                  <strong className="kpi-value">{history.length}</strong>
                </div>
                <div className="kpi-card warning">
                  <span className="kpi-label">Flagged Media</span>
                  <strong className="kpi-value">
                    {history.filter(r => r.forensic_assessment.verdict === "Suspicious / Manipulated" || r.forensic_assessment.verdict === "Likely AI-generated").length}
                  </strong>
                </div>
                <div className="kpi-card success">
                  <span className="kpi-label">Integrity Index</span>
                  <strong className="kpi-value">
                    {Math.round((history.reduce((acc, r) => acc + (1.0 - r.forensic_assessment.score), 0) / history.length) * 100)}%
                  </strong>
                </div>
              </div>
            )}

            {/* UPLOAD */}
            <section className="upload-section">
              <h2>Upload Media</h2>
              <p>Select an image to begin forensic analysis.</p>
              
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
              />

              {file && (
                <div className="selected-file">
                  Selected file: <strong>{file.name}</strong>
                </div>
              )}

              <button
                onClick={analyzeMedia}
                disabled={loading}
              >
                {loading ? "Analyzing..." : "Analyze Media"}
              </button>

              {error && (
                <div className="error">{error}</div>
              )}
            </section>

            {/* RESULTS */}
            {analysis && (
              <section className="results">
                <h2>Analysis Results</h2>
                
                <div className="workspace">
                  
                  {/* OVERVIEW */}
                  <div className="card">
                    <h3>Media Overview</h3>
                    <div className="overview-grid">
                      <div className="overview-item">
                        <span>Filename</span>
                        <strong>{analysis.filename}</strong>
                      </div>
                      <div className="overview-item">
                        <span>Format</span>
                        <strong>{analysis.format}</strong>
                      </div>
                      <div className="overview-item">
                        <span>Size</span>
                        <strong>{(analysis.size / 1024).toFixed(1)} KB</strong>
                      </div>
                      <div className="overview-item">
                        <span>Dimensions</span>
                        <strong>{analysis.width} x {analysis.height} px</strong>
                      </div>
                    </div>
                  </div>

                  {/* FORENSIC VERDICT REPORT */}
                  <div className="card verdict-card">
                    <h3>Forensic Verdict Report</h3>
                    
                    {analysis.forensic_assessment && (
                      <>
                        {/* Overall Verdict Banner */}
                        <div className={`verdict-banner ${analysis.forensic_assessment.verdict.toLowerCase().replace(/[^a-z0-9]/g, '-')}`}>
                          <div className="verdict-header">
                            <div className="verdict-badge">
                              <span className="verdict-label">Verdict Rating</span>
                              <strong className="verdict-value">{analysis.forensic_assessment.verdict}</strong>
                            </div>
                            <div className="verdict-confidence">
                              <span className="verdict-label">Confidence</span>
                              <strong className="verdict-value">{analysis.forensic_assessment.confidence}</strong>
                            </div>
                          </div>
                          {(() => {
                            const summaryText = analysis.forensic_assessment.summary_text;
                            const hasNote = summaryText.includes("Note:");
                            const [mainText, noteText] = hasNote ? summaryText.split("Note:") : [summaryText, ""];
                            return (
                              <p className="verdict-summary">
                                {mainText}
                                {hasNote && (
                                  <span className="verdict-note-highlight">
                                    <strong>Note:</strong> {noteText}
                                  </span>
                                )}
                              </p>
                            );
                          })()}
                        </div>

                        {/* SVG Integrity Gauge */}
                        {(() => {
                          const riskPercentage = Math.round(analysis.forensic_assessment.score * 100);
                          const strokeDashoffset = 251.2 - (251.2 * (100 - riskPercentage)) / 100;
                          
                          let gaugeColor = "#10b981"; // green
                          let riskLabel = "SECURE";
                          if (riskPercentage >= 70) {
                            gaugeColor = "#ef4444"; // red
                            riskLabel = "COMPROMISED";
                          } else if (riskPercentage >= 40) {
                            gaugeColor = "#f59e0b"; // amber
                            riskLabel = "SUSPICIOUS";
                          } else if (riskPercentage > 10) {
                            gaugeColor = "#3b82f6"; // blue
                            riskLabel = "LOW RISK";
                          }
                          
                          return (
                            <div className="gauge-wrapper">
                              <svg className="integrity-gauge" width="120" height="120" viewBox="0 0 100 100">
                                <circle 
                                  className="gauge-bg" 
                                  cx="50" 
                                  cy="50" 
                                  r="40" 
                                  stroke="#e2e8f0" 
                                  strokeWidth="8" 
                                  fill="transparent" 
                                />
                                <circle 
                                  className="gauge-fill" 
                                  cx="50" 
                                  cy="50" 
                                  r="40" 
                                  stroke={gaugeColor} 
                                  strokeWidth="8" 
                                  fill="transparent" 
                                  strokeDasharray="251.2" 
                                  strokeDashoffset={strokeDashoffset} 
                                  strokeLinecap="round" 
                                  transform="rotate(-90 50 50)" 
                                />
                                <text x="50" y="44" className="gauge-value" textAnchor="middle" fill="var(--text-h, #111)" fontWeight="bold" fontSize="14">
                                  {100 - riskPercentage}%
                                </text>
                                <text x="50" y="64" className="gauge-label" textAnchor="middle" fill={gaugeColor} fontWeight="bold" fontSize="9">
                                  {riskLabel}
                                </text>
                              </svg>
                              <div className="gauge-text-side">
                                <h4>Integrity Rating</h4>
                                <p>Aggregated confidence indicator. Higher ratings represent lower likelihood of AI generation, metadata tampering, or local splices.</p>
                              </div>
                            </div>
                          );
                        })()}

                        {/* Forensic Signals Breakdown */}
                        <div className="signals-breakdown">
                          <h4>Forensic Signal Analysis</h4>
                          
                          {/* 1. AI Generation Signal */}
                          <div className={`signal-row ${analysis.forensic_assessment.signals.ai_generation.status}`}>
                            <div className="signal-header">
                              <div className="signal-title-group">
                                <span className="signal-icon">🧠</span>
                                <strong>Neural Pattern Analysis</strong>
                              </div>
                              <span className={`signal-badge ${analysis.forensic_assessment.signals.ai_generation.status}`}>
                                {analysis.forensic_assessment.signals.ai_generation.status === 'success' ? 'PASSED' : 
                                 analysis.forensic_assessment.signals.ai_generation.status === 'warning' ? 'FLAGGED' : 'INFO'}
                              </span>
                            </div>
                            <p className="signal-details">
                              {analysis.forensic_assessment.signals.ai_generation.details}
                            </p>
                            <div className="progress-bar-bg small">
                              <div 
                                className="progress-bar-fill ai-fill" 
                                style={{ width: `${analysis.forensic_assessment.signals.ai_generation.score * 100}%` }}
                              ></div>
                            </div>
                          </div>

                          {/* 2. Metadata Integrity Signal */}
                          <div className={`signal-row ${analysis.forensic_assessment.signals.metadata_integrity.status}`}>
                            <div className="signal-header">
                              <div className="signal-title-group">
                                <span className="signal-icon">📋</span>
                                <strong>Metadata & EXIF Integrity</strong>
                              </div>
                              <span className={`signal-badge ${analysis.forensic_assessment.signals.metadata_integrity.status}`}>
                                {analysis.forensic_assessment.signals.metadata_integrity.status === 'success' ? 'PASSED' : 
                                 analysis.forensic_assessment.signals.metadata_integrity.status === 'warning' ? 'SUSPICIOUS' : 'INFO'}
                              </span>
                            </div>
                            <p className="signal-details">
                              {analysis.forensic_assessment.signals.metadata_integrity.details}
                            </p>
                          </div>

                          {/* 3. File Structure Signal */}
                          <div className={`signal-row ${analysis.forensic_assessment.signals.file_structure.status}`}>
                            <div className="signal-header">
                              <div className="signal-title-group">
                                <span className="signal-icon">🔍</span>
                                <strong>Header Signature Validation</strong>
                              </div>
                              <span className={`signal-badge ${analysis.forensic_assessment.signals.file_structure.status}`}>
                                {analysis.forensic_assessment.signals.file_structure.status === 'success' ? 'PASSED' : 'FLAGGED'}
                              </span>
                            </div>
                            <p className="signal-details">
                              {analysis.forensic_assessment.signals.file_structure.details}
                            </p>
                          </div>

                          {/* 4. Pixel Manipulation (ELA) Signal */}
                          {analysis.forensic_assessment.signals.pixel_manipulation && (
                            <div className={`signal-row ${analysis.forensic_assessment.signals.pixel_manipulation.status}`}>
                              <div className="signal-header">
                                <div className="signal-title-group">
                                  <span className="signal-icon">🔮</span>
                                  <strong>Error Level Analysis (ELA)</strong>
                                </div>
                                <span className={`signal-badge ${analysis.forensic_assessment.signals.pixel_manipulation.status}`}>
                                  {analysis.forensic_assessment.signals.pixel_manipulation.status === 'success' ? 'PASSED' : 
                                   analysis.forensic_assessment.signals.pixel_manipulation.status === 'warning' ? 'FLAGGED' : 'SUSPICIOUS'}
                                </span>
                              </div>
                              <p className="signal-details">
                                {analysis.forensic_assessment.signals.pixel_manipulation.details}
                              </p>
                            </div>
                          )}
                        </div>
                      </>
                    )}

                    {/* Forensic Disclaimer Callout */}
                    <div className="disclaimer-callout">
                      <div className="disclaimer-icon">💡</div>
                      <div className="disclaimer-text">
                        <strong>Forensic Disclaimer:</strong> This assessment aggregates multiple digital signals. AI classification and metadata checks are probabilistic. A clean report limits indicators of editing or AI generation but does not constitute absolute proof of authenticity.
                      </div>
                    </div>
                  </div>

                  {/* VISUAL TAMPERING ANALYSIS */}
                  {analysis.manipulation_detection && analysis.manipulation_detection.ela_filename && (
                    <div className="card ela-card-visual">
                      <h3>Visual Tampering Analysis (Error Level Analysis)</h3>
                      <p className="ela-intro">
                        Error Level Analysis (ELA) highlights differences in JPEG compression rates across the image. 
                        Authentic regions will show a uniform, dark distribution. Spliced elements or modified pixels 
                        typically show up as high-contrast glowing clusters.
                      </p>
                      
                      <div className="ela-comparison-grid">
                        <div className="ela-image-container">
                          <span className="image-label">Original Image</span>
                          <img 
                            src={`http://127.0.0.1:8000/uploads/${analysis.filename}`} 
                            alt="Original" 
                            className="forensic-image" 
                          />
                        </div>
                        <div className="ela-image-container">
                          <span className="image-label">ELA Heatmap</span>
                          <img 
                            src={`http://127.0.0.1:8000/uploads/${analysis.manipulation_detection.ela_filename}`} 
                            alt="Error Level Analysis" 
                            className="forensic-image ela-heatmap" 
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {/* METADATA */}
                  <div className="card">
                    <h3>Metadata</h3>
                    {Object.keys(analysis.metadata).length === 0 ? (
                      <p className="muted">No EXIF metadata was found in this image.</p>
                    ) : (
                      <div className="metadata">
                        {Object.entries(analysis.metadata).map(([key, value]) => (
                          <div className="metadata-row" key={key}>
                            <span>{key}</span>
                            <strong>{value}</strong>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                </div>
              </section>
            )}
          </main>

        </div>

      </div>

    </div>

  );

}


export default App;