import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, Sparkles, Zap } from 'lucide-react'
import Logo from '../components/Logo'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const toast = useToast()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    setBusy(true)
    try {
      await login(email, password)
      toast.success('Signed in successfully')
      navigate('/')
    } catch (error) {
      toast.error(error.message, 'Login failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="grid-bg min-h-screen lg:grid lg:grid-cols-[1.1fr_1fr]">
      <div className="relative hidden flex-col justify-between overflow-hidden border-r border-white/[0.06] p-12 lg:flex">
        <div className="absolute -left-32 top-1/3 h-96 w-96 rounded-full bg-electric-600/20 blur-[120px]" />
        <Logo />
        <div className="relative max-w-lg">
          <span className="chip mb-6 text-electric-300"><Sparkles className="h-3 w-3" /> AI-powered security intelligence</span>
          <h1 className="font-display text-5xl font-bold leading-tight tracking-tight text-white">
            Know your risks.<br /><span className="bg-gradient-to-r from-electric-400 to-electric-600 bg-clip-text text-transparent">Fix them faster.</span>
          </h1>
          <p className="muted mt-5 text-base">
            Safe, passive vulnerability detection with transparent risk scoring and beginner-friendly remediation guidance.
          </p>
          <div className="mt-10 space-y-4">
            {[
              [ShieldCheck, 'Scope-validated, non-destructive scanning'],
              [Zap, 'Security score, severity charts and trends'],
              [Sparkles, 'Local AI explanations — no external API required'],
            ].map(([Icon, text]) => (
              <div key={text} className="flex items-center gap-3 text-sm text-slate-300">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-electric-500/20 bg-electric-500/10 text-electric-300">
                  <Icon className="h-4 w-4" />
                </div>
                {text}
              </div>
            ))}
          </div>
        </div>
        <p className="text-xs text-slate-600">For authorized testing only. Local lab mode enabled by default.</p>
      </div>

      <div className="flex items-center justify-center px-5 py-12">
        <div className="w-full max-w-md animate-fade-up">
          <div className="mb-8 lg:hidden"><Logo /></div>
          <h2 className="font-display text-3xl font-bold text-white">Sign in</h2>
          <p className="muted mt-2">Access your SecureAI security workspace.</p>

          <form onSubmit={submit} className="panel mt-8 space-y-5 p-6">
            <div>
              <label className="label">Email address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input type="email" required value={email} onChange={(event) => setEmail(event.target.value)} className="field pl-10" placeholder="you@company.com" />
              </div>
            </div>
            <div>
              <label className="label">Password</label>
              <div className="relative">
                <LockKeyhole className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input type={showPassword ? 'text' : 'password'} required value={password} onChange={(event) => setPassword(event.target.value)} className="field px-10" placeholder="Enter your password" />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white" aria-label="Toggle password visibility">
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            <button type="submit" className="btn-primary w-full" disabled={busy}>
              {busy ? 'Signing in...' : <>Sign in <ArrowRight className="h-4 w-4" /></>}
            </button>
            <button
              type="button"
              onClick={() => { setEmail('demo@secureai.local'); setPassword('Demo@12345') }}
              className="btn-ghost w-full"
            >
              Fill demo credentials
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-slate-400">
            New to SecureAI? <Link to="/register" className="font-semibold text-electric-400 hover:text-electric-300">Create an account</Link>
          </p>
          <p className="mt-4 text-center text-[11px] text-slate-600">Demo: demo@secureai.local / Demo@12345</p>
        </div>
      </div>
    </div>
  )
}
