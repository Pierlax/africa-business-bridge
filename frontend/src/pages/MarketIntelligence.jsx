import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  Newspaper, 
  Bell, 
  FileText, 
  Search,
  ExternalLink,
  Calendar,
  MapPin,
  Tag,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Plus
} from 'lucide-react';

export default function MarketIntelligence() {
  const { token } = useAuth();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  
  const [reports, setReports] = useState([]);
  const [news, setNews] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [activeTab, setActiveTab] = useState('news');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadReports();
    loadNews();
    loadAlerts();
  }, []);

  const loadReports = async () => {
    try {
      const response = await fetch(`${API_URL}/market/reports?page_size=10`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setReports(data.items || []);
      }
    } catch (error) {
      console.error('Errore nel caricamento dei report:', error);
    }
  };

  const loadNews = async (refresh = false) => {
    if (refresh) setRefreshing(true);
    
    try {
      const url = `${API_URL}/market/news?page_size=20${refresh ? '&refresh=true' : ''}`;
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setNews(data.items || []);
        if (refresh) {
          setMessage({ type: 'success', text: 'Notizie aggiornate!' });
        }
      }
    } catch (error) {
      console.error('Errore nel caricamento delle notizie:', error);
      setMessage({ type: 'error', text: 'Errore nel caricamento delle notizie' });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await fetch(`${API_URL}/market/alerts`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setAlerts(data.items || []);
      }
    } catch (error) {
      console.error('Errore nel caricamento degli alert:', error);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Data non disponibile';
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const getCategoryColor = (category) => {
    const colors = {
      'economy': 'bg-blue-100 text-blue-800',
      'trade': 'bg-green-100 text-green-800',
      'technology': 'bg-purple-100 text-purple-800',
      'agriculture': 'bg-yellow-100 text-yellow-800',
      'default': 'bg-gray-100 text-gray-800'
    };
    return colors[category] || colors.default;
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
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="w-8 h-8 text-primary" />
              <h1 className="text-3xl font-bold">Market Intelligence</h1>
            </div>
            <p className="text-gray-600">
              Notizie, report e analisi dai mercati africani
            </p>
          </div>
          <Button 
            onClick={() => loadNews(true)} 
            disabled={refreshing}
            variant="outline"
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Aggiornamento...' : 'Aggiorna'}
          </Button>
        </div>
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
                <p className="text-sm text-gray-600">Notizie</p>
                <p className="text-2xl font-bold">{news.length}</p>
              </div>
              <Newspaper className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Report</p>
                <p className="text-2xl font-bold">{reports.length}</p>
              </div>
              <FileText className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Alert Attivi</p>
                <p className="text-2xl font-bold">{alerts.length}</p>
              </div>
              <Bell className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search Bar */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <Input
                placeholder="Cerca notizie, report, bandi..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button>Cerca</Button>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="news">
            <Newspaper className="mr-2 h-4 w-4" />
            Notizie
          </TabsTrigger>
          <TabsTrigger value="reports">
            <FileText className="mr-2 h-4 w-4" />
            Report
          </TabsTrigger>
          <TabsTrigger value="alerts">
            <Bell className="mr-2 h-4 w-4" />
            Alert
          </TabsTrigger>
        </TabsList>

        {/* Tab Notizie */}
        <TabsContent value="news">
          <div className="space-y-4">
            {news.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <Newspaper className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p className="text-gray-600">Nessuna notizia disponibile.</p>
                  <Button 
                    onClick={() => loadNews(true)} 
                    className="mt-4"
                    variant="outline"
                  >
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Carica Notizie
                  </Button>
                </CardContent>
              </Card>
            ) : (
              news.map((item) => (
                <Card key={item.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex gap-4">
                      {item.image_url && (
                        <div className="w-32 h-32 flex-shrink-0 rounded-lg overflow-hidden bg-gray-100">
                          <img 
                            src={item.image_url} 
                            alt={item.title}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      )}
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="text-lg font-semibold hover:text-primary cursor-pointer">
                            {item.title}
                          </h3>
                          <a 
                            href={item.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-primary hover:underline flex items-center gap-1 flex-shrink-0 ml-4"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        </div>
                        
                        {item.summary && (
                          <p className="text-gray-700 mb-3 line-clamp-2">
                            {item.summary}
                          </p>
                        )}
                        
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          {item.country && (
                            <div className="flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              {item.country}
                            </div>
                          )}
                          {item.category && (
                            <Badge className={getCategoryColor(item.category)}>
                              {item.category}
                            </Badge>
                          )}
                          {item.source && (
                            <span className="text-xs">
                              Fonte: {item.source}
                            </span>
                          )}
                          {item.published_at && (
                            <div className="flex items-center gap-1">
                              <Calendar className="w-4 h-4" />
                              {formatDate(item.published_at)}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        {/* Tab Report */}
        <TabsContent value="reports">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {reports.length === 0 ? (
              <Card className="col-span-2">
                <CardContent className="p-12 text-center">
                  <FileText className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p className="text-gray-600">Nessun report disponibile.</p>
                </CardContent>
              </Card>
            ) : (
              reports.map((report) => (
                <Card key={report.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">{report.title}</CardTitle>
                    <CardDescription>
                      {report.author && `di ${report.author}`}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {report.summary && (
                      <p className="text-gray-700 mb-4 line-clamp-3">
                        {report.summary}
                      </p>
                    )}
                    
                    <div className="flex items-center gap-2 mb-4">
                      {report.country && (
                        <Badge variant="outline">{report.country}</Badge>
                      )}
                      {report.sector && (
                        <Badge variant="outline">{report.sector}</Badge>
                      )}
                      {report.is_premium && (
                        <Badge className="bg-yellow-100 text-yellow-800">Premium</Badge>
                      )}
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>{report.views_count} visualizzazioni</span>
                      {report.publication_date && (
                        <span>{formatDate(report.publication_date)}</span>
                      )}
                    </div>
                    
                    <Button className="w-full mt-4" variant="outline">
                      <FileText className="mr-2 h-4 w-4" />
                      Leggi Report
                    </Button>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        {/* Tab Alert */}
        <TabsContent value="alerts">
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Crea Nuovo Alert</CardTitle>
                <CardDescription>
                  Ricevi notifiche personalizzate su notizie e bandi
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Crea Alert
                </Button>
              </CardContent>
            </Card>

            {alerts.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <Bell className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p className="text-gray-600">Nessun alert configurato.</p>
                </CardContent>
              </Card>
            ) : (
              alerts.map((alert) => (
                <Card key={alert.id}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg mb-2">{alert.name}</h3>
                        <div className="flex items-center gap-2 text-sm text-gray-600">
                          <Badge variant={alert.is_active ? 'default' : 'secondary'}>
                            {alert.is_active ? 'Attivo' : 'Disattivato'}
                          </Badge>
                          <span>Frequenza: {alert.frequency}</span>
                          {alert.triggers_count > 0 && (
                            <span>{alert.triggers_count} attivazioni</span>
                          )}
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        Modifica
                      </Button>
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

