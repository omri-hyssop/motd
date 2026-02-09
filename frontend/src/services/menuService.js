import api from './api';

const menuService = {
  /**
   * Get all menus
   */
  getMenus: async (params = {}) => {
    const response = await api.get('/menus', { params });
    return response.data.menus;
  },

  /**
   * Get available menus for a specific date
   */
  getAvailableMenus: async (date) => {
    const response = await api.get('/menus/available', {
      params: { date },
    });
    return response.data.menus;
  },

  /**
   * Get menu by ID with items
   */
  getMenu: async (menuId) => {
    const response = await api.get(`/menus/${menuId}`);
    return response.data;
  },

  /**
   * Create new menu (admin)
   */
  createMenu: async (menuData) => {
    const response = await api.post('/menus', menuData);
    return response.data.menu;
  },

  /**
   * Update menu (admin)
   */
  updateMenu: async (menuId, menuData) => {
    const response = await api.put(`/menus/${menuId}`, menuData);
    return response.data.menu;
  },

  /**
   * Delete menu (admin)
   */
  deleteMenu: async (menuId) => {
    const response = await api.delete(`/menus/${menuId}`);
    return response.data;
  },

  /**
   * Add menu item (admin)
   */
  addMenuItem: async (menuId, itemData) => {
    const response = await api.post(`/menus/${menuId}/items`, itemData);
    return response.data.item;
  },

  /**
   * Update menu item (admin)
   */
  updateMenuItem: async (itemId, itemData) => {
    const response = await api.put(`/menus/items/${itemId}`, itemData);
    return response.data.item;
  },

  /**
   * Delete menu item (admin)
   */
  deleteMenuItem: async (itemId) => {
    const response = await api.delete(`/menus/items/${itemId}`);
    return response.data;
  },
};

export default menuService;
