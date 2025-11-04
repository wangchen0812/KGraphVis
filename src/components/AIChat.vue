<template>
  <div class="ai-chat-container">
    <!-- 头部 -->
    <div class="chat-header">
      <!-- <h3>AI智能问答</h3> -->
      <div class="mode-selector">
        <button :class="['mode-btn', { active: currentMode === 'nl2cypher' }]" @click="switchMode('nl2cypher')">
          🔍图谱查询
        </button>
        <button :class="['mode-btn', { active: currentMode === 'rag' }]" @click="switchMode('rag')">
          💬智能问答
        </button>
      </div>
      <div class="clear-history">
        <button @click="clearHistory" class=" mode-btn clear-history-btn" title="清空当前模式的历史记录">
          🗑️ 清空
        </button>
      </div>

      <!-- <button @click="clearAllHistory" class="mode-btn clear-history-btn" title="清空所有模式的历史记录">
          🗑️ 清空所有
        </button> -->
    </div>

    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <div v-if="currentMessages.length === 0" class="welcome-message">
        <div class="welcome-content">

          <div v-if="currentMode === 'nl2cypher'" class="mode-intro">
            <div class="welcome-conten-title">🔍 <strong>图谱查询模式</strong></div>
            <p class="welcome-conten-context">用自然语言描述您想查询的内容，AI将生成相应的图谱查询并以可视化形式展示结果。</p>
            <div class="example-questions">
              <p>示例问题：</p>
              <div class="example-item" @click="setQuestion('任质斌前辈参加了哪些重要战役战斗？')">
                任质斌前辈参加了哪些重要战役战斗？
              </div>
              <div class="example-item" @click="setQuestion('李先念和任质斌有什么关系？')">
                李先念和任质斌有什么关系？
              </div>
              <div class="example-item" @click="setQuestion('参与侏儒山战役的人物有哪些？')">
                参与侏儒山战役的人物有哪些？
              </div>
            </div>
          </div>
          <div v-else class="mode-intro">
            <div class="welcome-conten-title">💬 <strong>智能问答模式</strong></div>
            <p class="welcome-conten-context">基于知识图谱内容，AI将为您提供详细的文字回答。</p>
            <div class="example-questions">
              <p>示例问题：</p>
              <div class="example-item" @click="setQuestion('任质斌前辈参加了哪些重要战役战斗？')">
                任质斌前辈参加了哪些重要战役战斗？
              </div>
              <div class="example-item" @click="setQuestion('任质斌与李先念前辈共同参加过什么战役？')">
                任质斌与李先念前辈共同参加过什么战役？
              </div>
              <div class="example-item" @click="setQuestion('请查询有多少位女性人物？')">
                请查询有多少位女性人物？
              </div>
              <div class="example-item" @click="setQuestion('刘少卿在抗日和解放战争时期按时间排序参与的组织机构和担任职务？')">
                刘少卿在抗日和解放战争时期按时间排序参与的组织机构和担任职务？
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-for="(message, index) in currentMessages" :key="message.id || index" class="message">
        <div :class="['message-bubble', message.type]">
          <div class="message-header">
            <span class="message-role">{{ message.type === 'user' ? '用户' : 'AI助手' }}</span>
            <span class="message-time">{{ formatTime(message.timestamp) }}</span>
          </div>

          <div class="message-content">
            <!-- 用户消息 -->
            <div v-if="message.type === 'user'" class="user-message">
              {{ message.content }}
            </div>

            <!-- AI回复 - 图谱查询模式 -->
            <div v-else-if="message.type === 'assistant' && message.mode === 'nl2cypher'" class="assistant-message">
              <div v-if="message.success" class="nl2cypher-success">
                <div class="cypher-info">
                  <h5>🔍 生成的查询语句：</h5>
                  <div class="cypher-code">{{ message.cypher }}</div>
                </div>
                <div class="result-info">
                  <p>✅ 查询成功，结果已在图谱中显示</p>
                  <p class="result-stats">
                    找到 {{ message.data?.nodes?.length || 0 }} 个节点，
                    {{ message.data?.links?.length || 0 }} 个关系
                  </p>
                </div>
              </div>
              <div v-else class="nl2cypher-error">
                <h5>❌ 查询失败：</h5>
                <p>{{ message.error }}</p>
                <div v-if="message.cypher" class="cypher-info">
                  <h6>生成的查询语句：</h6>
                  <div class="cypher-code">{{ message.cypher }}</div>
                </div>
              </div>
            </div>

            <!-- AI回复 - RAG问答模式 -->
            <div v-else-if="message.type === 'assistant' && message.mode === 'rag'" class="assistant-message">
              <div class="rag-answer markdown-body">
                <div v-if="!streamingMessage || message.id !== currentStreamingMessageId" class="answer-content"
                  v-html="formatAnswer(message.content)"></div>

                <!-- 流式响应时显示当前正在输入的内容 -->
                <div v-if="streamingMessage && message.id === currentStreamingMessageId && currentMode === 'rag'"
                  class="streaming-content">
                  <div class="streaming-text" v-html="formatAnswer(streamingMessage)"></div>
                </div>
                <div v-if="message.context && showContext" class="context-info">
                  <h6>📚 参考信息：</h6>
                  <div v-if="message.raw_context" class="context-content raw-context">
                    <div v-for="(section, index) in message.raw_context" :key="index">
                      <h4>{{ section.title }}</h4>
                      <ul>
                        <li v-for="(item, itemIndex) in section.content" :key="itemIndex"
                            :class="{'section-item': true, [section.type]: true}">
                          {{ item }}
                        </li>
                      </ul>
                    </div>
                  </div>
                  <div v-else class="context-content" v-html="formatContext(message.context)"></div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <!-- <div v-if="isLoading" class="loading-message">
        <div class="loading-bubble">
          <p>{{ currentMode === 'nl2cypher' ? '正在生成查询语句...' : '正在思考回答...' }}</p>
        </div>
      </div> -->

    </div>

    <!-- 输入区域 -->
    <div class="chat-input">
      <div class="input-wrapper">
        <input v-model="inputMessage" type="text"
          :placeholder="currentMode === 'nl2cypher' ? '请用自然语言描述您想查询的内容...' : '请输入您的问题...'" @keypress.enter="sendMessage"
          :disabled="isLoading" class="message-input" />
        <button @click="sendMessage" :disabled="!inputMessage.trim() || isLoading" class="send-button">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2,21L23,12L2,3V10L17,12L2,14V21Z" />
          </svg>
        </button>
      </div>
      <div class="input-footer">
        <label class="context-toggle">
          <input type="checkbox" v-model="showContext" />
          显示参考信息
        </label>
        <span class="mode-indicator">
          当前模式：{{ currentMode === 'nl2cypher' ? '图谱查询' : '智能问答' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, watch, computed } from 'vue'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['graph-query-result'])

