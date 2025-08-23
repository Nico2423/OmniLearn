import { useState, useEffect, useRef } from "react";

export function useLessonStream(baseUrl: string, params?: Record<string, any>) {
  const [traces, setTraces] = useState<any[]>([]);
  const [lesson, setLesson] = useState("");
  const [isStreamingComplete, setIsStreamingComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!baseUrl) return;
    
    // Construct URL with query parameters for GET request
    let url = baseUrl;
    if (params) {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        queryParams.append(key, String(value));
      });
      url += '?' + queryParams.toString();
    }
    
    esRef.current = new EventSource(url);

    if (esRef.current) {
      esRef.current.onmessage = (e: MessageEvent) => {
        try {
          const obj = JSON.parse(e.data);
          
          // STREAM FINISHED
          if (obj.event === "complete") {
            setIsStreamingComplete(true);
            if (esRef.current) {
              esRef.current.close();
            }
            return;
          }
          // REASONING TRACE
          if (obj.step_type) {
            setTraces(t => [...t, obj]);
            return;
          }
        } catch {
          /* not JSON → treat as markdown */
          setLesson(l => l + e.data + "\n");
        }
      };

      esRef.current.onerror = (event: Event) => {
        console.error("SSE error:", event);

        if (event instanceof MessageEvent) {
          setError(`SSE Message Error: ${event.data}`);
        } else if (event instanceof ErrorEvent) {
          setError(`SSE Error: ${event.message}`);
        } else {
          setError("Unknown SSE connection error occurred");
        }

        if (esRef.current) {
          esRef.current.close();
        }
      };
    }
    
    return () => {
      if (esRef.current) {
        esRef.current.close();
      }
    };
  }, [baseUrl, JSON.stringify(params)]);

  return { traces, lesson, isStreamingComplete, error };
}
