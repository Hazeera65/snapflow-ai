export default function Voice() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Voice Input</h1>
        <p className="text-gray-600 mt-2">Speak your queries</p>
      </div>

      <div className="card text-center py-12">
        <div className="text-4xl mb-4">🎤</div>
        <button className="btn-primary mt-4">Start Recording</button>
      </div>
    </div>
  )
}
