import openai
import re
import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Any, Generator

# 导入Neo4j图类型中缺失的模块
from neo4j.graph import Node, Relationship, Path

from config import config
from cache import cache_manager
from neo4j_driver import driver
from utils import generate_cache_key, process_graph_result, process_table_result

logger = logging.getLogger(__name__)

# 初始化AI客户端
client = openai.OpenAI(
    api_key=config.AI_API_KEY,
    base_url=config.AI_BASE_URL
)
logger.info(f"AI客户端已初始化: Provider={config.AI_PROVIDER}, Model={config.AI_MODEL}")

# 用于并行任务的线程池
executor = ThreadPoolExecutor(max_workers=config.MAX_WORKERS)

class OptimizedIntelligentAgent:
    def __init__(self):
        self.conversation_history = []
        self._schema_cache = None
        self._schema_cache_time = None
    
    def call_llm(self, messages: List[Dict], stream: bool = False, **kwargs):
        """调用大型语言模型"""
        try:
            params = {
                "model": config.AI_MODEL,
                "messages": messages,
                "temperature": config.AI_TEMPERATURE,
                "max_tokens": config.AI_MAX_TOKENS,
                "stream": stream
            }
            params.update(kwargs)
            
            return client.chat.completions.create(**params)
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            raise

#     def get_schema_cached(self) -> Dict:
#         """获取带有内存缓存优化的缓存Schema"""
#         if (self._schema_cache and self._schema_cache_time and 
#             (datetime.now() - self._schema_cache_time).seconds < 300):
#             return self._schema_cache
            
#         cache_key = "neo4j_schema"
#         cached_schema = cache_manager.get(cache_key)
#         if cached_schema:
#             schema = json.loads(cached_schema)
#             self._schema_cache = schema
#             self._schema_cache_time = datetime.now()
#             return schema
        
#         try:
#             logger.info("正在从数据库获取Schema")
#             with driver.session() as session:
#                 node_query = """
#                 CALL db.labels() YIELD label
# CALL {
#   WITH label
#   MATCH (n) 
#   WHERE ANY(l IN labels(n) WHERE l = label)
#   WITH n
#   RETURN n
# }
# WITH label, n
# UNWIND keys(n) AS propertyKey
# WITH label, propertyKey, 
#      apoc.meta.cypher.type(n[propertyKey]) AS dataType,
#      n[propertyKey] AS exampleValue
# WHERE exampleValue IS NOT NULL
# RETURN label AS nodeLabel,
#        propertyKey AS propertyName,
#        dataType AS dataType,
#        COLLECT(DISTINCT exampleValue)[..3] AS exampleValues,
#        COUNT(*) AS valueCount
# ORDER BY nodeLabel, propertyName
#                 """
#                 rel_query = """
#                 CALL db.relationshipTypes() YIELD relationshipType
# CALL {
#   WITH relationshipType
#   MATCH ()-[r]-()
#   WHERE type(r) = relationshipType
#   WITH r
#   RETURN r
# }
# WITH relationshipType, r
# UNWIND keys(r) AS propertyKey
# WITH relationshipType, propertyKey, 
#      apoc.meta.cypher.type(r[propertyKey]) AS dataType,
#      r[propertyKey] AS exampleValue
# WHERE exampleValue IS NOT NULL
# RETURN relationshipType AS relationshipType,
#        propertyKey AS propertyName,
#        dataType AS dataType,
#        COLLECT(DISTINCT exampleValue)[..3] AS exampleValues,
#        COUNT(*) AS valueCount
# ORDER BY relationshipType, propertyName
#                 """
#                 try:
#                     node_result = list(session.run(node_query))
#                     rel_result = list(session.run(rel_query))
#                 except:
#                     simple_node_query = "CALL db.labels() YIELD label RETURN label, [] as all_keys"
#                     simple_rel_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType, [] as all_keys"
#                     node_result = list(session.run(simple_node_query))
#                     rel_result = list(session.run(simple_rel_query))
                
#                 schema = {
#                     "nodes": {record["nodeLabel"]: record for record in node_result},
#                     "relationships": {record["relationshipType"]: record for record in rel_result}
#                 }
                
#                 cache_manager.set(cache_key, json.dumps(schema, ensure_ascii=False), config.SCHEMA_CACHE_TTL)
#                 self._schema_cache = schema
#                 self._schema_cache_time = datetime.now()
                
