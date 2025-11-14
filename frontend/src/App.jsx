import React from 'react'
import ChatBox from './components/ChatBox'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            RAG Chatbot
          </h1>
          <p className="text-gray-600">
            Powered by AWS Bedrock NovaLite & ChromaDB
          </p>
        </header>
        
        <ChatBox />
      </div>
    </div>
  )
}

export default App
