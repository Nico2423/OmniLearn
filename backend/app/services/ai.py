import json
from typing import List, Dict, Any, AsyncGenerator
from abc import ABC, abstractmethod

from openai import OpenAI, AsyncOpenAI
import google.generativeai as genai

from app.core.config import settings


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    async def generate_completion(self, messages: List[Dict[str, str]], use_json: bool = False) -> str:
        """Generate a completion from the AI provider."""
        pass
    
    @abstractmethod
    async def stream_completion(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Stream completion from the AI provider."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model
    
    async def generate_completion(self, messages: List[Dict[str, str]], use_json: bool = False) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages
        }
        
        if use_json:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    async def stream_completion(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Stream completion from OpenAI."""
        stream = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class OpenRouterProvider(AIProvider):
    """OpenRouter API provider (uses OpenAI client with different base URL)."""
    
    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.async_client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model
    
    async def generate_completion(self, messages: List[Dict[str, str]], use_json: bool = False) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages
        }
        
        if use_json:
            kwargs["response_format"] = {"type": "json_object"}
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    async def stream_completion(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Stream completion from OpenRouter."""
        stream = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class GeminiProvider(AIProvider):
    """Google Gemini API provider."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    async def generate_completion(self, messages: List[Dict[str, str]], use_json: bool = False) -> str:
        # Convert OpenAI-style messages to Gemini format
        prompt = ""
        for message in messages:
            if message["role"] == "system":
                prompt += f"System: {message['content']}\n\n"
            elif message["role"] == "user":
                prompt += f"User: {message['content']}\n\n"
        
        if use_json:
            prompt += "\nPlease respond with valid JSON only."
        
        response = self.model.generate_content(prompt)
        return response.text
    
    async def stream_completion(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Simulate streaming completion from Gemini by yielding the full response in chunks."""
        # Convert OpenAI-style messages to Gemini format
        prompt = ""
        for message in messages:
            if message["role"] == "system":
                prompt += f"System: {message['content']}\n\n"
            elif message["role"] == "user":
                prompt += f"User: {message['content']}\n\n"
        
        response = self.model.generate_content(prompt)
        full_text = response.text
        
        # Simulate streaming by yielding chunks of text
        chunk_size = 50  # characters per chunk
        for i in range(0, len(full_text), chunk_size):
            chunk = full_text[i:i+chunk_size]
            yield chunk


class AIService:
    """Configurable AI service that supports multiple providers."""
    
    def __init__(self):
        self.provider = self._create_provider()
        self.enable_multimedia = settings.ENABLE_MULTIMEDIA
    
    async def stream_completion(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Stream completion from the AI provider."""
        async for chunk in self.provider.stream_completion(messages):
            yield chunk
    
    def _create_provider(self) -> AIProvider:
        """Create the appropriate AI provider based on configuration."""
        provider_name = settings.AI_PROVIDER.lower()
        model = settings.AI_MODEL
        
        if provider_name == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
            return OpenAIProvider(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
                model=model
            )
        
        elif provider_name == "openrouter":
            if not settings.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY is required for OpenRouter provider")
            return OpenRouterProvider(
                api_key=settings.OPENROUTER_API_KEY,
                model=model
            )
        
        elif provider_name == "gemini":
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required for Gemini provider")
            return GeminiProvider(
                api_key=settings.GEMINI_API_KEY,
                model=model
            )
        
        else:
            raise ValueError(f"Unsupported AI provider: {provider_name}")
    
    async def generate_knowledge_tree(self, topic: str) -> Dict[str, Any]:
        """Generate a knowledge tree structure for a given topic."""
        prompt = f"""
        Create a comprehensive knowledge tree for the topic: "{topic}"
        
        The knowledge tree should be structured as follows:
        - A main topic with 3-5 sections
        - Each section should have 2-4 subsections
        - Each section and subsection should have a clear title and description
        - Focus on creating a logical learning progression
        
        Format the response as a JSON object with the following structure:
        {{
            "topic": "{topic}",
            "sections": [
                {{
                    "title": "Section Title",
                    "description": "Brief description of what this section covers",
                    "subsections": [
                        {{
                            "title": "Subsection Title",
                            "description": "Brief description of what this subsection covers"
                        }}
                    ]
                }}
            ]
        }}
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert educational content creator."},
                {"role": "user", "content": prompt}
            ]
            
            content = await self.provider.generate_completion(messages, use_json=True)
            if not content:
                raise ValueError("AI provider returned empty content")
                
            return json.loads(content)
            
        except Exception as e:
            print(f"Error generating knowledge tree: {str(e)}")
            raise ValueError(f"Failed to generate knowledge tree: {str(e)}")

    async def generate_lesson_content(self, subsection_title: str, subsection_description: str) -> str:
        """Generate lesson content for a subsection."""
        prompt = f"""
        Create comprehensive lesson content for the following subsection:
        
        Title: {subsection_title}
        Description: {subsection_description}
        
        The lesson should be:
        - Well-structured with clear headings and subheadings
        - Include practical examples where appropriate
        - Be educational and engaging
        - Use markdown formatting for better readability
        - Be comprehensive but not overwhelming
        
        Focus on explaining concepts clearly and providing actionable information that helps students learn effectively.
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert educational content creator specializing in creating clear, comprehensive lessons."},
                {"role": "user", "content": prompt}
            ]
            
            content = await self.provider.generate_completion(messages)
            if not content:
                raise ValueError("AI provider returned empty content")
                
            return content
            
        except Exception as e:
            print(f"Error generating lesson content: {str(e)}")
            raise ValueError(f"Failed to generate lesson content: {str(e)}")

    async def generate_multimedia(self, title: str, content: str) -> List[str]:
        """Generate multimedia content suggestions."""
        # Note: This is a placeholder implementation
        # In a real implementation, you would integrate with image/video generation APIs
        if not self.enable_multimedia:
            return []
        
        prompt = f"""
        Based on the lesson title "{title}" and content, suggest 2-3 multimedia elements that would enhance learning.
        
        Content: {content}
        
        For each concept, provide a brief description of what the image should depict.
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are an educational content creator."},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.provider.generate_completion(messages)
            concepts = response.split("\n\n")
            
            # Return placeholder URLs for now
            # In production, you would generate actual multimedia content
            return [f"https://placeholder.example.com/image_{i}.jpg" for i in range(min(2, len(concepts)))]
            
        except Exception as e:
            print(f"Error generating multimedia: {str(e)}")
            return []

    async def generate_questions(
        self, section_title: str, section_description: str, difficulty: str = "medium"
    ) -> List[Dict[str, Any]]:
        """Generate practice questions for a section."""
        prompt = f"""
        Generate 3 practice questions for the following section:
        
        Title: {section_title}
        Description: {section_description}
        Difficulty: {difficulty}
        
        The questions should cover key concepts from the section and be appropriate for the specified difficulty level.
        For each question, provide the question text and the correct answer.
        
        Format the response as a JSON object with a "questions" array:
        {{
            "questions": [
                {{
                    "text": "Question text",
                    "difficulty": "{difficulty}",
                    "correct_answer": "Correct answer"
                }}
            ]
        }}
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are an educational content creator."},
                {"role": "user", "content": prompt}
            ]
            
            content = await self.provider.generate_completion(messages, use_json=True)
            if not content:
                raise ValueError("AI provider returned empty content")
                
            result = json.loads(content)
            return result.get("questions", [])
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            raise ValueError(f"Failed to generate questions: {str(e)}")

    async def evaluate_answer(
        self, question: str, correct_answer: str, student_answer: str
    ) -> Dict[str, Any]:
        """Evaluate a student's answer to a question."""
        prompt = f"""
        You are a professional and highly experienced teacher. 
        Always speak in the first person, as if you are talking directly to the student. 
        Be gentle, tolerant, and supportive, even when the answer is wrong. 
        Your goal is to help the student feel confident, motivated, and eager to improve.

        Evaluate the student's answer to the following question:

        Question: {question}
        Correct Answer: {correct_answer}
        Student's Answer: {student_answer}

        Instructions:
        1. First, determine if the student's answer is correct or incorrect.
        2. Give detailed and constructive feedback in the first person:
        - If the answer is correct: Praise warmly, elaborate on the topic, and show enthusiasm for their effort.
        - If the answer is incorrect: Gently point out where they might be mistaken, guide them toward the correct understanding without simply giving the answer, and motivate them to try again.
        3. Always end with a short motivational message that encourages them to keep learning and improving.

        Format your response as a JSON object:
        {{
            "is_correct": true/false,
            "feedback": "Your warm, encouraging, first-person feedback here"
        }}
        """
        
        
        try:
            messages = [
                {"role": "system", "content": "You are an educational evaluator providing constructive feedback."},
                {"role": "user", "content": prompt}
            ]
            
            content = await self.provider.generate_completion(messages, use_json=True)
            if not content:
                raise ValueError("AI provider returned empty content")
                
            return json.loads(content)
            
        except Exception as e:
            print(f"Error evaluating answer: {str(e)}")
            raise ValueError(f"Failed to evaluate answer: {str(e)}")
