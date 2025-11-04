<template>
  <div class="global-stats">
    <!-- 实体统计项 -->
    <!-- 人物查询：MATCH (n:Person) RETURN n -->
    <div class="stat-item clickable" @click="handleStatClick(QUERIES.person)">
      <div class="text-content">
        <span class="stat-title">
          <Users class="stat-icon" :size="14" stroke-width="2" />人物
        </span>
        <span class="stat-value">{{ totalPersonNodes }}
          <span class="stat-unit">个</span>
        </span>
      </div>
    </div>

    <!-- 经历查询（假设为所有 Event 节点）：MATCH (n:Event) RETURN n -->
    <div class="stat-item clickable" @click="handleStatClick(QUERIES.event)">
      <div class="text-content">
        <span class="stat-title">
          <Building class="stat-icon" :size="14" stroke-width="2" />
          经历
        </span>
        <span class="stat-value">{{ totalEventNodes }}
          <span class="stat-unit">段</span>
        </span>
      </div>
    </div>

    <!-- 战役战斗查询：MATCH (n:Event {category:"参加的战役战斗"}) RETURN n -->
    <div class="stat-item clickable" @click="handleStatClick(QUERIES.battle)">
      <div class="text-content">
        <span class="stat-title">
          <Swords class="stat-icon" :size="14" stroke-width="2" />
          战役战斗
        </span>
        <span class="stat-value">{{ totalBattleNodes }}
          <span class="stat-unit">场</span>
        </span>
      </div>
    </div>

    <!-- 关系统计项 -->
    <!-- 战友关系查询：MATCH (n1)-[r:COMRADE_WITH|COMRADE]->(n2) RETURN r,n1,n2 LIMIT 250 -->
    <div class="stat-item clickable" @click="handleStatClick(QUERIES.comrade)">
      <div class="text-content relationship-count">
        <span class="stat-title">
          <Share2 class="stat-icon" :size="14" stroke-width="2" />
          战友关系
        </span>
        <span class="stat-value">{{ totalComradeEdges }}
          <span class="stat-unit">个</span>
        </span>
      </div>
    </div>

    <!-- 参与关系查询（假设关系类型为 PARTICIPATED）：MATCH (n1)-[r:PARTICIPATED]->(n2) RETURN r,n1,n2 LIMIT 250 -->
    <div class="stat-item clickable" @click="handleStatClick(QUERIES.participated)">
      <div class="text-content relationship-count">
        <span class="stat-title">
          <Share2 class="stat-icon" :size="14" stroke-width="2" />
          参与关系
        </span>
        <span class="stat-value">{{ totalParticipatedEdges }}
          <span class="stat-unit">个</span>
        </span>
      </div>
    </div>

    <!-- 亲友关系查询：MATCH (n1)-[r:FAMILY_WITH]->(n2) RETURN r,n1,n2 -->
    <div class="stat-item clickable" @click="handleStatClick(QUERIES.family)">
      <div class="text-content relationship-count">
        <span class="stat-title">
          <Share2 class="stat-icon" :size="14" stroke-width="2" />
          亲友关系
        </span>
        <span class="stat-value">{{ totalFamilyEdges }}
          <span class="stat-unit">个</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Share2, Users, Swords, Building } from 'lucide-vue-next';
import { defineProps, defineEmits } from 'vue'; // 确保导入 defineEmits

// 定义组件可发出的事件，包括 'runQuery'，它将携带 Cypher 查询字符串
const emit = defineEmits(['runQuery']);

// 定义每个统计项对应的 Cypher 查询
const QUERIES = {
  person: 'MATCH (n:Person) RETURN n',
  // 战役战斗
  // battle: 'MATCH (n:Event {category:"参加的战役战斗"}) RETURN n',
  battle: 'MATCH (n:Event) WHERE n.category IN ["参加的战役战斗", "战役战斗"] RETURN n',
  // 经历（假设为所有 Event 节点）
  event: 'MATCH (n:Event) RETURN n',
  // 亲友关系
  family: 'MATCH (n1)-[r:FAMILY_WITH]->(n2) RETURN r,n1,n2',
  // 战友关系
  comrade: 'MATCH (n1)-[r:COMRADE_WITH|COMRADE]->(n2) RETURN r,n1,n2 LIMIT 250',
  // 参与关系（假设关系类型为 PARTICIPATED）
  participated: 'MATCH (n1)-[r:PARTICIPATED]->(n2) RETURN r,n1,n2 LIMIT 250',
};

/**
 * 处理统计项点击事件，发出 runQuery 事件，并将 Cypher 语句作为参数传递给父组件。
 * @param {string} query 要执行的 Cypher 语句
 */
const handleStatClick = (query) => {
  console.log(`Stat clicked. Emitting query: ${query}`);
  emit('runQuery', query);
};

defineProps({
  totalPersonNodes: { type: Number, default: 0 },
  totalBattleNodes: { type: Number, default: 0 },
  totalEventNodes: { type: Number, default: 0 },
  totalComradeEdges: { type: Number, default: 0 },
  totalParticipatedEdges: { type: Number, default: 0 },
  totalFamilyEdges: { type: Number, default: 0 },
});
</script>

<style scoped>
/* 根容器：设置合理的间隙和换行，确保高度可控 */
.global-stats {
  display: flex;
  justify-content: space-between;
  gap: 6px 6px;
  padding: 5px;
  flex-wrap: wrap;
  /* 确保不占用过多垂直空间 */
  max-height: 180px; 
}

/* 核心：单个统计卡片的样式 */
.stat-item {
  max-width: 27%;
  flex: 0 0 calc(33.333% - 7px);
  display: flex;
  align-items: center;
  padding: 6px 6px;
  margin: 0;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(8px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

/* 添加可点击样式 */
.stat-item.clickable {
  cursor: pointer;
}

/* 鼠标悬停时的交互效果 */
.stat-item.clickable:hover {
  transform: translateY(-2px);
  border-color: rgba(var(--accent-color-rgb), 0.6);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1), 0 0 10px rgba(var(--accent-color-rgb), 0.2);
}

/* 鼠标按下时的点击反馈 */
.stat-item.clickable:active {
  transform: translateY(0);
  opacity: 0.9;
}

/* 图标样式 */
.stat-icon {
  color: var(--accent-color);
  margin-right: 4px;
  flex-shrink: 0;
}

/* 文字内容容器 - 统一使用 column 布局以更好地控制垂直空间 */
.text-content {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 100%;
}

/* 标题样式 */
.stat-title {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 2px;
  white-space: nowrap;
  display: flex;
  align-items: center;
}

/* 数值样式 */
.stat-value {
  font-size: 20px;
  font-weight: 400;
  color: var(--text-primary);
  line-height: 1;
  display: flex;
  align-items: flex-end;
}

/* 单位样式 */
.stat-unit {
  font-size: 10px;
  font-weight: 500;
  color: var(--text-muted);
  margin-left: 4px;
  padding-bottom: 2px;
}
</style>