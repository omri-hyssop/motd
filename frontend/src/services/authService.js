import api from './api';

const authService = {
  /**
   * Register a new user
   */
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  /**
   * Login user
   */
  login: async (identifier, password) => {
    const response = await api.post('/auth/login', { identifier, password });
    const { user, access_token } = response.data;

    // Store token and user in localStorage
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(user));

    return { user, token: access_token };
  },

  /**
   * Logout user
   */
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      // Clear local storage regardless of API response
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },

  /**
   * Get current user
   */
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    const user = response.data;
    localStorage.setItem('user', JSON.stringify(user));
    return user;
  },

  /**
   * Update user profile
   */
  updateProfile: async (profileData) => {
    const response = await api.put('/auth/me', profileData);
    const user = response.data.user;
    localStorage.setItem('user', JSON.stringify(user));
    return user;
  },

  /**
   * Change password
   */
  changePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },

  /**
   * Get stored user
   */
  getStoredUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Check if user is admin
   */
  isAdmin: () => {
    const user = authService.getStoredUser();
    return user?.role === 'admin';
  },
};

export default authService;
