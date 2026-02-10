import { useEffect, useMemo, useState } from 'react';
import Navbar from '../components/common/Navbar';
import Loading from '../components/common/Loading';
import orderService from '../services/orderService';

const AdminOrdersPage = () => {
  const todayIso = useMemo(() => {
    const now = new Date();
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const pad = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  }, []);

  const [selectedDate, setSelectedDate] = useState(todayIso);
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [draftOpen, setDraftOpen] = useState(false);
  const [draftLoading, setDraftLoading] = useState(false);
  const [draftError, setDraftError] = useState('');
  const [draft, setDraft] = useState(null);
  const [sending, setSending] = useState(false);
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchOrdersByDate(selectedDate);
  }, [selectedDate]);

  const fetchOrdersByDate = async (dateIso) => {
    try {
      setLoading(true);
      const data = await orderService.getOrdersByDateAdmin(dateIso);
      setGroups(data.groups || []);
      setError('');
    } catch (err) {
      console.error(err);
      setError('Failed to load orders.');
    } finally {
      setLoading(false);
    }
  };

  const openDraft = async (restaurantId) => {
    try {
      setDraftOpen(true);
      setDraftLoading(true);
      setDraftError('');
      setDraft(null);
      const d = await orderService.getRestaurantEmailDraftAdmin({
        date: selectedDate,
        restaurant_id: restaurantId,
      });
      setDraft(d);
    } catch (err) {
      console.error(err);
      const apiError = err?.response?.data?.error;
      setDraftError(apiError || 'Failed to build email draft.');
    } finally {
      setDraftLoading(false);
    }
  };

  const sendDraft = async () => {
    if (!draft?.restaurant_id) return;
    try {
      setSending(true);
      setDraftError('');
      const res = await orderService.sendRestaurantEmailAdmin({
        date: selectedDate,
        restaurant_id: draft.restaurant_id,
      });
      setSuccess(res?.message || 'Email logged.');
      setDraftOpen(false);
      await fetchOrdersByDate(selectedDate);
    } catch (err) {
      console.error(err);
      const apiError = err?.response?.data?.error;
      setDraftError(apiError || 'Failed to send email.');
    } finally {
      setSending(false);
    }
  };

  const sendAll = async () => {
    if (!window.confirm('Log email drafts for all restaurants with orders for this day?')) return;
    try {
      setSending(true);
      setError('');
      setSuccess('');
      const res = await orderService.sendAllRestaurantEmailsAdmin({ date: selectedDate });
      const skipped = Array.isArray(res?.skipped) && res.skipped.length > 0 ? ` Skipped: ${res.skipped.length}.` : '';
      setSuccess(`${res?.message || 'Emails logged.'}${skipped}`);
      await fetchOrdersByDate(selectedDate);
    } catch (err) {
      console.error(err);
      const apiError = err?.response?.data?.error;
      setError(apiError || 'Failed to send all emails.');
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Manage Orders</h1>
          <p className="mt-2 text-gray-600">View and send orders by day.</p>
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
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div className="max-w-sm">
              <label className="label">Selected day</label>
              <input
                className="input"
                type="date"
                value={selectedDate}
                onChange={(e) => {
                  setSuccess('');
                  setSelectedDate(e.target.value);
                }}
              />
            </div>
            <button className="btn-primary" onClick={sendAll} disabled={sending || loading || groups.length === 0}>
              {sending ? 'Sending...' : 'Send All Emails'}
            </button>
          </div>
        </div>

        {loading ? (
          <Loading message="Loading orders..." />
        ) : groups.length > 0 ? (
          <div className="space-y-6">
            {groups.map((g) => (
              <div key={g.restaurant.id} className="card">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{g.restaurant.name}</h2>
                    <p className="text-sm text-gray-600">
                      {g.restaurant.email ? g.restaurant.email : 'No email configured'}
                    </p>
                  </div>
                  <button
                    className={g.restaurant.email_sent ? 'btn-secondary opacity-80' : 'btn-primary'}
                    onClick={() => openDraft(g.restaurant.id)}
                    disabled={draftLoading}
                    title={g.restaurant.email_sent_at ? `Last sent: ${g.restaurant.email_sent_at}` : undefined}
                  >
                    {g.restaurant.email_sent ? 'Send Email Again' : 'Send Email'}
                  </button>
                </div>

                <div className="mt-4 divide-y divide-gray-200">
                  {g.orders.map((o) => (
                    <div key={o.id} className="py-3 flex flex-col md:flex-row md:items-start md:justify-between gap-2">
                      <div className="min-w-0">
                        <div className="text-sm font-medium text-gray-900">
                          {o.user_name} <span className="text-gray-400 font-normal">#{o.id}</span>
                        </div>
                        {o.order_text ? (
                          <div className="text-sm text-gray-700 whitespace-pre-wrap">{o.order_text}</div>
                        ) : (
                          <div className="text-sm text-gray-500">(No order text)</div>
                        )}
                        {o.notes && <div className="text-xs text-gray-500 mt-1">Notes: {o.notes}</div>}
                      </div>
                      <div className="text-sm text-gray-600">{o.status}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="card">
            <p className="text-gray-600">No orders for this day.</p>
          </div>
        )}
      </div>

      {draftOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-3xl bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-4 border-b flex items-center justify-between gap-4">
              <div>
                <div className="text-lg font-semibold text-gray-900">Email Draft</div>
                <div className="text-sm text-gray-600">For {selectedDate}</div>
              </div>
              <button className="btn-secondary" onClick={() => setDraftOpen(false)} disabled={sending}>
                Close
              </button>
            </div>

            <div className="p-4">
              {draftError && (
                <div className="mb-4 rounded-md bg-red-50 p-4">
                  <p className="text-sm text-red-800">{draftError}</p>
                </div>
              )}
              {draftLoading ? (
                <Loading message="Building draft..." />
              ) : draft ? (
                <div className="space-y-3">
                  <div className="text-sm">
                    <div className="text-gray-500">To</div>
                    <div className="text-gray-900">{draft.to || '(missing)'}</div>
                  </div>
                  <div className="text-sm">
                    <div className="text-gray-500">Subject</div>
                    <div className="text-gray-900">{draft.subject}</div>
                  </div>
                  <div className="text-sm">
                    <div className="text-gray-500">Body</div>
                    <pre className="whitespace-pre-wrap text-sm text-gray-800 bg-gray-50 p-4 rounded-md overflow-auto max-h-[60vh]">
                      {draft.body}
                    </pre>
                  </div>
                </div>
              ) : (
                <p className="text-gray-600">No draft.</p>
              )}
            </div>

            <div className="p-4 border-t flex items-center justify-end gap-2">
              <button className="btn-secondary" onClick={() => setDraftOpen(false)} disabled={sending}>
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={sendDraft}
                disabled={sending || draftLoading || !draft?.to}
                title={!draft?.to ? 'Restaurant email is missing' : undefined}
              >
                {sending ? 'Sending...' : 'Send (Log)'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AdminOrdersPage;
