import { useEffect, useMemo, useState } from 'react';
import Navbar from '../components/common/Navbar';
import Loading from '../components/common/Loading';
import api from '../services/api';

const AdminMotdPage = () => {
  const todayWeekday = useMemo(() => {
    const now = new Date();
    const jsDay = now.getDay(); // 0 Sun .. 6 Sat
    const mondayBased = (jsDay + 6) % 7; // 0 Mon .. 6 Sun
    return Math.min(4, mondayBased); // clamp to Mon-Fri for UI default
  }, []);

  const [selectedWeekday, setSelectedWeekday] = useState(todayWeekday);
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [editId, setEditId] = useState(null);
  const [editText, setEditText] = useState('');

  useEffect(() => {
    fetchRows(selectedWeekday);
  }, [selectedWeekday]);

  const fetchRows = async (weekday) => {
    try {
      setLoading(true);
      const res = await api.get('/admin/motd', { params: { weekday } });
      setRows(res.data.restaurants || []);
      setError('');
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.error || 'Failed to load MOTD options.');
    } finally {
      setLoading(false);
    }
  };

  const startEdit = (restaurantId) => {
    const row = rows.find((r) => r.restaurant.id === restaurantId);
    setEditId(restaurantId);
    setEditText(row?.motd_option || '');
    setSuccess('');
    setError('');
  };

  const cancelEdit = () => {
    setEditId(null);
    setEditText('');
  };

  const save = async () => {
    if (!editId) return;
    try {
      setSavingId(editId);
      setError('');
      setSuccess('');
      await api.put('/admin/motd', {
        weekday: selectedWeekday,
        restaurant_id: editId,
        option_text: editText,
      });
      setSuccess('MOTD saved.');
      cancelEdit();
      await fetchRows(selectedWeekday);
    } catch (err) {
      console.error(err);
      setError(err?.response?.data?.error || 'Failed to save MOTD.');
    } finally {
      setSavingId(null);
    }
  };

  return (
    <>
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Manage MOTD</h1>
          <p className="mt-2 text-gray-600">Set quick Meal of the Day options per restaurant weekday.</p>
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

        <div className="card mb-6">
          <div className="flex items-center justify-center gap-3">
            {[
              { label: 'M', value: 0 },
              { label: 'T', value: 1 },
              { label: 'W', value: 2 },
              { label: 'T', value: 3 },
              { label: 'F', value: 4 },
            ].map((b) => {
              const active = selectedWeekday === b.value;
              return (
                <button
                  key={`${b.label}-${b.value}`}
                  type="button"
                  className={`h-11 w-11 rounded-full border flex items-center justify-center font-semibold ${
                    active ? 'bg-primary-600 text-white border-primary-600' : 'bg-white text-gray-700 border-gray-300'
                  }`}
                  onClick={() => {
                    setSuccess('');
                    setError('');
                    setSelectedWeekday(b.value);
                  }}
                >
                  {b.label}
                </button>
              );
            })}
          </div>
        </div>

        {loading ? (
          <Loading message="Loading MOTD options..." />
        ) : rows.length === 0 ? (
          <div className="card">
            <p className="text-gray-600">No restaurants available for this weekday.</p>
          </div>
        ) : (
          <div className="card overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Restaurant</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">MOTD Option</th>
                  <th className="px-4 py-3" />
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {rows.map((r) => {
                  const isEditing = editId === r.restaurant.id;
                  return (
                    <tr key={r.restaurant.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm text-gray-900">{r.restaurant.name}</td>
                      <td className="px-4 py-3 text-sm text-gray-700">
                        {isEditing ? (
                          <textarea
                            className="input"
                            rows={3}
                            value={editText}
                            onChange={(e) => setEditText(e.target.value)}
                            placeholder="Enter a quick MOTD option (leave blank to clear)"
                          />
                        ) : r.motd_option ? (
                          <div className="whitespace-pre-wrap">{r.motd_option}</div>
                        ) : (
                          <span className="text-gray-400">Nothing</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right text-sm">
                        {isEditing ? (
                          <div className="flex items-center justify-end gap-2">
                            <button className="btn-secondary" onClick={cancelEdit} disabled={savingId === r.restaurant.id}>
                              Cancel
                            </button>
                            <button className="btn-primary" onClick={save} disabled={savingId === r.restaurant.id}>
                              {savingId === r.restaurant.id ? 'Saving...' : 'Save'}
                            </button>
                          </div>
                        ) : (
                          <button className="btn-secondary" onClick={() => startEdit(r.restaurant.id)}>
                            {r.motd_option ? 'Edit MOTD' : 'Add MOTD'}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
};

export default AdminMotdPage;
