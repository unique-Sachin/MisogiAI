'use client'

import { useState, useRef } from 'react'
import axios from 'axios'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  citations?: Citation[]
}

interface Citation {
  source_path: string
  chunk_index: string
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploadStatus('Uploading...')
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post('/api/upload-doc', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setUploadStatus(`✅ Uploaded successfully! ${response.data.chunks_indexed} chunks indexed.`)
    } catch (error) {
      console.error('Upload error:', error)
      setUploadStatus('❌ Upload failed. Please try again.')
    }
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await axios.post('/api/chat', {
        query: inputValue
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.data.answer,
        citations: response.data.citations
      }

      console.log('Assistant response:', response.data)
      console.log('Assistant message:', assistantMessage)
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="container">
      <h1 style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '2.5rem', fontWeight: 'bold' }}>
        HR Knowledge Assistant
      </h1>

      {/* Upload Area */}
      <div className="upload-area">
        <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: '600' }}>
          Upload HR Documents
        </h2>
        <div className="file-input">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileUpload}
          />
        </div>
        {uploadStatus && (
          <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
            {uploadStatus}
          </div>
        )}
      </div>

      {/* Chat Interface */}
      <div className="chat-container">
        <div className="chat-header">
          <h2 style={{ margin: 0, fontSize: '1.5rem' }}>Ask HR Questions</h2>
          <p style={{ margin: '0.5rem 0 0 0', opacity: 0.9 }}>
            Ask questions about policies, benefits, and procedures
          </p>
        </div>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#64748b', marginTop: '2rem' }}>
              <p>👋 Welcome! Upload some HR documents and start asking questions.</p>
              <p style={{ fontSize: '0.875rem', marginTop: '1rem' }}>
                Try asking: "How many vacation days do I get?" or "What's the remote work policy?"
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.type}`}
              >
                <div className="message-content">
                  {message.content}
                </div>
                {message.citations && message.citations.length > 0 && (
                  <div className="citations">
                    <strong>Sources:</strong>
                    {message.citations.map((citation, index) => (
                      <span key={index} className="citation">
                        {citation.source_path} (chunk #{citation.chunk_index})
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
          {isLoading && (
            <div className="message assistant">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div className="loading"></div>
                Thinking...
              </div>
            </div>
          )}
        </div>

        <div className="input-area">
          <div className="input-group">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about HR policies..."
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
              className="btn btn-primary"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  )
} 