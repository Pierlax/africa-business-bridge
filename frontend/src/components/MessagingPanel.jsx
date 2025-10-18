import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar } from '@/components/ui/avatar';
import { Send, User, Clock } from 'lucide-react';

export default function MessagingPanel({ matchId, partnerName }) {
  const { token } = useAuth();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadMessages();
    // Poll per nuovi messaggi ogni 5 secondi
    const interval = setInterval(loadMessages, 5000);
    return () => clearInterval(interval);
  }, [matchId]);

  useEffect(() => {
    // Scroll automatico all'ultimo messaggio
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      const response = await fetch(
        `${API_URL}/matching/messages?match_id=${matchId}&page_size=50`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setMessages(data.items || []);
      }
    } catch (error) {
      console.error('Errore nel caricamento dei messaggi:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim()) return;

    setSending(true);

    try {
      const response = await fetch(`${API_URL}/matching/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          match_id: matchId,
          content: newMessage.trim()
        })
      });

      if (response.ok) {
        setNewMessage('');
        await loadMessages();
      }
    } catch (error) {
      console.error('Errore nell\'invio del messaggio:', error);
    } finally {
      setSending(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Ora';
    if (diffMins < 60) return `${diffMins}m fa`;
    if (diffHours < 24) return `${diffHours}h fa`;
    if (diffDays < 7) return `${diffDays}g fa`;
    
    return date.toLocaleDateString('it-IT', { 
      day: 'numeric', 
      month: 'short' 
    });
  };

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader className="border-b">
        <div className="flex items-center gap-3">
          <Avatar className="h-10 w-10 bg-primary text-white flex items-center justify-center">
            <User className="h-5 w-5" />
          </Avatar>
          <div>
            <CardTitle className="text-lg">{partnerName}</CardTitle>
            <p className="text-sm text-gray-500">Match #{matchId}</p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <Send className="w-12 h-12 mb-3 text-gray-400" />
            <p>Nessun messaggio ancora.</p>
            <p className="text-sm">Inizia la conversazione!</p>
          </div>
        ) : (
          <>
            {messages.map((message) => {
              const isOwn = message.sender_type === 'pmi'; // Assumi che l'utente corrente sia PMI
              
              return (
                <div
                  key={message.id}
                  className={`flex ${isOwn ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2`}
                >
                  <div className={`max-w-[70%] ${isOwn ? 'order-2' : 'order-1'}`}>
                    <div
                      className={`rounded-2xl px-4 py-2 ${
                        isOwn
                          ? 'bg-primary text-white rounded-br-none'
                          : 'bg-gray-100 text-gray-900 rounded-bl-none'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-wrap break-words">
                        {message.content}
                      </p>
                    </div>
                    <div
                      className={`flex items-center gap-1 mt-1 text-xs text-gray-500 ${
                        isOwn ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      <Clock className="w-3 h-3" />
                      <span>{formatTime(message.created_at)}</span>
                      {message.is_read && isOwn && (
                        <span className="ml-1 text-primary">✓✓</span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={messagesEndRef} />
          </>
        )}
      </CardContent>

      <div className="border-t p-4">
        <form onSubmit={handleSendMessage} className="flex items-center gap-2">
          <Input
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Scrivi un messaggio..."
            disabled={sending}
            className="flex-1"
            maxLength={1000}
          />
          <Button 
            type="submit" 
            disabled={sending || !newMessage.trim()}
            size="icon"
            className="flex-shrink-0"
          >
            {sending ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </form>
        <p className="text-xs text-gray-500 mt-2">
          {newMessage.length}/1000 caratteri
        </p>
      </div>
    </Card>
  );
}

