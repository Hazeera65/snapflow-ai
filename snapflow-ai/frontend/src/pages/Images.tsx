export default function Images() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Image Intelligence</h1>
        <p className="text-gray-600 mt-2">Extract text and analyze images</p>
      </div>

      <div className="card border-2 border-dashed border-gray-300 text-center py-12">
        <div className="text-4xl mb-4">🖼️</div>
        <h3 className="text-lg font-semibold">Upload an image</h3>
        <p className="text-gray-600 mt-2">Screenshots, documents, diagrams</p>
        <input type="file" accept="image/*" className="hidden" />
      </div>
    </div>
  )
}
