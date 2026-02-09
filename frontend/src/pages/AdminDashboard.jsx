import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, parseISO } from 'date-fns';
import orderService from '../services/orderService';
import Navbar from '../components/common/Navbar';
import Loading from '../components/common/Loading';
import {
  LayoutDashboard,
  Users,
  ShoppingBag,
  DollarSign,
  Calendar,
  AlertCircle,
  TrendingUp,
  Package,
} from 'lucide-react';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      const data = await orderService.getDashboardStats();
      setStats(data);
      setError('');
    } catch (err) {
      setError('Failed to load dashboard data.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, title, value, subtitle, color = 'primary' }) => {
    const colorClasses = {
      primary: 'bg-primary-50 text-primary-600',
      green: 'bg-green-50 text-green-600',
      blue: 'bg-blue-50 text-blue-600',
      yellow: 'bg-yellow-50 text-yellow-600',
      red: 'bg-red-50 text-red-600',
    };

    return (
      <div className="card">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-gray-600 mb-1">{title}</p>
            <p className="text-3xl font-bold text-gray-900">{value}</p>
            {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
          </div>
          <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
            <Icon className="w-6 h-6" />
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <Loading message="Loading dashboard..." />
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
            <LayoutDashboard className="w-8 h-8 mr-3 text-primary-600" />
            Admin Dashboard
          </h1>
          <p className="mt-2 text-gray-600">Overview of your meal ordering system</p>
        </div>

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {stats && (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                icon={ShoppingBag}
                title="Total Orders Today"
                value={stats.total_orders_today || 0}
                subtitle="Active orders"
                color="primary"
              />
              <StatCard
                icon={Users}
                title="Total Users"
                value={stats.total_users || 0}
                subtitle="Registered accounts"
                color="blue"
              />
              <StatCard
                icon={DollarSign}
                title="Revenue Today"
                value={`$${parseFloat(stats.total_revenue_today || 0).toFixed(2)}`}
                subtitle="From today's orders"
                color="green"
              />
              <StatCard
                icon={AlertCircle}
                title="Pending Orders"
                value={stats.pending_orders || 0}
                subtitle="Needs attention"
                color="yellow"
              />
            </div>

            {/* Quick Actions */}
            <div className="card mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <button
                  onClick={() => navigate('/admin/orders')}
                  className="btn-primary flex items-center justify-center"
                >
                  <Package className="w-4 h-4 mr-2" />
                  Manage Orders
                </button>
                <button
                  onClick={() => navigate('/admin/restaurants')}
                  className="btn-primary flex items-center justify-center"
                >
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Manage Restaurants
                </button>
                <button
                  onClick={() => navigate('/admin/menus')}
                  className="btn-primary flex items-center justify-center"
                >
                  <Calendar className="w-4 h-4 mr-2" />
                  Manage Menus
                </button>
              </div>
            </div>

            {/* Recent Orders */}
            <div className="card mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Orders</h2>
              {stats.recent_orders && stats.recent_orders.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Order ID
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          User
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Restaurant
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Date
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Amount
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {stats.recent_orders.map((order) => (
                        <tr
                          key={order.id}
                          className="hover:bg-gray-50 cursor-pointer"
                          onClick={() => navigate(`/orders/${order.id}`)}
                        >
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            #{order.id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {order.user_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {order.restaurant_name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {format(parseISO(order.order_date), 'MMM d, yyyy')}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            ${parseFloat(order.total_amount).toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span
                              className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                order.status === 'pending'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : order.status === 'confirmed'
                                  ? 'bg-blue-100 text-blue-800'
                                  : order.status === 'completed'
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-gray-100 text-gray-800'
                              }`}
                            >
                              {order.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No recent orders</p>
              )}
            </div>

            {/* Orders by Status */}
            {stats.orders_by_status && (
              <div className="card">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Orders by Status</h2>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  {Object.entries(stats.orders_by_status).map(([status, count]) => (
                    <div key={status} className="text-center p-4 bg-gray-50 rounded-lg">
                      <p className="text-2xl font-bold text-gray-900">{count}</p>
                      <p className="text-sm text-gray-600 capitalize">{status.replace('_', ' ')}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </>
  );
};

export default AdminDashboard;
