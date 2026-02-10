import { useMemo, useState, useEffect } from 'react';
import { format, parseISO } from 'date-fns';
import orderService from '../services/orderService';
import restaurantService from '../services/restaurantService';
import Navbar from '../components/common/Navbar';
import Loading from '../components/common/Loading';
import { Calendar, Plus, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Confetti from '../components/common/Confetti';

const HomePage = () => {
  const { user } = useAuth();
  const [days, setDays] = useState([]);
  const [ordersByDate, setOrdersByDate] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [selectedDate, setSelectedDate] = useState(null);
  const [availableRestaurants, setAvailableRestaurants] = useState([]);
  const [selectedRestaurantId, setSelectedRestaurantId] = useState('');
  const [orderText, setOrderText] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  const isBirthdayToday = useMemo(() => {
    const birth = user?.birth_date;
    if (!birth) return false;
    const m = String(birth).slice(5, 7);
    const d = String(birth).slice(8, 10);
    if (!m || !d) return false;
    const now = new Date();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    return mm === m && dd === d;
  }, [user?.birth_date]);

  useEffect(() => {
    bootstrap();
  }, []);

  const computeNextWorkdays = () => {
    const result = [];
    const now = new Date();
    let cursor = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    while (result.length < 5) {
      const weekday = cursor.getDay(); // 0 Sun .. 6 Sat
      if (weekday >= 1 && weekday <= 5) {
        result.push(format(cursor, 'yyyy-MM-dd'));
      }
      cursor = new Date(cursor.getTime() + 24 * 60 * 60 * 1000);
    }
    return result;
  };

  const bootstrap = async () => {
    try {
      setLoading(true);
      const nextDays = computeNextWorkdays();
      setDays(nextDays);

      const dateFrom = nextDays[0];
      const dateTo = nextDays[nextDays.length - 1];
      const orders = await orderService.getOrders({ date_from: dateFrom, date_to: dateTo });
      const map = {};
      orders.forEach((o) => {
        map[o.order_date] = o;
      });
      setOrdersByDate(map);
      setError('');
    } catch (err) {
      setError('Failed to load orders. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectDay = async (dateIso) => {
    setSelectedDate(dateIso);
    setFormError('');
    setSelectedRestaurantId('');
    setOrderText('');
    setNotes('');
    try {
      const restaurants = await restaurantService.getAvailableRestaurants(dateIso);
      setAvailableRestaurants(restaurants);
    } catch (err) {
      console.error(err);
      setAvailableRestaurants([]);
      setFormError('Failed to load available restaurants.');
    }
  };

  const startChangeOrder = async (dateIso) => {
    const existing = ordersByDate[dateIso];
    await selectDay(dateIso);
    if (existing) {
      setSelectedRestaurantId(String(existing.restaurant_id || ''));
      setOrderText(existing.order_text || '');
      setNotes(existing.notes || '');
    }
  };

  const selectedRestaurant = useMemo(() => {
    return availableRestaurants.find((r) => String(r.restaurant.id) === String(selectedRestaurantId)) || null;
  }, [availableRestaurants, selectedRestaurantId]);

  const applyMotd = (motdText) => {
    const next = String(motdText || '').trim();
    if (!next) return;
    setOrderText((prev) => {
      const cur = String(prev || '').trim();
      if (!cur) return next;
      if (cur.includes(next)) return prev;
      return `${cur}\n${next}`;
    });
  };

  const submitOrder = async () => {
    if (!selectedDate) return;
    if (!selectedRestaurantId) {
      setFormError('Please select a restaurant');
      return;
    }
    if (!orderText.trim()) {
      setFormError('Please enter your order');
      return;
    }

    try {
      setSubmitting(true);
      setFormError('');
      const existing = ordersByDate[selectedDate];
      const createPayload = {
        restaurant_id: Number(selectedRestaurantId),
        order_date: selectedDate,
        order_text: orderText.trim(),
        notes: notes.trim() || undefined,
      };
      const updatePayload = {
        restaurant_id: Number(selectedRestaurantId),
        order_text: orderText.trim(),
        notes: notes.trim() || undefined,
      };

      const order = existing
        ? await orderService.updateSimpleOrder(existing.id, updatePayload)
        : await orderService.createSimpleOrder(createPayload);

      setOrdersByDate((prev) => ({ ...prev, [selectedDate]: order }));
      setSelectedDate(null);
      setAvailableRestaurants([]);
      setSelectedRestaurantId('');
      setOrderText('');
      setNotes('');
    } catch (err) {
      console.error(err);
      const apiError = err?.response?.data;
      const validationMessages = apiError?.messages
        ? Object.entries(apiError.messages)
            .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : String(msgs)}`)
            .join(' • ')
        : null;
      setFormError(validationMessages || apiError?.error || 'Failed to submit order.');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
      ordered: { color: 'bg-indigo-100 text-indigo-800', label: 'Ordered' },
      confirmed: { color: 'bg-blue-100 text-blue-800', label: 'Confirmed' },
      sent_to_restaurant: { color: 'bg-purple-100 text-purple-800', label: 'Sent' },
      completed: { color: 'bg-green-100 text-green-800', label: 'Completed' },
      cancelled: { color: 'bg-red-100 text-red-800', label: 'Cancelled' },
    };

    const config = statusConfig[status] || statusConfig.pending;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <Loading message="Loading your orders..." />
      </>
    );
  }

  return (
    <>
      <Navbar />
      <Confetti active={isBirthdayToday} />
      <div
        className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 ${
          isBirthdayToday ? 'bg-gradient-to-br from-pink-50 via-yellow-50 to-purple-50 rounded-2xl' : ''
        }`}
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Calendar className="w-8 h-8 mr-3 text-primary-600" />
            My Orders
          </h1>
          <p className="mt-2 text-gray-600">
            Order for the next five work days
          </p>
          {isBirthdayToday && (
            <div className="mt-4 rounded-lg border border-pink-200 bg-white/70 p-4">
              <div className="text-lg font-semibold text-gray-900">Happy Birthday{user?.first_name ? `, ${user.first_name}` : ''}!</div>
              <div className="text-sm text-gray-700">Today’s a great day for a great meal.</div>
            </div>
          )}
        </div>

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Workweek List */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {days.map((dateIso) => {
            const date = parseISO(dateIso);
            const order = ordersByDate[dateIso] || null;
            const hasOrder = !!order;

            return (
              <div
                key={dateIso}
                onClick={() => selectDay(dateIso)}
                className={`card cursor-pointer transition-all hover:shadow-lg ${
                  hasOrder
                    ? 'border-2 border-green-300 bg-green-50'
                    : 'border-2 border-red-300 bg-red-50'
                }`}
              >
                {/* Date Header */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {format(date, 'EEEE')}
                    </h3>
                    <p className="text-sm text-gray-600">{format(date, 'MMM d, yyyy')}</p>
                  </div>
                  {hasOrder ? (
                    <CheckCircle className="w-8 h-8 text-green-600" />
                  ) : (
                    <AlertCircle className="w-8 h-8 text-red-600" />
                  )}
                </div>

                {/* Order Details or CTA */}
                {hasOrder ? (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700">
                        {order.restaurant_name}
                      </span>
                      {getStatusBadge(order.status)}
                    </div>
                    {order.order_text && (
                      <p className="text-sm text-gray-700 line-clamp-2">{order.order_text}</p>
                    )}
                    {order.notes && <p className="text-xs text-gray-500 line-clamp-1">Notes: {order.notes}</p>}
                    <button
                      className="mt-2 w-full btn-secondary text-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        startChangeOrder(dateIso);
                      }}
                    >
                      Change Order
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-4">
                    <Plus className="w-12 h-12 text-red-500 mb-2" />
                    <p className="text-sm font-medium text-gray-700 mb-1">
                      No order placed
                    </p>
                    <button
                      className="mt-2 btn-primary text-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        selectDay(dateIso);
                      }}
                    >
                      Order Now
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Empty State */}
        {days.length === 0 && !loading && (
          <div className="text-center py-12">
            <Calendar className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No orders yet
            </h3>
            <p className="text-gray-600 mb-4">
              Start planning your meals for the week
            </p>
          </div>
        )}

        {/* Order Form */}
        {selectedDate && (
          <div className="card mt-8">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Create Order</h2>
                <p className="text-sm text-gray-600 mt-1">
                  For {format(parseISO(selectedDate), 'EEEE, MMM d, yyyy')}
                </p>
              </div>
              <button className="btn-secondary" onClick={() => setSelectedDate(null)} disabled={submitting}>
                Close
              </button>
            </div>

            {formError && (
              <div className="mt-4 rounded-md bg-red-50 p-4">
                <p className="text-sm text-red-800">{formError}</p>
              </div>
            )}

            <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1">
                <label className="label">Restaurant</label>
                <select
                  className="input"
                  value={selectedRestaurantId}
                  onChange={(e) => setSelectedRestaurantId(e.target.value)}
                >
                  <option value="">Select restaurant</option>
                  {availableRestaurants.map((r) => (
                    <option key={r.restaurant.id} value={r.restaurant.id}>
                      {r.restaurant.name}
                    </option>
                  ))}
                </select>
                {availableRestaurants.length === 0 && (
                  <p className="text-sm text-gray-600 mt-2">No restaurants available for this day.</p>
                )}
              </div>

              <div className="lg:col-span-2">
                {selectedRestaurant?.menu ? (
                  <div className="mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Menu: {selectedRestaurant.menu.name}
                    </h3>
                    {selectedRestaurant.menu.menu_text && (
                      <pre className="whitespace-pre-wrap text-sm text-gray-800 bg-gray-50 p-4 rounded-md overflow-auto">
                        {selectedRestaurant.menu.menu_text}
                      </pre>
                    )}
                    {selectedRestaurant.menu.menu_file_url && (
                      <div className="mt-4">
                        {String(selectedRestaurant.menu.menu_file_mime || '').startsWith('image/') ? (
                          <img
                            src={selectedRestaurant.menu.menu_file_url}
                            alt={selectedRestaurant.menu.menu_file_name || 'Menu'}
                            className="max-h-[70vh] w-auto rounded-md border"
                          />
                        ) : (
                          <a className="btn-secondary inline-flex" href={selectedRestaurant.menu.menu_file_url} target="_blank" rel="noreferrer">
                            Show Menu
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                ) : selectedRestaurantId ? (
                  <p className="text-sm text-gray-600 mb-6">No menu found for this restaurant/date.</p>
                ) : null}

                {selectedRestaurantId && selectedRestaurant?.motd_option && (
                  <div className="mb-6">
                    <div className="text-sm font-medium text-gray-700 mb-2">MOTD</div>
                    <button className="btn-secondary" onClick={() => applyMotd(selectedRestaurant.motd_option)}>
                      {selectedRestaurant.motd_option}
                    </button>
                    <div className="text-xs text-gray-500 mt-2">Click to add to your order.</div>
                  </div>
                )}

                <div>
                  <label className="label">Your Order *</label>
                  <textarea
                    className="input"
                    rows={4}
                    value={orderText}
                    onChange={(e) => setOrderText(e.target.value)}
                    placeholder="e.g. Turkey sandwich, chips, and a Coke"
                  />
                </div>

                <div className="mt-4">
                  <label className="label">Notes</label>
                  <input
                    className="input"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="e.g. no relish"
                  />
                </div>

                <div className="mt-6 flex justify-end">
                  <button className="btn-primary" onClick={submitOrder} disabled={submitting || availableRestaurants.length === 0}>
                    {submitting ? 'Saving...' : 'Save Order'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default HomePage;
