import { useState } from 'react'

export default function Assistant() {
  const [messages, setMessages] = useState<{role: string, content: string}[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    setMessages([...messages, { role: 'user', content: input }])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input })
      })
      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer }])
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 flex flex-col h-full">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Assistant</h1>
        <p className="text-gray-600 mt-2">Ask questions about your documents</p>
      </div>

      <div className="flex-1 card overflow-y-auto space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-center">
            <div>
              <div className="text-4xl mb-2">💬</div>
              <p className="text-gray-600">Start by asking a question about your documents</p>
            </div>
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-snapflow-100 ml-8' : 'bg-gray-100 mr-8'}`}
          >
            <p className="font-semibold text-sm mb-1">
              {msg.role === 'user' ? 'You' : 'SnapFlow'}
            </p>
            <p className="text-gray-900">{msg.content}</p>
          </div>
        ))}
        
        {loading && (
          <div className="flex gap-2 items-center">
            <div className="animate-pulse">⏳</div>
            <p className="text-gray-600">Thinking...</p>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-snapflow-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="btn-primary"
        >
          Send
        </button>
      </form>
    </div>
  )
}
