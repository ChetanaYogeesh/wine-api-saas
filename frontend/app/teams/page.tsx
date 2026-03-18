'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { teams } from '../../lib/api';

interface Team {
  id: number;
  name: string;
  owner_id: number;
  created_at: string;
  members?: TeamMember[];
}

interface TeamMember {
  id: number;
  user_id: number;
  email: string;
  role: string;
  created_at: string;
}

export default function TeamsPage() {
  const router = useRouter();
  
  const [teamList, setTeamList] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showMemberForm, setShowMemberForm] = useState<number | null>(null);
  const [newTeamName, setNewTeamName] = useState('');
  const [newMemberEmail, setNewMemberEmail] = useState('');
  const [newMemberRole, setNewMemberRole] = useState('member');
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    loadTeams();
  }, [router]);

  const loadTeams = async () => {
    try {
      const data = await teams.list();
      setTeamList(data);
    } catch (err) {
      console.error('Failed to load teams:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadTeamDetails = async (teamId: number) => {
    try {
      const data = await teams.get(teamId);
      setTeamList(prev => prev.map(t => t.id === teamId ? { ...t, members: data.members || [] } : t));
    } catch (err) {
      console.error('Failed to load team details:', err);
    }
  };

  const handleCreateTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setCreating(true);

    try {
      await teams.create(newTeamName);
      setSuccess('Team created successfully');
      setNewTeamName('');
      setShowCreateForm(false);
      loadTeams();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create team');
    } finally {
      setCreating(false);
    }
  };

  const handleAddMember = async (teamId: number, e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await teams.addMember(teamId, newMemberEmail, newMemberRole);
      setSuccess('Member added successfully');
      setNewMemberEmail('');
      setNewMemberRole('member');
      setShowMemberForm(null);
      loadTeamDetails(teamId);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to add member');
    }
  };

  const handleRemoveMember = async (teamId: number, memberId: number) => {
    if (!confirm('Are you sure you want to remove this member?')) {
      return;
    }

    try {
      await teams.removeMember(teamId, memberId);
      setSuccess('Member removed');
      loadTeamDetails(teamId);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to remove member');
    }
  };

  const handleDeleteTeam = async (teamId: number) => {
    if (!confirm('Are you sure you want to delete this team?')) {
      return;
    }

    try {
      await teams.delete(teamId);
      setSuccess('Team deleted');
      loadTeams();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete team');
    }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="container">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <h1>Teams</h1>
          <button onClick={() => setShowCreateForm(!showCreateForm)} className="btn btn-primary">
            {showCreateForm ? 'Cancel' : '+ Create Team'}
          </button>
        </div>

        {error && <div className="alert alert-error" style={{ marginBottom: '1rem' }}>{error}</div>}
        {success && <div className="alert alert-success" style={{ marginBottom: '1rem' }}>{success}</div>}

        {showCreateForm && (
          <div className="card" style={{ marginBottom: '2rem' }}>
            <h2 style={{ marginBottom: '1rem' }}>Create New Team</h2>
            <form onSubmit={handleCreateTeam} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Team Name</label>
                <input
                  type="text"
                  className="input"
                  value={newTeamName}
                  onChange={(e) => setNewTeamName(e.target.value)}
                  placeholder="Engineering Team"
                  required
                  style={{ width: '300px' }}
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={creating}>
                {creating ? 'Creating...' : 'Create Team'}
              </button>
            </form>
          </div>
        )}

        <div className="card">
          <h2 style={{ marginBottom: '1.5rem' }}>Your Teams</h2>
          
          {teamList.length === 0 ? (
            <p style={{ color: 'var(--gray-500)' }}>
              No teams yet. Create a team to collaborate with others.
            </p>
          ) : (
            teamList.map((team) => (
              <div key={team.id} style={{ 
                border: '1px solid #e5e7eb', 
                borderRadius: '8px', 
                padding: '1.5rem', 
                marginBottom: '1rem' 
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold' }}>{team.name}</h3>
                    <p style={{ fontSize: '0.875rem', color: 'var(--gray-500)' }}>
                      Created {new Date(team.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button 
                      onClick={() => setShowMemberForm(showMemberForm === team.id ? null : team.id)}
                      className="btn btn-primary"
                      style={{ padding: '0.5rem 1rem' }}
                    >
                      Add Member
                    </button>
                    <button
                      onClick={() => handleDeleteTeam(team.id)}
                      className="btn"
                      style={{ 
                        backgroundColor: '#fee2e2', 
                        color: '#991b1b',
                        padding: '0.5rem 1rem'
                      }}
                    >
                      Delete
                    </button>
                  </div>
                </div>

                {showMemberForm === team.id && (
                  <form onSubmit={(e) => handleAddMember(team.id, e)} style={{ 
                    display: 'flex', 
                    gap: '1rem', 
                    marginBottom: '1rem',
                    padding: '1rem',
                    backgroundColor: '#f9fafb',
                    borderRadius: '4px'
                  }}>
                    <input
                      type="email"
                      className="input"
                      value={newMemberEmail}
                      onChange={(e) => setNewMemberEmail(e.target.value)}
                      placeholder="member@example.com"
                      required
                      style={{ flex: 1 }}
                    />
                    <select
                      className="input"
                      value={newMemberRole}
                      onChange={(e) => setNewMemberRole(e.target.value)}
                      style={{ width: '150px' }}
                    >
                      <option value="member">Member</option>
                      <option value="admin">Admin</option>
                    </select>
                    <button type="submit" className="btn btn-primary">Add</button>
                  </form>
                )}

                {team.members && team.members.length > 0 && (
                  <div>
                    <h4 style={{ fontSize: '0.875rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>Members</h4>
                    <table style={{ width: '100%', fontSize: '0.875rem' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid #e5e7eb' }}>
                          <th style={{ textAlign: 'left', padding: '0.5rem 0' }}>Email</th>
                          <th style={{ textAlign: 'left', padding: '0.5rem 0' }}>Role</th>
                          <th style={{ textAlign: 'left', padding: '0.5rem 0' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {team.members.map((member) => (
                          <tr key={member.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                            <td style={{ padding: '0.5rem 0' }}>{member.email}</td>
                            <td style={{ padding: '0.5rem 0' }}>
                              <span style={{
                                padding: '0.125rem 0.5rem',
                                borderRadius: '4px',
                                fontSize: '0.75rem',
                                backgroundColor: member.role === 'admin' ? '#dbeafe' : '#f3f4f6',
                                color: member.role === 'admin' ? '#1e40af' : '#6b7280',
                              }}>
                                {member.role}
                              </span>
                            </td>
                            <td style={{ padding: '0.5rem 0' }}>
                              <button
                                onClick={() => handleRemoveMember(team.id, member.id)}
                                style={{ 
                                  background: 'none', 
                                  border: 'none', 
                                  color: '#991b1b',
                                  cursor: 'pointer',
                                  fontSize: '0.875rem'
                                }}
                              >
                                Remove
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        <div style={{ marginTop: '2rem' }}>
          <Link href="/dashboard" className="btn btn-secondary">Back to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
