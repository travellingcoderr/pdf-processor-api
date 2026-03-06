import { useState, useCallback } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

const ACCEPT_RESUME = '.pdf,.docx'
const ACCEPT_MIME = 'application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document'
const ALLOWED_TYPES = new Set([
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
])

function isAllowedFile(file) {
  return file && (ALLOWED_TYPES.has(file.type) || /\.(pdf|docx)$/i.test(file.name))
}

function wrapFetchError(err, url) {
  if (err instanceof TypeError && err.message === 'Failed to fetch') {
    return new Error(
      `Network error: cannot reach API at ${url}. Check that the backend is running and VITE_API_URL (or /api proxy) is correct.`
    )
  }
  return err
}

async function uploadFile(file) {
  const url = `${API_BASE}/upload`
  let res
  try {
    const formData = new FormData()
    formData.append('file', file)
    res = await fetch(url, { method: 'POST', body: formData })
  } catch (err) {
    throw wrapFetchError(err, url)
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || res.statusText || `Upload failed (${res.status})`)
  }
  return res.json()
}

async function getFileStatus(id) {
  const url = `${API_BASE}/${id}`
  let res
  try {
    res = await fetch(url)
  } catch (err) {
    throw wrapFetchError(err, url)
  }
  if (!res.ok) throw new Error(`Failed to fetch status (${res.status})`)
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
    if (!isAllowedFile(f)) {
      setError('Please upload a PDF or Word (.docx) resume only.')
      return
    }
    setError(null)
    setLoading(true)
    setStatus(null)
    setFileId(null)
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

  const isRoasting = fileId && (!status || (status.status !== 'processed' && status.status !== 'failed'))

  const setFileIfAllowed = (f) => {
    if (!f) {
      setFile(null)
      setFileId(null)
      setStatus(null)
      setError(null)
      return
    }
    if (!isAllowedFile(f)) {
      setError('Only PDF or Word (.docx) resumes are accepted.')
      setFile(null)
      return
    }
    setError(null)
    setFile(f)
    setFileId(null)
    setStatus(null)
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDragover(false)
    const f = e.dataTransfer.files?.[0]
    setFileIfAllowed(f)
  }

  const onDragOver = (e) => {
    e.preventDefault()
    setDragover(true)
  }

  const onDragLeave = () => setDragover(false)

  return (
    <>
      <h1 className="app-title">
        Resume Roaster <span className="wink" aria-hidden>😉</span>
      </h1>
      <p className="subtitle">
        Drop your resume (PDF or Word). We’ll roast it.
      </p>

      <div
        className={`upload-zone ${dragover ? 'dragover' : ''}`}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
      >
        <input
          type="file"
          id="resume-input"
          accept={ACCEPT_MIME}
          onChange={(e) => setFileIfAllowed(e.target.files?.[0] ?? null)}
        />
        <label htmlFor="resume-input">
          {file ? file.name : 'Choose a resume or drop it here'}
        </label>
        <p className="upload-hint">PDF or Word (.docx) only. Word files are converted to PDF automatically.</p>
        <p style={{ marginTop: '1rem' }}>
          <button
            type="button"
            className="btn btn-primary"
            disabled={!file || loading}
            onClick={() => handleUpload()}
          >
            {loading ? 'Roasting…' : 'Roast my resume'}
          </button>
        </p>
      </div>

      {error && <p className="error">{error}</p>}

      {fileId && (
        <div className="result-card">
          <h3>Your roast</h3>
          <div className="file-id">{fileId}</div>
          {isRoasting ? (
            <div className="roasting-state" aria-live="polite">
              <div className="roasting-emoji" aria-hidden>
                <span className="roast-doc">📄</span>
                <span className="roast-arrow">→</span>
                <span className="roast-fire">🔥</span>
              </div>
              <p className="roasting-text">Your resume is in the oven…</p>
              <p className="roasting-sub">Our chefs are reading every line. No pressure.</p>
            </div>
          ) : status ? (
            <>
              <span className={`status ${status.status}`}>{status.status}</span>
              {status.result != null && (
                <div className="result-text">{status.result}</div>
              )}
            </>
          ) : null}
        </div>
      )}
    </>
  )
}
