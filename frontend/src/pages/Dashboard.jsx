import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Globe, 
  LayoutDashboard, 
  Store, 
  Users, 
  TrendingUp, 
  GraduationCap, 
  Calendar,
  Settings,
  LogOut,
  Menu,
  X,
  Bell,
  Search,
  Building2,
  FileText,
  MessageSquare,
  BarChart3
} from 'lucide-react';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Menu items basati sul ruolo
  const getMenuItems = () => {
    const baseItems = [
      { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
    ];

    if (user?.role === 'pmi') {
      return [
        ...baseItems,
        { icon: Store, label: 'Expo Virtuale', path: '/expo' },
        { icon: Users, label: 'Partner Locali', path: '/partners' },
        { icon: Calendar, label: 'Incontri B2B', path: '/meetings' },
        { icon: TrendingUp, label: 'Market Intelligence', path: '/market' },
        { icon: GraduationCap, label: 'Formazione', path: '/training' },
        { icon: MessageSquare, label: 'Messaggi', path: '/messages' },
        { icon: Settings, label: 'Impostazioni', path: '/settings' },
      ];
    } else if (user?.role === 'partner') {
      return [
        ...baseItems,
        { icon: Building2, label: 'Il Mio Profilo', path: '/profile' },
        { icon: Users, label: 'PMI Italiane', path: '/pmi' },
        { icon: Calendar, label: 'Incontri', path: '/meetings' },
        { icon: MessageSquare, label: 'Messaggi', path: '/messages' },
        { icon: GraduationCap, label: 'Formazione', path: '/training' },
        { icon: Settings, label: 'Impostazioni', path: '/settings' },
      ];
    } else if (user?.role === 'admin') {
      return [
        ...baseItems,
        { icon: Users, label: 'Gestione Utenti', path: '/admin/users' },
        { icon: FileText, label: 'Contenuti', path: '/admin/content' },
        { icon: BarChart3, label: 'Statistiche', path: '/admin/stats' },
        { icon: TrendingUp, label: 'Market Intelligence', path: '/admin/market' },
        { icon: GraduationCap, label: 'Formazione', path: '/admin/training' },
        { icon: Settings, label: 'Configurazione', path: '/admin/settings' },
      ];
    }

    return baseItems;
  };

  const menuItems = getMenuItems();

  // Statistiche di esempio basate sul ruolo
  const getStats = () => {
    if (user?.role === 'pmi') {
      return [
        { label: 'Visualizzazioni Expo', value: '1,234', icon: Store, color: 'text-blue-600' },
        { label: 'Match Suggeriti', value: '12', icon: Users, color: 'text-green-600' },
        { label: 'Incontri Programmati', value: '3', icon: Calendar, color: 'text-orange-600' },
        { label: 'Report Disponibili', value: '45', icon: FileText, color: 'text-purple-600' },
      ];
    } else if (user?.role === 'partner') {
      return [
        { label: 'Visualizzazioni Profilo', value: '856', icon: Building2, color: 'text-blue-600' },
        { label: 'PMI Interessate', value: '8', icon: Users, color: 'text-green-600' },
        { label: 'Incontri Completati', value: '15', icon: Calendar, color: 'text-orange-600' },
        { label: 'Rating Medio', value: '4.8', icon: BarChart3, color: 'text-purple-600' },
      ];
    } else if (user?.role === 'admin') {
      return [
        { label: 'Utenti Totali', value: '342', icon: Users, color: 'text-blue-600' },
        { label: 'PMI Registrate', value: '156', icon: Building2, color: 'text-green-600' },
        { label: 'Partner Attivi', value: '89', icon: Users, color: 'text-orange-600' },
        { label: 'Match Creati', value: '523', icon: BarChart3, color: 'text-purple-600' },
      ];
    }
    return [];
  };

  const stats = getStats();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-white border-r border-gray-200 transition-all duration-300 overflow-hidden flex flex-col`}>
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Globe className="w-8 h-8 text-primary" />
            <div className={`${sidebarOpen ? 'block' : 'hidden'}`}>
              <h2 className="font-bold text-lg">Africa Business</h2>
              <p className="text-xs text-gray-500">Bridge</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item, index) => (
            <Link
              key={index}
              to={item.path}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 transition-colors text-left"
            >
              <item.icon className="w-5 h-5 text-gray-600" />
              <span className={`${sidebarOpen ? 'block' : 'hidden'} text-sm font-medium text-gray-700`}>
                {item.label}
              </span>
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-red-50 text-red-600 transition-colors"
          >
            <LogOut className="w-5 h-5" />
            <span className={`${sidebarOpen ? 'block' : 'hidden'} text-sm font-medium`}>
              Esci
            </span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
              
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-sm text-gray-500">
                  Benvenuto, {user?.full_name}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Cerca..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </Button>

              <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
                  <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
                </div>
                <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-semibold">
                  {user?.full_name?.charAt(0).toUpperCase()}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="flex-1 p-6 overflow-auto">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            {stats.map((stat, index) => (
              <Card key={index}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">{stat.label}</p>
                      <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                    </div>
                    <stat.icon className={`w-12 h-12 ${stat.color}`} />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Azioni Rapide</CardTitle>
                <CardDescription>Operazioni frequenti</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {user?.role === 'pmi' && (
                  <>
                    <Button className="w-full justify-start" variant="outline">
                      <Store className="mr-2 w-4 h-4" />
                      Aggiorna Expo Virtuale
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Users className="mr-2 w-4 h-4" />
                      Cerca Partner
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Calendar className="mr-2 w-4 h-4" />
                      Prenota Incontro
                    </Button>
                  </>
                )}
                {user?.role === 'partner' && (
                  <>
                    <Button className="w-full justify-start" variant="outline">
                      <Building2 className="mr-2 w-4 h-4" />
                      Aggiorna Profilo
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Users className="mr-2 w-4 h-4" />
                      Esplora PMI
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <Calendar className="mr-2 w-4 h-4" />
                      Gestisci Disponibilità
                    </Button>
                  </>
                )}
                {user?.role === 'admin' && (
                  <>
                    <Button className="w-full justify-start" variant="outline">
                      <Users className="mr-2 w-4 h-4" />
                      Gestisci Utenti
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <FileText className="mr-2 w-4 h-4" />
                      Pubblica Contenuto
                    </Button>
                    <Button className="w-full justify-start" variant="outline">
                      <BarChart3 className="mr-2 w-4 h-4" />
                      Visualizza Report
                    </Button>
                  </>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Attività Recenti</CardTitle>
                <CardDescription>Ultimi aggiornamenti</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-blue-500 mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Nuovo match disponibile</p>
                      <p className="text-xs text-gray-500">2 ore fa</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-green-500 mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Incontro confermato</p>
                      <p className="text-xs text-gray-500">5 ore fa</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-2 h-2 rounded-full bg-orange-500 mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Nuovo report disponibile</p>
                      <p className="text-xs text-gray-500">1 giorno fa</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}

