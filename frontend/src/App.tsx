import './index.css'
import LandingPage from './pages/landing'
import SchoolPage from './pages/school'
import UnivPage from './pages/univ'

import UnivAppPage from './pages/univ-app'
import LoginPage from './pages/login'
import SelectPage from './pages/select'
import TestUploadPage from './pages/testupload'

import TeacherUploadPage from './pages/teacher/upload'
import ExtractionReviewPage from './pages/teacher/extraction-review'
import QuestionGenerationPage from './pages/teacher/question-generation'
import ExportPage from './pages/teacher/export'

import { ReviewSessionProvider } from './context/ReviewSessionContext'

function TeacherRoutes({ path }: { path: string }) {
  if (path === '/teacher/upload') {
    return <TeacherUploadPage />;
  }
  if (path === '/teacher/extraction-review') {
    return <ExtractionReviewPage />;
  }
  if (path === '/teacher/question-generation') {
    return <QuestionGenerationPage />;
  }
  if (path === '/teacher/export') {
    return <ExportPage />;
  }
  return <TeacherUploadPage />;
}

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

  if (path.startsWith('/teacher')) {
    return (
      <ReviewSessionProvider>
        <TeacherRoutes path={path} />
      </ReviewSessionProvider>
    );
  }

  return <LandingPage />;
}

export default App
