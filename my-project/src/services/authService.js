import api from './api';

export const authService = {
  signup: async (email, password, role = 'Member') => {
    const response = await api.post('/auth/signup', {
      email,
      password,
      role,
    });
    return response.data;
  },

  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    
    const userInfo = await authService.getCurrentUser();
    localStorage.setItem('user', JSON.stringify(userInfo));
    
    return { token: access_token, user: userInfo };
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/users/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },

  getStoredUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
};
