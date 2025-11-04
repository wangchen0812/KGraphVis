from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging
import json
from datetime import datetime
import traceback

# 导入模块
from config import config
from cache import cache_manager
from neo4j_driver import driver
from agent import OptimizedIntelligentAgent, executor
from utils import generate_cache_key

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask 应用初始化
app = Flask(__name__)
CORS(app)

# 创建代理实例
agent = OptimizedIntelligentAgent()

# --- API 路由 ---
@app.route('/graph', methods=['POST'])
def get_graph_data():
    """原始图数据API"""
    try:
        data = request.get_json()
        cypher_query = data.get('cypher', 'MATCH p=(n)-[r]->(m) RETURN p LIMIT 10')
        logger.info(f"收到 Cypher 查询请求: {cypher_query}")
        
        cache_key = generate_cache_key("graph", cypher_query)
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            logger.info("从缓存返回查询结果")
            return jsonify(json.loads(cached_result))
        
        result = agent.execute_cypher_query(cypher_query)
        if result['success']:
            result_data = {"type": result["type"], "data": result["data"]}
            cache_manager.set(cache_key, json.dumps(result_data, ensure_ascii=False), config.QUERY_CACHE_TTL)
            logger.info("Cypher 查询执行成功，返回数据")
            return jsonify(result_data)
        else:
            return jsonify({"error": result["error"]}), 500

    except Exception as e:
        logger.error("原生 Cypher 查询失败", exc_info=True)
        return jsonify({"error": f"内部服务器错误: {type(e).__name__}"}), 500

@app.route('/ai/nl2cypher', methods=['POST'])
def natural_language_to_cypher():
    """优化的自然语言到Cypher查询转换"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        logger.info(f"收到 NL2Cypher 请求: {question}")
        
        if not question:
            return jsonify({"error": "问题不能为空"}), 400
        
        cache_key = generate_cache_key("nl2cypher", question)
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            logger.info("从缓存返回 NL2Cypher 结果")
            return jsonify(json.loads(cached_result))
        
        result = None
        for response_chunk in agent.unified_nl2cypher_and_rag(question, mode="nl2cypher"):
            if isinstance(response_chunk, dict) and response_chunk.get("success") is not None:
                result = response_chunk
                break
        
        if result is None:
            result = {"success": False, "error": "处理超时或失败"}
        
        if result.get("success"):
            cache_manager.set(cache_key, json.dumps(result, ensure_ascii=False), config.QUERY_CACHE_TTL)
        
        logger.info(f"NL2Cypher 处理完成: success={result.get('success')}")
        return jsonify(result)
        
    except Exception as e:
        logger.error("NL2Cypher 处理失败", exc_info=True)
        return jsonify({"error": f"内部服务器错误: {str(e)}"}), 500

@app.route('/ai/rag', methods=['POST'])
def intelligent_rag_answer():
    """优化的智能 RAG 问答 - 流式响应"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        logger.info(f"收到智能 RAG 请求: {question}")
        
        if not question:
            return jsonify({"error": "问题不能为空"}), 400
        
        def generate_stream():
            """生成流式响应"""
            try:
                yield 'event: start\ndata: {"type": "start"}\n\n'
                
                for response_chunk in agent.unified_nl2cypher_and_rag(question, mode="rag"):
                    event_type = response_chunk.get('type', 'message')
                    data = json.dumps(response_chunk, ensure_ascii=False)
                    message = f'event: {event_type}\ndata: {data}\n\n'
                    yield message
                    
                yield 'event: complete\ndata: {"type": "complete"}\n\n'
                
            except Exception as e:
                logger.error(f"RAG 流式处理失败: {e}")
                error_data = json.dumps({
                    'type': 'error',
                    'error': str(e)
                }, ensure_ascii=False)
                yield f'event: error\ndata: {error_data}\n\n'
        
        logger.info("开始 RAG 流式响应")
        response = Response(
            generate_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache, no-transform',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
                'Content-Type': 'text/event-stream; charset=utf-8',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Cache-Control',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            }
        )
        return response
        
    except Exception as e:
        logger.error("RAG 请求处理失败", exc_info=True)
        return jsonify({"error": f"内部服务器错误: {str(e)}"}), 500

@app.route('/ai/person_chat', methods=['POST'])
def person_chat():
    """人物角色扮演聊天 - 流式响应"""
    try:
        data = request.get_json()
        person_name = data.get('person_name', '')
        chat_history = data.get('chat_history', [])
        user_message = data.get('user_message', '')
        
        logger.info(f"收到人物聊天请求: 人物={person_name}, 消息={user_message}")
        
        if not person_name or not user_message:
            return jsonify({"error": "人物名称和用户消息不能为空"}), 400
        
        def generate_stream():
            """生成流式响应"""
            try:
                yield 'event: start\ndata: {"type": "start"}\n\n'
                
                for response_chunk in agent.person_roleplay_chat(person_name, chat_history, user_message):
                    event_type = response_chunk.get('type', 'message')
                    data = json.dumps(response_chunk, ensure_ascii=False)
                    message = f'event: {event_type}\ndata: {data}\n\n'
                    yield message
                    
                yield 'event: complete\ndata: {"type": "complete"}\n\n'
                
            except Exception as e:
                logger.error(f"人物聊天流式处理失败: {e}")
                error_data = json.dumps({
                    'type': 'error',
                    'error': str(e)
                }, ensure_ascii=False)
                yield f'event: error\ndata: {error_data}\n\n'
        
        logger.info("开始人物聊天流式响应")
        response = Response(
            generate_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache, no-transform',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
                'Content-Type': 'text/event-stream; charset=utf-8',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Cache-Control',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            }
        )
        return response
        
    except Exception as e:
        logger.error("人物聊天请求处理失败", exc_info=True)
        return jsonify({"error": f"内部服务器错误: {str(e)}"}), 500

