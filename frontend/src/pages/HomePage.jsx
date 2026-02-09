import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, addDays, startOfWeek, isSameDay, parseISO } from 'date-fns';
import orderService from '../services/orderService';
import Navbar from '../components/common/Navbar';
import Loading from '../components/common/Loading';
import { Calendar, Plus, CheckCircle, AlertCircle } from 'lucide-react';

const HomePage = () => {
  const [weeklyOrders, setWeeklyOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchWeeklyOrders();
  }, []);

  const fetchWeeklyOrders = async () => {
    try {
      setLoading(true);
      const data = await orderService.getWeeklyOrders();
      setWeeklyOrders(data.days || []);
      setError('');
    } catch (err) {
      setError('Failed to load orders. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleOrderClick = (day) => {
    if (day.order) {
      navigate(`/orders/${day.order.id}`);
    } else {
      navigate(`/order/new?date=${day.date}`);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <Calendar className="w-8 h-8 mr-3 text-primary-600" />
            My Weekly Orders
          </h1>
          <p className="mt-2 text-gray-600">
            Plan your meals for the upcoming week
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Weekly Calendar Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {weeklyOrders.map((day) => {
            const date = parseISO(day.date);
            const hasOrder = day.order !== null;

            return (
              <div
                key={day.date}
                onClick={() => handleOrderClick(day)}
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
                        {day.order.restaurant_name}
                      </span>
                      {getStatusBadge(day.order.status)}
                    </div>
                    <p className="text-sm text-gray-600">
                      {day.order.item_count} {day.order.item_count === 1 ? 'item' : 'items'}
                    </p>
                    <p className="text-lg font-bold text-gray-900">
                      ${parseFloat(day.order.total_amount).toFixed(2)}
                    </p>
                    <button className="mt-2 w-full text-sm text-primary-600 hover:text-primary-700 font-medium">
                      View Details →
                    </button>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-4">
                    <Plus className="w-12 h-12 text-red-500 mb-2" />
                    <p className="text-sm font-medium text-gray-700 mb-1">
                      No order placed
                    </p>
                    <button className="mt-2 btn-primary text-sm">
                      Order Now
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Empty State */}
        {weeklyOrders.length === 0 && !loading && (
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
      </div>
    </>
  );
};

export default HomePage;
