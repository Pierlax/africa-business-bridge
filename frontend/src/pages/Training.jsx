import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  GraduationCap, 
  Video, 
  Calendar, 
  Clock, 
  Users, 
  Award,
  CheckCircle,
  AlertCircle,
  Play,
  BookOpen,
  Download
} from 'lucide-react';

export default function Training() {
  const { token } = useAuth();
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  
  const [events, setEvents] = useState([]);
  const [courses, setCourses] = useState([]);
  const [myRegistrations, setMyRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [activeTab, setActiveTab] = useState('events');

  useEffect(() => {
    loadEvents();
    loadCourses();
  }, []);

  const loadEvents = async () => {
    try {
      const response = await fetch(`${API_URL}/training/events?upcoming=true&page_size=20`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEvents(data.items || []);
      }
    } catch (error) {
      console.error('Errore nel caricamento degli eventi:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCourses = async () => {
    try {
      const response = await fetch(`${API_URL}/training/courses?page_size=20`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setCourses(data.items || []);
      }
    } catch (error) {
      console.error('Errore nel caricamento dei corsi:', error);
    }
  };

  const handleRegisterEvent = async (eventId) => {
    try {
      const response = await fetch(`${API_URL}/training/events/${eventId}/register`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Registrazione completata! Riceverai una email di conferma.' });
        loadEvents();
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Errore nella registrazione' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Errore di connessione' });
    }
  };

  const handleEnrollCourse = async (courseId) => {
    try {
      const response = await fetch(`${API_URL}/training/courses/${courseId}/enroll`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Iscrizione al corso completata!' });
        loadCourses();
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.detail || 'Errore nell\'iscrizione' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Errore di connessione' });
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Data da definire';
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getEventTypeLabel = (type) => {
    const labels = {
      'webinar': 'Webinar',
      'workshop': 'Workshop',
      'course': 'Corso'
    };
    return labels[type] || type;
  };

  const getEventTypeColor = (type) => {
    const colors = {
      'webinar': 'bg-blue-100 text-blue-800',
      'workshop': 'bg-purple-100 text-purple-800',
      'course': 'bg-green-100 text-green-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const getLevelColor = (level) => {
    const colors = {
      'beginner': 'bg-green-100 text-green-800',
      'intermediate': 'bg-yellow-100 text-yellow-800',
      'advanced': 'bg-red-100 text-red-800'
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
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
          <GraduationCap className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold">Formazione</h1>
        </div>
        <p className="text-gray-600">
          Webinar, workshop e corsi per espandere il tuo business in Africa
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
                <p className="text-sm text-gray-600">Eventi Disponibili</p>
                <p className="text-2xl font-bold">{events.length}</p>
              </div>
              <Video className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Corsi Disponibili</p>
                <p className="text-2xl font-bold">{courses.length}</p>
              </div>
              <BookOpen className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Certificati</p>
                <p className="text-2xl font-bold">0</p>
              </div>
              <Award className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="events">
            <Video className="mr-2 h-4 w-4" />
            Eventi
          </TabsTrigger>
          <TabsTrigger value="courses">
            <BookOpen className="mr-2 h-4 w-4" />
            Corsi
          </TabsTrigger>
          <TabsTrigger value="certificates">
            <Award className="mr-2 h-4 w-4" />
            Certificati
          </TabsTrigger>
        </TabsList>

        {/* Tab Eventi */}
        <TabsContent value="events">
          <div className="space-y-4">
            {events.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <Video className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p className="text-gray-600">Nessun evento in programma al momento.</p>
                </CardContent>
              </Card>
            ) : (
              events.map((event) => (
                <Card key={event.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={getEventTypeColor(event.event_type)}>
                            {getEventTypeLabel(event.event_type)}
                          </Badge>
                          {event.issues_certificate && (
                            <Badge variant="outline" className="flex items-center gap-1">
                              <Award className="w-3 h-3" />
                              Certificato
                            </Badge>
                          )}
                        </div>
                        <CardTitle className="text-xl mb-2">{event.title}</CardTitle>
                        <CardDescription>{event.description}</CardDescription>
                      </div>
                      {event.cover_image_url && (
                        <div className="w-32 h-32 flex-shrink-0 ml-4 rounded-lg overflow-hidden bg-gray-100">
                          <img 
                            src={event.cover_image_url} 
                            alt={event.title}
                            className="w-full h-full object-cover"
                          />
                        </div>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      {event.scheduled_at && (
                        <div className="flex items-center gap-2 text-sm">
                          <Calendar className="w-4 h-4 text-gray-500" />
                          <span>{formatDate(event.scheduled_at)}</span>
                        </div>
                      )}
                      {event.duration_minutes && (
                        <div className="flex items-center gap-2 text-sm">
                          <Clock className="w-4 h-4 text-gray-500" />
                          <span>{event.duration_minutes} min</span>
                        </div>
                      )}
                      {event.max_participants && (
                        <div className="flex items-center gap-2 text-sm">
                          <Users className="w-4 h-4 text-gray-500" />
                          <span>{event.registrations_count}/{event.max_participants}</span>
                        </div>
                      )}
                      {event.instructor_name && (
                        <div className="text-sm">
                          <span className="text-gray-500">Relatore: </span>
                          <span className="font-medium">{event.instructor_name}</span>
                        </div>
                      )}
                    </div>

                    <Button 
                      onClick={() => handleRegisterEvent(event.id)}
                      className="w-full"
                    >
                      <CheckCircle className="mr-2 h-4 w-4" />
                      Registrati
                    </Button>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        {/* Tab Corsi */}
        <TabsContent value="courses">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {courses.length === 0 ? (
              <Card className="col-span-2">
                <CardContent className="p-12 text-center">
                  <BookOpen className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                  <p className="text-gray-600">Nessun corso disponibile al momento.</p>
                </CardContent>
              </Card>
            ) : (
              courses.map((course) => (
                <Card key={course.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    {course.cover_image_url && (
                      <div className="w-full h-48 rounded-lg overflow-hidden bg-gray-100 mb-4">
                        <img 
                          src={course.cover_image_url} 
                          alt={course.title}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    )}
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className={getLevelColor(course.level)}>
                        {course.level}
                      </Badge>
                      {course.issues_certificate && (
                        <Badge variant="outline" className="flex items-center gap-1">
                          <Award className="w-3 h-3" />
                          Certificato
                        </Badge>
                      )}
                    </div>
                    <CardTitle>{course.title}</CardTitle>
                    <CardDescription className="line-clamp-2">
                      {course.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 mb-4 text-sm text-gray-600">
                      {course.duration_hours && (
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          <span>{course.duration_hours} ore</span>
                        </div>
                      )}
                      {course.lessons_count > 0 && (
                        <div className="flex items-center gap-2">
                          <BookOpen className="w-4 h-4" />
                          <span>{course.lessons_count} lezioni</span>
                        </div>
                      )}
                      {course.enrollments_count > 0 && (
                        <div className="flex items-center gap-2">
                          <Users className="w-4 h-4" />
                          <span>{course.enrollments_count} iscritti</span>
                        </div>
                      )}
                      {course.instructor_name && (
                        <div>
                          <span className="text-gray-500">Docente: </span>
                          <span className="font-medium">{course.instructor_name}</span>
                        </div>
                      )}
                    </div>

                    <Button 
                      onClick={() => handleEnrollCourse(course.id)}
                      className="w-full"
                    >
                      <Play className="mr-2 h-4 w-4" />
                      Iscriviti al Corso
                    </Button>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>

        {/* Tab Certificati */}
        <TabsContent value="certificates">
          <Card>
            <CardContent className="p-12 text-center">
              <Award className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p className="text-gray-600 mb-2">Nessun certificato ancora.</p>
              <p className="text-sm text-gray-500">
                Completa eventi e corsi per ottenere certificati di partecipazione.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

