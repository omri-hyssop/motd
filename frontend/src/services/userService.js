import api from './api';

const userService = {
  listUsers: async (params = {}) => {
    const response = await api.get('/users', { params });
    return response.data;
  },

  createUser: async (payload) => {
    const response = await api.post('/users', payload);
    return response.data.user;
  },

  updateUser: async (userId, payload) => {
    const response = await api.put(`/users/${userId}`, payload);
    return response.data.user;
  },
};

export default userService;

