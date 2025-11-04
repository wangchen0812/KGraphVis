<!-- src/components/SystemIntroduction.vue -->
<template>
  <!-- 系统简介覆盖页面 -->
  <div v-if="showIntroduction" class="system-introduction-overlay">
    <div class="introduction-content">
      <div class="content-wrapper">
        <!-- 标题区域 -->
        <div class="title-section">
          <h1 class="main-title">新四军五师红色信息图谱</h1>
          <div class="title-decoration"></div>
        </div>

        <!-- 内容区域 - 双栏布局 -->
        <div class="content-grid">
          <!-- 左侧：新四军第五师简介 -->
          <div class="content-column">
            <div class="intro-card">
              <div class="card-header">
                <h2 class="section-title">新四军第五师</h2>
                <span class="section-badge">近代军事部队</span>
              </div>
              <div class="card-content">
                <div class="highlight-text">中国共产党领导下的一支重要抗日武装力量，成立于抗日战争时期。</div>
                <ul class="feature-list">
                  <li>主要由湖北、河南、安徽等地的红军游击队和抗日义勇军组成，后来发展成为新四军的重要组成部分。第五师在抗日战争中英勇作战，为中国人民的解放事业作出了重要贡献。</li>
                  <li> 五师主要领导人是李先念，他在抗日战争和解放战争中发挥了重要作用。五师在敌后开展游击战争，有效地打击了日本侵略者，保护了人民群众生命财产安全，为中国共产党在华中地区的发展奠定了基础。
                  </li>
                  <li> 抗日战争胜利后，新四军五师继续参与解放战争，为中国人民的解放事业奋斗。1949年中华人民共和国成立后，五师许多成员成为新中国建设和国防重要力量。
                  </li>
                  <li> 新四军五师历史是中国革命史一部分，它的英勇事迹和牺牲精神永远铭记在中国人民心中。
                  </li>
                </ul>

                <!-- <button class="audio-play-btn" @click="playIntroAudio" title="播放简介音频">
                  <Volume2 :size="18" />
                  <span>播放</span>
                </button> -->

                <button class="audio-play-btn" @click="toggleIntroAudio('wushi')" :title="wushiPlaying ? '暂停' : '播放'">
                  <PauseCircle v-if="wushiPlaying" :size="18" />
                  <Volume2 v-else :size="18" />
                  <span>{{ wushiPlaying ? '暂停' : '播放' }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 右侧：系统简介 -->
          <div class="content-column">
            <div class="intro-card">
              <div class="card-header">
                <h2 class="section-title">系统功能</h2>
                <span class="section-badge">知识图谱</span>
              </div>
              <div class="card-content">
                <div class="highlight-text">
                  构建可交互知识图谱，便捷查询历史关系。
                </div>
                <ul class="feature-list">
                  <li>
                    系统通过<b>北京新四军研究会五师分会会员自愿填写调查问卷、公开出版物和百度百科等相对可靠</b>的形式收集新四军五师前辈信息、包括教育与工作经历、参加战役战斗等，构建可交互知识图谱，便捷查询"战友、同乡、战役"等关系，为新四军五师革命历史研究提供辅助工具。
                  </li>
                  <li>
                    支持输入人物的姓名查询人物关系、教育与工作经历、参与的战役战斗。
                  </li>
                  <li>
                    输入战役战斗的名称查看共同参与的人物。
                  </li>
                  <li>
                    图谱可展示、可交互，提供时间轴过滤、属性详情展示功能。
                  </li>
                  <li>
                    提供智能问答，可返回图谱子图，也可提供自然语言答案。
                  </li>
                </ul>

                <button class="audio-play-btn" @click="toggleIntroAudio('system')" :title="systemPlaying ? '暂停' : '播放'">
                  <PauseCircle v-if="systemPlaying" :size="18" />
                  <Volume2 v-else :size="18" />
                  <span>{{ systemPlaying ? '暂停' : '播放' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 按钮区域 -->
        <div class="button-section">
          <button class="enter-system-btn" @click="enterSystem">
            <span class="btn-text">进入系统</span>
            <span class="btn-icon">→</span>
          </button>
          <p class="btn-subtitle">探索新四军第五师革命历史</p>
        </div>
      </div>
    </div>
  </div>

  <!-- 右下角小图标 -->
  <div v-if="!showIntroduction" class="floating-icon" @click="showIntroduction = true" title="查看系统简介">
    <BookOpen :size="18" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { BookOpen, Volume2, PauseCircle } from 'lucide-vue-next'

/* 响应式数据 */
const showIntroduction = ref(true)

/* 方法 */
function enterSystem() {
  showIntroduction.value = false
  audioWushi.currentTime = 0;
  audioWushi.pause()
  wushiPlaying.value = false
  
  audioSystem.currentTime = 0;
  audioSystem.pause()
  systemPlaying.value = false
}

// /* 播放音频 */
// const introAudioUrl = new URL('../assets/audio/新四军五师介绍.mp3', import.meta.url).href
// function playIntroAudio() {
//   const audio = new Audio(introAudioUrl)
//   audio.play().catch(() => alert('音频加载失败，请检查文件路径'))
// }

/* ---------- 音频 ---------- */
const audioWushi = new Audio(new URL('../assets/audio/新四军五师介绍.mp3', import.meta.url).href)
const audioSystem = new Audio(new URL('../assets/audio/系统功能介绍.mp3', import.meta.url).href)

/* 各卡片独立的播放状态 */
const wushiPlaying = ref(false)
const systemPlaying = ref(false)

/* 播放/暂停 */
function toggleIntroAudio(label) {
  if (label === 'wushi') {
    if (wushiPlaying.value) {
      audioWushi.pause()
    } else {
      audioWushi.play().catch(() => alert('音频加载失败'))
    }
    wushiPlaying.value = !wushiPlaying.value
    // 保证另一支一定停止
    if (systemPlaying.value) {
      audioSystem.pause()
      systemPlaying.value = false
    }
  }

  if (label === 'system') {
    if (systemPlaying.value) {
      audioSystem.pause()
    } else {
      audioSystem.play().catch(() => alert('音频加载失败'))
    }
    systemPlaying.value = !systemPlaying.value
    if (wushiPlaying.value) {
      audioWushi.pause()
      wushiPlaying.value = false
    }
  }
}



</script>

<style scoped>
.system-introduction-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: url('../assets/背景1.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(1px);
  overflow: hidden;
}

.introduction-content {
  width: min(90vw, 1400px);
  height: min(100vh, 900px);
  background: rgba(255, 255, 255, 0);
  border-radius: clamp(10px, 2vw, 20px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-wrapper {
  /* padding: clamp(10px, 2vh, 20px) clamp(10px, 2vw, 30px); */
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: clamp(10px, 2vh, 20px);
}

/* 标题区域 */
.title-section {
  text-align: center;
  flex-shrink: 0;
}

.main-title {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  font-weight: bold;
  color: #2c1810;
  margin-bottom: clamp(8px, 1.5vh, 15px);
  text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.8);
  line-height: 1.2;
}

.title-decoration {
  width: clamp(100px, 20vw, 200px);
  height: clamp(2px, 0.5vh, 4px);
  background: linear-gradient(90deg, transparent, #8B4513, transparent);
  margin: 0 auto;
  border-radius: 2px;
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(15px, 3vw, 30px);
  flex: 1;
  min-height: 0;
  /* 允许内容收缩 */
}

.content-column {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.intro-card {
  background: rgba(255, 248, 220, 0.65);
  border-radius: clamp(8px, 1.5vw, 15px);
  border: 2px solid rgba(139, 69, 19, 0.3);
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  min-height: 0;
  overflow: hidden;
}

.card-header {
  padding: clamp(15px, 2.5vh, 25px) clamp(15px, 2.5vw, 25px) clamp(10px, 1.5vh, 15px);
  border-bottom: 2px solid rgba(139, 69, 19, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
  flex-wrap: wrap;
  gap: 10px;
}

.section-title {
  font-size: clamp(1.2rem, 2.5vw, 1.6rem);
  font-weight: bold;
  color: #2C1810;
  margin: 0;
  line-height: 1.2;
}

.section-badge {
  background: linear-gradient(135deg, #8B4513, #CD853F);
  color: white;
  padding: clamp(3px, 0.5vh, 5px) clamp(8px, 1.5vw, 12px);
  border-radius: 20px;
  font-size: clamp(0.7rem, 1.5vw, 0.8rem);
  font-weight: 500;
  white-space: nowrap;
}

.card-content {
  padding: clamp(15px, 2.5vh, 25px);
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  min-height: 0;
}

.highlight-text {
  font-size: clamp(0.9rem, 2vw, 1.1rem);
  font-weight: 600;
  color: #2C1810;
  margin-bottom: clamp(8px, 1.5vh, 15px);
  padding: clamp(8px, 1.5vh, 12px);
  background: rgba(222, 184, 135, 0.4);
  border-radius: clamp(6px, 1vw, 10px);
  border-left: 4px solid #8B4513;
  line-height: 1.4;
  flex-shrink: 0;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  flex: 1;
  overflow-y: auto;
}

.feature-list li {
  padding: clamp(6px, 1vh, 10px) 0;
  color: #2C1810;
  font-size: clamp(0.8rem, 1.8vw, 1rem);
  position: relative;
  padding-left: clamp(16px, 3vw, 20px);
  line-height: 1.5;
  margin-bottom: clamp(4px, 0.8vh, 8px);
}

.feature-list li::before {
  content: "★";
  color: #8B4513;
  font-weight: bold;
  position: absolute;
  left: 0;
  top: clamp(6px, 1vh, 10px);
}

/* 按钮区域 */
.button-section {
  text-align: center;
  padding-top: clamp(10px, 2vh, 20px);
  border-top: 2px solid rgba(139, 69, 19, 0.2);
  flex-shrink: 0;
}

.enter-system-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: clamp(8px, 1.5vw, 12px);
  padding: clamp(12px, 2vh, 15px) clamp(25px, 5vw, 40px);
  background: linear-gradient(135deg, #8B4513, #CD853F);
  color: white;
  border: none;
  border-radius: 50px;
  font-size: clamp(1rem, 2.2vw, 1.3rem);
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(139, 69, 19, 0.4);
  margin-bottom: clamp(5px, 1vh, 10px);
}

.enter-system-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 35px rgba(139, 69, 19, 0.5);
  background: linear-gradient(135deg, #A0522D, #DEB887);
}

.btn-text {
  font-size: clamp(0.9rem, 2vw, 1.2rem);
}

.btn-icon {
  font-size: clamp(1.1rem, 2.2vw, 1.4rem);
  transition: transform 0.3s ease;
}

.enter-system-btn:hover .btn-icon {
  transform: translateX(3px);
}

.btn-subtitle {
  color: #000;
  font-size: clamp(0.7rem, 1.6vw, 0.9rem);
  margin: 0;
  font-style: italic;
  line-height: 1.3;
}

.floating-icon {
  position: fixed;
  bottom: clamp(10px, 4vh, 20px);
  right: clamp(20px, 4vw, 30px);
  width: clamp(35px, 8vw, 40px);
  height: clamp(35px, 8vw, 40px);
  background: linear-gradient(135deg, #8B4513, #CD853F);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 8px 25px rgba(139, 69, 19, 0.4);
  transition: all 0.3s ease;
  z-index: 1000;
  color: white;
}

.floating-icon:hover {
  transform: scale(1.1);
  box-shadow: 0 12px 35px rgba(139, 69, 19, 0.5);
}

.floating-icon svg {
  width: clamp(20px, 4vw, 28px);
  height: clamp(20px, 4vw, 28px);
}

/* 响应式断点 */
@media (max-width: 1200px) {
  .content-grid {
    gap: clamp(10px, 2vw, 20px);
  }
}

@media (max-width: 900px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: clamp(15px, 2vh, 20px);
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    text-align: left;
  }

  .section-badge {
    align-self: flex-start;
  }
}

@media (max-width: 600px) {
  .introduction-content {
    width: 98vw;
    height: 100vh;
  }

  .content-wrapper {
    padding: clamp(8px, 1.5vh, 15px) clamp(8px, 2vw, 15px);
  }

  .card-content {
    padding: clamp(10px, 2vh, 15px);
  }

  .feature-list li {
    font-size: clamp(0.75rem, 3.5vw, 0.9rem);
  }
}

@media (max-height: 600px) {
  .introduction-content {
    height: 100vh;
  }

  .content-wrapper {
    gap: clamp(5px, 1vh, 10px);
  }

  .title-section {
    margin-bottom: 0;
  }

  .main-title {
    margin-bottom: clamp(5px, 1vh, 10px);
  }

  .card-content {
    padding: clamp(10px, 1.5vh, 15px);
  }

  .button-section {
    padding-top: clamp(5px, 1vh, 10px);
  }
}

/* 超小屏幕优化 */
@media (max-width: 400px) {
  .feature-list li {
    padding-left: 15px;
    font-size: 0.75rem;
  }

  .highlight-text {
    font-size: 0.85rem;
    padding: 8px;
  }
}

/* 滚动条样式 */
.card-content::-webkit-scrollbar,
.feature-list::-webkit-scrollbar {
  width: 4px;
}

.card-content::-webkit-scrollbar-track,
.feature-list::-webkit-scrollbar-track {
  background: rgba(139, 69, 19, 0.1);
  border-radius: 2px;
}

.card-content::-webkit-scrollbar-thumb,
.feature-list::-webkit-scrollbar-thumb {
  background: rgba(139, 69, 19, 0.4);
  border-radius: 2px;
}

.card-content::-webkit-scrollbar-thumb:hover,
.feature-list::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 69, 19, 0.6);
}


/* 播放按钮：固定在卡片右下角 */
.audio-play-btn {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  background: rgba(139, 69, 19, 0.8);
  color: #fff;
  border: none;
  border-radius: 16px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: background 0.3s ease;
}

.audio-play-btn:hover {
  background: rgba(160, 82, 45, 0.95);
}

/* 让 card-content 成为定位参照 */
.card-content {
  position: relative;
}
</style>

<!-- <div class="highlight-text">
                  中国共产党领导下的重要抗日武装力量，主要领导人李先念
                </div>
                <ul class="feature-list">
                  <li>由湖北、河南、安徽等地红军游击队组成</li>
                  <li>在敌后开展游击战争，有效打击日本侵略者</li>
                  <li>为华中地区发展奠定重要基础</li>
                  <li>英勇事迹永远铭记在中国人民心中</li>
                </ul> -->

<!-- <div class="features-grid">
                  <div class="feature-item">
                    <div class="feature-icon">👥</div>
                    <div class="feature-name">人物关系</div>
                  </div>
                  <div class="feature-item">
                    <div class="feature-icon">🎓</div>
                    <div class="feature-name">教育经历</div>
                  </div>
                  <div class="feature-item">
                    <div class="feature-icon">⚔️</div>
                    <div class="feature-name">战役战斗</div>
                  </div>
                  <div class="feature-item">
                    <div class="feature-icon">🤖</div>
                    <div class="feature-name">智能问答</div>
                  </div>
                </div> -->
