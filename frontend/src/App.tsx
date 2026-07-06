import './index.css'
import LandingPage from './pages/landing'
import SchoolPage from './pages/school'
import UnivPage from './pages/univ'
import TestUploadPage from './pages/testupload'

function App() {
  const path = window.location.pathname;

  if (path === '/school') {
    return <SchoolPage />;
  }
  if (path === '/university') {
    return <UnivPage />;
  }
  if (path === '/test-upload') {
    return <TestUploadPage />;
  }

  return <LandingPage />;
}

export default App
