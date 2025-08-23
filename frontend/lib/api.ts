import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
    } else if (error.message === 'Network Error') {
      console.error('Network error - check if backend is running');
    }
    return Promise.reject(error);
  }
);

// Set auth token for API requests
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

// Auth API
export const registerUser = async (email: string, password: string, name: string) => {
  const response = await api.post('/auth/register', { email, password, name });
  return response.data;
};

export const loginUser = async (email: string, password: string) => {
  const response = await api.post('/auth/login', null, {
    params: { email, password }
  });
  return response.data;
};

export const googleAuth = async (accessToken: string) => {
  const response = await api.post('/auth/google', { access_token: accessToken });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// Course API
export const createCourse = async (courseData: {
  title: string;
  description?: string;
  topic: string;
  visibility?: 'PRIVATE' | 'ORGANIZATION' | 'PUBLIC';
  organization_id?: number;
}) => {
  const response = await api.post('/courses/', courseData);
  return response.data;
};

export const getCourses = async (organizationId?: number) => {
  const params = organizationId ? { organization_id: organizationId } : {};
  const response = await api.get('/courses/', { params });
  return response.data;
};

export const getCourse = async (courseId: number) => {
  const response = await api.get(`/courses/${courseId}`);
  return response.data;
};

export const enrollInCourse = async (courseId: number) => {
  const response = await api.post(`/courses/${courseId}/enroll`);
  return response.data;
};

export const getCourseEnrollment = async (courseId: number) => {
  const response = await api.get(`/courses/${courseId}/enrollment`);
  return response.data;
};

export const updateCourseProgress = async (courseId: number, progressData: {
  subsection_id: number;
  score?: number;
  completed: boolean;
}) => {
  const response = await api.post(`/courses/${courseId}/progress`, progressData);
  return response.data;
};

// Organization API
export const createOrganization = async (orgData: { name: string; description?: string }) => {
  const response = await api.post('/organizations/', orgData);
  return response.data;
};

export const getMyOrganizations = async () => {
  const response = await api.get('/organizations/');
  return response.data;
};

export const getOrganization = async (orgId: number) => {
  const response = await api.get(`/organizations/${orgId}`);
  return response.data;
};

export const inviteUserToOrganization = async (orgId: number, inviteData: {
  email: string;
  role?: 'admin' | 'member';
}) => {
  const response = await api.post(`/organizations/${orgId}/invites`, inviteData);
  return response.data;
};

export const acceptOrganizationInvite = async (token: string) => {
  const response = await api.post(`/organizations/invites/${token}/accept`);
  return response.data;
};

// Knowledge Tree API (updated to work with courses)
export const createKnowledgeTree = async (topic: string) => {
  const response = await api.post('/knowledge-tree/', { topic });
  return response.data;
};

export const getKnowledgeTree = async (treeId: number) => {
  const response = await api.get(`/knowledge-tree/${treeId}`);
  return response.data;
};

// Lesson API
export const getLesson = async (subsectionId: number) => {
  const response = await api.get(`/lessons/subsection/${subsectionId}`);
  return response.data;
};

export const streamLesson = async (subsectionId: number, subsectionTitle: string) => {
  const response = await api.post('/lessons/stream', { 
    subsection_id: subsectionId, 
    subsection_title: subsectionTitle 
  }, {
    responseType: 'stream'
  });
  return response.data;
};

// Questions API
export const getQuestions = async (sectionId: number) => {
  const response = await api.get(`/questions/section/${sectionId}`);
  return response.data;
};

export const createQuestions = async (sectionId: number, sectionTitle: string) => {
  const response = await api.post('/questions/', { 
    section_id: sectionId, 
    section_title: sectionTitle 
  });
  return response.data;
};

export const evaluateAnswer = async (questionId: number, answer: string) => {
  const response = await api.post('/questions/evaluate', { question_id: questionId, answer });
  return response.data;
};

// Legacy user progress (keeping for backward compatibility)
export const updateUserProgress = async (subsectionId: number, score: number) => {
  const response = await api.post('/users/progress', { subsection_id: subsectionId, score });
  return response.data;
};

export default api;
export const deleteCourse = async (courseId: number) => {
  const response = await api.delete(`/courses/${courseId}`);
  return response.data;
};

export const linkKnowledgeTreeToCourse = async (courseId: number, knowledgeTreeId: number) => {
  const response = await api.put(`/courses/${courseId}/knowledge-tree`, null, {
    params: { knowledge_tree_id: knowledgeTreeId }
  });
  return response.data;
};
