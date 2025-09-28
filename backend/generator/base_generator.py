import os
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()


class Base:
    def __init__(self):
        os.environ["GROQ_API_KEY"] = os.getenv("groq_api_key")
        self.client = Groq()

        self.LLAMA3_70B_INSTRUCT = "llama-3.3-70b-versatile"
        self.LLAMA3_8B_INSTRUCT = "llama3.1-8b-instant"
        self.DEFAULT_MODEL = self.LLAMA3_70B_INSTRUCT

        # MongoDB setup
        mongo_uri = os.getenv("mongo_uri")
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client["creatiz"]
        self.collection = self.db["post_created_data"]

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

    def save_to_mongodb(self, input_data: dict, generated_content: dict) -> str:
        """
        Save the input parameters and generated content to MongoDB

        Args:
            input_data: Original input parameters
            generated_content: Generated content result

        Returns:
            str: MongoDB document ID
        """
        try:
            document = {
                "input_data": input_data,
                "generated_content": generated_content,
                "created_at": datetime.utcnow(),
                "model_used": self.DEFAULT_MODEL
            }

            result = self.collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving to MongoDB: {e}")
            return None


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
        """Generate content for both LinkedIn and X platforms and save to MongoDB"""
        result = {}

        # Generate content for LinkedIn
        result[platform] = self.generate_content_for_platform(
            idea, target_audience, platform, post_category
        )

        # Prepare input data for MongoDB
        input_data = {
            "idea": idea,
            "target_audience": target_audience,
            "platform": platform,
            "post_category": post_category
        }

        # Save to MongoDB
        document_id = self.save_to_mongodb(input_data, result)

        # Add document ID to result
        result["document_id"] = document_id

        return result


class MongoDBUtils:
    """Utility class for MongoDB operations"""

    def __init__(self):
        mongo_uri = os.getenv("mongo_uri")
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client["creatiz"]
        self.collection = self.db["post_created_data"]

    # Additional MongoDB utility functions
    def get_post_by_id(self, document_id: str) -> dict:
        """Retrieve a post by its MongoDB document ID"""
        try:
            collection = self.db["post_created_data"]
            result = collection.find_one({"_id": ObjectId(document_id)})
            if result:
                # Convert ObjectId to string
                result["_id"] = str(result["_id"])
            return result
        except Exception as e:
            print(f"Error retrieving from MongoDB: {e}")
            return None
        finally:
            self.client.close()

    def get_posts_by_filters(self, filters: dict = None, limit: int = 10) -> list:
        """Retrieve posts with optional filters"""
        try:

            query = filters if filters else {}
            results = list(self.collection.find(query).limit(
                limit).sort("created_at", -1))

            # Convert ObjectId to string for JSON serialization
            for result in results:
                result["_id"] = str(result["_id"])

            return results
        except Exception as e:
            print(f"Error retrieving from MongoDB: {e}")
            return []
        finally:
            self.client.close()

    def delete_post_by_id(self, document_id: str) -> bool:
        """Delete a post by its MongoDB document ID"""
        try:

            result = self.collection.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting from MongoDB: {e}")
            return False
        finally:
            self.client.close()
