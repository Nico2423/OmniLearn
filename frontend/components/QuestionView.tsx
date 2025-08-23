"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "./ui/button";
import { Form, FormControl, FormField, FormItem } from "./ui/form";
import { Textarea } from "./ui/textarea";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "./ui/card";
import { Collapsible } from "./ui/collapsible";
import { MarkdownRenderer } from "./ui/markdown-renderer";
import { getQuestions, createQuestions, evaluateAnswer } from "../lib/api";

interface QuestionViewProps {
  sectionId: number;
}

const answerSchema = z.object({
  answer: z.string().min(1, { message: "Please provide an answer." }),
});

type AnswerFormValues = z.infer<typeof answerSchema>;

export default function QuestionView({ sectionId }: QuestionViewProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [feedback, setFeedback] = useState<{ isCorrect: boolean; feedback: string } | null>(null);

  const { data: questions, isLoading, error, refetch } = useQuery({
    queryKey: ["questions", sectionId],
    queryFn: () => getQuestions(sectionId),
    enabled: !!sectionId,
  });

  const createQuestionsMutation = useMutation({
    mutationFn: ({ sectionId, sectionTitle }: { sectionId: number; sectionTitle: string }) => 
      createQuestions(sectionId, sectionTitle),
    onSuccess: () => {
      refetch(); // Refetch questions after creating them
    },
  });

  const form = useForm<AnswerFormValues>({
    resolver: zodResolver(answerSchema),
    defaultValues: {
      answer: "",
    },
  });

  const evaluateMutation = useMutation({
    mutationFn: (data: { questionId: number; answer: string }) => 
      evaluateAnswer(data.questionId, data.answer),
    onSuccess: (data) => {
      setFeedback(data);
    },
  });

  if (isLoading) {
    return <div className="text-center py-4">Loading questions...</div>;
  }

  if (error) {
    return (
      <div className="text-center py-4 text-red-500">
        Error loading questions. Please try again.
      </div>
    );
  }

  if (!questions || questions.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="mb-4">No practice questions available for this section.</p>
        <Button 
          onClick={() => createQuestionsMutation.mutate({ sectionId, sectionTitle: `Section ${sectionId}` })}
          disabled={createQuestionsMutation.isPending}
        >
          {createQuestionsMutation.isPending ? "Generating Questions..." : "Generate Practice Questions"}
        </Button>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];

  const onSubmit = (values: AnswerFormValues) => {
    evaluateMutation.mutate({
      questionId: currentQuestion.id,
      answer: values.answer,
    });
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setFeedback(null);
      form.reset();
    }
  };

  return (
    <div>
      <Card>
        <CardHeader>
          <CardTitle>
            Question {currentQuestionIndex + 1} of {questions.length}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4">{currentQuestion.text}</p>
          
          
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="answer"
                render={({ field }) => (
                  <FormItem>
                    <FormControl>
                      <Textarea
                        placeholder="Type your answer here..."
                        className="min-h-[100px]"
                        disabled={!!feedback}
                        {...field}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
              {!feedback && (
                <Button type="submit" disabled={evaluateMutation.isPending}>
                  {evaluateMutation.isPending ? "Checking..." : "Submit Answer"}
                </Button>
              )}
            </form>
          </Form>

          {feedback && (
            <div className={`mt-6 p-4 rounded-lg ${feedback.isCorrect ? "bg-green-50" : "bg-red-50"}`}>
              <h3 className={`font-medium ${feedback.isCorrect ? "text-green-700" : "text-red-700"}`}>
                {feedback.isCorrect ? "Correct!" : "Not quite right"}
              </h3>
              <p className="mt-2">{feedback.feedback}</p>
              
            </div>
          )}
        </CardContent>
        {feedback && (
          <CardFooter>
            <Button onClick={handleNextQuestion} disabled={currentQuestionIndex >= questions.length - 1}>
              Next Question
            </Button>
          </CardFooter>
        )}
      </Card>
    </div>
  );
}
