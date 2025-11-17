import React, { useEffect, useState, ChangeEvent } from 'react'
import { userService } from '@/services/userService'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts'
import axios from 'axios'

/*
  Single-file React component (TypeScript) updated with improved UI/CSS.
  - Clean, modern card design
  - Polished tabs with active indicator
  - Reusable Modal component
  - Styled forms, inputs, file upload preview
  - Responsive grid and table for analytics
  - Accessible buttons and subtle animations

  No external UI libraries required.
*/

interface UserProfile {
  id: number
  email: string
  username?: string
  full_name?: string
  learning_goals?: string[]
  daily_study_time?: number
  difficulty_preference?: string
  created_at?: string
  oauth_avatar?: string
  oauth_provider?: string
  is_oauth_account?: boolean
  token?: string
}

interface LearningStats {
  words_learned: number
  retention_rate: number
  avg_quiz_score: number
  progress: number
  active_days: number
  progress_over_time: { month: string; progress: number }[]
  retention_data: { name: string; value: number }[]
  quiz_by_topic: { topic: string; score: number }[]
}

function IconButton({ children, title, onClick, style }: any) {
  return (
    <button
      aria-label={title}
      title={title}
      onClick={onClick}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 8,
        padding: '8px 12px',
        borderRadius: 10,
        border: '1px solid rgba(10,20,40,0.06)',
        background: 'white',
        cursor: 'pointer',
        boxShadow: '0 1px 4px rgba(6,24,44,0.06)',
        transition: 'transform .12s ease, box-shadow .12s ease',
        ...style,
      }}
      onMouseOver={(e) => (e.currentTarget.style.transform = 'translateY(-2px)')}
      onMouseOut={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
    >
      {children}
    </button>
  )
}

function Modal({ children, onClose }: { children: React.ReactNode; onClose: () => void }) {
  return (
    <div className="modal-overlay" role="dialog" aria-modal="true">
      <div className="modal-box">
        <button className="modal-close" onClick={onClose} aria-label="Close modal">✕</button>
        {children}
      </div>
    </div>
  )
}

