"use client";

import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { getCourses, deleteCourse } from "../lib/api";

interface Course {
  id: number;
  title: string;
  description?: string;
  topic: string;
  visibility: string;
  created_at: string;
  knowledge_tree_id?: number;
}

interface CourseDashboardProps {
  onCreateNew: () => void;
  onSelectCourse: (courseId: number, knowledgeTreeId?: number) => void;
}

export function CourseDashboard({
  onCreateNew,
  onSelectCourse,
}: CourseDashboardProps) {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const userCourses = await getCourses();
      setCourses(userCourses);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load courses");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCourse = async (courseId: number) => {
    if (
      !confirm(
        "Are you sure you want to delete this course? This action cannot be undone."
      )
    ) {
      return;
    }

    try {
      await deleteCourse(courseId);
      setCourses(courses.filter((c) => c.id !== courseId));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete course");
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const getVisibilityBadge = (visibility: string) => {
    const colors = {
      PRIVATE: "bg-gray-100 text-gray-800",
      ORGANIZATION: "bg-blue-100 text-blue-800",
      PUBLIC: "bg-green-100 text-green-800",
    };

    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium ${
          colors[visibility as keyof typeof colors] || colors.PRIVATE
        }`}
      >
        {visibility.toLowerCase()}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              <div className="h-4 bg-gray-200 rounded w-4/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">My Courses</h2>
          <Button onClick={onCreateNew}>Create New Course</Button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {courses.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg
                className="mx-auto h-12 w-12"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No courses yet
            </h3>
            <p className="text-gray-600 mb-4">
              Create your first course to start learning!
            </p>
            <Button onClick={onCreateNew}>Create Your First Course</Button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {courses.map((course) => (
              <div
                key={course.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-900 truncate">
                    {course.title}
                  </h3>
                  {getVisibilityBadge(course.visibility)}
                </div>

                <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                  Topic: {course.topic}
                </p>

                {course.description && (
                  <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                    {course.description}
                  </p>
                )}

                <div className="flex justify-between items-center text-xs text-gray-400 mb-3">
                  <span>Created {formatDate(course.created_at)}</span>
                </div>

                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    onClick={() =>
                      onSelectCourse(course.id, course.knowledge_tree_id)
                    }
                    className="flex-1"
                  >
                    Open
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleDeleteCourse(course.id)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    Delete
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
