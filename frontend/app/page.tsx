'use client';

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '../lib/auth-context';
import { AuthScreen } from '../components/auth/AuthScreen';
import { Header } from '../components/Header';
import { CourseForm } from '../components/CourseForm';
import { CourseDashboard } from '../components/CourseDashboard';
import KnowledgeTreeView from '../components/KnowledgeTreeView';
import { getCourse, createKnowledgeTree, linkKnowledgeTreeToCourse, enrollInCourse } from '../lib/api';

const queryClient = new QueryClient();

type ViewState = 'dashboard' | 'create' | 'learning';

function AppContent() {
  const { user, loading } = useAuth();
  const [currentView, setCurrentView] = useState<ViewState>('dashboard');
  const [activeTreeId, setActiveTreeId] = useState<number | null>(null);
  const [activeCourseId, setActiveCourseId] = useState<number | null>(null);

  const handleKnowledgeTreeCreated = (treeId: number) => {
    setActiveTreeId(treeId);
    setCurrentView('learning');
  };

  const handleCourseSelected = async (courseId: number, knowledgeTreeId?: number) => {
    console.log('Opening course:', courseId, 'with knowledge tree:', knowledgeTreeId);
    setActiveCourseId(courseId);
    
    try {
      if (knowledgeTreeId) {
        // Course has knowledge tree, just load it
        setActiveTreeId(knowledgeTreeId);
        setCurrentView('learning');
        
        // Try to enroll user in course (in background)
        enrollInCourse(courseId).catch(error => {
          console.log('Background enrollment note:', error.response?.data?.detail || error.message);
        });
      } else {
        // Course exists but no knowledge tree yet - need to generate it
        console.log('Generating knowledge tree for course...');
        
        const course = await getCourse(courseId);
        console.log('Got course:', course.title);
        
        const knowledgeTree = await createKnowledgeTree(course.topic);
        console.log('Generated knowledge tree:', knowledgeTree.id);
        
        await linkKnowledgeTreeToCourse(courseId, knowledgeTree.id);
        console.log('Linked knowledge tree to course');
        
        await enrollInCourse(courseId);
        console.log('Enrolled in course');
        
        setActiveTreeId(knowledgeTree.id);
        setCurrentView('learning');
      }
    } catch (error) {
      console.error('Failed to open course:', error);
      alert('Failed to open course. Please try again.');
      setCurrentView('dashboard');
    }
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    setActiveTreeId(null);
    setActiveCourseId(null);
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
        {currentView === 'dashboard' && (
          <CourseDashboard 
            onCreateNew={() => setCurrentView('create')}
            onSelectCourse={handleCourseSelected}
          />
        )}
        
        {currentView === 'create' && (
          <div>
            <div className="mb-4">
              <button
                onClick={handleBackToDashboard}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                ← Back to Dashboard
              </button>
            </div>
            <CourseForm onSuccess={handleKnowledgeTreeCreated} />
          </div>
        )}
        
        {currentView === 'learning' && activeTreeId && (
          <div>
            <div className="mb-4">
              <button
                onClick={handleBackToDashboard}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                ← Back to Dashboard
              </button>
            </div>
            <KnowledgeTreeView treeId={activeTreeId} />
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