export default function ProfileOverviewFull() {
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'analytics'>('overview')
  const [stats, setStats] = useState<LearningStats | null>(null)

  // UI state for modals
  const [showEditModal, setShowEditModal] = useState(false)
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [showPlanModal, setShowPlanModal] = useState(false)

  // Forms
  const [editForm, setEditForm] = useState({ full_name: '', learning_goals: '', difficulty_preference: 'medium', daily_study_time: 30 })
  const [passwordForm, setPasswordForm] = useState({ old_password: '', new_password: '', confirm_password: '' })
  const [avatarFile, setAvatarFile] = useState<File | null>(null)

  // notifications
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadData() {
      setLoading(true)
      try {
        const [profile, learningStats] = await Promise.all([userService.getProfile(), userService.getLearningStats()])
        setUser(profile)
        setStats(learningStats)
        // initialize edit form
        setEditForm({
          full_name: profile.full_name || '',
          learning_goals: (profile.learning_goals || []).join(', '),
          difficulty_preference: profile.difficulty_preference || 'medium',
          daily_study_time: profile.daily_study_time || 30,
        })
      } catch (e: any) {
        console.error(e)
        setError('Failed to load user data.')
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  useEffect(() => {
    if (message) {
      const t = setTimeout(() => setMessage(null), 3500)
      return () => clearTimeout(t)
    }
  }, [message])

  useEffect(() => {
    if (error) {
      const t = setTimeout(() => setError(null), 5000)
      return () => clearTimeout(t)
    }
  }, [error])

  if (loading) return <p className="center">Loading profile...</p>
  if (!user) return <p className="center">Could not load user data.</p>

  const displayInitials = user.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').toUpperCase()
    : user.username?.[0]?.toUpperCase() || 'U'

  const joinedDate = user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'

  // --- Handlers ---
  async function handleEditSubmit(e?: React.FormEvent) {
    if (e) e.preventDefault()
    try {
      const payload = {
        full_name: editForm.full_name || undefined,
        learning_goals: editForm.learning_goals ? editForm.learning_goals.split(',').map((s) => s.trim()).filter(Boolean) : [],
        difficulty_preference: editForm.difficulty_preference,
        daily_study_time: Number(editForm.daily_study_time) || 0,
      }
      const updated = await userService.updateProfile(payload)
      setUser(updated)
      setShowEditModal(false)
      setMessage('Profile updated successfully')
    } catch (e: any) {
      console.error(e)
      setError(e?.response?.data?.detail || 'Update failed')
    }
  }

  async function handlePasswordChange(e?: React.FormEvent) {
    if (e) e.preventDefault()
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError('New password and confirmation do not match')
      return
    }
    try {
      await userService.changePassword(passwordForm.old_password, passwordForm.new_password)
      setShowPasswordModal(false)
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' })
      setMessage('Password changed successfully')
    } catch (e: any) {
      console.error(e)
      setError(e?.response?.data?.detail || 'Password change failed')
    }
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] || null
    setAvatarFile(f)
  }

  async function handleUploadAvatar(file: File) {
  if (!file) {
    toast.error('No file selected')
    return
  }

  try {
    const updatedUser = await userService.uploadAvatar(file)

    // Update Zustand immediately after upload
    const { updateUser } = useAuthStore.getState()
    updateUser(updatedUser)

    // Show notification and close modal
    toast.success('Avatar uploaded successfully!')
    setMessage('Avatar uploaded successfully')
    setShowUploadModal(false)
    setAvatarFile(null)
  } catch (err: any) {
    console.error('❌ Upload avatar failed:', err)
    toast.error(err?.response?.data?.detail || 'Upload failed')
    setError(err?.response?.data?.detail || 'Upload failed')
  }
}

  function openEdit() {
    setEditForm({
      full_name: user?.full_name || '',
      learning_goals: (user?.learning_goals || []).join(', '),
      difficulty_preference: user?.difficulty_preference || 'medium',
      daily_study_time: user?.daily_study_time || 30,
    })
    setShowEditModal(true)
  }

  function openPlan() {
    setShowPlanModal(true)
  }

  // helper: formatted percent
  const pct = (v?: number) => (typeof v === 'number' ? `${Math.round(v * 100)}%` : '—')

  return (
    <div className="page-wrap">
      {/* global styles */}
      <style dangerouslySetInnerHTML={{ __html: `
        :root{
          --bg:#f6f8fb; --card:#ffffff; --muted:#6b7280; --accent:#1e40af; --glass: rgba(255,255,255,0.6);
        }
        *{box-sizing:border-box}
        .page-wrap{max-width:1100px;margin:28px auto;padding:20px;font-family:Inter,ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,'Helvetica Neue',Arial}
        .center{text-align:center;margin-top:36px;color:var(--muted)}
        .profile-card{background:linear-gradient(180deg, rgba(255,255,255,0.9), var(--card));padding:20px;border-radius:14px;box-shadow:0 8px 30px rgba(14,30,70,0.06);display:flex;gap:18px;align-items:center}
        .avatar{width:96px;height:96px;border-radius:14px;overflow:hidden;flex-shrink:0;border:2px solid rgba(10,20,40,0.04);display:flex;align-items:center;justify-content:center;font-weight:700;background:linear-gradient(135deg,#e8f0ff,#ffffff);font-size:28px;color:var(--accent)}
        .profile-info{flex:1}
        .profile-name{font-size:20px;font-weight:700}
        .profile-email{color:var(--muted);font-size:13px}
        .joined{font-size:13px;color:var(--muted);margin-top:6px}
        .actions{margin-top:12px;display:flex;gap:8px;flex-wrap:wrap}
        .actions .primary{background:linear-gradient(90deg,var(--accent),#3b82f6);color:white;border:none;padding:10px 14px;border-radius:10px;cursor:pointer;font-weight:600}
        .tabbar{display:flex;background:transparent;margin-top:18px;border-bottom:1px solid rgba(15,23,42,0.06);gap:8px;border-radius:10px;overflow:hidden}
        .tab{flex:1;padding:12px 14px;text-align:center;cursor:pointer;font-weight:600;color:var(--muted);background:transparent;border:none}
        .tab.active{color:var(--accent);position:relative}
        .tab.active::after{content:'';position:absolute;left:24%;right:24%;bottom:0;height:3px;background:linear-gradient(90deg,var(--accent),#3b82f6);border-radius:4px}
        .grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:18px}
        .stat-card{background:var(--card);padding:14px;border-radius:10px;box-shadow:0 4px 18px rgba(12,24,48,0.04);}
        .stat-title{font-weight:700;color:var(--accent)}
        .stat-value{font-size:20px;margin-top:8px;color:var(--accent)}

        /* analytics layout */
        .analytics-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px}
        .chart-card{background:var(--card);padding:14px;border-radius:10px}
        .table-panel{background:var(--card);padding:14px;border-radius:10px;margin-top:18px}
        table{width:100%;border-collapse:collapse}
        th,td{padding:10px;text-align:left;border-bottom:1px solid rgba(15,23,42,0.04)}
        th{font-weight:700;color:var(--muted);font-size:13px}
        td.score{font-weight:700;color:var(--accent)}

        /* modal */
        .modal-overlay{position:fixed;inset:0;background:linear-gradient(0deg, rgba(2,6,23,0.45), rgba(2,6,23,0.45));display:flex;align-items:center;justify-content:center;padding:20px;z-index:60}
        .modal-box{background:var(--card);padding:22px;border-radius:12px;box-shadow:0 24px 48px rgba(2,6,23,0.4);position:relative;max-height:90vh;overflow:auto;width:min(92vw,720px)}
        .modal-close{position:absolute;right:12px;top:12px;border:none;background:transparent;font-size:18px;cursor:pointer}

        /* form styles */
        .form-row{display:grid;grid-template-columns:1fr 1fr;gap:10px}
        label{display:flex;flex-direction:column;font-size:13px;color:var(--muted);gap:6px}
        input[type=text],input[type=password],input[type=number],select,textarea{padding:10px;border-radius:8px;border:1px solid rgba(10,20,40,0.06);outline:none;font-size:14px}
        input[type=file]{padding:8px}
        .form-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:14px}
        .btn-cancel{background:#f3f4f6;border:none;padding:10px 12px;border-radius:8px;cursor:pointer}
        .btn-save{background:linear-gradient(90deg,var(--accent),#3b82f6);color:white;border:none;padding:10px 12px;border-radius:8px;cursor:pointer}

        /* file preview */
        .avatar-preview{width:120px;height:120px;border-radius:12px;overflow:hidden;border:1px solid rgba(10,20,40,0.06);display:flex;align-items:center;justify-content:center}

        @media (max-width:900px){
          .grid-3{grid-template-columns:1fr}
          .analytics-grid{grid-template-columns:1fr}
          .profile-card{flex-direction:column;align-items:flex-start}
        }
      ` }} />

      <div className="profile-card">
        <div className="avatar" aria-hidden>
          {user.oauth_avatar ? (
            <img src={user.oauth_avatar} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 10 }} />
          ) : (
            <span>{displayInitials}</span>
          )}
        </div>

        <div className="profile-info">
          <div className="profile-name">{user.full_name || user.username || 'Unnamed User'}</div>
          <div className="profile-email">{user.email}</div>
          <div className="joined"><strong>Joined:</strong> {joinedDate}</div>

          <div className="actions">
            <button className="primary" onClick={openEdit}>✏️ Edit Profile</button>
            <IconButton title="Change password" onClick={() => setShowPasswordModal(true)}>🔒 Change Password</IconButton>
            <IconButton title="Upload avatar" onClick={() => setShowUploadModal(true)}>📤 Upload Avatar</IconButton>
            <IconButton title="View learning plan" onClick={openPlan}>📖 Plan</IconButton>
          </div>
        </div>
      </div>

      {error && <div style={{ background: '#fff5f5', padding: 12, borderRadius: 10, color: '#b91c1c', marginTop: 12 }}>{error}</div>}
      {message && <div style={{ background: '#f0fdf4', padding: 12, borderRadius: 10, color: '#064e3b', marginTop: 12 }}>{message}</div>}

      <div style={{ marginTop: 18 }}>
        <div className="tabbar">
          <button className={`tab ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>Profile Overview</button>
          <button className={`tab ${activeTab === 'analytics' ? 'active' : ''}`} onClick={() => setActiveTab('analytics')}>Learning Analytics</button>
        </div>

        {activeTab === 'overview' && (
          <><div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: 20,
              marginTop: 24,
            }}
          >
            {/* Learning Goals */}
            <div
              style={{
                background: "#ffffff",
                borderRadius: 12,
                padding: "16px 18px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
                border: "1px solid #e2e8f0",
                transition: "transform 0.2s ease, box-shadow 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-3px)"
                e.currentTarget.style.boxShadow = "0 4px 10px rgba(0,0,0,0.08)"
              } }
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)"
                e.currentTarget.style.boxShadow = "0 2px 6px rgba(0,0,0,0.05)"
              } }
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#1d4ed8" }}>
                <span style={{ fontSize: 18 }}>💡</span>
                <div style={{ fontWeight: 600, fontSize: 15 }}>Learning Goals</div>
              </div>
              <div
                style={{
                  marginTop: 8,
                  color: "#334155",
                  fontSize: 14,
                  lineHeight: 1.5,
                }}
              >
                {user.learning_goals?.length ? user.learning_goals.join(", ") : "Not set"}
              </div>
            </div>

            {/* Study Schedule */}
            <div
              style={{
                background: "#ffffff",
                borderRadius: 12,
                padding: "16px 18px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
                border: "1px solid #e2e8f0",
                transition: "transform 0.2s ease, box-shadow 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-3px)"
                e.currentTarget.style.boxShadow = "0 4px 10px rgba(0,0,0,0.08)"
              } }
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)"
                e.currentTarget.style.boxShadow = "0 2px 6px rgba(0,0,0,0.05)"
              } }
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#1d4ed8" }}>
                <span style={{ fontSize: 18 }}>⏰</span>
                <div style={{ fontWeight: 600, fontSize: 15 }}>Study Schedule</div>
              </div>
              <div
                style={{
                  marginTop: 8,
                  color: "#334155",
                  fontSize: 14,
                  lineHeight: 1.5,
                }}
              >
                {user.daily_study_time ? `Daily, ${user.daily_study_time} mins` : "Not set"}
              </div>
            </div>

            {/* Difficulty */}
            <div
              style={{
                background: "#ffffff",
                borderRadius: 12,
                padding: "16px 18px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
                border: "1px solid #e2e8f0",
                transition: "transform 0.2s ease, box-shadow 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-3px)"
                e.currentTarget.style.boxShadow = "0 4px 10px rgba(0,0,0,0.08)"
              } }
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)"
                e.currentTarget.style.boxShadow = "0 2px 6px rgba(0,0,0,0.05)"
              } }
            >
              <div style={{ display: "flex", alignItems: "center", gap: 8, color: "#1d4ed8" }}>
                <span style={{ fontSize: 18 }}>🎯</span>
                <div style={{ fontWeight: 600, fontSize: 15 }}>Difficulty</div>
              </div>
              <div
                style={{
                  marginTop: 8,
                  color: "#334155",
                  fontSize: 14,
                  lineHeight: 1.5,
                }}
              >
                {user.difficulty_preference || "Not set"}
              </div>
            </div>
          </div><div
            style={{
              marginTop: 24,
              borderRadius: 14,
              overflow: "hidden",
              boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
              background: "var(--card, #fff)",
            }}
          >
              {/* Header */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '7px',
                  paddingBottom: '5px',
                  marginBottom: '10px',
                  marginTop: '10px',
                  marginLeft: '10px',
                  borderBottom: '2px solid rgb(37, 99, 235)',
                  width: 'fit-content',
    }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#2563eb" viewBox="0 0 24 24">
                  <path d="M12 12c2.7 0 4.9-2.2 4.9-4.9S14.7 2.2 12 2.2 7.1 4.4 7.1 7.1 9.3 12 12 12zm0 2.4c-3.1 0-9.3 1.6-9.3 4.8V22h18.6v-2.8c0-3.2-6.2-4.8-9.3-4.8z" />
                </svg>
                <h3 style={{ fontSize: 15, fontWeight: 600, color: "#1e3a8a", margin: 0 }}>Account</h3>
              </div>

              {/* Body */}
              <div
                style={{
                  padding: 20,
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                  gap: 16,
                  background: "#fafafa",
                }}
              >
                <div
                  style={{
                    background: "#fff",
                    borderRadius: 10,
                    padding: "12px 16px",
                    boxShadow: "0 2px 6px rgba(0,0,0,0.04)",
                  }}
                >
                  <div style={{ color: "#6b7280", fontSize: 13, marginBottom: 4 }}>
                    ID
                  </div>
                  <div style={{ fontWeight: 600, color: "#111827" }}>{user.id}</div>
                </div>

                <div
                  style={{
                    background: "#fff",
                    borderRadius: 10,
                    padding: "12px 16px",
                    boxShadow: "0 2px 6px rgba(0,0,0,0.04)",
                  }}
                >
                  <div style={{ color: "#6b7280", fontSize: 13, marginBottom: 4 }}>
                    Email
                  </div>
                  <div style={{ fontWeight: 600, color: "#111827" }}>{user.email}</div>
                </div>

                <div
                  style={{
                    background: "#fff",
                    borderRadius: 10,
                    padding: "12px 16px",
                    boxShadow: "0 2px 6px rgba(0,0,0,0.04)",
                  }}
                >
                  <div style={{ color: "#6b7280", fontSize: 13, marginBottom: 4 }}>
                    Provider
                  </div>
                  <div style={{ fontWeight: 600, color: "#111827" }}>
                    {user.oauth_provider || "local"}
                  </div>
                </div>
              </div>
            </div></>
        )}

        {activeTab === 'analytics' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5,1fr)', gap: 12, marginTop: 12 }}>
              {[
                { title: 'Words Learned', value: stats?.words_learned?.toLocaleString() ?? '—', note: 'vs last month' },
                { title: 'Retention Rate', value: stats ? `${Math.round((stats.retention_rate ?? 0) * 100)}%` : '—', note: '' },
                { title: 'Avg Quiz Score', value: stats ? `${Math.round((stats.avg_quiz_score ?? 0) * 100)}%` : '—', note: '' },
                { title: 'Learning Progress', value: stats ? `${Math.round((stats.progress ?? 0) * 100)}%` : '—', note: '' },
                { title: 'Active Days', value: stats?.active_days ? `${stats.active_days}/30` : '—', note: '' },
              ].map((item, i) => (
                <div key={i} className="stat-card">
                  <div className="stat-title">{item.title}</div>
                  <div className="stat-value">{item.value}</div>
                  <div style={{ fontSize: 12, color: 'var(--muted)' }}>{item.note}</div>
                </div>
              ))}
            </div>

            <div className="analytics-grid">
              <div className="chart-card">
                <h4 style={{ marginTop: 2 }}>📈 Learning Progress Over Time</h4>
                <div style={{ width: '100%', height: 260 }}>
                  <ResponsiveContainer width="100%" height={240}>
                    <LineChart data={stats?.progress_over_time ?? []}>
                      <XAxis dataKey="month" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="progress" stroke="#1e40af" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="chart-card">
                <h4 style={{ marginTop: 2 }}>🎯 Retention vs. Review Words</h4>
                <div style={{ width: '100%', height: 240 }}>
                  <ResponsiveContainer width="100%" height={240}>
                    <PieChart>
                      <Pie data={stats?.retention_data ?? []} cx="50%" cy="50%" outerRadius={80} dataKey="value">
                        <Cell fill="#4c8aff" />
                        <Cell fill="#a3c4ff" />
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div className="table-panel">
              <h4 style={{ marginTop: 2 }}>🧠 Quiz Performance by Topic</h4>

              <div style={{ overflowX: 'auto' }}>
                <table>
                  <thead>
                    <tr>
                      <th>Topic</th>
                      <th style={{ width: 180 }}>Score</th>
                      <th style={{ width: 200 }}>Progress Bar</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(stats?.quiz_by_topic ?? []).map((q, i) => (
                      <tr key={i}>
                        <td>{q.topic}</td>
                        <td className="score">{Math.round(q.score * 100)}%</td>
                        <td>
                          <div style={{ background: 'rgba(14,30,70,0.06)', height: 10, borderRadius: 20, overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${Math.min(100, Math.round(q.score * 100))}%`, background: 'linear-gradient(90deg,#60a5fa,#1e40af)' }} />
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

            </div>

            <div style={{ marginTop: 12 }}>
              {/* Bar chart summary */}
              <div style={{ background: 'var(--card)', padding: 14, borderRadius: 10 }}>
                <div style={{ width: '100%', height: 300 }}>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={stats?.quiz_by_topic ?? []}>
                      <XAxis dataKey="topic" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="score" fill="#4c8aff" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
{/* Modals */}
{/* ========================= UPDATE PROFILE MODAL ========================= */}
{showEditModal && (
  <Modal onClose={() => setShowEditModal(false)}>
    <form onSubmit={(e) => handleEditSubmit(e)}>
      {/* HEADER */}
   
<div
  style={{
    display: "flex",
    alignItems: "center",
    gap: 8,
    paddingBottom: 6,
    marginBottom: 16,
    borderBottom: "2px solid #2563eb", // underline
    width: "fit-content", // underline only as wide as text
  }}
>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="18"
    height="18"
    fill="#2563eb"
    viewBox="0 0 24 24"
  >
    <path d="M12 12c2.7 0 4.9-2.2 4.9-4.9S14.7 2.2 12 2.2 7.1 4.4 7.1 7.1 9.3 12 12 12zm0 2.4c-3.1 0-9.3 1.6-9.3 4.8V22h18.6v-2.8c0-3.2-6.2-4.8-9.3-4.8z" />
  </svg>

  <h3
    style={{
      fontSize: 15,
      fontWeight: 600,
      color: "#1e3a8a", // dark blue for emphasis
      margin: 0,
    }}
  >
    Update Profile
  </h3>
</div>


      {/* FORM */}
      <div className="form-row" style={{ marginTop: 8 }}>
        <label>
          Full Name
          <input type="text" value={editForm.full_name} onChange={(e) => setEditForm(s => ({ ...s, full_name: e.target.value }))} />
        </label>

        <label>
          Daily Study Time (minutes)
          <input type="number" min={1} value={editForm.daily_study_time} onChange={(e) => setEditForm(s => ({ ...s, daily_study_time: Number(e.target.value) }))} />
        </label>

        <label style={{ gridColumn: '1 / -1' }}>
          Learning Goals (separated by commas)
          <input type="text" value={editForm.learning_goals} onChange={(e) => setEditForm(s => ({ ...s, learning_goals: e.target.value }))} />
        </label>

        <label>
          Preferred Difficulty
          <select value={editForm.difficulty_preference} onChange={(e) => setEditForm(s => ({ ...s, difficulty_preference: e.target.value }))}>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </label>
      </div>

      {/* ACTIONS */}
      <div className="form-actions">
        <button type="button" className="btn-cancel" onClick={() => setShowEditModal(false)}>Cancel</button>
        <button type="submit" className="btn-save">Save</button>
      </div>
    </form>
  </Modal>
)}

