import { useState, useCallback } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || res.statusText || 'Upload failed')
  }
  return res.json()
}

async function getFileStatus(id) {
  const res = await fetch(`${API_BASE}/${id}`)
  if (!res.ok) throw new Error('Failed to fetch status')
  return res.json()
}

export default function App() {
  const [file, setFile] = useState(null)
  const [fileId, setFileId] = useState(null)
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragover, setDragover] = useState(false)

  const pollStatus = useCallback(async (id) => {
    const data = await getFileStatus(id)
    setStatus(data)
    if (data.status !== 'processed' && data.status !== 'failed') {
      setTimeout(() => pollStatus(id), 1500)
    }
  }, [])

  const handleUpload = async (e) => {
    const f = e?.target?.files?.[0] ?? file
    if (!f) return
    setError(null)
    setLoading(true)
    setStatus(null)
    try {
      const { file_id } = await uploadFile(f)
      setFileId(file_id)
      pollStatus(file_id)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragover(false)
    const f = e.dataTransfer.files?.[0]
    if (f?.type === 'application/pdf') {
      setFile(f)
      setFileId(null)
      setStatus(null)
    }
  }

  const onDragOver = (e) => {
    e.preventDefault()
    setDragover(true)
  }

  const onDragLeave = () => setDragover(false)

  return (
    <>
      <h1>PDF Processor</h1>
      <p className="subtitle">Upload a PDF to process it with the backend API.</p>

      <div
        className={`upload-zone ${dragover ? 'dragover' : ''}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
      >
        <input
          type="file"
          id="pdf-input"
          accept="application/pdf"
          onChange={(e) => {
            setFile(e.target.files?.[0] ?? null)
            setFileId(null)
            setStatus(null)
          }}
        />
        <label htmlFor="pdf-input">
          {file ? file.name : 'Choose a PDF or drop it here'}
        </label>
        <p>Only PDF files are accepted.</p>
        <p style={{ marginTop: '1rem' }}>
          <button
            type="button"
            className="btn btn-primary"
            disabled={!file || loading}
            onClick={() => handleUpload()}
          >
            {loading ? 'Uploading…' : 'Upload & process'}
          </button>
        </p>
      </div>

      {error && <p className="error">{error}</p>}

      {fileId && (
        <div className="result-card">
          <h3>File</h3>
          <div className="file-id">{fileId}</div>
          {status ? (
            <>
              <span className={`status ${status.status}`}>{status.status}</span>
              {status.result != null && (
                <div className="result-text">{status.result}</div>
              )}
            </>
          ) : (
            <p className="loading">Loading status…</p>
          )}
        </div>
      )}
    </>
  )
}
