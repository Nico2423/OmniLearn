'use client';

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '../lib/auth-context';
import { AuthScreen } from '../components/auth/AuthScreen';
import { Header } from '../components/Header';
import { CourseForm } from '../components/CourseForm';
import KnowledgeTreeView from '../components/KnowledgeTreeView';

const queryClient = new QueryClient();

function AppContent() {
  const { user, loading } = useAuth();
  const [activeCourseId, setActiveCourseId] = useState<number | null>(null);

  const handleCourseCreated = (courseId: number) => {
    setActiveCourseId(courseId);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <AuthScreen />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto py-8">
        {!activeCourseId ? (
          <CourseForm onSuccess={handleCourseCreated} />
        ) : (
          <div>
            <div className="mb-4">
              <button
                onClick={() => setActiveCourseId(null)}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                ← Back to Course Creation
              </button>
            </div>
            {/* TODO: Integrate course with knowledge tree */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4">Course Created Successfully!</h2>
              <p className="text-gray-600">
                Course ID: {activeCourseId}. Knowledge tree integration coming soon.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default function Home() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </QueryClientProvider>
  );
}