{/* ========================= CHANGE PASSWORD MODAL ========================= */}
{showPasswordModal && (
  <Modal onClose={() => setShowPasswordModal(false)}>
    <form onSubmit={(e) => handlePasswordChange(e)}>
      <div
  style={{
    display: "flex",
    alignItems: "center",
    gap: 8,
    paddingBottom: 6,
    marginBottom: 16,
    borderBottom: "2px solid #2563eb",
    width: "fit-content",
  }}
>
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#2563eb" viewBox="0 0 24 24">
    <path d="M12 1a5 5 0 0 0-5 5v4H5v14h14V10h-2V6a5 5 0 0 0-5-5zm-3 9V6a3 3 0 0 1 6 0v4h-6z" />
  </svg>
  <h3 style={{ fontSize: 15, fontWeight: 600, color: "#1e3a8a", margin: 0 }}>Change Password</h3>
</div>

      <div style={{ marginTop: 8, display: 'grid', gap: 10 }}>
        <label>
          Old Password
          <input type="password" value={passwordForm.old_password} onChange={(e) => setPasswordForm(s => ({ ...s, old_password: e.target.value }))} required />
        </label>
        <label>
          New Password
          <input type="password" value={passwordForm.new_password} onChange={(e) => setPasswordForm(s => ({ ...s, new_password: e.target.value }))} required minLength={6} />
        </label>
        <label>
          Confirm Password
          <input type="password" value={passwordForm.confirm_password} onChange={(e) => setPasswordForm(s => ({ ...s, confirm_password: e.target.value }))} required />
        </label>

        <div className="form-actions">
          <button type="button" className="btn-cancel" onClick={() => setShowPasswordModal(false)}>Cancel</button>
          <button type="submit" className="btn-save">Change</button>
        </div>
      </div>
    </form>
  </Modal>
)}

