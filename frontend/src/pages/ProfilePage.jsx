import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import authService from '../services/authService';
import Navbar from '../components/common/Navbar';
import { User, Mail, Phone, Key, Save } from 'lucide-react';

const ProfilePage = () => {
  const { user, updateProfile } = useAuth();
  const [editing, setEditing] = useState(false);
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    phone_number: user?.phone_number || '',
    birth_date: user?.birth_date || '',
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePasswordChange = (e) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmitProfile = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage('');
    setError('');

    try {
      await updateProfile(formData);
      setMessage('Profile updated successfully!');
      setEditing(false);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleSubmitPassword = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    setChangingPassword(true);

    try {
      await authService.changePassword(passwordData.current_password, passwordData.new_password);
      setMessage('Password changed successfully!');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to change password');
    } finally {
      setChangingPassword(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <User className="w-8 h-8 mr-3 text-primary-600" />
            My Profile
          </h1>
          <p className="mt-2 text-gray-600">Manage your account information</p>
        </div>

        {message && (
          <div className="mb-6 rounded-md bg-green-50 p-4">
            <p className="text-sm text-green-800">{message}</p>
          </div>
        )}

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Profile Information */}
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Profile Information</h2>
            {!editing && (
              <button
                onClick={() => setEditing(true)}
                className="btn-secondary text-sm"
              >
                Edit Profile
              </button>
            )}
          </div>

          <form onSubmit={handleSubmitProfile}>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">First Name</label>
                  <input
                    type="text"
                    name="first_name"
                    className="input"
                    value={formData.first_name}
                    onChange={handleChange}
                    disabled={!editing}
                    required
                  />
                </div>

                <div>
                  <label className="label">Last Name</label>
                  <input
                    type="text"
                    name="last_name"
                    className="input"
                    value={formData.last_name}
                    onChange={handleChange}
                    disabled={!editing}
                    required
                  />
                </div>
              </div>

              <div>
                <label className="label flex items-center">
                  <Mail className="w-4 h-4 mr-2" />
                  Email Address
                </label>
                <input
                  type="email"
                  className="input bg-gray-100"
                  value={user?.email || ''}
                  disabled
                />
                <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
              </div>

              <div>
                <label className="label flex items-center">
                  <Phone className="w-4 h-4 mr-2" />
                  Phone Number
                </label>
                <input
                  type="tel"
                  name="phone_number"
                  className="input"
                  value={formData.phone_number}
                  onChange={handleChange}
                  disabled={!editing}
                  placeholder="+1234567890"
                />
              </div>

              <div>
                <label className="label">Birthday</label>
                <input
                  type="date"
                  name="birth_date"
                  className="input"
                  value={formData.birth_date || ''}
                  onChange={handleChange}
                  disabled={!editing}
                />
              </div>

              <div>
                <label className="label">Role</label>
                <input
                  type="text"
                  className="input bg-gray-100 capitalize"
                  value={user?.role || ''}
                  disabled
                />
              </div>
            </div>

            {editing && (
              <div className="flex space-x-4 mt-6">
                <button
                  type="submit"
                  disabled={saving}
                  className="btn-primary"
                >
                  <Save className="w-4 h-4 mr-2 inline" />
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setEditing(false);
                    setFormData({
                      first_name: user?.first_name || '',
                      last_name: user?.last_name || '',
                      phone_number: user?.phone_number || '',
                      birth_date: user?.birth_date || '',
                    });
                  }}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Change Password */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <Key className="w-5 h-5 mr-2" />
            Change Password
          </h2>

          <form onSubmit={handleSubmitPassword}>
            <div className="space-y-4">
              <div>
                <label className="label">Current Password</label>
                <input
                  type="password"
                  name="current_password"
                  className="input"
                  value={passwordData.current_password}
                  onChange={handlePasswordChange}
                  required
                  placeholder="Enter current password"
                />
              </div>

              <div>
                <label className="label">New Password</label>
                <input
                  type="password"
                  name="new_password"
                  className="input"
                  value={passwordData.new_password}
                  onChange={handlePasswordChange}
                  required
                  placeholder="Enter new password"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Must be at least 8 characters with uppercase, lowercase, and number
                </p>
              </div>

              <div>
                <label className="label">Confirm New Password</label>
                <input
                  type="password"
                  name="confirm_password"
                  className="input"
                  value={passwordData.confirm_password}
                  onChange={handlePasswordChange}
                  required
                  placeholder="Re-enter new password"
                />
              </div>
            </div>

            <div className="mt-6">
              <button
                type="submit"
                disabled={changingPassword}
                className="btn-primary"
              >
                {changingPassword ? 'Changing Password...' : 'Change Password'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
};

export default ProfilePage;
