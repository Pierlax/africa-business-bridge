import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ExpoVirtuale from './pages/ExpoVirtuale';
import Partners from './pages/Partners';
import MarketIntelligence from './pages/MarketIntelligence';
import Training from './pages/Training';
import BlockchainContracts from './pages/BlockchainContracts';
import Payments from './pages/Payments';
import Verification from './pages/Verification';
import Orders from './pages/Orders';
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import './App.css';

// Componente per proteggere le route che richiedono autenticazione
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
}

// Componente per le route pubbliche (redirect se già autenticato)
function PublicRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return !isAuthenticated ? children : <Navigate to="/dashboard" />;
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Route pubbliche */}
          <Route 
            path="/login" 
            element={
              <PublicRoute>
                <Login />
              </PublicRoute>
            } 
          />
          <Route 
            path="/register" 
            element={
              <PublicRoute>
                <Register />
              </PublicRoute>
            } 
          />

          {/* Route protette */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/expo" 
            element={
              <ProtectedRoute>
                <ExpoVirtuale />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/partners" 
            element={
              <ProtectedRoute>
                <Partners />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/market" 
            element={
              <ProtectedRoute>
                <MarketIntelligence />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/training" 
            element={
              <ProtectedRoute>
                <Training />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/blockchain" 
            element={
              <ProtectedRoute>
                <BlockchainContracts />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/payments" 
            element={
              <ProtectedRoute>
                <Payments />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/verification" 
            element={
              <ProtectedRoute>
                <Verification />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/orders" 
            element={
              <ProtectedRoute>
                <Orders />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/analytics" 
            element={
              <ProtectedRoute>
                <AnalyticsDashboard />
              </ProtectedRoute>
            } 
          />

          {/* Redirect root alla dashboard o login */}
          <Route path="/" element={<Navigate to="/dashboard" />} />

          {/* 404 - Pagina non trovata */}
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;

