import os
from groq import Groq


class Base:
    def __init__(self):
        os.environ["GROQ_API_KEY"] = "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"
        self.client = Groq()

        self.LLAMA3_70B_INSTRUCT = "llama-3.3-70b-versatile"
        self.LLAMA3_8B_INSTRUCT = "llama3.1-8b-instant"
        self.DEFAULT_MODEL = self.LLAMA3_70B_INSTRUCT

    def chat_completion(self, messages, temperature=0.6, top_p=0.9) -> str:
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.DEFAULT_MODEL,
                temperature=temperature,
                top_p=top_p,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"


class MediaBasedContentGenerator(Base):
    def __init__(self):
        super().__init__()

    def create_content_prompt(self, idea, target_audience, platform, post_category, content_size):
        """Create a prompt for generating content based on parameters"""
        size_guidelines = {
            "small": "Keep it concise, under 100 words, perfect for quick engagement",
            "medium": "Medium length, 100-200 words, balanced detail and engagement",
            "long": "Detailed content, 200+ words, comprehensive and in-depth"
        }

        platform_guidelines = {
            "linkedin": "Professional tone, business-focused, thought leadership style",
            "x": "Conversational, punchy, hashtag-friendly, Twitter/X optimized"
        }

        prompt = f"""
        Create a {content_size} {platform} post about: {idea}
        
        Target Audience: {target_audience}
        Category: {post_category}
        
        Platform Guidelines: {platform_guidelines.get(platform, "General social media style")}
        Size Guidelines: {size_guidelines.get(content_size, "")}
        
        Make it engaging, relevant to the target audience, and optimized for {platform}.
        Return only the post content, no additional formatting or explanations.
        """

        return prompt

    def generate_content_for_platform(self, idea, target_audience, platform, post_category):
        """Generate small, medium, and long content for a specific platform"""
        content = {}

        for size in ["small", "medium", "long"]:
            prompt = self.create_content_prompt(
                idea, target_audience, platform, post_category, size)
            messages = [{"role": "user", "content": prompt}]
            content[size] = self.chat_completion(messages)

        return content

    def generate_all_content(self, idea, target_audience, platform, post_category):
        """Generate content for both LinkedIn and X platforms"""
        result = {}

        # Generate content for LinkedIn
        result[platform] = self.generate_content_for_platform(
            idea, target_audience, platform, post_category
        )

        return result
