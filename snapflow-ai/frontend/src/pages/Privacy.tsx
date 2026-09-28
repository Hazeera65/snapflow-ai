export default function Privacy() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Privacy & Data</h1>
        <p className="text-gray-600 mt-2">Your privacy is our priority</p>
      </div>

      <div className="card">
        <h2 className="text-xl font-bold mb-4">🔒 Privacy First Design</h2>
        <ul className="space-y-2 text-gray-700">
          <li>✓ Documents stay on device</li>
          <li>✓ AI inference runs locally when supported</li>
          <li>✓ No document uploaded to cloud servers</li>
          <li>✓ Local knowledge base</li>
          <li>✓ No telemetry by default</li>
        </ul>
      </div>
    </div>
  )
}