@app.route('/ai/schema', methods=['GET'])
def get_schema():
    """获取知识图谱模式信息"""
    logger.info("收到模式请求")
    try:
        schema = agent.get_schema_cached()
        logger.info("成功检索并返回模式")
        return jsonify({"success": True, "schema": schema})
            
    except Exception as e:
        logger.error("模式请求处理失败", exc_info=True)
        return jsonify({"error": f"内部服务器错误: {str(e)}"}), 500

@app.route('/ai/debug/entities', methods=['POST'])
def debug_entity_extraction():
    """调试实体提取功能"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({"error": "问题不能为空"}), 400
        
        entities = agent.extract_entities_cached(question)
        
        return jsonify({
            "success": True,
            "question": question,
            "entities": entities,
            "error": None
        })
        
    except Exception as e:
        logger.error("实体提取调试失败", exc_info=True)
        return jsonify({"error": f"实体提取失败: {str(e)}"}), 500

@app.route('/admin/cache/status', methods=['GET'])
def cache_status():
    """缓存状态监控"""
    try:
        if cache_manager.cache_enabled:
            info = cache_manager.redis_client.info()
            return jsonify({
                "cache_type": "Redis",
                "status": "已连接",
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0)
            })
        else:
            return jsonify({
                "cache_type": "内存",
                "status": "活跃",
                "cache_size": len(cache_manager.memory_cache),
                "cached_keys": list(cache_manager.memory_cache.keys())
            })
    except Exception as e:
        logger.error("获取缓存状态失败", exc_info=True)
        return jsonify({"error": f"获取缓存状态失败: {str(e)}"}), 500

@app.route('/admin/cache/clear', methods=['POST'])
def clear_cache():
    """清除缓存"""
    try:
        if cache_manager.cache_enabled:
            cache_manager.redis_client.flushdb()
            message = "Redis 缓存已清除"
        else:
            cache_manager.memory_cache.clear()
            message = "内存缓存已清除"
        
        agent._schema_cache = None
        agent._schema_cache_time = None
        
        logger.info(message)
        return jsonify({"success": True, "message": message})
        
    except Exception as e:
        logger.error("清除缓存失败", exc_info=True)
        return jsonify({"error": f"清除缓存失败: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查 - 增强版"""
    health_status = {
        "status": "健康",
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }
    
    # 检查数据库连接
    try:
        with driver.session() as session:
            result = session.run("RETURN 1").single()
            if result:
                health_status["services"]["database"] = "已连接"
            else:
                health_status["services"]["database"] = "响应异常"
                health_status["status"] = "部分健康"
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        health_status["services"]["database"] = f"连接失败: {str(e)[:50]}"
        health_status["status"] = "不健康"
    
    # 检查AI服务（快速测试，不影响主要状态）
    try:
        test_response = agent.call_llm(
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        health_status["services"]["ai_service"] = "已连接"
    except Exception as e:
        logger.warning(f"AI服务健康检查失败: {e}")
        health_status["services"]["ai_service"] = f"异常: {str(e)[:50]}"
        # AI服务失败不影响整体健康状态
    
    # 检查缓存
    health_status["services"]["cache"] = "已连接" if cache_manager.cache_enabled else "内存回退"
    
    status_code = 200 if health_status["status"] == "健康" else 503
    return jsonify(health_status), status_code

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "API 未找到"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error("内部服务器错误", exc_info=True)
    return jsonify({"error": "内部服务器错误"}), 500

# 应用启动
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 智能知识图谱问答系统 v3.0 正在启动...")
    print(f"📊 Neo4j 连接: {config.NEO4J_URI}")
    print(f"🤖 AI 模型: {config.AI_MODEL} ({config.AI_PROVIDER})")
    print(f"💾 缓存方式: {'Redis' if cache_manager.cache_enabled else '内存'}")
    print(f"⚡ 线程池: {config.MAX_WORKERS} 个工作线程")
    print("\n🌐 服务运行在: http://127.0.0.1:5001")
    print("📋 API 端点:")
    print("  - POST /ai/nl2cypher        (优化的自然语言到 Cypher)")
    print("  - POST /ai/rag              (优化的 RAG，带流式传输)")
    print("  - GET  /ai/schema           (获取数据库模式)")
    print("  - POST /ai/debug/*         (调试端点)")
    print("  - GET  /admin/*            (管理端点)")
    print("  - GET  /health              (健康检查)")
    print("\n按 Ctrl+C 退出")
    print("="*60 + "\n")
    
    try:
        app.run(debug=False, port=5001, threaded=True)
        # app.run(host='0.0.0.0', debug=False, port=5001, threaded=True)
    except KeyboardInterrupt:
        print("\n正在关闭服务...")
        executor.shutdown(wait=True)
        driver.close()
        print("服务已安全关闭")
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        print(f"❌ 应用启动失败: {e}")
    finally:
        try:
            driver.close()
        except:
            pass