// 响应式数据
const currentMode = ref('nl2cypher') // 'nl2cypher' | 'rag'
const inputMessage = ref('')
const isLoading = ref(false)
// 将messages改为分模式存储
const messagesStore = reactive({
  'nl2cypher': [],
  'rag': []
})
const messagesContainer = ref(null)
const showContext = ref(false)
const streamingMessage = ref('') // 用于存储流式响应的当前内容
const currentStreamingMessageId = ref(null) // 当前流式消息的ID
let messageIdCounter = 0 // 消息ID计数器

// 计算当前模式下的消息
const currentMessages = computed(() => {
  return messagesStore[currentMode.value]
})

// 生成唯一消息ID
const generateMessageId = () => {
  return `msg_${Date.now()}_${++messageIdCounter}`
}

// 初始化或加载本地存储的数据
const loadStoredMessages = () => {
  try {
    const stored = localStorage.getItem('ai-chat-messages')
    if (stored) {
      const parsedData = JSON.parse(stored)
      if (parsedData && typeof parsedData === 'object') {
        // 确保每个模式都存在
        messagesStore['nl2cypher'] = parsedData['nl2cypher'] || []
        messagesStore['rag'] = parsedData['rag'] || []

        // 确保每条消息都有ID
        Object.keys(messagesStore).forEach(mode => {
          messagesStore[mode].forEach(message => {
            if (!message.id) {
              message.id = generateMessageId()
            }
            // 确保时间戳是Date对象
            if (message.timestamp && typeof message.timestamp === 'string') {
              message.timestamp = new Date(message.timestamp)
            }
          })
        })
      }
    }
  } catch (error) {
    console.warn('加载本地存储的消息失败:', error)
    // 如果加载失败，初始化空数据
    messagesStore['nl2cypher'] = []
    messagesStore['rag'] = []
  }
}

