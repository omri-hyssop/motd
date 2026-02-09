import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { format, parseISO } from 'date-fns';
import orderService from '../services/orderService';
import Navbar from '../components/common/Navbar';
import Loading from '../components/common/Loading';
import { Receipt, Calendar, User, MapPin, FileText, XCircle } from 'lucide-react';

const OrderDetailPage = () => {
  const { orderId } = useParams();
  const navigate = useNavigate();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchOrderDetails();
  }, [orderId]);

  const fetchOrderDetails = async () => {
    try {
      setLoading(true);
      const data = await orderService.getOrder(orderId);
      setOrder(data);
      setError('');
    } catch (err) {
      setError('Failed to load order details.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelOrder = async () => {
    if (!confirm('Are you sure you want to cancel this order?')) {
      return;
    }

    setCancelling(true);
    try {
      await orderService.cancelOrder(orderId);
      navigate('/', { state: { message: 'Order cancelled successfully' } });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to cancel order');
    } finally {
      setCancelling(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
      confirmed: { color: 'bg-blue-100 text-blue-800', label: 'Confirmed' },
      sent_to_restaurant: { color: 'bg-purple-100 text-purple-800', label: 'Sent to Restaurant' },
      completed: { color: 'bg-green-100 text-green-800', label: 'Completed' },
      cancelled: { color: 'bg-red-100 text-red-800', label: 'Cancelled' },
    };

    const config = statusConfig[status] || statusConfig.pending;

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <Loading message="Loading order details..." />
      </>
    );
  }

  if (!order) {
    return (
      <>
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Order not found</h2>
            <button onClick={() => navigate('/')} className="btn-primary">
              Back to Home
            </button>
          </div>
        </div>
      </>
    );
  }

  const canCancelOrder = order.status === 'pending' || order.status === 'confirmed';

  return (
    <>
      <Navbar />
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <Receipt className="w-8 h-8 mr-3 text-primary-600" />
              Order #{order.id}
            </h1>
            {getStatusBadge(order.status)}
          </div>
          <button
            onClick={() => navigate('/')}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            ← Back to Orders
          </button>
        </div>

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Order Details Card */}
        <div className="card mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start">
              <Calendar className="w-5 h-5 text-gray-400 mt-1 mr-3" />
              <div>
                <p className="text-sm text-gray-500">Order Date</p>
                <p className="font-semibold text-gray-900">
                  {format(parseISO(order.order_date), 'EEEE, MMM d, yyyy')}
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <MapPin className="w-5 h-5 text-gray-400 mt-1 mr-3" />
              <div>
                <p className="text-sm text-gray-500">Restaurant</p>
                <p className="font-semibold text-gray-900">{order.restaurant_name}</p>
              </div>
            </div>

            {order.notes && (
              <div className="flex items-start md:col-span-2">
                <FileText className="w-5 h-5 text-gray-400 mt-1 mr-3" />
                <div>
                  <p className="text-sm text-gray-500">Special Instructions</p>
                  <p className="text-gray-900">{order.notes}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Order Items */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Order Items</h2>
          <div className="space-y-4">
            {order.items.map((item) => (
              <div key={item.id} className="flex justify-between items-start border-b pb-4 last:border-b-0">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{item.menu_item_name}</h3>
                  <p className="text-sm text-gray-600">Quantity: {item.quantity}</p>
                  <p className="text-sm text-gray-600">
                    ${parseFloat(item.price).toFixed(2)} each
                  </p>
                  {item.notes && <p className="text-sm text-gray-500 mt-1">{item.notes}</p>}
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">
                    ${(parseFloat(item.price) * item.quantity).toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Total */}
          <div className="border-t pt-4 mt-4">
            <div className="flex justify-between text-xl font-bold">
              <span>Total:</span>
              <span className="text-primary-600">${parseFloat(order.total_amount).toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        {canCancelOrder && (
          <div className="card bg-red-50">
            <h3 className="font-semibold text-gray-900 mb-2">Cancel Order</h3>
            <p className="text-sm text-gray-600 mb-4">
              You can cancel this order before it's sent to the restaurant.
            </p>
            <button
              onClick={handleCancelOrder}
              disabled={cancelling}
              className="btn-danger"
            >
              <XCircle className="w-4 h-4 mr-2 inline" />
              {cancelling ? 'Cancelling...' : 'Cancel Order'}
            </button>
          </div>
        )}
      </div>
    </>
  );
};

export default OrderDetailPage;
