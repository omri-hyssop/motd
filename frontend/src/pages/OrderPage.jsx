import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { format, parseISO } from 'date-fns';
import menuService from '../services/menuService';
import orderService from '../services/orderService';
import Navbar from '../components/common/Navbar';
import Loading from '../components/common/Loading';
import { ShoppingCart, Plus, Minus, Trash2 } from 'lucide-react';

const OrderPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const orderDate = searchParams.get('date');

  const [menus, setMenus] = useState([]);
  const [selectedMenu, setSelectedMenu] = useState(null);
  const [cart, setCart] = useState({});
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!orderDate) {
      navigate('/');
      return;
    }
    fetchAvailableMenus();
  }, [orderDate]);

  const fetchAvailableMenus = async () => {
    try {
      setLoading(true);
      const data = await menuService.getAvailableMenus(orderDate);
      setMenus(data);
      if (data.length > 0) {
        loadMenuDetails(data[0].id);
      }
      setError('');
    } catch (err) {
      setError('Failed to load menus. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadMenuDetails = async (menuId) => {
    try {
      const menuData = await menuService.getMenu(menuId);
      setSelectedMenu(menuData);
    } catch (err) {
      setError('Failed to load menu details.');
      console.error(err);
    }
  };

  const handleMenuChange = (menuId) => {
    loadMenuDetails(menuId);
    setCart({}); // Clear cart when switching menus
  };

  const addToCart = (item) => {
    setCart((prev) => ({
      ...prev,
      [item.id]: {
        ...item,
        quantity: (prev[item.id]?.quantity || 0) + 1,
      },
    }));
  };

  const removeFromCart = (itemId) => {
    setCart((prev) => {
      const newCart = { ...prev };
      if (newCart[itemId].quantity > 1) {
        newCart[itemId].quantity -= 1;
      } else {
        delete newCart[itemId];
      }
      return newCart;
    });
  };

  const deleteFromCart = (itemId) => {
    setCart((prev) => {
      const newCart = { ...prev };
      delete newCart[itemId];
      return newCart;
    });
  };

  const calculateTotal = () => {
    return Object.values(cart).reduce(
      (total, item) => total + parseFloat(item.price) * item.quantity,
      0
    );
  };

  const handleSubmitOrder = async () => {
    if (Object.keys(cart).length === 0) {
      setError('Please add at least one item to your order');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const items = Object.values(cart).map((item) => ({
        menu_item_id: item.id,
        quantity: item.quantity,
      }));

      await orderService.createOrder({
        menu_id: selectedMenu.id,
        order_date: orderDate,
        items,
        notes,
      });

      navigate('/', { state: { message: 'Order placed successfully!' } });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to place order. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <Loading message="Loading menus..." />
      </>
    );
  }

  if (menus.length === 0) {
    return (
      <>
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              No menus available for {orderDate && format(parseISO(orderDate), 'MMM d, yyyy')}
            </h2>
            <p className="text-gray-600 mb-6">
              Please check back later or try a different date
            </p>
            <button onClick={() => navigate('/')} className="btn-primary">
              Back to Home
            </button>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Order for {orderDate && format(parseISO(orderDate), 'EEEE, MMM d, yyyy')}
          </h1>
          <p className="mt-2 text-gray-600">
            Select your meal from available menus
          </p>
        </div>

        {error && (
          <div className="mb-6 rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Menu Selection and Items */}
          <div className="lg:col-span-2">
            {/* Menu Selector */}
            {menus.length > 1 && (
              <div className="mb-6">
                <label className="label">Select Restaurant</label>
                <select
                  className="input"
                  value={selectedMenu?.id || ''}
                  onChange={(e) => handleMenuChange(parseInt(e.target.value))}
                >
                  {menus.map((menu) => (
                    <option key={menu.id} value={menu.id}>
                      {menu.restaurant_name} - {menu.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Menu Items */}
            {selectedMenu && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  {selectedMenu.restaurant_name}
                </h2>
                <p className="text-gray-600 mb-6">{selectedMenu.description}</p>

                {(selectedMenu.menu_text || selectedMenu.menu_file_url) && (
                  <div className="card mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Menu</h3>
                    {selectedMenu.menu_text && (
                      <pre className="whitespace-pre-wrap text-sm text-gray-800 bg-gray-50 p-4 rounded-md overflow-auto">
                        {selectedMenu.menu_text}
                      </pre>
                    )}
                    {selectedMenu.menu_file_url && (
                      <div className="mt-4">
                        {String(selectedMenu.menu_file_mime || '').startsWith('image/') ? (
                          <img
                            src={selectedMenu.menu_file_url}
                            alt={selectedMenu.menu_file_name || 'Menu'}
                            className="max-h-[70vh] w-auto rounded-md border"
                          />
                        ) : (
                          <a className="btn-secondary inline-flex" href={selectedMenu.menu_file_url} target="_blank" rel="noreferrer">
                            Show Menu
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                )}

                <div className="space-y-4">
                  {selectedMenu.items.map((item) => (
                    <div key={item.id} className="card flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">{item.name}</h3>
                        <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                        {item.dietary_info && (
                          <p className="text-xs text-gray-500 mt-2">{item.dietary_info}</p>
                        )}
                        <p className="text-lg font-bold text-primary-600 mt-2">
                          ${parseFloat(item.price).toFixed(2)}
                        </p>
                      </div>
                      <button
                        onClick={() => addToCart(item)}
                        disabled={!item.is_available}
                        className="btn-primary ml-4"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Cart Sidebar */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <ShoppingCart className="w-6 h-6 mr-2" />
                Your Order
              </h2>

              {Object.keys(cart).length === 0 ? (
                <p className="text-gray-500 text-center py-8">Your cart is empty</p>
              ) : (
                <>
                  <div className="space-y-3 mb-4">
                    {Object.values(cart).map((item) => (
                      <div key={item.id} className="flex items-center justify-between border-b pb-3">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{item.name}</p>
                          <p className="text-sm text-gray-600">
                            ${parseFloat(item.price).toFixed(2)} each
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => removeFromCart(item.id)}
                            className="p-1 hover:bg-gray-100 rounded"
                          >
                            <Minus className="w-4 h-4" />
                          </button>
                          <span className="font-medium w-8 text-center">{item.quantity}</span>
                          <button
                            onClick={() => addToCart(item)}
                            className="p-1 hover:bg-gray-100 rounded"
                          >
                            <Plus className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => deleteFromCart(item.id)}
                            className="p-1 hover:bg-red-100 rounded text-red-600"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="mb-4">
                    <label className="label">Special Instructions (Optional)</label>
                    <textarea
                      className="input"
                      rows="3"
                      placeholder="Any special requests?"
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                  </div>

                  <div className="border-t pt-4 mb-4">
                    <div className="flex justify-between text-lg font-bold">
                      <span>Total:</span>
                      <span className="text-primary-600">${calculateTotal().toFixed(2)}</span>
                    </div>
                  </div>

                  <button
                    onClick={handleSubmitOrder}
                    disabled={submitting}
                    className="w-full btn-primary"
                  >
                    {submitting ? 'Placing Order...' : 'Place Order'}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default OrderPage;
