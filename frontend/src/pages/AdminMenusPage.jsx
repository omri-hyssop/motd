import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import Loading from '../components/common/Loading';
import restaurantService from '../services/restaurantService';
import menuService from '../services/menuService';

const AdminMenusPage = () => {
  const [searchParams] = useSearchParams();
  const restaurantIdFromQuery = searchParams.get('restaurant_id');

  const [restaurants, setRestaurants] = useState([]);
  const [menus, setMenus] = useState([]);
  const [activeMenu, setActiveMenu] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const todayIso = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    restaurant_id: restaurantIdFromQuery || '',
    name: '',
    description: '',
    available_from: todayIso,
    available_until: '',
    menu_text: '',
  });
  const [menuFile, setMenuFile] = useState(null);
  const [clearFile, setClearFile] = useState(false);
  const [specifyEndDate, setSpecifyEndDate] = useState(false);

  const canSubmit = useMemo(() => {
    return (
      !saving &&
      String(form.restaurant_id).trim().length > 0 &&
      form.name.trim().length > 0 &&
      form.available_from &&
      (form.menu_text.trim().length > 0 || !!menuFile || (!!activeMenu && !clearFile))
    );
  }, [form, saving, menuFile, activeMenu, clearFile]);

  useEffect(() => {
    bootstrap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (restaurantIdFromQuery && String(form.restaurant_id) !== String(restaurantIdFromQuery)) {
      setForm((prev) => ({ ...prev, restaurant_id: restaurantIdFromQuery }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [restaurantIdFromQuery]);

  const bootstrap = async () => {
    try {
      setLoading(true);
      const [restData, menuData] = await Promise.all([
        restaurantService.getRestaurants(),
        menuService.getMenus(),
      ]);
      setRestaurants(restData.filter((r) => r.is_active));
      setMenus(menuData);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to load menus/restaurants.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const restId = String(form.restaurant_id || '');
    if (!restId) {
      setActiveMenu(null);
      return;
    }
    const existing = menus.find((m) => String(m.restaurant_id) === restId) || null;
    setActiveMenu(existing);
  }, [menus, form.restaurant_id]);

  useEffect(() => {
    if (!activeMenu) {
      setClearFile(false);
      return;
    }
    setForm((prev) => ({
      ...prev,
      name: prev.name || activeMenu.name || '',
      description: prev.description || activeMenu.description || '',
      available_from: prev.available_from || activeMenu.available_from || todayIso,
      available_until: prev.available_until || (activeMenu.available_until === '2099-12-31' ? '' : activeMenu.available_until || ''),
    }));
    setSpecifyEndDate(activeMenu.available_until !== '2099-12-31');
  }, [activeMenu]);

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const onCreate = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    try {
      setSaving(true);
      setSuccess('');
      setError('');

      if (!activeMenu) {
        const fd = new FormData();
        fd.set('restaurant_id', String(form.restaurant_id));
        fd.set('name', form.name.trim());
        if (form.description.trim()) fd.set('description', form.description.trim());
        if (form.available_from) fd.set('available_from', form.available_from);
        if (specifyEndDate && form.available_until) fd.set('available_until', form.available_until);
        if (form.menu_text.trim()) fd.set('menu_text', form.menu_text.trim());
        if (menuFile) fd.set('menu_file', menuFile);
        await menuService.createMenuWithContent(fd);
        setSuccess('Menu created.');
      } else {
        await menuService.updateMenu(activeMenu.id, {
          name: form.name.trim(),
          description: form.description.trim() || undefined,
          available_from: form.available_from,
          ...(specifyEndDate && form.available_until ? { available_until: form.available_until } : {}),
        });

        const fd = new FormData();
        if (form.menu_text.trim()) fd.set('menu_text', form.menu_text.trim());
        if (menuFile) fd.set('menu_file', menuFile);
        if (clearFile) fd.set('clear_file', 'true');
        if ([...fd.keys()].length > 0) {
          await menuService.updateMenuContent(activeMenu.id, fd);
        }
        setSuccess('Menu updated.');
      }

      setForm((prev) => ({ ...prev, name: '', description: '', menu_text: '' }));
      setMenuFile(null);
      setClearFile(false);
      setSpecifyEndDate(false);
      await bootstrap();
    } catch (err) {
      console.error(err);
      const message =
        err?.response?.data?.error ||
        (err?.response?.data?.messages ? 'Validation error.' : null) ||
        (activeMenu ? 'Failed to update menu.' : 'Failed to create menu.');
      setError(message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <Loading message="Loading..." />
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Manage Menus</h1>
          <p className="mt-2 text-gray-600">Create menus for restaurants (then add items via API for now).</p>
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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {activeMenu ? 'Edit Menu' : 'New Menu'}
            </h2>
            {restaurants.length === 0 ? (
              <p className="text-gray-600">Create a restaurant first.</p>
            ) : (
              <form onSubmit={onCreate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Restaurant *</label>
                  <select className="input" name="restaurant_id" value={form.restaurant_id} onChange={onChange} required>
                    <option value="" disabled>
                      Select restaurant
                    </option>
                    {restaurants.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                  <input className="input" name="name" value={form.name} onChange={onChange} required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                  <input className="input" name="description" value={form.description} onChange={onChange} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Menu Text</label>
                  <textarea
                    className="input"
                    name="menu_text"
                    value={form.menu_text}
                    onChange={onChange}
                    rows={6}
                    placeholder="Paste the menu here (optional if uploading a file)"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Menu File (PDF/Image)</label>
                  <input
                    className="input"
                    type="file"
                    accept=".pdf,image/*"
                    onChange={(e) => setMenuFile(e.target.files?.[0] || null)}
                  />
                  {menuFile && <p className="text-xs text-gray-500 mt-1">{menuFile.name}</p>}
                  {activeMenu?.menu_file_name && (
                    <div className="mt-2 flex items-center justify-between gap-2">
                      <p className="text-xs text-gray-600">
                        Current file: <span className="font-medium">{activeMenu.menu_file_name}</span>
                      </p>
                      <label className="text-xs text-gray-700 flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={clearFile}
                          onChange={(e) => setClearFile(e.target.checked)}
                        />
                        Remove file
                      </label>
                    </div>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Available From *</label>
                    <input
                      className="input"
                      type="date"
                      name="available_from"
                      value={form.available_from}
                      onChange={onChange}
                      required
                    />
                  </div>
                  <div>
                    <div className="flex items-center justify-between">
                      <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                      <label className="text-xs text-gray-700 flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={specifyEndDate}
                          onChange={(e) => {
                            setSpecifyEndDate(e.target.checked);
                            if (!e.target.checked) {
                              setForm((prev) => ({ ...prev, available_until: '' }));
                            }
                          }}
                        />
                        Specify end date
                      </label>
                    </div>
                    <input
                      className="input"
                      type="date"
                      name="available_until"
                      value={form.available_until}
                      onChange={onChange}
                      disabled={!specifyEndDate}
                      required={specifyEndDate}
                    />
                    {!specifyEndDate && <p className="text-xs text-gray-500 mt-1">Defaults to no end date.</p>}
                  </div>
                </div>
                <button type="submit" className="btn-primary w-full" disabled={!canSubmit}>
                  {saving ? (activeMenu ? 'Updating...' : 'Creating...') : activeMenu ? 'Update Menu' : 'Create Menu'}
                </button>
              </form>
            )}
          </div>

          <div className="card">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Menus</h2>
            {menus
              .filter((m) => (form.restaurant_id ? String(m.restaurant_id) === String(form.restaurant_id) : true))
              .length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Menu
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Restaurant
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Dates
                      </th>
                      <th className="px-4 py-3" />
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {menus
                      .filter((m) =>
                        form.restaurant_id ? String(m.restaurant_id) === String(form.restaurant_id) : true
                      )
                      .map((m) => (
                        <tr key={m.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-900">{m.name}</td>
                          <td className="px-4 py-3 text-sm text-gray-700">{m.restaurant_name || m.restaurant_id}</td>
                          <td className="px-4 py-3 text-sm text-gray-500">
                          {String(m.available_from)} → {m.available_until === '2099-12-31' ? 'No end date' : String(m.available_until)}
                          </td>
                          <td className="px-4 py-3 text-right text-sm">
                            <button
                              className="btn-secondary"
                              onClick={() => {
                                setForm((prev) => ({
                                  ...prev,
                                  restaurant_id: String(m.restaurant_id),
                                  name: m.name || '',
                                  description: m.description || '',
                                  available_from: m.available_from || prev.available_from,
                                  available_until: m.available_until === '2099-12-31' ? '' : (m.available_until || prev.available_until),
                                  menu_text: m.menu_text || '',
                                }));
                                setMenuFile(null);
                                setClearFile(false);
                                setSpecifyEndDate(m.available_until !== '2099-12-31');
                                setActiveMenu(m);
                              }}
                            >
                              Edit
                            </button>
                          </td>
                        </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500">No menus yet.</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default AdminMenusPage;
