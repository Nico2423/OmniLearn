"use client";

import { useState } from "react";
import { useLessonStream } from "../../lib/useLessonStream";
import ReactMarkdown from "react-markdown";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "../ui/card";
import { Button } from "../ui/button";

interface StreamingLessonViewProps {
  subsectionId: number;
  subsectionTitle: string;
  onBack: () => void;
}

interface ReasoningTrace {
  step_number: number;
  step_type: string;
  content: string;
}

export default function StreamingLessonView({ subsectionId, subsectionTitle, onBack }: StreamingLessonViewProps) {
  const [showReasoning, setShowReasoning] = useState(true);
  const { traces, lesson, isStreamingComplete, error } = useLessonStream(
    `${process.env.NEXT_PUBLIC_API_URL}/api/v1/lessons/stream`,
    {
      subsection_id: subsectionId,
      subsection_title: encodeURIComponent(subsectionTitle)
    }
  );

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-red-500">Error loading lesson: {error}</p>
        </CardContent>
      </Card>
    );
  }

  // Simple loading skeleton component
  const LoadingSkeleton = () => (
    <div className="animate-pulse space-y-3">
      <div className="h-4 bg-gray-200 rounded w-full"></div>
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
    </div>
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {showReasoning && (
        <Card className="lg:col-span-1 h-fit">
          <CardHeader>
            <CardTitle>Reasoning Traces</CardTitle>
            <CardDescription>Watch how the AI thinks through the lesson</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {traces.length === 0 && !isStreamingComplete && (
                <div className="space-y-3">
                  <LoadingSkeleton />
                </div>
              )}
              
              {traces.map((trace: ReasoningTrace, index: number) => (
                <div key={index} className="p-3 bg-gray-50 rounded text-sm">
                  <div className="font-medium text-gray-700">{trace.step_type}</div>
                  <div className="text-gray-600 mt-1">{trace.content}</div>
                </div>
              ))}
              
              {isStreamingComplete && traces.length === 0 && (
                <div className="text-center text-gray-500 py-4">
                  No reasoning traces available
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
      
      <Card className="lg:col-span-2">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>{subsectionTitle}</CardTitle>
              <CardDescription>
                {isStreamingComplete ? "Lesson complete" : "Generating lesson content..."}
              </CardDescription>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => setShowReasoning(!showReasoning)}
            >
              {showReasoning ? "Hide" : "Show"} Reasoning
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {lesson ? (
            <div className="prose max-w-none">
              <ReactMarkdown>{lesson}</ReactMarkdown>
            </div>
          ) : (
            <div className="space-y-4">
              <LoadingSkeleton />
            </div>
          )}
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button variant="outline" onClick={onBack}>
            Back to Learning Path
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}
