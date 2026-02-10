import api from './api';

const orderService = {
  /**
   * Get user's orders
   */
  getOrders: async (params = {}) => {
    const response = await api.get('/orders', { params });
    return response.data.orders;
  },

  /**
   * Get order by ID
   */
  getOrder: async (orderId) => {
    const response = await api.get(`/orders/${orderId}`);
    return response.data;
  },

  /**
   * Create new order
   */
  createOrder: async (orderData) => {
    const response = await api.post('/orders', orderData);
    return response.data.order;
  },

  /**
   * Create new simple freeform order
   */
  createSimpleOrder: async (orderData) => {
    const response = await api.post('/orders/simple', orderData);
    return response.data.order;
  },

  /**
   * Update existing simple order
   */
  updateSimpleOrder: async (orderId, orderData) => {
    const response = await api.put(`/orders/${orderId}/simple`, orderData);
    return response.data.order;
  },

  /**
   * Update order
   */
  updateOrder: async (orderId, orderData) => {
    const response = await api.put(`/orders/${orderId}`, orderData);
    return response.data.order;
  },

  /**
   * Cancel order
   */
  cancelOrder: async (orderId) => {
    const response = await api.delete(`/orders/${orderId}`);
    return response.data;
  },

  /**
   * Get weekly orders view
   */
  getWeeklyOrders: async (startDate) => {
    const params = startDate ? { start_date: startDate } : {};
    const response = await api.get('/orders/week', { params });
    return response.data;
  },

  /**
   * Get missing order days
   */
  getMissingDays: async (daysAhead = 7) => {
    const response = await api.get('/orders/missing-days', {
      params: { days_ahead: daysAhead },
    });
    return response.data.missing_dates;
  },

  /**
   * Get all orders (admin)
   */
  getAllOrders: async (params = {}) => {
    const response = await api.get('/admin/orders', { params });
    return response.data.orders;
  },

  /**
   * Get orders for a selected day grouped by restaurant (admin)
   */
  getOrdersByDateAdmin: async (date) => {
    const response = await api.get('/admin/orders/by-date', { params: { date } });
    return response.data;
  },

  /**
   * Get email draft for a restaurant/date (admin)
   */
  getRestaurantEmailDraftAdmin: async ({ date, restaurant_id }) => {
    const response = await api.post('/admin/orders/email-draft', { date, restaurant_id });
    return response.data.draft;
  },

  /**
   * Log "send" email for restaurant/date (admin)
   */
  sendRestaurantEmailAdmin: async ({ date, restaurant_id }) => {
    const response = await api.post('/admin/orders/send-email', { date, restaurant_id });
    return response.data;
  },

  /**
   * Log "send" emails for all restaurants with orders (admin)
   */
  sendAllRestaurantEmailsAdmin: async ({ date }) => {
    const response = await api.post('/admin/orders/send-all-emails', { date });
    return response.data;
  },

  /**
   * Update order status (admin)
   */
  updateOrderStatus: async (orderId, status) => {
    const response = await api.put(`/admin/orders/${orderId}/status`, { status });
    return response.data.order;
  },

  /**
   * Get dashboard stats (admin)
   */
  getDashboardStats: async () => {
    const response = await api.get('/admin/dashboard');
    return response.data;
  },

  /**
   * Get users without orders (admin)
   */
  getUsersWithoutOrders: async (orderDate) => {
    const response = await api.get('/admin/users-without-orders', {
      params: { order_date: orderDate },
    });
    return response.data.users;
  },
};

export default orderService;
