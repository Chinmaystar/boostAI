import './index.css'
import LandingPage from './pages/landing'
import SchoolPage from './pages/school'
import UnivPage from './pages/univ'

import UnivAppPage from './pages/univ-app'
import LoginPage from './pages/login'
import SelectPage from './pages/select'
import TestUploadPage from './pages/testupload'

function App() {
  const path = window.location.pathname;

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

export default App
