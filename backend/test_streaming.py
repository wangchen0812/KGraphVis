"""测试流式响应"""
import requests
import json

def test_person_chat_streaming():
    url = "http://localhost:5001/ai/person_chat"
    
    payload = {
        "person_name": "任质斌",
        "chat_history": [],
        "user_message": "你好，请简单介绍一下你自己"
    }
    
    print("发送请求到:", url)
    print("请求数据:", json.dumps(payload, ensure_ascii=False))
    print("\n" + "="*60)
    print("开始接收流式响应:\n")
    
    try:
        response = requests.post(
            url,
            json=payload,
            stream=True,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            print(f"❌ HTTP错误: {response.status_code}")
            print(response.text)
            return
        
        print("✅ 连接成功，开始接收数据...\n")
        
        chunk_count = 0
        buffer = ''
        
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                buffer += chunk
                
                # 按 \n\n 分割事件
                events = buffer.split('\n\n')
                buffer = events.pop() if events else ''
                
                for event in events:
                    if not event.strip():
                        continue
                    
                    # 解析事件
                    lines = event.split('\n')
                    event_type = 'message'
                    event_data = ''
                    
                    for line in lines:
                        if line.startswith('event: '):
                            event_type = line[7:].strip()
                        elif line.startswith('data: '):
                            event_data = line[6:]
                    
                    if event_data:
                        try:
                            data = json.loads(event_data)
                            
                            if data.get('type') == 'step':
                                print(f"📋 步骤: {data.get('message')}")
                            
                            elif data.get('type') == 'answer_chunk':
                                chunk_count += 1
                                content = data.get('content', '')
                                print(content, end='', flush=True)
                            
                            elif data.get('type') == 'complete':
                                print(f"\n\n✅ 完成! 共接收 {chunk_count} 个数据块")
                                if data.get('full_answer'):
                                    print(f"完整答案长度: {len(data['full_answer'])} 字符")
                            
                            elif data.get('type') == 'error':
                                print(f"\n❌ 错误: {data.get('error')}")
                        
                        except json.JSONDecodeError as e:
                            print(f"\n⚠️ JSON解析错误: {e}")
                            print(f"原始数据: {event_data[:100]}...")
        
        print("\n" + "="*60)
        print("流式响应接收完成")
        
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 测试人物聊天流式响应")
    print("="*60 + "\n")
    test_person_chat_streaming()
