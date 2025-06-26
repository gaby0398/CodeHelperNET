export interface ChatResponse {
  response: string;
  error?: string;
  details?: string;
}

export class ChatService {
  private static instance: ChatService;
  private baseUrl: string;

  private constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || '/api';
  }

  public static getInstance(): ChatService {
    if (!ChatService.instance) {
      ChatService.instance = new ChatService();
    }
    return ChatService.instance;
  }

  async sendMessage(message: string): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
      }

      const data: ChatResponse = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      return data.response;

    } catch (error) {
      console.error('Error enviando mensaje:', error);
      
      if (error instanceof Error) {
        // Si es un error de red, dar un mensaje más amigable
        if (error.message.includes('fetch')) {
          throw new Error('No se pudo conectar con el servidor. Verifica que el backend esté ejecutándose.');
        }
        throw error;
      }
      
      throw new Error('Error desconocido al enviar mensaje');
    }
  }

  // Método para verificar si el backend está disponible
  async checkBackendHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      return response.ok;
    } catch (error) {
      console.error('Error verificando salud del backend:', error);
      return false;
    }
  }
}

export const chatService = ChatService.getInstance(); 