// 保存消息到本地存储
const saveMessagesToStorage = () => {
  try {
    localStorage.setItem('ai-chat-messages', JSON.stringify(messagesStore))
  } catch (error) {
    console.warn('保存消息到本地存储失败:', error)
  }
}

// 方法
const setQuestion = (question) => {
  inputMessage.value = question
}

// 切换模式时不清空消息，而是切换到对应模式的消息
const switchMode = (mode) => {
  currentMode.value = mode
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const messageId = generateMessageId()
  const userMessage = {
    id: messageId,
    type: 'user',
    content: inputMessage.value,
    timestamp: new Date(),
    mode: currentMode.value
  }

  // 添加到当前模式的消息列表
  messagesStore[currentMode.value].push(userMessage)
  saveMessagesToStorage() // 保存到本地存储

  const question = inputMessage.value
  inputMessage.value = ''
  isLoading.value = true
  streamingMessage.value = '' // 重置流式消息
  currentStreamingMessageId.value = null

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    if (currentMode.value === 'nl2cypher') {
      await handleNL2Cypher(question)
    } else {
      await handleRAGStream(question) // 使用流式处理
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    const errorMessageId = generateMessageId()
    const errorMessage = {
      id: errorMessageId,
      type: 'assistant',
      content: '抱歉，服务暂时不可用，请稍后再试。',
      timestamp: new Date(),
      mode: currentMode.value,
      success: false,
      error: error.message
    }
    messagesStore[currentMode.value].push(errorMessage)
    saveMessagesToStorage()
  } finally {
    isLoading.value = false
    streamingMessage.value = ''
    currentStreamingMessageId.value = null
    await nextTick()
    scrollToBottom()
  }
}

const handleNL2Cypher = async (question) => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL
    
    // 第一步：获取Cypher查询语句
    const nl2cypherResponse = await fetch(`${apiUrl}/ai/nl2cypher`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    })

    if (!nl2cypherResponse.ok) {
      throw new Error(`生成查询语句失败: ${nl2cypherResponse.status}`)
    }

    const nl2cypherResult = await nl2cypherResponse.json()
    
    if (!nl2cypherResult.success) {
      throw new Error(nl2cypherResult.error || '生成查询语句失败')
    }

    // 第二步：使用生成的Cypher语句查询图谱
    const graphResponse = await fetch(`${apiUrl}/graph`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cypher: nl2cypherResult.cypher })
    })

    if (!graphResponse.ok) {
      throw new Error(`执行查询失败: ${graphResponse.status}`)
    }

    const graphResult = await graphResponse.json()
    const messageId = generateMessageId()

    // 准备消息内容
    const assistantMessage = {
      id: messageId,
      type: 'assistant',
      timestamp: new Date(),
      mode: 'nl2cypher',
      success: true,
      cypher: nl2cypherResult.cypher,
      data: graphResult.data
    }

    messagesStore[currentMode.value].push(assistantMessage)
    saveMessagesToStorage()

    // 处理Event节点category并触发图谱更新
    if (graphResult.data && graphResult.data.nodes) {
      graphResult.data.nodes.forEach(n => {
        if ((n.category === 'Event' || n.category === 'Battle') && n.properties?.category) {
          n.category = n.properties.category
        }
      })

      emit('graph-query-result', {
        type: 'graph',
        data: {
          nodes: graphResult.data.nodes || [],
          links: graphResult.data.links || []
        },
        cypher: nl2cypherResult.cypher
      })
    }

  } catch (error) {
    const errorMessageId = generateMessageId()
    const errorMessage = {
      id: errorMessageId,
      type: 'assistant',
      timestamp: new Date(),
      mode: 'nl2cypher',
      success: false,
      error: `网络请求失败: ${error.message}`
    }
    messagesStore[currentMode.value].push(errorMessage)
    saveMessagesToStorage()
  }
}

// 原来的非流式RAG处理（保留作为备用）
const handleRAG = async (question) => {
  try {
    const apiUrl = import.meta.env.VITE_API_URL
    const response = await fetch(`${apiUrl}/ai/rag`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'  // 指定接受流式响应
      },
      body: JSON.stringify({ question })
    })

    const result = await response.json()
    const messageId = generateMessageId()

    const message = {
      id: messageId,
      type: 'assistant',
      content: result.answer,
      context: result.context,
      timestamp: new Date(),
      mode: 'rag',
      success: result.success
    }

    messagesStore[currentMode.value].push(message)
    saveMessagesToStorage()

  } catch (error) {
    const errorMessageId = generateMessageId()
    const errorMessage = {
      id: errorMessageId,
      type: 'assistant',
      content: '抱歉，无法获取回答，请稍后再试。',
      timestamp: new Date(),
      mode: 'rag',
      success: false,
      error: error.message
    }
    messagesStore[currentMode.value].push(errorMessage)
    saveMessagesToStorage()
  }
}

