import { useState, useEffect, useRef } from 'react';
import logo from '../assets/logo.avif';
import { Eye } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

const GOOGLE_CLIENT_ID = "788338050972-f5fe672viv49m3b5lbcoepftp1qe03ic.apps.googleusercontent.com";

type AuthMode = 'signup' | 'login';

export default function LoginPage() {
  const { login, signup, user } = useAuth();
  const [mode, setMode] = useState<AuthMode>('signup');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const codeExchanged = useRef(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const r = params.get('role') || 'school';
    setRole(r);

    const code = params.get('code');
    if (code && !codeExchanged.current) {
      codeExchanged.current = true;
      window.history.replaceState({}, '', window.location.pathname);
      setSubmitting(true);
      fetch("http://localhost:3001/api/auth/google/callback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, role: r }),
      })
        .then(async (res) => {
          const data = await res.json();
          if (!res.ok) throw new Error(data.error || "Google sign-in failed");
          localStorage.setItem("token", data.token);
          window.location.href = data.user.role === "univ" ? "/university/app" : "/school";
        })
        .catch((err) => {
          setError((err as Error).message);
          setSubmitting(false);
        });
    }
  }, []);

  useEffect(() => {
    if (user) {
      window.location.href = user.role === 'univ' ? '/university/app' : '/school';
    }
  }, [user]);

  const handleGoogleSignIn = () => {
    const params = new URLSearchParams({
      client_id: GOOGLE_CLIENT_ID,
      redirect_uri: "http://localhost:3000",
      response_type: "code",
      scope: "email profile",
      state: role || "univ",
    });
    window.location.href = `https://accounts.google.com/o/oauth2/auth?${params.toString()}`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (mode === 'signup' && password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setSubmitting(true);
    try {
      if (mode === 'signup') {
        await signup(email, password, role || 'school');
      } else {
        await login(email, password);
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  const isSchool = role === 'school';
  const badgeText = isSchool ? 'EXAMS' : 'OPEN';
  const switchTarget = isSchool ? 'univ' : 'school';
  const switchText = isSchool ? 'Switch to BoostAI Open' : 'Switch to BoostAI Exams';
  const platformText = isSchool ? 'exam platform' : 'university platform';

  return (
    <div className="min-h-screen bg-white font-sans text-gray-900 flex flex-col relative px-4">
      <div className="absolute top-6 left-6 flex items-center gap-3">
        <div className="flex items-center gap-2">
           <img src={logo} alt="BoostAI Logo" className="w-8 h-8 object-contain rounded-md" />
           <span className="text-[22px] font-bold tracking-tight">BoostAI</span>
        </div>
        <div className="px-3 py-1 bg-blue-100 text-blue-600 text-xs font-bold rounded-full uppercase tracking-wide">
          {badgeText}
        </div>
      </div>

      <div className="flex-1 flex flex-col items-center pt-24 pb-12 w-full max-w-[440px] mx-auto">
        <a
          href={`/login?role=${switchTarget}`}
          className="mb-10 px-5 py-2 bg-gray-100 hover:bg-gray-200 transition-colors text-sm font-semibold rounded-full flex items-center gap-2"
        >
          {switchText}
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </a>

        <h1 className="text-[40px] font-bold tracking-tight mb-3 text-center leading-tight">
          {mode === 'signup' ? 'Try BoostAI for free' : 'Welcome back'}
        </h1>
        <p className="text-[15px] text-gray-800 mb-8 text-center font-medium">
          {mode === 'signup'
            ? `Sign up to get started on your all-in-one ${platformText}.`
            : `Log in to continue on your ${platformText}.`}
        </p>

        <div className="flex items-center bg-gray-100 rounded-full p-1 mb-8 w-full max-w-[280px]">
          <button
            onClick={() => { setMode('signup'); setError(null); }}
            className={`flex-1 py-2 text-sm font-bold rounded-full transition-colors ${
              mode === 'signup' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Sign up
          </button>
          <button
            onClick={() => { setMode('login'); setError(null); }}
            className={`flex-1 py-2 text-sm font-bold rounded-full transition-colors ${
              mode === 'login' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Log in
          </button>
        </div>

        <div className="w-full flex flex-col gap-4 mb-8">
          <button
            type="button"
            onClick={handleGoogleSignIn}
            disabled={submitting}
            className="w-full flex items-center justify-center gap-3 px-4 py-3.5 bg-white border border-gray-200 hover:bg-gray-50 rounded-[18px] text-[15px] font-bold transition-colors shadow-sm disabled:opacity-50"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Continue with Google
          </button>

          <button type="button" className="w-full flex items-center justify-center gap-3 px-4 py-3.5 bg-white border border-gray-200 hover:bg-gray-50 rounded-[18px] text-[15px] font-bold transition-colors shadow-sm opacity-60 cursor-not-allowed">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.04 2.26-.7 3.59-.7 1.57.06 2.76.62 3.61 1.63-3.19 1.76-2.61 5.92.51 7.03-.78 1.96-1.74 3.32-2.79 4.21zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
            </svg>
            Continue with Apple
          </button>

          <button type="button" className="w-full flex items-center justify-center gap-3 px-4 py-3.5 bg-white border border-gray-200 hover:bg-gray-50 rounded-[18px] text-[15px] font-bold transition-colors shadow-sm opacity-60 cursor-not-allowed">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.4 24H0V12.6h11.4V24zM24 24H12.6V12.6H24V24zM11.4 11.4H0V0h11.4v11.4zM24 11.4H12.6V0H24v11.4z" fill="#00a4ef"/>
              <path d="M11.4 11.4H0V0h11.4v11.4z" fill="#f25022"/>
              <path d="M24 11.4H12.6V0H24v11.4z" fill="#7fba00"/>
              <path d="M11.4 24H0V12.6h11.4V24z" fill="#00a4ef"/>
              <path d="M24 24H12.6V12.6H24V24z" fill="#ffb900"/>
            </svg>
            Continue with Microsoft
          </button>
        </div>

        <div className="w-full flex items-center gap-4 mb-8">
          <div className="h-px bg-gray-200 flex-1"></div>
          <span className="text-[15px] text-gray-500 font-medium">or</span>
          <div className="h-px bg-gray-200 flex-1"></div>
        </div>

        {error && (
          <div className="w-full p-3 mb-4 bg-red-50 border border-red-200 rounded-2xl text-sm font-medium text-red-600 text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="w-full space-y-5">
          <div>
            <label className="block text-[15px] font-bold text-gray-900 mb-2" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              className="w-full px-4 py-3.5 bg-[#F9FAFB] border border-gray-100 rounded-2xl text-[15px] font-semibold text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-300 transition-all"
              required
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-[15px] font-bold text-gray-900" htmlFor="password">
                Password
              </label>
              {mode === 'login' && (
                <a href="#" className="text-[14px] text-blue-500 hover:underline font-medium">
                  Forgot password?
                </a>
              )}
            </div>
            <div className="relative">
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                className="w-full px-4 py-3.5 bg-[#F9FAFB] border border-gray-100 rounded-2xl text-[15px] font-semibold text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-300 transition-all pr-12"
                required
              />
              <button type="button" className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                <Eye size={20} />
              </button>
            </div>
          </div>

          {mode === 'signup' && (
            <div>
              <label className="block text-[15px] font-bold text-gray-900 mb-2" htmlFor="confirmPassword">
                Confirm password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm password"
                className="w-full px-4 py-3.5 bg-[#F9FAFB] border border-gray-100 rounded-2xl text-[15px] font-semibold text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-300 transition-all"
                required
              />
            </div>
          )}

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-4 mt-8 bg-white text-gray-900 border border-gray-200 font-bold rounded-2xl text-lg shadow-xl transition-all transform hover:bg-gray-50 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {submitting ? 'Please wait...' : mode === 'signup' ? 'Create account' : 'Log in'}
          </button>
        </form>

        <p className="mt-8 text-center text-[15px] text-gray-800 font-medium">
          {mode === 'signup' ? (
            <>Already have an account? <button onClick={() => { setMode('login'); setError(null); }} className="text-blue-500 hover:underline font-medium bg-transparent border-none p-0 cursor-pointer">Log in</button></>
          ) : (
            <>Don't have an account? <button onClick={() => { setMode('signup'); setError(null); }} className="text-blue-500 hover:underline font-medium bg-transparent border-none p-0 cursor-pointer">Sign up</button></>
          )}
        </p>
      </div>
    </div>
  );
}
