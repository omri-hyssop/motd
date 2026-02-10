import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import Loading from '../components/common/Loading';
import restaurantService from '../services/restaurantService';
import api from '../services/api';

const emptyForm = {
  name: '',
  contact_name: '',
  phone_number: '',
  email: '',
  address: '',
};

const AdminRestaurantsPage = () => {
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState('create'); // create|edit
  const [activeId, setActiveId] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const navigate = useNavigate();
  const [availability, setAvailability] = useState({});

  const canSubmit = useMemo(() => form.name.trim().length > 0 && !saving, [form.name, saving]);

  useEffect(() => {
    fetchRestaurants();
    fetchAvailability();
  }, []);

  const fetchRestaurants = async () => {
    try {
      setLoading(true);
      const data = await restaurantService.getRestaurants();
      setRestaurants(data);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to load restaurants.');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailability = async () => {
    try {
      const res = await api.get('/admin/restaurants/availability');
      setAvailability(res.data.availability || {});
    } catch (err) {
      console.error(err);
    }
  };

  const toggleWeekday = async (restaurantId, weekday) => {
    const key = String(restaurantId);
    const current = new Set(availability[key] || []);
    if (current.has(weekday)) current.delete(weekday);
    else current.add(weekday);
    const weekdays = Array.from(current).sort((a, b) => a - b);
    setAvailability((prev) => ({ ...prev, [key]: weekdays }));
    try {
      await api.put(`/admin/restaurants/${restaurantId}/availability`, { weekdays });
      setSuccess('Availability updated.');
    } catch (err) {
      console.error(err);
      setError('Failed to update availability.');
    }
  };

  const weekdayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const openCreate = () => {
    setSuccess('');
    setError('');
    setModalMode('create');
    setActiveId(null);
    setForm(emptyForm);
    setModalOpen(true);
  };

  const openEdit = (restaurant) => {
    setSuccess('');
    setError('');
    setModalMode('edit');
    setActiveId(restaurant.id);
    setForm({
      name: restaurant.name || '',
      contact_name: restaurant.contact_name || '',
      phone_number: restaurant.phone_number || '',
      email: restaurant.email || '',
      address: restaurant.address || '',
    });
    setModalOpen(true);
  };

  const closeModal = () => {
    if (saving) return;
    setModalOpen(false);
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;

    try {
      setSaving(true);
      setSuccess('');
      setError('');

      const payload = {
        name: form.name.trim(),
        contact_name: form.contact_name.trim() || undefined,
        phone_number: form.phone_number.trim() || undefined,
        email: form.email.trim() || undefined,
        address: form.address.trim() || undefined,
      };

      if (modalMode === 'edit' && activeId) {
        await restaurantService.updateRestaurant(activeId, payload);
        setSuccess('Restaurant updated.');
      } else {
        await restaurantService.createRestaurant(payload);
        setSuccess('Restaurant created.');
      }
      setModalOpen(false);
      setForm(emptyForm);
      await fetchRestaurants();
    } catch (err) {
      console.error(err);
      const message =
        err?.response?.data?.error ||
        (err?.response?.data?.messages ? 'Validation error.' : null) ||
        (modalMode === 'edit' ? 'Failed to update restaurant.' : 'Failed to create restaurant.');
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  const onDeactivate = async (restaurantId) => {
    if (!window.confirm('Deactivate this restaurant?')) return;
    try {
      setError('');
      setSuccess('');
      await restaurantService.deleteRestaurant(restaurantId);
      setSuccess('Restaurant deactivated.');
      await fetchRestaurants();
    } catch (err) {
      console.error(err);
      setError('Failed to deactivate restaurant.');
    }
  };

  return (
    <>
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Manage Restaurants</h1>
            <p className="mt-2 text-gray-600">Set availability and menus for restaurants.</p>
          </div>
          <button className="btn-primary" onClick={openCreate}>
            Add Restaurant
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

        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Restaurants</h2>
          {loading ? (
            <Loading message="Loading restaurants..." />
          ) : restaurants.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Availability
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {restaurants.map((r) => (
                    <tr key={r.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-900">{r.name}</td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex items-center gap-2">
                          {['M', 'T', 'W', 'T', 'F'].map((label, i) => {
                            const selected = (availability[String(r.id)] || []).includes(i);
                            return (
                              <button
                                key={`${r.id}-${label}-${i}`}
                                type="button"
                                disabled={!r.is_active}
                                onClick={() => toggleWeekday(r.id, i)}
                                className={`h-8 w-8 rounded-full border flex items-center justify-center text-xs font-semibold ${
                                  selected
                                    ? 'bg-primary-600 text-white border-primary-600'
                                    : 'bg-gray-100 text-gray-700 border-gray-200'
                                } ${!r.is_active ? 'opacity-60 cursor-not-allowed' : ''}`}
                                title={weekdayLabels[i]}
                              >
                                {label}
                              </button>
                            );
                          })}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            r.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {r.is_active ? 'active' : 'inactive'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right text-sm">
                        {r.is_active ? (
                          <div className="flex items-center justify-end gap-2">
                            <button className="btn-secondary" onClick={() => openEdit(r)}>
                              Edit
                            </button>
                            <button className="btn-secondary" onClick={() => navigate(`/admin/menus?restaurant_id=${r.id}`)}>
                              Update Menu
                            </button>
                            <button className="btn-secondary" onClick={() => onDeactivate(r.id)}>
                              Deactivate
                            </button>
                          </div>
                        ) : (
                          <span className="text-gray-400">—</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500">No restaurants yet.</p>
          )}
        </div>
      </div>

      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-2xl bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-4 border-b flex items-center justify-between gap-4">
              <div>
                <div className="text-lg font-semibold text-gray-900">
                  {modalMode === 'edit' ? 'Edit Restaurant' : 'Add Restaurant'}
                </div>
              </div>
              <button className="btn-secondary" onClick={closeModal} disabled={saving}>
                Close
              </button>
            </div>

            <form onSubmit={onSubmit} className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input className="input" name="name" value={form.name} onChange={onChange} placeholder="Restaurant name" required />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Contact Name</label>
                  <input className="input" name="contact_name" value={form.contact_name} onChange={onChange} placeholder="Contact person" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input className="input" name="phone_number" value={form.phone_number} onChange={onChange} placeholder="+1..." />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input className="input" type="email" name="email" value={form.email} onChange={onChange} placeholder="orders@restaurant.com" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                <input className="input" name="address" value={form.address} onChange={onChange} placeholder="Street, City" />
              </div>
              <div className="pt-2 flex items-center justify-end gap-2">
                <button type="button" className="btn-secondary" onClick={closeModal} disabled={saving}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={saving || !canSubmit}>
                  {saving ? 'Saving...' : modalMode === 'edit' ? 'Save Changes' : 'Create Restaurant'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default AdminRestaurantsPage;
