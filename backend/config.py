import os
from dataclasses import dataclass

@dataclass
class Config:
    # Neo4j configuration
    # 星彤安姐的数据库
    # NEO4J_URI: str = os.getenv("NEO4J_URI", "neo4j+ssc://3ed60672.databases.neo4j.io")
    # NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    # NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "FV3a-3QE7Ohm0FALOPjXS4s-ou0ZBC085KChw1Nxfhs")
    
    # 汪晨亮的数据库  1d0a4f56
    NEO4J_URI: str = os.getenv("NEO4J_URI", "neo4j+ssc://1d0a4f56.databases.neo4j.io")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "avvEdZo3G7vI6sg5W8PmvjlApCY80eWKHfniJNE63Z8")
    
    # 赵佳乐的google账号 数据库 全量数据库（未合并）
    # NEO4J_URI: str = os.getenv("NEO4J_URI", "neo4j+ssc://77676871.databases.neo4j.io")
    # NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    # NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "afQnPFnrooTkThQP-cjpOHm1kVdq5h1x_4ZwcXGuqUs")

    # # 赵佳乐的163账号 数据库  人物合并后的全量数据库
    # NEO4J_URI: str = os.getenv("NEO4J_URI", "neo4j+s://01038fe5.databases.neo4j.io")
    # NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    # NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "yaO20izaPikvn82y1noARwyoEthccxXrStv41XSsbj4")
    
    
    # AI configuration
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "deepseek")
    AI_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "sk-f500c51dadeb406ea046ab2abf8d95bf")
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "https://api.deepseek.com/v1")
    AI_MODEL: str = os.getenv("AI_MODEL", "deepseek-chat")
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.001"))
    AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", "8192"))
    
    # Redis configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # Cache configuration
    SCHEMA_CACHE_TTL: int = int(os.getenv("SCHEMA_CACHE_TTL", "3600"))  # 1 hour
    QUERY_CACHE_TTL: int = int(os.getenv("QUERY_CACHE_TTL", "1800"))   # 30 minutes
    ENTITY_CACHE_TTL: int = int(os.getenv("ENTITY_CACHE_TTL", "1200")) # 20 minutes
    
    # Performance configuration
    MAX_WORKERS: int = int(os.getenv("MAX_WORKERS", "4"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "2"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

config = Config()