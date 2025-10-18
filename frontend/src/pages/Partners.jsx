import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Users, 
  MapPin, 
  Briefcase, 
  Star, 
  CheckCircle, 
  AlertCircle,
  TrendingUp,
  MessageSquare,
  Calendar,
  Sparkles
} from 'lucide-react';

export default function Partners() {
  const { token } = useAuth();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  
  const [suggestions, setSuggestions] = useState([]);
  const [myMatches, setMyMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [activeTab, setActiveTab] = useState('suggestions');

  useEffect(() => {
    loadSuggestions();
    loadMyMatches();
  }, []);

  const loadSuggestions = async () => {
    try {
      const response = await fetch(`${API_URL}/matching/suggestions?limit=20`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.matches || []);
      }
    } catch (error) {
      console.error('Errore nel caricamento dei suggerimenti:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMyMatches = async () => {
    try {
      const response = await fetch(`${API_URL}/matching/my-matches`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setMyMatches(data || []);
      }
    } catch (error) {
      console.error('Errore nel caricamento dei match:', error);
    }
  };

  const handleAcceptMatch = async (partnerId) => {
    try {
      const response = await fetch(`${API_URL}/matching/accept/${partnerId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Match accettato! Il partner è stato aggiunto ai tuoi contatti.' });
        loadSuggestions();
        loadMyMatches();
        setActiveTab('matches');
      } else {
        setMessage({ type: 'error', text: 'Errore nell\'accettare il match' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Errore di connessione' });
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-blue-600 bg-blue-50';
    if (score >= 40) return 'text-orange-600 bg-orange-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Eccellente';
    if (score >= 60) return 'Buono';
    if (score >= 40) return 'Discreto';
    return 'Basso';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Users className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold">Partner Locali</h1>
        </div>
        <p className="text-gray-600">
          Trova i partner giusti per espandere il tuo business in Africa
        </p>
      </div>

      {/* Messages */}
      {message.text && (
        <Alert className={`mb-6 ${message.type === 'success' ? 'bg-green-50 text-green-900 border-green-200' : 'bg-red-50 text-red-900 border-red-200'}`}>
          {message.type === 'success' ? <CheckCircle className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
          <AlertDescription>{message.text}</AlertDescription>
        </Alert>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Suggerimenti IA</p>
                <p className="text-2xl font-bold">{suggestions.length}</p>
              </div>
              <Sparkles className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Match Attivi</p>
                <p className="text-2xl font-bold">{myMatches.length}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Incontri</p>
                <p className="text-2xl font-bold">0</p>
              </div>
              <Calendar className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="suggestions">
            <Sparkles className="mr-2 h-4 w-4" />
            Suggerimenti IA
          </TabsTrigger>
          <TabsTrigger value="matches">
            <CheckCircle className="mr-2 h-4 w-4" />
            I Miei Match
          </TabsTrigger>
        </TabsList>

        {/* Tab Suggerimenti */}
        <TabsContent value="suggestions">
          <div className="space-y-4">
            {suggestions.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <Sparkles className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p className="text-gray-600">
                    Nessun suggerimento disponibile al momento.
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    Completa il tuo profilo per ricevere match personalizzati.
                  </p>
                </CardContent>
              </Card>
            ) : (
              suggestions.map((suggestion) => (
                <Card key={suggestion.partner_id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-xl mb-2">
                          {suggestion.partner_name}
                        </CardTitle>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <MapPin className="w-4 h-4" />
                            {suggestion.partner_data.country}
                            {suggestion.partner_data.city && `, ${suggestion.partner_data.city}`}
                          </div>
                          {suggestion.partner_data.partner_type && (
                            <div className="flex items-center gap-1">
                              <Briefcase className="w-4 h-4" />
                              {suggestion.partner_data.partner_type}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full font-semibold ${getScoreColor(suggestion.match_score)}`}>
                          <TrendingUp className="w-4 h-4" />
                          {Math.round(suggestion.match_score)}%
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {getScoreLabel(suggestion.match_score)} Match
                        </p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {/* Descrizione */}
                    {suggestion.partner_data.description && (
                      <p className="text-gray-700">
                        {suggestion.partner_data.description}
                      </p>
                    )}

                    {/* Spiegazione Match */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-start gap-2">
                        <Sparkles className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-sm font-medium text-blue-900 mb-1">
                            Perché questo match?
                          </p>
                          <p className="text-sm text-blue-800">
                            {suggestion.explanation}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Breakdown Scores */}
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                      <div className="text-center">
                        <p className="text-xs text-gray-500 mb-1">Settore</p>
                        <p className="text-lg font-bold text-gray-900">
                          {Math.round(suggestion.breakdown.sector_score)}%
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-500 mb-1">Paese</p>
                        <p className="text-lg font-bold text-gray-900">
                          {Math.round(suggestion.breakdown.country_score)}%
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-500 mb-1">Servizi</p>
                        <p className="text-lg font-bold text-gray-900">
                          {Math.round(suggestion.breakdown.service_score)}%
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-500 mb-1">Dimensione</p>
                        <p className="text-lg font-bold text-gray-900">
                          {Math.round(suggestion.breakdown.size_score)}%
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-500 mb-1">Affinità</p>
                        <p className="text-lg font-bold text-gray-900">
                          {Math.round(suggestion.breakdown.keyword_score)}%
                        </p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 pt-2">
                      <Button 
                        onClick={() => handleAcceptMatch(suggestion.partner_id)}
                        className="flex-1"
                      >
                        <CheckCircle className="mr-2 h-4 w-4" />
                        Accetta Match
                      </Button>
                      <Button variant="outline">
                        <MessageSquare className="mr-2 h-4 w-4" />
                        Contatta
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        {/* Tab I Miei Match */}
        <TabsContent value="matches">
          <div className="space-y-4">
            {myMatches.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p className="text-gray-600">
                    Non hai ancora match attivi.
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    Esplora i suggerimenti per trovare partner compatibili.
                  </p>
                </CardContent>
              </Card>
            ) : (
              myMatches.map((match) => (
                <Card key={match.id}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg mb-2">Match #{match.id}</h3>
                        <div className="flex items-center gap-4">
                          <Badge variant={match.status === 'accepted' ? 'default' : 'secondary'}>
                            {match.status}
                          </Badge>
                          {match.match_score && (
                            <span className="text-sm text-gray-600">
                              Score: {Math.round(match.match_score)}%
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <MessageSquare className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Calendar className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

