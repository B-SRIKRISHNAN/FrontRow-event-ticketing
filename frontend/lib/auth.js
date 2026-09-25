/**
 * FrontRow Authentication & Session Manager (SSR-Safe)
 * Manages JWT bearer tokens and user profile state in localStorage with in-memory fallbacks.
 */

const TOKEN_KEY = 'frontrow_jwt_token';
const USER_KEY = 'frontrow_user_profile';

let memoryToken = null;
let memoryUser = null;

const isClient = typeof window !== 'undefined';

export function getToken() {
  if (isClient) {
    try {
      return localStorage.getItem(TOKEN_KEY) || memoryToken;
    } catch (e) {
      return memoryToken;
    }
  }
  return memoryToken;
}

export function setToken(token) {
  memoryToken = token;
  if (isClient) {
    try {
      if (token) {
        localStorage.setItem(TOKEN_KEY, token);
      } else {
        localStorage.removeItem(TOKEN_KEY);
      }
    } catch (e) {
      console.warn('localStorage error setting token:', e);
    }
  }
}

export function removeToken() {
  memoryToken = null;
  memoryUser = null;
  if (isClient) {
    try {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    } catch (e) {
      console.warn('localStorage error removing token:', e);
    }
  }
}

export function getUser() {
  if (isClient) {
    try {
      const stored = localStorage.getItem(USER_KEY);
      return stored ? JSON.parse(stored) : memoryUser;
    } catch (e) {
      return memoryUser;
    }
  }
  return memoryUser;
}

export function setUser(user) {
  memoryUser = user;
  if (isClient) {
    try {
      if (user) {
        localStorage.setItem(USER_KEY, JSON.stringify(user));
      } else {
        localStorage.removeItem(USER_KEY);
      }
    } catch (e) {
      console.warn('localStorage error setting user:', e);
    }
  }
}

export function isAuthenticated() {
  return !!getToken();
}
