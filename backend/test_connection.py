"""
Neo4j 连接测试脚本
用于验证数据库连接是否正常
"""
import sys
import time
from neo4j_driver import driver
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_connection():
    """测试 Neo4j 连接"""
    print("\n" + "="*60)
    print("🔍 开始测试 Neo4j 数据库连接...")
    print("="*60 + "\n")
    
    try:
        # 测试 1: 基本连接
        print("📌 测试 1: 验证驱动初始化...")
        if driver:
            print("   ✅ 驱动已成功初始化")
        else:
            print("   ❌ 驱动初始化失败")
            return False
        
        # 测试 2: 执行简单查询
        print("\n📌 测试 2: 执行简单查询 (RETURN 1)...")
        with driver.session() as session:
            result = session.run("RETURN 1 as number").single()
            if result and result["number"] == 1:
                print("   ✅ 查询执行成功")
            else:
                print("   ❌ 查询返回结果异常")
                return False
        
        # 测试 3: 查询数据库统计
        print("\n📌 测试 3: 查询数据库节点统计...")
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count").single()
            node_count = result["count"]
            print(f"   ✅ 数据库中共有 {node_count} 个节点")
        
        # 测试 4: 查询人物节点
        print("\n📌 测试 4: 查询人物节点 (前5个)...")
        with driver.session() as session:
            results = session.run("MATCH (n:Person) RETURN n.name as name LIMIT 5")
            persons = [record["name"] for record in results]
            if persons:
                print(f"   ✅ 找到人物: {', '.join(persons)}")
            else:
                print("   ⚠️ 未找到人物节点")
        
        # 测试 5: 测试连接稳定性
        print("\n📌 测试 5: 测试连接稳定性 (执行3次查询)...")
        for i in range(3):
            with driver.session() as session:
                session.run("RETURN 1").single()
            print(f"   ✅ 第 {i+1} 次查询成功")
            time.sleep(0.5)
        
        print("\n" + "="*60)
        print("✅ 所有测试通过！数据库连接正常")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ 连接测试失败: {e}")
        print("="*60 + "\n")
        logger.error(f"详细错误信息: {e}", exc_info=True)
        return False
    finally:
        # 不关闭驱动，因为它是全局的
        pass

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
