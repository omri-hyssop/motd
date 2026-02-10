import { useEffect, useMemo, useState } from 'react';
import Navbar from '../components/common/Navbar';
import Loading from '../components/common/Loading';
import userService from '../services/userService';

const emptyForm = {
  username: '',
  email: '',
  password: '',
  first_name: '',
  last_name: '',
  phone_number: '',
  birth_date: '',
  role: 'user',
};

const AdminUsersPage = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);

  const canSubmit = useMemo(() => {
    return (
      form.email.trim().length > 0 &&
      form.password.trim().length > 0 &&
      form.first_name.trim().length > 0 &&
      form.last_name.trim().length > 0 &&
      !saving
    );
  }, [form, saving]);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await userService.listUsers({ per_page: 200, page: 1 });
      setUsers(data.users || []);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to load users.');
    } finally {
      setLoading(false);
    }
  };

  const openCreate = () => {
    setSuccess('');
    setError('');
    setForm(emptyForm);
    setModalOpen(true);
  };

  const closeModal = () => {
    if (saving) return;
    setModalOpen(false);
  };

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      await userService.createUser({
        username: form.username.trim() || undefined,
        email: form.email.trim(),
        password: form.password,
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        phone_number: form.phone_number.trim() || undefined,
        birth_date: form.birth_date || undefined,
        role: form.role,
      });
      setSuccess('User created.');
      setModalOpen(false);
      setForm(emptyForm);
      await fetchUsers();
    } catch (err) {
      console.error(err);
      const apiError = err?.response?.data;
      const validationMessages = apiError?.messages
        ? Object.entries(apiError.messages)
            .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : String(msgs)}`)
            .join(' • ')
        : null;
      setError(validationMessages || apiError?.error || 'Failed to create user.');
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (user) => {
    if (!window.confirm(`${user.is_active ? 'Deactivate' : 'Activate'} ${user.email}?`)) return;
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      await userService.updateUser(user.id, { is_active: !user.is_active });
      setSuccess('User updated.');
      await fetchUsers();
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.error || 'Failed to update user.');
    } finally {
      setSaving(false);
    }
  };

  const toggleAdmin = async (user) => {
    const nextRole = user.role === 'admin' ? 'user' : 'admin';
    const verb = nextRole === 'admin' ? 'Make admin' : 'Remove admin';
    if (!window.confirm(`${verb} for ${user.email}?`)) return;
    try {
      setSaving(true);
      setError('');
      setSuccess('');
      await userService.updateUser(user.id, { role: nextRole });
      setSuccess('User updated.');
      await fetchUsers();
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.error || 'Failed to update user.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Manage Users</h1>
            <p className="mt-2 text-gray-600">Create, activate, and deactivate user accounts.</p>
          </div>
          <button className="btn-primary" onClick={openCreate}>
            Add User
          </button>
        </div>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
        {success && (
          <div className="mb-4 rounded-md bg-green-50 p-4">
            <p className="text-sm text-green-800">{success}</p>
          </div>
        )}

        {loading ? (
          <Loading message="Loading users..." />
        ) : (
          <div className="card overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Username</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Role</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-900">{u.full_name || `${u.first_name} ${u.last_name}`}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{u.email}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{u.username || '-'}</td>
                    <td className="px-4 py-3 text-sm text-gray-700">{u.role}</td>
                    <td className="px-4 py-3 text-sm">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          u.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {u.is_active ? 'active' : 'inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-sm">
                      <div className="flex items-center justify-end gap-2">
                        <button className="btn-secondary" onClick={() => toggleAdmin(u)} disabled={saving}>
                          {u.role === 'admin' ? 'Remove Admin' : 'Make Admin'}
                        </button>
                        <button className="btn-secondary" onClick={() => toggleActive(u)} disabled={saving}>
                          {u.is_active ? 'Deactivate' : 'Activate'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
                {users.length === 0 && (
                  <tr>
                    <td className="px-4 py-6 text-sm text-gray-500" colSpan={6}>
                      No users.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-2xl bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-4 border-b flex items-center justify-between gap-4">
              <div className="text-lg font-semibold text-gray-900">Add User</div>
              <button className="btn-secondary" onClick={closeModal} disabled={saving}>
                Close
              </button>
            </div>

            <form onSubmit={onSubmit} className="p-4 space-y-4">
              <div>
                <label className="label">Email *</label>
                <input className="input" name="email" type="email" value={form.email} onChange={onChange} placeholder="user@example.com" required />
              </div>
              <div>
                <label className="label">Username</label>
                <input className="input" name="username" value={form.username} onChange={onChange} placeholder="Optional (defaults from email)" />
              </div>
              <div>
                <label className="label">Password *</label>
                <input className="input" name="password" type="password" value={form.password} onChange={onChange} placeholder="Temporary password" required />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">First name *</label>
                  <input className="input" name="first_name" value={form.first_name} onChange={onChange} required />
                </div>
                <div>
                  <label className="label">Last name *</label>
                  <input className="input" name="last_name" value={form.last_name} onChange={onChange} required />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Phone</label>
                  <input className="input" name="phone_number" value={form.phone_number} onChange={onChange} placeholder="+1..." />
                </div>
                <div>
                  <label className="label">Role</label>
                  <select className="input" name="role" value={form.role} onChange={onChange}>
                    <option value="user">user</option>
                    <option value="admin">admin</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="label">Birthday</label>
                <input className="input" name="birth_date" type="date" value={form.birth_date} onChange={onChange} />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2">
                <button type="button" className="btn-secondary" onClick={closeModal} disabled={saving}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={!canSubmit}>
                  {saving ? 'Saving...' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default AdminUsersPage;
