'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { createCourse } from '../lib/api';

const courseSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters'),
  description: z.string().optional(),
  topic: z.string().min(3, 'Topic must be at least 3 characters'),
  visibility: z.enum(['private', 'organization', 'public']).default('private'),
});

type CourseFormData = z.infer<typeof courseSchema>;

interface CourseFormProps {
  onSuccess: (courseId: number) => void;
}

export function CourseForm({ onSuccess }: CourseFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CourseFormData>({
    resolver: zodResolver(courseSchema),
    defaultValues: {
      visibility: 'private',
    },
  });

  const onSubmit = async (data: CourseFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const course = await createCourse(data);
      reset();
      onSuccess(course.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create course. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-center mb-6">Create New Course</h2>
        <p className="text-gray-600 text-center mb-6">
          Create a personalized learning course on any topic.
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <Label htmlFor="title">Course Title</Label>
            <Input
              id="title"
              {...register('title')}
              className="mt-1"
              placeholder="e.g., Introduction to Quantum Physics"
            />
            {errors.title && (
              <p className="text-red-500 text-sm mt-1">{errors.title.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="topic">Learning Topic</Label>
            <Input
              id="topic"
              {...register('topic')}
              className="mt-1"
              placeholder="e.g., Quantum Physics"
            />
            {errors.topic && (
              <p className="text-red-500 text-sm mt-1">{errors.topic.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="description">Description (Optional)</Label>
            <Textarea
              id="description"
              {...register('description')}
              className="mt-1"
              placeholder="Describe what this course will cover..."
              rows={3}
            />
            {errors.description && (
              <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="visibility">Visibility</Label>
            <select
              id="visibility"
              {...register('visibility')}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="private">Private (Only me)</option>
              <option value="organization">Organization (Team members)</option>
              <option value="public">Public (Everyone)</option>
            </select>
            {errors.visibility && (
              <p className="text-red-500 text-sm mt-1">{errors.visibility.message}</p>
            )}
          </div>

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? 'Creating Course...' : 'Create Course'}
          </Button>
        </form>
      </div>
    </div>
  );
}