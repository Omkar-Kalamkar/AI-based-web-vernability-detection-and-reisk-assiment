import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowRight, AtSign, Eye, EyeOff, LockKeyhole, ShieldCheck, UserRound } from 'lucide-react'
import Logo from '../components/Logo'
import { useAuth } from '../hooks/useAuth'
import { useToast } from '../hooks/useToast'

export default function Register() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const toast = useToast()
  const [form, setForm] = useState({ username: '', email: '', password: '', confirm: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [busy, setBusy] = useState(false)

  const update = (key) => (event) => setForm((current) => ({ ...current, [key]: event.target.value }))

  const submit = async (event) => {
    event.preventDefault()
    if (form.password !== form.confirm) {
      toast.error('Passwords do not match')
      return
    }
    if (form.password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    setBusy(true)
    try {
      await register(form.username, form.email, form.password)
      toast.success('Account created. Welcome to SecureAI!')
      navigate('/')
    } catch (error) {
      toast.error(error.message, 'Registration failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="grid-bg flex min-h-screen items-center justify-center px-5 py-12">
      <div className="w-full max-w-lg animate-fade-up">
        <div className="mb-8"><Logo /></div>
        <h1 className="font-display text-3xl font-bold text-white">Create your account</h1>
        <p className="muted mt-2">Start scanning authorized applications in minutes.</p>

        <form onSubmit={submit} className="panel mt-7 space-y-5 p-6">
          <div>
            <label className="label">Username</label>
            <div className="relative">
              <UserRound className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <input required value={form.username} onChange={update('username')} className="field pl-10" placeholder="security_analyst" />
            </div>
          </div>
          <div>
            <label className="label">Email address</label>
            <div className="relative">
              <AtSign className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
              <input type="email" required value={form.email} onChange={update('email')} className="field pl-10" placeholder="you@company.com" />
            </div>
          </div>
          <div className="grid gap-5 sm:grid-cols-2">
            <div>
              <label className="label">Password</label>
              <div className="relative">
                <LockKeyhole className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input type={showPassword ? 'text' : 'password'} required value={form.password} onChange={update('password')} className="field px-10" placeholder="8+ characters" />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white" aria-label="Toggle password visibility">
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>
            <div>
              <label className="label">Confirm password</label>
              <input type={showPassword ? 'text' : 'password'} required value={form.confirm} onChange={update('confirm')} className="field" placeholder="Repeat password" />
            </div>
          </div>
          <div className="flex items-start gap-2 rounded-xl border border-electric-500/15 bg-electric-500/[0.06] p-3 text-xs text-slate-400">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-electric-300" />
            Passwords are hashed with scrypt. Sessions expire automatically.
          </div>
          <button type="submit" className="btn-primary w-full" disabled={busy}>
            {busy ? 'Creating account...' : <>Create account <ArrowRight className="h-4 w-4" /></>}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-400">
          Already have an account? <Link to="/login" className="font-semibold text-electric-400 hover:text-electric-300">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