// 新增的流式RAG处理方法
const handleRAGStream = async (question) => {
  const apiUrl = import.meta.env.VITE_API_URL

  streamingMessage.value = ''
  const assistantMessageId = generateMessageId()
  currentStreamingMessageId.value = assistantMessageId

  // 创建一个空的消息对象
  const assistantMessage = {
    id: assistantMessageId,
    type: 'assistant',
    content: '',
    timestamp: new Date(),
    mode: 'rag',
    success: true
  }
  
  // 添加消息到列表
  messagesStore[currentMode.value].push(assistantMessage)
  saveMessagesToStorage()


  try {
    const response = await fetch(`${apiUrl}/ai/rag`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream'  // 指定接受流式响应
      },
      body: JSON.stringify({ question })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    if (!response.body) {
      throw new Error('ReadableStream not supported')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    let assistantMessage = null
    let fullContent = ''

    try {
      while (true) {
        const { done, value } = await reader.read()

        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              // console.log('Received SSE data:', data);
              
              if (data.type === 'answer_chunk') {
                // 更新流式内容
                fullContent = data.full_content
                if (!assistantMessage) {
                  assistantMessage = {
                    id: assistantMessageId,
                    type: 'assistant',
                    content: fullContent,
                    timestamp: new Date(),
                    mode: 'rag',
                    success: true
                  }
                  messagesStore[currentMode.value].pop() // 移除之前的空消息
                  messagesStore[currentMode.value].push(assistantMessage)
                } else {
                  assistantMessage.content = fullContent
                }
                streamingMessage.value = fullContent
                saveMessagesToStorage()
                await nextTick()
                scrollToBottom()
                isLoading.value = false
                
              } else if (data.type === 'complete') {
                // 流式响应完成
                if (data.final_answer) {
                  assistantMessage.content = data.final_answer
                  if (data.retrieved_context) {
                    assistantMessage.context = data.retrieved_context
                  }
                }
                streamingMessage.value = ''
                saveMessagesToStorage()
                await nextTick()
                scrollToBottom()
                
                break
              }
            } catch (parseError) {
              console.warn('解析SSE数据失败:', parseError, line)
            }
          }
        }
      }
    } finally {
      isLoading.value = false
      reader.releaseLock()
    }

  } catch (error) {
    console.error('流式请求失败:', error)
    const errorMessageId = generateMessageId()
    const errorMessage = {
      id: errorMessageId,
      type: 'assistant',
      content: '抱歉，无法获取回答，请稍后再试。',
      timestamp: new Date(),
      mode: 'rag',
      success: false,
      error: error.message
    }
    messagesStore[currentMode.value].push(errorMessage)
    saveMessagesToStorage()
  }
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}


const formatAnswer = (answer) => {
  if (!answer) return '';
  try {
    return md.render(answer);
  } catch (error) {
    console.error('Markdown渲染失败:', error);
    return answer;
  }
}

// 格式化参考信息
const formatContext = (context) => {
  if (!context) return '';

  // 检查是否为 raw_context_data 格式
  if (Array.isArray(context)) {
    let htmlContent = '';
    context.forEach((section) => {
      htmlContent += `<h4>${section.title}</h4>`;
      if (Array.isArray(section.content) && section.content.length > 0) {
        htmlContent += '<ul>';
        section.content.forEach((item) => {
          htmlContent += `<li>${item}</li>`;
        });
        htmlContent += '</ul>';
      } else if (section.type === 'graph' && section.graph) {
        // 展示graph类型的节点和关系
        if (section.graph.nodes && section.graph.nodes.length > 0) {
          htmlContent += '<ul>';
          section.graph.nodes.forEach((node, idx) => {
            htmlContent += `<li class='section-item person-profile'>[节点${idx+1}] ${node.name || node.id} (${node.category || ''})</li>`;
          });
          htmlContent += '</ul>';
        }
        if (section.graph.links && section.graph.links.length > 0) {
          htmlContent += '<ul>';
          section.graph.links.forEach((link, idx) => {
            htmlContent += `<li class='section-item relationship'>[关系${idx+1}] ${link.source} --${link.name || link.type}--> ${link.target}</li>`;
          });
          htmlContent += '</ul>';
        }
      }
    });
    return htmlContent;
  }

  // 原始格式化逻辑
  const sections = context.split('===').map((s) => s.trim()).filter(Boolean);
  let htmlContent = '';

  sections.forEach((section) => {
    const [title, ...contentLines] = section.split('\n');
    htmlContent += `<h4>${title}</h4>`;
    if (contentLines.length) {
      htmlContent += '<ul>';
      contentLines.forEach((line) => {
        htmlContent += `<li>${line}</li>`;
      });
      htmlContent += '</ul>';
    }
  });

  return htmlContent;
};

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 清空当前模式的历史记录
const clearHistory = () => {
  if (confirm(`确定要清空${currentMode.value === 'nl2cypher' ? '图谱查询' : '智能问答'}模式的历史记录吗？`)) {
    messagesStore[currentMode.value] = []
    runclearHistory()
    saveMessagesToStorage()
  }
}


