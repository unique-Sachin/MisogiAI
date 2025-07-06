'use client'

export default function DebugPage() {
  const sampleMessage = {
    id: '1',
    type: 'assistant' as const,
    content: 'The salary mentioned in the offer letter is ₹ 5,00,004/- per annum, which is your Total Annual Earning Potential [chunk#2].',
    citations: [
      { source_path: 'illumifin India_Offer Letter_ Swarnab Basu.pdf', chunk_index: '19' },
      { source_path: 'illumifin India_Offer Letter_ Swarnab Basu.pdf', chunk_index: '25' },
      { source_path: 'illumifin India_Offer Letter_ Swarnab Basu.pdf', chunk_index: '13' },
      { source_path: 'illumifin India_Offer Letter_ Swarnab Basu.pdf', chunk_index: '2' }
    ]
  }

  return (
    <div style={{ padding: '2rem', background: '#f5f5f5' }}>
      <h1>Debug Message Display</h1>
      
      <div style={{ marginBottom: '2rem' }}>
        <h2>Raw Message Data:</h2>
        <pre style={{ background: '#fff', padding: '1rem', borderRadius: '4px', fontSize: '0.875rem' }}>
          {JSON.stringify(sampleMessage, null, 2)}
        </pre>
      </div>

      <div style={{ marginBottom: '2rem' }}>
        <h2>Rendered Message:</h2>
        <div className={`message ${sampleMessage.type}`}>
          <div className="message-content">
            {sampleMessage.content}
          </div>
          {sampleMessage.citations && sampleMessage.citations.length > 0 && (
            <div className="citations">
              <strong>Sources:</strong>
              {sampleMessage.citations.map((citation, index) => (
                <span key={index} className="citation">
                  {citation.source_path} (chunk #{citation.chunk_index})
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div>
        <h2>Expected:</h2>
        <p>You should see the AI response text clearly displayed above the citations.</p>
        <p>If you only see citations, there's a CSS or rendering issue.</p>
      </div>
    </div>
  )
} 