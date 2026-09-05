"""
Data loading script for Winnipeg Regulations Agent

This script:
1. Reads regulation data from JSON files
2. Creates embeddings using OpenAI
3. Indexes in Pinecone vector database
4. Stores metadata in PostgreSQL database
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

try:
    from openai import OpenAI
    from pinecone import Pinecone
except ImportError:
    print("Error: Required packages not installed. Run: pip install -r requirements.txt")
    exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RegulationDataLoader:
    """Load and index regulation data"""
    
    def __init__(self):
        """Initialize the data loader"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
        self.pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.index = self.pc.Index(self.pinecone_index_name)
        
        logger.info("RegulationDataLoader initialized")
    
    def load_regulation_files(self, data_dir: str = "data/regulations") -> List[Dict[str, Any]]:
        """
        Load all regulation JSON files from directory
        
        Args:
            data_dir: Directory containing regulation files
            
        Returns:
            List of regulation dictionaries
        """
        logger.info(f"Loading regulation files from {data_dir}")
        
        all_regulations = []
        data_path = Path(data_dir)
        
        if not data_path.exists():
            logger.error(f"Directory {data_dir} does not exist")
            return []
        
        # Load all JSON files
        for json_file in data_path.glob("*.json"):
            logger.info(f"Loading {json_file.name}")
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                    # Handle both direct regulation list or nested structure
                    if isinstance(data, dict) and "regulations" in data:
                        all_regulations.extend(data["regulations"])
                    elif isinstance(data, list):
                        all_regulations.extend(data)
                    
                logger.info(f"Loaded {len(data)} regulations from {json_file.name}")
            except Exception as e:
                logger.error(f"Error loading {json_file.name}: {str(e)}")
        
        logger.info(f"Total regulations loaded: {len(all_regulations)}")
        return all_regulations
    
    def create_embeddings(self, text: str) -> List[float]:
        """
        Create embedding for text using OpenAI
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return []
    
    def prepare_regulation_vector(self, regulation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare regulation for vector indexing
        
        Args:
            regulation: Regulation dictionary
            
        Returns:
            Prepared vector with metadata
        """
        # Create embedding text combining title and content
        embedding_text = f"{regulation.get('title', '')} {regulation.get('section', '')} {regulation.get('text', '')}"
        
        # Create embedding
        embedding = self.create_embeddings(embedding_text)
        
        if not embedding:
            logger.warning(f"Failed to create embedding for regulation {regulation.get('id')}")
            return None
        
        # Create unique ID
        vector_id = f"{regulation.get('id', '')}-{regulation.get('section', '')}"
        
        # Prepare metadata (exclude embeddings)
        metadata = {
            "id": regulation.get("id", ""),
            "title": regulation.get("title", ""),
            "section": regulation.get("section", ""),
            "subsection": regulation.get("subsection", ""),
            "text": regulation.get("text", "")[:500],  # Limit text for metadata
            "category": regulation.get("category", ""),
            "effective_date": regulation.get("effective_date", ""),
            "source_url": regulation.get("source_url", ""),
            "tags": ",".join(regulation.get("tags", []))
        }
        
        return {
            "id": vector_id,
            "values": embedding,
            "metadata": metadata
        }
    
    def index_regulations(self, regulations: List[Dict[str, Any]], batch_size: int = 100):
        """
        Index regulations in Pinecone
        
        Args:
            regulations: List of regulation dictionaries
            batch_size: Number of vectors to upsert at once
        """
        logger.info(f"Indexing {len(regulations)} regulations in Pinecone")
        
        vectors_to_upsert = []
        successful = 0
        failed = 0
        
        for i, regulation in enumerate(regulations):
            try:
                vector = self.prepare_regulation_vector(regulation)
                
                if vector:
                    vectors_to_upsert.append(vector)
                    successful += 1
                else:
                    failed += 1
                
                # Upsert in batches
                if len(vectors_to_upsert) >= batch_size:
                    logger.info(f"Upserting batch of {len(vectors_to_upsert)} vectors...")
                    self.index.upsert(vectors=vectors_to_upsert)
                    vectors_to_upsert = []
                
                # Progress logging
                if (i + 1) % 50 == 0:
                    logger.info(f"Processed {i + 1}/{len(regulations)} regulations")
            
            except Exception as e:
                logger.error(f"Error processing regulation {i}: {str(e)}")
                failed += 1
                continue
        
        # Upsert remaining vectors
        if vectors_to_upsert:
            logger.info(f"Upserting final batch of {len(vectors_to_upsert)} vectors...")
            self.index.upsert(vectors=vectors_to_upsert)
        
        logger.info(f"Indexing complete: {successful} successful, {failed} failed")
    
    def run(self, data_dir: str = "data/regulations"):
        """
        Run the complete data loading pipeline
        
        Args:
            data_dir: Directory containing regulation files
        """
        try:
            # Load regulation files
            regulations = self.load_regulation_files(data_dir)
            
            if not regulations:
                logger.warning("No regulations loaded. Exiting.")
                return
            
            # Index in Pinecone
            self.index_regulations(regulations)
            
            logger.info("✓ Data loading complete!")
            logger.info(f"  - Total regulations indexed: {len(regulations)}")
            logger.info(f"  - Pinecone index: {self.pinecone_index_name}")
            
        except Exception as e:
            logger.error(f"Fatal error during data loading: {str(e)}")
            raise


def main():
    """Main entry point"""
    import sys
    
    logger.info("Starting Winnipeg Regulations Data Loader")
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_ENVIRONMENT", "PINECONE_INDEX_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these in your .env file")
        return 1
    
    try:
        loader = RegulationDataLoader()
        loader.run()
        return 0
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
