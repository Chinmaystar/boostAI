import './index.css'
import { AuthProvider } from './hooks/useAuth'
import LandingPage from './pages/landing'
import SchoolPage from './pages/school'
import UnivPage from './pages/univ'
import UnivAppPage from './pages/univ-app'
import LoginPage from './pages/login'
import SelectPage from './pages/select'
import TestUploadPage from './pages/testupload'

function AppContent() {
  const path = window.location.pathname;
  const params = new URLSearchParams(window.location.search);

  if (params.has("code") && path === "/") {
    const role = params.get("state") || "univ";
    window.location.href = `/login?code=${encodeURIComponent(params.get("code")!)}&role=${role}`;
    return null;
  }

  if (path === '/school') {
    return <SchoolPage />;
  }
  if (path === '/university') {
    return <UnivPage />;
  }
  if (path === '/university/app') {
    return <UnivAppPage />;
  }
  if (path === '/login') {
    return <LoginPage />;
  }
  if (path === '/select') {
    return <SelectPage />;
  }
  if (path === '/test-upload') {
    return <TestUploadPage />;
  }

  return <LandingPage />;
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App