{/* ========================= UPLOAD AVATAR MODAL ========================= */}
{showUploadModal && (
  <Modal onClose={() => { setShowUploadModal(false); setAvatarFile(null); }}>
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (avatarFile) handleUploadAvatar(avatarFile);
      }}
    >
      <div
  style={{
    display: "flex",
    alignItems: "center",
    gap: 8,
    paddingBottom: 6,
    marginBottom: 16,
    borderBottom: "2px solid #2563eb",
    width: "fit-content",
  }}
>
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#2563eb" viewBox="0 0 24 24">
    <path d="M19 3H5c-1.1 0-2 .9-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2zm-7 3a3 3 0 1 1 0 6 3 3 0 0 1 0-6zm0 13c-2.33 0-7 1.17-7 3.5V21h14v-1.5C19 20.17 14.33 19 12 19z" />
  </svg>
  <h3 style={{ fontSize: 15, fontWeight: 600, color: "#1e3a8a", margin: 0 }}>Upload Avatar</h3>
</div>

      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (e.dataTransfer.files.length > 0) setAvatarFile(e.dataTransfer.files[0]);
        }}
        style={{
          border: '2px dashed #0a61daff',
          borderRadius: 10,
          padding: 24,
          textAlign: 'center',
          background: '#f0fdfa',
          cursor: 'pointer',
          marginBottom: 12,
        }}
        onClick={() => document.getElementById('avatarInput')?.click()}
      >
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <svg xmlns="http://www.w3.org/2000/svg" width="42" height="42" fill="#0a61daff" viewBox="0 0 24 24">
            <path d="M5 20h14v-2H5m14-9h-4V3H9v6H5l7 7 7-7z" />
          </svg>
          <p style={{ marginTop: 6, color: '#adcfffff', fontWeight: 500 }}>Drag & drop or click to select an image</p>
        </div>
        <input id="avatarInput" type="file" accept="image/*" onChange={handleFileChange} style={{ display: 'none' }} />
      </div>

      {avatarFile && (
        <div style={{ textAlign: 'center' }}>
          <div className="avatar-preview" style={{
            width: 100, height: 100, margin: '0 auto', borderRadius: '50%', overflow: 'hidden', boxShadow: '0 2px 6px rgba(0,0,0,0.1)'
          }}>
            <img src={URL.createObjectURL(avatarFile)} alt="preview" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </div>
          <div style={{ marginTop: 8, fontSize: 13, color: '#334155' }}>{avatarFile.name}</div>
        </div>
      )}

      <div className="form-actions">
        <button type="button" className="btn-cancel" onClick={() => { setShowUploadModal(false); setAvatarFile(null); }}>Cancel</button>
        <button type="submit" className="btn-save">Upload</button>
      </div>
    </form>
  </Modal>
)}

