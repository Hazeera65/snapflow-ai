import { useState, useRef } from 'react'

export default function Documents() {
  const [files, setFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles = Array.from(e.target.files || [])
    setFiles([...files, ...newFiles])
  }

  const handleDragDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const droppedFiles = Array.from(e.dataTransfer.files)
    setFiles([...files, ...droppedFiles])
  }

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  const uploadFiles = async () => {
    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)
      
      try {
        const response = await fetch('/api/documents/upload', {
          method: 'POST',
          body: formData
        })
        
        if (response.ok) {
          console.log(`Uploaded ${file.name}`)
        }
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error)
      }
    }
    setFiles([])
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
        <p className="text-gray-600 mt-2">Upload and manage your documents</p>
      </div>

      {/* Upload Area */}
      <div
        className="card border-2 border-dashed border-gray-300 hover:border-snapflow-500 transition cursor-pointer"
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDragDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          accept=".pdf,.txt,.png,.jpg,.jpeg,.docx"
        />

        <div className="text-center py-12">
          <div className="text-4xl mb-4">📁</div>
          <h3 className="text-lg font-semibold text-gray-900">
            Drag and drop files here
          </h3>
          <p className="text-gray-600 mt-2">
            or click to select files
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Supported: PDF, TXT, DOC, PNG, JPG
          </p>
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-bold mb-4">Files to Upload ({files.length})</h3>
          <div className="space-y-2">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                <div className="flex items-center gap-3">
                  <span>📄</span>
                  <div>
                    <p className="font-medium">{file.name}</p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
          
          <div className="mt-4 flex gap-2">
            <button
              onClick={uploadFiles}
              className="btn-primary"
            >
              Upload {files.length} File{files.length !== 1 ? 's' : ''}
            </button>
            <button
              onClick={() => setFiles([])}
              className="btn-secondary"
            >
              Clear
            </button>
          </div>
        </div>
      )}

      {/* Demo Workspace */}
      <div className="card">
        <h3 className="text-lg font-bold mb-2">📚 Demo Workspace</h3>
        <p className="text-gray-600 mb-4">
          Load sample documents to see SnapFlow AI in action
        </p>
        <button className="btn-secondary">
          Load Demo Workspace
        </button>
      </div>
    </div>
  )
}