#                 return schema
#         except Exception as e:
#             logger.error(f"获取Schema失败: {e}")
#             raise

    def get_schema_cached(self) -> Dict:
        """获取带有内存缓存优化的缓存Schema"""
        if (self._schema_cache and self._schema_cache_time and 
            (datetime.now() - self._schema_cache_time).seconds < 300):
            return self._schema_cache
            
        cache_key = "neo4j_schema"
        cached_schema = cache_manager.get(cache_key)
        if cached_schema:
            schema = json.loads(cached_schema)
            self._schema_cache = schema
            self._schema_cache_time = datetime.now()
            return schema
        
        try:
            logger.info("正在从数据库获取Schema")
            with driver.session() as session:
                node_query = """
                CALL db.labels() YIELD label
    CALL {
    WITH label
    MATCH (n) 
    WHERE ANY(l IN labels(n) WHERE l = label)
    WITH n
    RETURN n
    }
    WITH label, n
    UNWIND keys(n) AS propertyKey
    WITH label, propertyKey, 
        apoc.meta.cypher.type(n[propertyKey]) AS dataType,
        n[propertyKey] AS exampleValue
    WHERE exampleValue IS NOT NULL
    RETURN label AS nodeLabel,
        propertyKey AS propertyName,
        dataType AS dataType,
        COLLECT(DISTINCT exampleValue)[..3] AS exampleValues,
        COUNT(*) AS valueCount
    ORDER BY nodeLabel, propertyName
                """
                rel_query = """
                CALL db.relationshipTypes() YIELD relationshipType
    CALL {
    WITH relationshipType
    MATCH ()-[r]-()
    WHERE type(r) = relationshipType
    WITH r
    RETURN r
    }
    WITH relationshipType, r
    UNWIND keys(r) AS propertyKey
    WITH relationshipType, propertyKey, 
        apoc.meta.cypher.type(r[propertyKey]) AS dataType,
        r[propertyKey] AS exampleValue
    WHERE exampleValue IS NOT NULL
    RETURN relationshipType AS relationshipType,
        propertyKey AS propertyName,
        dataType AS dataType,
        COLLECT(DISTINCT exampleValue)[..3] AS exampleValues,
        COUNT(*) AS valueCount
    ORDER BY relationshipType, propertyName
                """
                try:
                    node_result = list(session.run(node_query))
                    rel_result = list(session.run(rel_query))
                except Exception as query_error:
                    logger.warning(f"详细Schema查询失败，使用简化查询: {query_error}")
                    simple_node_query = "CALL db.labels() YIELD label RETURN label, [] as all_keys"
                    simple_rel_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType, [] as all_keys"
                    node_result = list(session.run(simple_node_query))
                    rel_result = list(session.run(simple_rel_query))
                
                # 自定义JSON序列化器处理Neo4j特殊类型
                def neo4j_json_serializer(obj):
                    """处理Neo4j特殊数据类型的JSON序列化"""
                    if hasattr(obj, 'isoformat'):
                        # 处理DateTime、Date、Time等时间类型
                        return obj.isoformat()
                    elif isinstance(obj, (bytes, bytearray)):
                        # 处理二进制数据
                        return obj.hex()
                    elif hasattr(obj, '__str__'):
                        # 处理其他Neo4j特殊类型
                        return str(obj)
                    else:
                        # 默认处理，如果还是无法序列化会抛出异常
                        return obj
                
                # 修复：正确聚合节点属性，并处理特殊数据类型
                nodes_schema = {}
                for record in node_result:
                    node_label = record["nodeLabel"]
                    if node_label not in nodes_schema:
                        nodes_schema[node_label] = {
                            "nodeLabel": node_label,
                            "properties": []
                        }
                    
                    # 处理exampleValues中的特殊数据类型
                    example_values = record["exampleValues"]
                    serialized_example_values = []
                    for value in example_values:
                        try:
                            # 尝试序列化每个值
                            serialized_value = neo4j_json_serializer(value)
                            serialized_example_values.append(serialized_value)
                        except Exception as e:
                            logger.warning(f"无法序列化示例值 {value}: {e}")
                            serialized_example_values.append(str(value))
                    
                    # 添加属性到列表中
                    property_info = {
                        "propertyName": record["propertyName"],
                        "dataType": record["dataType"],
                        "exampleValues": serialized_example_values,
                        "valueCount": int(record["valueCount"])  # 确保数值类型可序列化
                    }
                    nodes_schema[node_label]["properties"].append(property_info)
                
                # 修复：正确聚合关系属性，并处理特殊数据类型
                relationships_schema = {}
                for record in rel_result:
                    rel_type = record["relationshipType"]
                    if rel_type not in relationships_schema:
                        relationships_schema[rel_type] = {
                            "relationshipType": rel_type,
                            "properties": []
                        }
                    
                    # 处理exampleValues中的特殊数据类型
                    example_values = record["exampleValues"]
                    serialized_example_values = []
                    for value in example_values:
                        try:
                            # 尝试序列化每个值
                            serialized_value = neo4j_json_serializer(value)
                            serialized_example_values.append(serialized_value)
                        except Exception as e:
                            logger.warning(f"无法序列化示例值 {value}: {e}")
                            serialized_example_values.append(str(value))
                    
                    # 添加属性到列表中
                    property_info = {
                        "propertyName": record["propertyName"],
                        "dataType": record["dataType"],
                        "exampleValues": serialized_example_values,
                        "valueCount": int(record["valueCount"])  # 确保数值类型可序列化
                    }
                    relationships_schema[rel_type]["properties"].append(property_info)
                
                schema = {
                    "nodes": nodes_schema,
                    "relationships": relationships_schema
                }
                
                # 记录调试信息
                total_node_properties = sum(len(node_data["properties"]) for node_data in nodes_schema.values())
                total_rel_properties = sum(len(rel_data["properties"]) for rel_data in relationships_schema.values())
                logger.info(f"Schema获取完成: {len(nodes_schema)}种节点类型, {total_node_properties}个节点属性, "
                        f"{len(relationships_schema)}种关系类型, {total_rel_properties}个关系属性")
                
                # 使用自定义序列化器缓存Schema
                try:
                    serialized_schema = json.dumps(schema, default=neo4j_json_serializer, ensure_ascii=False)
                    cache_manager.set(cache_key, serialized_schema, config.SCHEMA_CACHE_TTL)
                    self._schema_cache = schema
                    self._schema_cache_time = datetime.now()
                except Exception as serialization_error:
                    logger.error(f"Schema序列化失败: {serialization_error}")
                    # 即使序列化失败也返回schema，但不缓存
                    self._schema_cache = schema
                    self._schema_cache_time = datetime.now()
                
                return schema
        except Exception as e:
            logger.error(f"获取Schema失败: {e}")
            raise

    def extract_entities_cached(self, question: str) -> Dict:
        """缓存的实体提取"""
        cache_key = generate_cache_key("entities", question)
        cached_entities = cache_manager.get(cache_key)
        if cached_entities:
            logger.info("正在从缓存中获取实体提取结果")
            return json.loads(cached_entities)
        
        try:
            prompt = f"""你是一位专业的命名实体识别专家。请从先理解问题的主要意图，并提取所有相关的实体。
            
            问题: {question}

            要包含的实体类型:
            1. 人物姓名（例如：任质斌、李先念、陈少敏等）
            2. 事件名称（例如：某某战役、某某战争、某某战斗、某某会议、某某运动等）
            3. 地点名称（例如：大悟山、浅水、中原、鄂豫、湖北等）
            4. 组织机构（例如：新四军第五师、中原军区等）
            5. 时间时期（例如：1941年、1941年1月、1941-01-01、早期革命、土地革命、抗日战争、解放战争等）
            6. 职务职位（例如：师长、政委、指挥员等）

            要求:
            - 只提取与问题直接相关的实体。
            - 以JSON格式返回，包含上述6个类别。
            - 每个类别都应是字符串列表。
            - 如果某个类别没有实体，返回一个空列表。
            - 只提取文本中提及的实体，避免引入未提及的内容。

            请以JSON格式返回结果:"""

            response = self.call_llm([
                {"role": "system", "content": "你是一位专业的命名实体识别专家，专注于革命历史领域。"},
                {"role": "user", "content": prompt}
            ])
            
            result_text = response.choices[0].message.content.strip()
            
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                entities = json.loads(json_match.group())
            else:
                entities = json.loads(result_text)
            
            standardized_entities = {
                "persons": entities.get("人物姓名", entities.get("persons", [])),
                "events": entities.get("事件名称", entities.get("events", [])),
                "locations": entities.get("地点名称", entities.get("locations", [])),
                "organizations": entities.get("组织机构", entities.get("organizations", [])),
                "time_periods": entities.get("时间时期", entities.get("time_periods", [])),
                "positions": entities.get("职务职位", entities.get("positions", []))
            }
            
            cache_manager.set(cache_key, json.dumps(standardized_entities, ensure_ascii=False), config.ENTITY_CACHE_TTL)
            
            return standardized_entities
            
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            raise

    def generate_cypher_queries(self, question: str, schema: dict) -> List[Dict]:
        # def generate_cypher_queries(self, question: str, entities: dict, schema: dict) -> List[Dict]:
        """生成优化的Cypher查询"""
        # cache_key = generate_cache_key("cypher_gen", question, entities)
        cache_key = generate_cache_key("cypher_gen", question)
        cached_queries = cache_manager.get(cache_key)
        if cached_queries:
            logger.info("正在从缓存中获取Cypher查询")
            return json.loads(cached_queries)
        
        try:
            # Ensure 'name' is properly defined before using it in the Cypher query
            if 'name' not in locals():
                name = "默认值"  # Replace "默认值" with an appropriate default value or handle it dynamically

            # entities_str = json.dumps(entities, ensure_ascii=False, indent=2)
                        # - **提取的实体**: {entities_str}
            schema_str = json.dumps(schema, ensure_ascii=False, indent=2)

            prompt = f'''
            # 角色
            你是一位卓越的Neo4j Cypher查询生成专家，专注于将自然语言问题精准转换为高效的图数据库查询。你的核心使命是：基于用户的问题意图，严格按照知识图谱Schema结构，生成返回可视化图结构的最优Cypher查询。
            请特别注意：
            无论问题的具体内容或查询目的为何，你生成的Cypher查询必须返回图格式结果！必须使用 RETURN n, r, m 或等效的图结构返回语句！
            确保查询可直接执行，语法正确且性能优化！
            你将以专业、准确的方式完成自然语言到Cypher查询的"翻译"工作，始终确保结果的可视化呈现能力。
            ---

            ## 1. 知识图谱schema
            - {schema_str}

            ## 2. 用户输入
            - **用户问题**: {question}

            ## 3. 生成Cypher查询的核心要求
            1.  **目标**: 严格根据知识图谱模式层schema信息，生成1个与用户问题意图最匹配的Cypher查询。
            2.  **实体类别**:
                - 人物：根据属性person_category来划分，目前主要有三类："新四军五师前辈"、"百岁诞辰前辈"、"九公山纪念馆"，person_category有两类数据格式一个是String 一个是List of String，一个人可以同时包含多个标签。当人物没有任何标签的时候，即这个人不属于新四军五师的时候，person_category属性为NULL。
                - 事件：根据属性category来划分，目前主要有三类："战役战斗"、"参加的战役战斗"、"教育和工作经历"。
                - 事件仅仅划分了上述三个类别，没有更多的信息。
            3.  **关系查询**:
                - 默认使用无方向查询 `(n)-[r]-(m)` 来探索两个节点间的所有关系，除非问题明确指定了方向，但是要注意查询的关系的去重，即两条相同的边不能同时被查询出。
                - 亲友关系即FAMILY_WITH中对关系的描述relationship_type仅包含："父辈","子辈","孙辈","祖辈","同辈"
                - 查询间接关系，优先查询两跳即 `(n)-[*1..2]-(x)`
            4.  **时间处理逻辑 **:
                - 时间有三类表示方式，主要存在于边的属性中：`time_value`（精确时间点）、`time_period`（历史时期）、`time_start` 和 `time_end`（时间范围）。
                - **精确时间点**: 如果问题涉及具体年份或日期（如“1949年发生了什么”），优先使用 `time_value` 属性进行精确匹配。`WHERE r.time_value = '1949'`。
                - **历史时期**: 如果问题涉及一个时期（如“抗日战争时期”），使用 `time_period` 属性进行模糊匹配。`WHERE r.time_period CONTAINS '抗日'`。
                - **时间范围**: 如果问题涉及一个时间段（如“1937年到1945年之间”），结合使用 `time_start` 和 `time_end` 属性。`WHERE r.time_start >= '1937' AND r.time_end <= '1945'`。
            5.  **返回格式**:
                - 所有问题的查询必须返回可视化的图格式，即 `RETURN n, r, m`或者`RETURN n`。
                - 必须包含`RETURN`子句。
                - 查询语句只返回不重复的关系和节点。。
            6.  **性能**: 请注意查询结果的去重；避免重复路径返回。并且在查询末尾添加 LIMIT 500 以限制返回结果数量，避免过载。
            

            ## 4. 示例
            ### 示例 1:
            用户问题: "查询任质斌的战友"
            预期Cypher查询: MATCH (p:Person {{name:"任质斌"}})-[r:COMRADE|COMRADE_WITH|INFERRED_COMRADE_WITH]-(c:Person) RETURN p, r, c LIMIT 300
            
            ### 示例 2:
            用户问题: "解放战争时期，任质斌参与了哪些战斗？"
            预期Cypher查询:  MATCH (p:Person {{name:"任质斌"}})-[r:PARTICIPATED_IN|INFERRED_PARTICIPATED_IN]->(e:Event) WHERE r.time_period CONTAINS '解放战争' AND e.category CONTAINS '战役战斗' RETURN p, r, e LIMIT 300
           
            ### 示例 3: 
            用户问题: "目前中总共多少位属于新四军五师？"
            预期Cypher查询: MATCH (n:Person) WHERE "新四军五师前辈" IN n.person_category OR n.person_category CONTAINS "新四军五师前辈" RETURN n

            ### 示例 4: 
            用户问题: "参与侏儒山战役的人有哪些？"
            预期Cypher查询:  MATCH (p:Person)-[r:PARTICIPATED_IN|INFERRED_PARTICIPATED_IN]->(e:Event) WHERE e.name = '侏儒山战役' RETURN p, r, e LIMIT 500
            
            ### 示例 5: 
            用户问题: "任质斌前辈参加了哪些重要战役战斗？"
            预期Cypher查询:  MATCH (p:Person)-[r:PARTICIPATED_IN|INFERRED_PARTICIPATED_IN]->(e:Event) WHERE e.category CONTAINS '战役战斗' RETURN p, r, e LIMIT 500
                     
            ### 示例 6: 
            用户问题: "刘少卿在抗日和解放战争时期按时间排序参与的组织机构和担任职务？？"
            预期Cypher查询:  MATCH (p:Person)-[r:PARTICIPATED_IN|INFERRED_PARTICIPATED_IN]->(e:Event) WHERE n.name='刘少卿' (r.time_period CONTAINS '抗日' OR r.time_period CONTAINS '解放战争') RETURN p, r, e ORDER BY r.time_value LIMIT 500
            
            ### 示例 7: 
            用户问题: "哪些家庭收录了三代？哪些家庭收录了两代？主要是哪些关系？？？"
            预期Cypher查询:  MATCH (n1)-[r:FAMILY_WITH]->(n2) RETURN r,n1,n2
            
                 
            ## 5. 输出格式要求
            请特别注意：
            无论问题的具体内容或查询目的为何，你生成的Cypher查询必须返回图格式结果！必须使用 RETURN n, r, m 或等效的图结构返回语句！
            请严格按照以下JSON格式返回，不要添加任何额外的解释或说明文字。
            {{
            "queries": [
                {{"purpose": "", "cypher": "MATCH ..."}}
            ]
            }}
            '''
            
            
            response = self.call_llm([
                {"role": "system", "content": "你是一位专业的Neo4j Cypher查询专家，专注于根据问题生成查询语句。"},
                {"role": "user", "content": prompt}
            ])
            
            result_text = response.choices[0].message.content.strip()
            
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                queries_data = json.loads(json_match.group())
                
                if 'queries' in queries_data:
                    validated_queries = []
                    for query_info in queries_data['queries']:
                        cypher = query_info.get('cypher', '').strip()
                        
                        if cypher:
                            cypher = self.validate_and_fix_cypher(cypher)
                            if cypher:
                                validated_queries.append({
                                    'purpose': query_info.get('purpose', '未知目的'),
                                    'cypher': cypher
                                })
                    
                    queries_data['queries'] = validated_queries
                
                cache_manager.set(cache_key, json.dumps(queries_data, ensure_ascii=False), config.QUERY_CACHE_TTL)
                
                return queries_data['queries']
            else:
                raise ValueError("无法解析查询生成结果")
                
        except Exception as e:
            logger.error(f"Cypher查询生成失败: {e}")
            raise

    def validate_and_fix_cypher(self, cypher: str) -> str:
        """验证并修复Cypher查询"""
        try:
            cypher = re.sub(r'\s+', ' ', cypher).strip()
            
            if re.search(r'\bRETURN\s*$', cypher, re.IGNORECASE):
                if 'path' in cypher.lower():
                    cypher += ' path LIMIT 500'
                elif re.search(r'\b(p|person)\b.*\b(e|event)\b', cypher, re.IGNORECASE):
                    cypher += ' p, r, e LIMIT 500'
                elif re.search(r'\b(p|person)\b', cypher, re.IGNORECASE):
                    cypher += ' p LIMIT 500'
                else:
                    cypher += ' * LIMIT 500'
            
            elif not re.search(r'\bRETURN\b', cypher, re.IGNORECASE):
                if 'path' in cypher.lower():
                    cypher += ' RETURN path LIMIT 500'
                else:
                    cypher += ' RETURN * LIMIT 500'
            
            if not re.search(r'\bLIMIT\b', cypher, re.IGNORECASE):
                cypher += ' LIMIT 500'
            
            return cypher
            
        except Exception as e:
            logger.warning(f"Cypher修复失败: {e}")
            return ""

    def execute_cypher_query(self, cypher_query: str, max_retries: int = 3) -> Dict:
        """执行一个Cypher查询,带有重试机制"""
        global driver
        import time
        
        for attempt in range(max_retries):
            try:
                logger.info(f"正在执行Cypher查询 (尝试 {attempt + 1}/{max_retries}): {cypher_query}")
                
                # 使用超时设置创建会话
                with driver.session(default_access_mode='READ') as session:
                    # 设置事务超时
                    result = session.run(cypher_query)
                    keys = result.keys()
                    records_list = list(result)
                    
                    is_graph = any(isinstance(value, (Node, Relationship, Path)) 
                                   for record in records_list for value in record.values())
                    
                    if is_graph:
                        data = process_graph_result(records_list)
                        result_type = "graph"
                    else:
                        data = process_table_result(keys, records_list)
                        result_type = "table"
                    
                    logger.info(f"Cypher查询执行成功，返回 {len(records_list)} 条记录")
                    return {"success": True, "type": result_type, "data": data}
                    
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Cypher执行尝试 {attempt + 1} 失败: {error_msg}")
                
                # 如果是连接错误，尝试重新初始化驱动
                if "ConnectionResetError" in error_msg or "Unable to retrieve routing" in error_msg:
                    if attempt < max_retries - 1:
                        logger.info("检测到连接问题，等待后重试...")
                        time.sleep(2 ** attempt)  # 指数退避: 1秒, 2秒, 4秒
                        
                        # 尝试重新初始化连接
                        try:
                            from neo4j_driver import initialize_neo4j_driver
                            driver = initialize_neo4j_driver()
                            logger.info("Neo4j驱动已重新初始化")
                        except Exception as reinit_error:
                            logger.error(f"重新初始化驱动失败: {reinit_error}")
                        
                        continue
                    else:
                        logger.error(f"Cypher执行在 {max_retries} 次尝试后仍然失败: {error_msg}")
                        return {
                            "success": False, 
                            "error": f"数据库连接错误，请稍后重试。详情: {error_msg}"
                        }
                else:
                    # 非连接错误，直接返回
                    logger.error(f"Cypher执行失败: {error_msg}")
                    return {"success": False, "error": error_msg}
        
        return {
            "success": False, 
            "error": f"查询在 {max_retries} 次尝试后失败"
        }

    def execute_single_query(self, queries: List[Dict]) -> List[Dict]:
        """执行单个查询，返回结果列表，适配原有的格式"""
        # 检查传入的是否为列表，如果不是，则将其转换为一个单元素列表
        if isinstance(queries, dict):
            queries = queries['queries']
            
        if not queries:
            return []
        
        query_info = queries[0]
        result = self.execute_cypher_query(query_info['cypher'])
        
        if result['success']:
            return [{
                "purpose": query_info['purpose'],
                "data": result,
                "query": query_info['cypher']
            }]
        else:
            return []

    # def format_all_context_data(self, context_data: List[Dict]) -> str:
    #     """优化的上下文格式化"""
    #     if not context_data:
    #         return "未找到相关信息。"
            
    #     formatted_sections = []
        
    #     for item in context_data:
    #         purpose = item.get("purpose", "未知目的")
    #         data = item.get("data", {})
            
    #         formatted_sections.append(f"======{purpose}======")
            
    #         if data.get("type") == "table":
    #             rows = data.get("data", {}).get("rows", [])
    #             if rows:
    #                 for i,row in enumerate(rows):
    #                     row_text = ", ".join([f"{k}: {v}" for k, v in row.items() if v is not None])
    #                     formatted_sections.append(f"[{i+1}]  - {row_text}")
            
    #         elif data.get("type") == "graph":
    #             nodes = data.get("data", {}).get("nodes", [])
    #             links = data.get("data", {}).get("links", [])
                
    #             person_nodes = [n for n in nodes if n.get("category") == "Person"]
    #             event_nodes = [n for n in nodes if n.get("category") == "Event"]
                
    #             if person_nodes:
    #                 formatted_sections.append("【人物信息】")
    #                 for i,node in enumerate(person_nodes):
    #                     name = node.get("name", "未知")
    #                     props = node.get("properties", {})
    #                     info_parts = [f"姓名：{name}"]
                        
    #                     if props.get("birth_place"): info_parts.append(f"出生地：{props['birth_place']}")
    #                     if props.get("new_fourth_army_fifth_division"): info_parts.append(f"五师前辈：{props['new_fourth_army_fifth_division']}")
    #                     if props.get("aliases"): info_parts.append(f"别名：{props['aliases']}")
    #                     if props.get("birth_date"): info_parts.append(f"出生日期：{props['birth_date']}")
    #                     if props.get("death_date"): info_parts.append(f"逝世日期：{props['death_date']}")
                                             
    #                     formatted_sections.append(f"[{i+1}] - {', '.join(info_parts)}")
                
    #             if event_nodes:
    #                 formatted_sections.append("【事件信息】")
    #                 for i,node in enumerate(event_nodes):
    #                     name = node.get("name", "未知")
    #                     props = node.get("properties", {})
    #                     category = props.get("category", "未知类型")
    #                     formatted_sections.append(f"[{i+1}]--------------------{name} ({category})--------------------")
    #                     if props.get('new_fourth_army_battle'): 
    #                         formatted_sections.append(f"五师战役: {props.get('new_fourth_army_battle')}")
    #                     if props.get('background'):
    #                         formatted_sections.append(f"背景：{props.get('background')})")
    #                     if props.get('belligerents'):
    #                         formatted_sections.append(f"交战方：{props.get('belligerents')}")
    #                     if props.get('key_figures'):
    #                         formatted_sections.append(f"人物：{props.get('key_figures')}")
    #                     if props.get('location_details'):
    #                         formatted_sections.append(f"地点：{props.get('location_details')}")
    #                     if props.get('time_details'):
    #                         formatted_sections.append(f"时间：{props.get('time_details')}")
    #                     if props.get('result'):
    #                         formatted_sections.append(f"结果：{props.get('result')}")
    #                     if props.get('process_and_tactics'):
    #                         formatted_sections.append(f"战术：{props.get('process_and_tactics')}")
    #                     if props.get('impact'):
    #                         formatted_sections.append(f"影响：{props.get('impact')}")
                
    #             if links:
    #                 formatted_sections.append("【重要关系】")
    #                 for i,link in enumerate(links):
    #                     rel_name = link.get("name", "未知关系")
    #                     rel_props = link.get("properties", {})
    #                     source_node = next((n for n in nodes if n["id"] == link.get("source")), None)
    #                     target_node = next((n for n in nodes if n["id"] == link.get("target")), None)
                        
    #                     if source_node and target_node:
    #                         formatted_sections.append(f"[{i+1}]-------------------- {source_node['name']} --{rel_name}--> {target_node['name']} ---------- " )
    #                         if rel_props.get('time_value'):
    #                             formatted_sections.append(f"({rel_props.get('time_value')})")
    #                         elif rel_props.get('time_period'):
    #                             formatted_sections.append(f"({rel_props.get('time_period')})")
    #                         elif rel_props.get('time_end','time_start'):
    #                             formatted_sections.append(f"开始时间：({rel_props.get('time_start')})")
    #                             formatted_sections.append(f"结束时间：({rel_props.get('time_end')})")
    #                         if rel_props.get('location'):
    #                             formatted_sections.append(f"地点：{rel_props.get('location')}")
    #                         if rel_props.get('organization'):
    #                             formatted_sections.append(f"组织：{rel_props.get('organization')}")
    #                         if rel_props.get('relationship'):
    #                             formatted_sections.append(f"关系：{rel_props.get('relationship')}")
    #                         if rel_props.get('relationship_type'):
    #                             formatted_sections.append(f"关系：{rel_props.get('relationship_type')}")
    #                         if rel_props.get('relationship_verb'):
    #                             formatted_sections.append(f"关系：{rel_props.get('relationship_verb')}")
    #                         if rel_props.get('position'):
    #                             formatted_sections.append(f"职位：{rel_props.get('position')}")
            
    #         formatted_sections.append("")
    #     # 格式化上下文结果
    #     return "\n".join(formatted_sections)

    def format_all_context_data(self, context_data: List[Dict]) -> str:
        """优化的上下文格式化 - 支持完整模式层"""
        if not context_data:
            return "未找到相关信息。"
            
        formatted_sections = []
        
        for item in context_data:
            purpose = item.get("purpose", "未知目的")
            data = item.get("data", {})
            
            formatted_sections.append(f"======{purpose}======")
            
            if data.get("type") == "table":
                rows = data.get("data", {}).get("rows", [])
                if rows:
                    for i, row in enumerate(rows):
                        row_text = ", ".join([f"{k}: {v}" for k, v in row.items() if v is not None])
                        formatted_sections.append(f"[{i+1}] - {row_text}")
            
            elif data.get("type") == "graph":
                nodes = data.get("data", {}).get("nodes", [])
                links = data.get("data", {}).get("links", [])
                
                # 分类节点
                person_nodes = [n for n in nodes if n.get("category") == "Person"]
                event_nodes = [n for n in nodes if n.get("category") == "Event"]
                
                # 格式化人物节点
                if person_nodes:
                    formatted_sections.append("【人物信息】")
                    for i, node in enumerate(person_nodes):
                        name = node.get("name", "未知")
                        props = node.get("properties", {})
                        info_parts = [f"姓名：{name}"]
                        
                        # 基础信息
                        if props.get("gender"): 
                            info_parts.append(f"性别：{props['gender']}")
                        if props.get("aliases"): 
                            # 别名可能是 '[]' 字符串或列表
                            aliases = props['aliases']
                            if isinstance(aliases, str) and aliases != '[]':
                                # 清理别名字符串中的方括号与引号，避免在格式化时出现语法问题
                                cleaned_aliases = aliases.strip('[]').replace("'", "")
                                info_parts.append("别名：" + cleaned_aliases)
                            elif isinstance(aliases, list) and aliases:
                                info_parts.append(f"别名：{', '.join(aliases)}")
                        if props.get("birth_date"): 
                            info_parts.append(f"出生日期：{props['birth_date']}")
                        if props.get("death_date"): 
                            info_parts.append(f"逝世日期：{props['death_date']}")
                        if props.get("birth_place"): 
                            info_parts.append(f"出生地：{props['birth_place']}")

                        # 革命经历
                        if props.get("join_revolution_date"): 
                            info_parts.append(f"参加革命时间：{props['join_revolution_date']}")
                        if props.get("join_party_date"): 
                            info_parts.append(f"入党时间：{props['join_party_date']}")
                        
                        # 分类标签
                        if props.get("person_category"):
                            category = props['person_category']
                            if isinstance(category, list):
                                info_parts.append(f"类别：{', '.join(category)}")
                            else:
                                info_parts.append(f"类别：{category}")
                        
                        # 家庭关系
                        if props.get("is_family_member"): 
                            info_parts.append(f"是否家属：是")
                        if props.get("generation"): 
                            info_parts.append(f"辈分：{props['generation']}")
                                            
                        formatted_sections.append(f"[{i+1}] - {', '.join(info_parts)}")
                
                # 格式化事件节点
                if event_nodes:
                    formatted_sections.append("【事件信息】")
                    for i, node in enumerate(event_nodes):
                        name = node.get("name", "未知")
                        props = node.get("properties", {})
                        category = props.get("category", "未知类型")
                        
                        formatted_sections.append(f"[{i+1}]- {name} ({category}) ")
                        
                        # 战役战斗相关信息
                        if props.get('battle_time'): 
                            formatted_sections.append(f"  战役时间：{props['battle_time']}")
                        if props.get('battle_area'): 
                            formatted_sections.append(f"  战役地区：{props['battle_area']}")
                        if props.get('our_forces'): 
                            formatted_sections.append(f"  我方兵力：{props['our_forces']}")
                        if props.get('enemy_forces'): 
                            formatted_sections.append(f"  敌方兵力：{props['enemy_forces']}")
                        if props.get('battle_process'): 
                            process = props['battle_process']
                            # 截断过长的战斗过程
                            if len(process) > 500:
                                process = process[:500] + "..."
                            formatted_sections.append(f"  战斗过程：{process}")
                        if props.get('battle_result'): 
                            formatted_sections.append(f"  战斗结果：{props['battle_result']}")
                
                # 格式化关系
                if links:
                    formatted_sections.append("【关系信息】")
                    for i, link in enumerate(links):
                        rel_name = link.get("name", "未知关系")
                        rel_props = link.get("properties", {})
                        source_node = next((n for n in nodes if n["id"] == link.get("source")), None)
                        target_node = next((n for n in nodes if n["id"] == link.get("target")), None)
                        
                        if source_node and target_node:
                            formatted_sections.append(
                                f"[{i+1}] {source_node['name']} --{rel_name}--> {target_node['name']}"
                            )
                            
                            # 时间信息
                            if rel_props.get('time_value'):
                                formatted_sections.append(f"  时间：{rel_props['time_value']}")
                            if rel_props.get('time_period'):
                                formatted_sections.append(f"  时期：{rel_props['time_period']}")
                            if rel_props.get('time_start'):
                                formatted_sections.append(f"  开始时间：{rel_props['time_start']}")
                            if rel_props.get('time_end'):
                                formatted_sections.append(f"  结束时间：{rel_props['time_end']}")
                            
                            # 地点信息
                            if rel_props.get('location'):
                                formatted_sections.append(f"  地点：{rel_props['location']}")
                            
                            # 组织/机构
                            if rel_props.get('institution'):
                                formatted_sections.append(f"  组织/机构：{rel_props['institution']}")
                            
                            # 职位
                            if rel_props.get('position'):
                                formatted_sections.append(f"  职位：{rel_props['position']}")
                            
                            # 关系详情
                            rel_type = rel_props.get('relationship_type') or rel_props.get('relationship') or rel_props.get('relationship_to_event')
                            if rel_type:
                                formatted_sections.append(f"  关系类型：{rel_type}")
                            if rel_props.get('relationship_description'):
                                formatted_sections.append(f"  关系描述：{rel_props['relationship_description']}")

                            # 事件关联
                            if rel_props.get('event_name'):
                                formatted_sections.append(f"  关联事件：{rel_props['event_name']}")
                            if rel_props.get('battle_event_name'):
                                formatted_sections.append(f"  关联战役：{rel_props['battle_event_name']}")

                            # 推理信息
                            if rel_props.get('inference_reasoning'):
                                formatted_sections.append(f"  推理依据：{rel_props['inference_reasoning']}")
                            if rel_props.get('inference_confidence'):
                                formatted_sections.append(f"  置信度：{rel_props['inference_confidence']}")
                            
                            # 原始文本
                            if rel_props.get('source_text'):
                                text = rel_props['source_text']
                                if len(text) > 100:
                                    text = text[:100] + "..."
                                formatted_sections.append(f'''  原始文本："{text}"''')
            
            formatted_sections.append("")
        
        # 格式化上下文结果
        return "\n".join(formatted_sections)


    def unified_nl2cypher_and_rag(self, question: str, mode: str = "rag") -> Generator[Dict, None, None]:
        """统一的NL2Cypher和RAG处理流程"""
        logger.info(f"开始统一处理: {question}, 模式: {mode}")
        
        try:
            if mode == "rag":
                yield {"type": "step", "step": "处理", "message": "正在提取实体和获取Schema..."}
            
            schema_future = executor.submit(self.get_schema_cached)
            # entities_future = executor.submit(self.extract_entities_cached, question)
            
            schema = schema_future.result()
            # entities = entities_future.result()
            
            # if mode == "rag":
                # yield {"type": "entities", "data": entities}
            
            if mode == "rag":
                yield {"type": "step", "step": "生成查询策略", "message": "正在生成优化的检索查询..."}
            
            # queries = self.generate_cypher_queries(question, entities, schema)
            queries = self.generate_cypher_queries(question, schema)
            
            if isinstance(queries, dict) and 'queries' in queries:
                queries_list = queries['queries']
            else:
                queries_list = queries
            
            if mode == "rag":
                yield {"type": "retrieval_plan", "data": {"queries": queries}}
            
            if mode == "rag":
                yield {"type": "step", "step": "执行查询", "message": "正在执行检索查询..."}
            
            # 使用新的单次查询执行方法
            all_context_data = self.execute_single_query(queries)
            
            # if mode == "nl2cypher":
            #     if queries and all_context_data:
            #         first_query = queries[0]
            #         first_result = all_context_data[0] if all_context_data else None
            #         if first_result and first_result.get('data', {}).get('success'):
            #             return {
            #                 "success": True,
            #                 "question": question,
            #                 "cypher": first_query['cypher'],
            #                 "result": first_result['data'],
            #                 "attempts": 1
            #             }
            #     return {"success": False, "error": "无法生成有效的Cypher查询"}
            if mode == "nl2cypher":
                if queries_list and all_context_data:
                    first_query = queries_list[0]
                    first_result = all_context_data[0] if all_context_data else None
                    if first_result and first_result.get('data', {}).get('success'):
                        # 将 return 语句改为 yield，并添加 'complete' 类型以标识结束
                        yield {
                            "type": "complete",
                            "success": True,
                            "question": question,
                            "cypher": first_query['cypher'],
                            "result": first_result['data'],
                            "attempts": 1
                        }
                        return # 结束生成器
                
                # 将失败的 return 语句也改为 yield
                yield {"type": "error", "success": False, "error": "无法生成有效的Cypher查询"}
                return # 结束生成器
            
            if all_context_data:
                yield {
                    "type": "retrieval_result", 
                    "purpose": all_context_data[0]['purpose'], 
                    "success": True, 
                    "data": all_context_data[0]['data']
                }
            
            yield {"type": "step", "step": "组织上下文", "message": "正在组织所有检索到的信息..."}
            
            formatted_context = self.format_all_context_data(all_context_data)
            yield {"type": "context", "data": formatted_context}
            
            yield {"type": "step", "step": "生成专业回答", "message": "正在基于检索到的信息生成专业的历史回答..."}
            
            final_prompt = f"""你是一名数据分析助手，尤其是擅长新四军五师的历史研究。你的任务是严格根据下方的[查询到的数据]来回答[用户问题]。

            [查询到的数据]
            {formatted_context}

            [用户问题]
            {question}

            [回答规则]
            1. **完全基于数据**: 你的答案必须完全来自[查询到的数据]。不要使用你自己的任何背景知识或数据以外的信息。
            2. **直接引用**: 在可能的情况下，直接从数据中提取信息来构建答案。
            3. **信息未找到**: 如果[查询到的数据]中没有足够的信息来回答[用户问题]，你必须明确声明：“根据查询到的信息，无法回答此问题。”
            4. **简洁明了**: 使用清晰、直接的语言来回答问题。
            5. **良好格式**: 适当地使用Markdown格式来突出重点。

            [重要指导]
            1. **历史准确性**: 严格遵循提供的数据，确保所有事实、时间、地点和关系的准确性。
            2. **内容深度**: 不要只回答表面问题；提供更深层次的分析，例如历史背景、战略意义和历史影响。
            3. **逻辑结构**: 按时间顺序或逻辑顺序组织答案，使内容清晰、结构良好。
            4. **革命精神**: 突出革命先辈的英雄事迹、牺牲精神和历史贡献。
            5. **关系分析**: 分析人物与事件之间的内在联系和相互影响。
            6. **信息完整**：应完整准确的提供出所有信息，不用“等XX战役、等XX人物”来省略。

            请严格遵循上述规则和重要指导来生成你的答案:"""

            final_response = self.call_llm([
                {"role": "system", "content": "你是一位专业的革命历史专家，拥有深厚的历史知识和丰富的研究经验。"},
                {"role": "user", "content": final_prompt}
            ], stream=True)
            
            full_answer = ""
            for chunk in final_response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_answer += content
                    yield {"type": "answer_chunk", "content": content, "full_content": full_answer, "context": formatted_context}
            
            yield {
                "type": "complete", 
                "final_answer": full_answer, 
                "retrieved_context": formatted_context,
                "raw_context_data": all_context_data,
                "context": formatted_context,
            }
            
        except Exception as e:
            logger.error(f"统一处理流程失败: {e}")
            if mode == "rag":
                yield {"type": "error", "error": f"处理过程中发生错误: {str(e)}"}
            else:
                return {"success": False, "error": str(e)}

    def person_roleplay_chat(self, person_name: str, chat_history: List[Dict], user_message: str) -> Generator[Dict, None, None]:
        """人物角色扮演聊天"""
        logger.info(f"开始人物角色扮演聊天: 人物={person_name}, 消息={user_message}")
        
        try:
            # 步骤1: 查询人物相关信息
            yield {"type": "step", "message": f"正在查询{person_name}的相关信息..."}
            
            cypher_query = f'MATCH path = (p:Person {{name: "{person_name}"}})-[*1..2]-(n:Person) UNWIND relationships(path) AS rel WITH DISTINCT rel RETURN startNode(rel) AS source, rel, endNode(rel) AS target'
            
            # cypher_query = f'MATCH path = (n:Person {{name:"{person_name}"}})-[*1..2]->(m) RETURN DISTINCT path LIMIT 500'
            query_result = self.execute_cypher_query(cypher_query)
            
            if not query_result.get('success'):
                yield {"type": "error", "error": f"无法查询到{person_name}的信息"}
                return
            
            # 步骤2: 格式化人物上下文
            yield {"type": "step", "message": "正在整理人物生平信息..."}
            
            context_data = [{
                "purpose": f"{person_name}的生平信息",
                "data": query_result
            }]
            
            formatted_context = self.format_all_context_data(context_data)
            
            # 步骤3: 构建系统提示词
            system_prompt = f"""# 角色设定
你现在要扮演新四军中的革命历史人物：**{person_name}**

## 人物背景信息
{formatted_context}

## 角色扮演要求
1. **第一人称视角**：你就是{person_name}本人，使用"我"来称呼自己。
2. **历史真实性**：严格基于上述背景信息，不要编造任何不存在的经历。
3. **时代语境**：使用符合那个年代的语言风格和表达方式。
4. **情感真实**：展现一个真实的革命者形象，有理想、有情怀、有血有肉。
5. **适度谦逊**：作为革命前辈，展现出应有的谦虚和朴实作风。
6. **回忆口吻**：可以用回忆的方式讲述自己的经历，增强代入感。

## 对话风格
- 请你像一个真正的人一样与用户交流，展现出你的个性和情感，不要每次的回答都像一样的模板。
- 如果用户问及你的生平经历，详细讲述你的革命历程
- 如果用户问及战友或同志，讲述你们之间的战斗情谊
- 如果用户问及战役或事件，分享你的亲身经历和感受
- 如果用户问及你未经历或不知道的事情，诚实地表示"这件事我不太清楚"

## 细节指导
- 有些人物记录了他的后代信息，但是仅仅只记录了后代姓名和他们之间的关系：父辈、子辈、同辈、祖辈、孙辈，请不要编造这些后代的具体信息，尤其是注意性别。
- 请你不要编造任何你不知道的信息。
- 如果该人物已经有逝世日期的记录，请不要编造其逝世之后的任何经历。回答中不要出现他仍然在世、现在的工作等内容，也不要以“我在天堂”等方式表达。请确保角色始终以已逝革命者的身份出现，不要让他以在世者的口吻与用户交流。


请始终记住：你是{person_name}，一位为中国革命事业奋斗终生的革命者。"""

            # 步骤4: 构建对话历史
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加历史对话（最多保留最近10轮）
            recent_history = chat_history[-20:] if len(chat_history) > 20 else chat_history
            for msg in recent_history:
                messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})
            
            # 步骤5: 调用LLM进行流式响应
            yield {"type": "step", "message": f"{person_name}正在回复..."}
            
            response = self.call_llm(messages, stream=True, temperature=0.8, max_tokens=2000)
            
            full_answer = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_answer += content
                    yield {"type": "answer_chunk", "content": content}
            
            yield {
                "type": "complete",
                "full_answer": full_answer,
                "person_name": person_name
            }
            
        except Exception as e:
            logger.error(f"人物角色扮演聊天失败: {e}")
            yield {"type": "error", "error": f"对话过程中发生错误: {str(e)}"}

# 创建代理实例
agent = OptimizedIntelligentAgent()