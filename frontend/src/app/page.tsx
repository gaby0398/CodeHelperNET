'use client';

import { useState } from 'react';
import ChatInterface from '@/components/ChatInterface';
import { chatService } from '@/services/chatService';

export default function Home() {
  const handleSendMessage = async (message: string): Promise<string> => {
    try {
      const response = await chatService.sendMessage(message);
      return response;
    } catch (error) {
      console.error('Error en handleSendMessage:', error);
      throw error;
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header simplificado */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">CH</span>
            </div>
            <h1 className="text-xl font-bold text-white">
              CodeHelperNET
            </h1>
            <span className="text-gray-400 text-sm">
              Asistente IA para C# y .NET
            </span>
          </div>
        </div>
      </header>

      {/* Chat Area - Ocupa todo el espacio disponible */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        <div className="h-[calc(100vh-120px)]">
          <ChatInterface onSendMessage={handleSendMessage} />
        </div>
      </main>
    </div>
  );
}
