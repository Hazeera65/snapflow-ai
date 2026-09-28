export default function Tasks() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
        <p className="text-gray-600 mt-2">Manage extracted action items</p>
      </div>

      <div className="card text-center py-12">
        <div className="text-4xl mb-4">✓</div>
        <p className="text-gray-600">No tasks yet. Extract tasks from documents.</p>
      </div>
    </div>
  )
}
