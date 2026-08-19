import { useState } from "react";
import "./App.css";

function App() {

  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {

    const selectedFile = event.target.files[0];

    if (selectedFile) {

      setFile(selectedFile);
      setAnalysis(null);
      setError("");

    }

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

        setAnalysis({ ...data.analysis, ai_detection: data.ai_detection });

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
            Media Forensics
          </h1>

          <p className="subtitle">
            Detect • Analyze • Trace
          </p>

          <p className="description">
            Analyze digital media for forensic
            evidence and authenticity indicators.
          </p>

        </header>


        {/* UPLOAD */}

        <section className="upload-section">

          <h2>
            Upload Media
          </h2>

          <p>
            Select an image to begin forensic analysis.
          </p>


          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
          />


          {file && (

            <div className="selected-file">

              Selected file:

              <strong>
                {file.name}
              </strong>

            </div>

          )}


          <button
            onClick={analyzeMedia}
            disabled={loading}
          >

            {loading
              ? "Analyzing..."
              : "Analyze Media"}

          </button>


          {error && (

            <div className="error">
              {error}
            </div>

          )}

        </section>


        {/* RESULTS */}

        {analysis && (

          <section className="results">

            <h2>
              Forensic Analysis
            </h2>


            {/* FILE INFORMATION */}

            <div className="card">

              <h3>
                File Information
              </h3>


              <div className="grid">

                <div>
                  <span>Filename</span>
                  <strong>
                    {analysis.filename}
                  </strong>
                </div>


                <div>
                  <span>Format</span>
                  <strong>
                    {analysis.format}
                  </strong>
                </div>


                <div>
                  <span>Resolution</span>
                  <strong>
                    {analysis.width} × {analysis.height}
                  </strong>
                </div>


                <div>
                  <span>Color Mode</span>
                  <strong>
                    {analysis.mode}
                  </strong>
                </div>


                <div>
                  <span>File Size</span>
                  <strong>
                    {(
                      analysis.file_size_bytes /
                      1024 /
                      1024
                    ).toFixed(2)} MB
                  </strong>
                </div>

              </div>

            </div>


            {/* FILE INTEGRITY */}

            <div className="card">

              <h3>
                File Integrity
              </h3>

              <div className="hash">

                <span>
                  SHA-256
                </span>

                <code>
                  {analysis.sha256 || "Not available"}
                </code>

              </div>


              <div className="hash">

                <span>
                  Perceptual Hash
                </span>

                <code>
                  {analysis.perceptual_hash || "Not available"}
                </code>

              </div>

            </div>
            {/* AI GENERATION ANALYSIS */}

            <div className="card">

              <h3>
                AI Generation Analysis
              </h3>

              <div className="ai-result">

                <div className="ai-score">

                  <span>
                    AI-generated probability
                  </span>

                  <strong>
                    {analysis.ai_detection
                      ? `${(analysis.ai_detection.ai_probability * 100).toFixed(2)}%`
                      : "Not available"}
                  </strong>

                </div>


                <div className="ai-score">

                  <span>
                    Human-created probability
                  </span>

                  <strong>
                    {analysis.ai_detection
                      ? `${(analysis.ai_detection.human_probability * 100).toFixed(2)}%`
                      : "Not available"}
                  </strong>

                </div>

              </div>

            </div>


            {/* METADATA */}

            <div className="card">

              <h3>
                Metadata
              </h3>


              {Object.keys(
                analysis.metadata
              ).length === 0 ? (

                <p className="muted">
                  No EXIF metadata was found
                  in this image.
                </p>

              ) : (

                <div className="metadata">

                  {Object.entries(
                    analysis.metadata
                  ).map(
                    ([key, value]) => (

                      <div
                        className="metadata-row"
                        key={key}
                      >

                        <span>
                          {key}
                        </span>

                        <strong>
                          {value}
                        </strong>

                      </div>

                    )
                  )}

                </div>

              )}

            </div>

          </section>

        )}

      </div>

    </div>

  );

}


export default App;