async function runclearHistory() {
  try {
    const apiUrl = import.meta.env.VITE_API_URL;
    const response = await fetch(`${apiUrl}/admin/cache/clear`, {
      method: 'POST'
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    const result = await response.json();
    if (result.error) throw new Error(result.error);
    console.log("清空后端历史缓存:", result.message);
  } catch (e) {
    console.error("清空后端历史缓存时出错:", e);
  } finally {

  }
}

// 可选：清空所有模式的历史记录
const clearAllHistory = () => {
  if (confirm('确定要清空所有模式的历史记录吗？此操作不可恢复！')) {
    messagesStore['nl2cypher'] = []
    messagesStore['rag'] = []
    saveMessagesToStorage()
  }
}

// 组件挂载时加载存储的消息
loadStoredMessages()

// 监听模式切换，但不再清空消息
watch(currentMode, (newMode) => {
  // 切换模式时滚动到底部
  nextTick(() => {
    scrollToBottom()
  })
})

// 监听消息变化，自动滚动
watch(() => currentMessages.value.length, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

</script>

<style scoped>
.ai-chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--bg-secondary);
  border-radius: 8px;
  overflow: hidden;
  color: var(--text-primary);
}

.chat-header {
  padding: 0;
  position: fixed;
  top: 95px;
  left: 320px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 70%;
}

.chat-header h3 {
  margin: 0 0 12px 0;
  color: var(--text-primary);
  font-size: 18px;
}

.mode-selector {
  display: flex;
  gap: 8px;
  flex-direction: column;
}

.mode-btn {
  padding: 2px 2px;
  border: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  width: 30px;
}

.mode-btn:hover {
  background-color: var(--bg-hover);
}

.mode-btn.active {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.welcome-message {
  text-align: center;
  color: var(--text-secondary);
  padding: 0px 50px 0px 100px;
}

.welcome-content h4 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
}

.mode-intro {
  text-align: left;
  max-width: 600px;
  margin: 0 auto;
}

.mode-intro p {
  margin: 8px 0;
  line-height: 1.5;
}

.example-questions {
  margin-top: 20px;
}

.example-questions p {
  font-weight: 500;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.example-item {
  color: var(--text-muted);
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 8px 12px;
  margin: 4px 0;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.example-item:hover {
  background-color: var(--bg-hover);
  border-color: var(--primary-color);
}

.message {
  display: flex;
  flex-direction: column;
}

.message-bubble {
  max-width: 85%;
  border-radius: 12px;
  padding: 12px 16px;
  word-wrap: break-word;
}

.message-bubble.user {
  align-self: flex-end;
  background-color: var(--primary-color);
  color: white;
}

.message-bubble.assistant {
  margin-left: 30px;
  align-self: flex-start;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  opacity: 0.7;
}

.message-content {
  line-height: 1.5;
}

.user-message {
  color: var(--text-primary);
}

.assistant-message {
  color: var(--text-primary);
}

.nl2cypher-success {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.cypher-info h5 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  font-size: 14px;
}

.cypher-code {
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 8px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: var(--text-primary);
  overflow-x: auto;
}

.result-info {
  padding: 8px;
  background-color: rgba(34, 197, 94, 0.1);
  border-radius: 4px;
  border-left: 3px solid #22c55e;
}

.result-info p {
  margin: 4px 0;
  font-size: 14px;
}

.result-stats {
  color: var(--text-secondary);
  font-size: 12px;
}

.nl2cypher-error {
  padding: 8px;
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: 4px;
  border-left: 3px solid #ef4444;
}

.nl2cypher-error h5 {
  margin: 0 0 8px 0;
  color: #ef4444;
  font-size: 14px;
}

.rag-answer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.answer-content {
  line-height: 1.5;
  color: var(--text-primary);
}

.context-info {
  margin-top: 12px;
  padding: 8px;
  background-color: var(--bg-secondary);
  border-radius: 4px;
  border-left: 3px solid var(--primary-color);
}

.context-info h6 {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.context-content {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.loading-message {
  display: flex;
  justify-content: flex-start;
  margin: 30px;
}

.loading-bubble {
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 85%;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--primary-color);
  animation: loading-bounce 1.4s ease-in-out infinite both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

/* 流式响应相关样式 */
.streaming-content {
  margin-top: 8px;
  padding: 8px;
  background-color: var(--bg-secondary);
  border-radius: 4px;
  border-left: 3px solid var(--primary-color);
}

.streaming-text {
  line-height: 1.5;
  color: var(--text-primary);
}

/* 流式响应时的动态效果 */
.streaming-text::after {
  content: '|';
  animation: blink 1s infinite;
  color: var(--primary-color);
}

@keyframes blink {

  0%,
  50% {
    opacity: 1;
  }

  51%,
  100% {
    opacity: 0;
  }
}

@keyframes loading-bounce {

  0%,
  80%,
  100% {
    transform: scale(0);
  }

  40% {
    transform: scale(1);
  }
}

.chat-input {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-primary);
}

.input-wrapper {
  display: flex;
  gap: 8px;
  align-items: center;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 24px;
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.message-input:focus {
  border-color: var(--primary-color);
}

.message-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-button {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: var(--primary-color);
  /* color: white; */
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.send-button:hover:not(:disabled) {
  background-color: var(--primary-color-hover);
  transform: scale(1.05);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  margin-right: 50px;
  font-size: 12px;
  color: var(--text-secondary);
}

.context-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

.context-toggle input {
  margin: 0;
}

.mode-indicator {
  font-weight: 500;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

.chat-messages::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

.context-content h4 {
  margin: 12px 0 8px;
  font-size: 14px;
  color: var(--text-primary);
  border-left: 3px solid var(--primary-color);
  padding-left: 8px;
}

.context-content ul {
  list-style-type: none;
  padding-left: 12px;
  margin: 0;
}

.context-content li {
  margin-bottom: 4px;
  font-size: 13px;
  line-height: 1.4;
  color: var(--text-secondary);
}

.raw-context {
  margin-top: 8px;
}

.raw-context h4 {
  font-size: 14px;
  color: var(--text-primary);
  margin: 12px 0 8px;
  padding: 4px 8px;
  background-color: var(--bg-primary);
  border-radius: 4px;
  border-left: 3px solid var(--primary-color);
}

.raw-context ul {
  list-style-type: none;
  padding-left: 16px;
  margin: 8px 0;
}

.section-item {
  padding: 4px 0;
  border-bottom: 1px dashed var(--border-color);
}

.section-item:last-child {
  border-bottom: none;
}

.section-item.person-profile {
  color: var(--text-primary);
  font-weight: 500;
}

.section-item.event {
  color: #2563eb;
}

.section-item.relationship {
  color: #059669;
}

.section-item.timeline {
  color: #7c3aed;
}

.context-content .detail-info {
  font-size: 11px;
  color: #6c757d;
  /* 更浅的颜色 */
}

.context-content .highlight-info {
  font-weight: bold;
  color: var(--primary-color);
}

.welcome-conten-title {
  font-size: 25px;
  padding: 15px 0;
  color: var(--text-secondary);
  margin-bottom: 15px;
  border-bottom: 2px solid var(--text-muted);
}

.welcome-conten-context {
  font-size: 16px;
  color: var(--text-muted);
  margin-bottom: 15px;
}

.markdown-body {
  background-color: var(--bg-secondary);
  padding: 8px;
  border-radius: 4px;
}

.markdown-body table {
  background-color: var(--bg-secondary);
  padding: 8px;
  border-radius: 4px;
}

.clear-history-btn {
  padding: 4px 8px;
  border: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 12px;
}

.clear-history-btn:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  /* 添加间距 */
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}
</style>