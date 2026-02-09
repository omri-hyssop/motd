import api from './api';

const restaurantService = {
  /**
   * Get all restaurants
   */
  getRestaurants: async () => {
    const response = await api.get('/restaurants');
    return response.data.restaurants;
  },

  /**
   * Get restaurant by ID
   */
  getRestaurant: async (restaurantId) => {
    const response = await api.get(`/restaurants/${restaurantId}`);
    return response.data;
  },

  /**
   * Create new restaurant (admin)
   */
  createRestaurant: async (restaurantData) => {
    const response = await api.post('/restaurants', restaurantData);
    return response.data.restaurant;
  },

  /**
   * Update restaurant (admin)
   */
  updateRestaurant: async (restaurantId, restaurantData) => {
    const response = await api.put(`/restaurants/${restaurantId}`, restaurantData);
    return response.data.restaurant;
  },

  /**
   * Deactivate restaurant (admin)
   */
  deleteRestaurant: async (restaurantId) => {
    const response = await api.delete(`/restaurants/${restaurantId}`);
    return response.data;
  },
};

export default restaurantService;