{/* ========================= STUDY PLAN MODAL ========================= */}
{showPlanModal && (
  <Modal onClose={() => setShowPlanModal(false)}>
    <div
  style={{
    display: "flex",
    alignItems: "center",
    gap: 8,
    paddingBottom: 6,
    marginBottom: 16,
    borderBottom: "2px solid #2563eb",
    width: "fit-content",
  }}
>
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#2563eb" viewBox="0 0 24 24">
    <path d="M13 2v8h8M13 2l8 8-8-8zM3 13h8v8H3z" />
  </svg>
  <h3 style={{ fontSize: 15, fontWeight: 600, color: "#1e3a8a", margin: 0 }}>Study Plan</h3>
</div>

      <p style={{ fontSize: 14, color: '#475569' }}>This section shows your study plan — you can later expand it into a detailed table or connect it with an API.</p>
      <div style={{
        display: 'grid',
        gap: 8,
        background: '#f9fafb',
        borderRadius: 8,
        padding: 12,
        marginBottom: 10,
      }}>
        <div><strong>Goals:</strong> {(user.learning_goals?.length) ? user.learning_goals.join(', ') : 'No goals set'}</div>
        <div><strong>Study Time:</strong> {user.daily_study_time ?? '—'} mins/day</div>
        <div><strong>Difficulty:</strong> {user.difficulty_preference ?? '—'}</div>
      </div>

      <div>
        <h4 style={{ fontSize: 15, fontWeight: 600, color: '#1e3a8a' }}>Weekly Task Suggestions</h4>
        <ol style={{ fontSize: 14, marginTop: 6, color: '#334155' }}>
          <li>Learn 20 new words per day</li>
          <li>Practice listening for 15 minutes</li>
          <li>Take a vocabulary test</li>
        </ol>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 14 }}>
        <button className="btn-cancel" onClick={() => setShowPlanModal(false)}>Close</button>
      </div>
    
  </Modal>
)}



    </div>
  )
}
