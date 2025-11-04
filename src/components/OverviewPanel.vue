<!-- src/components/OverviewPanel.vue -->
<template>
  <el-card class="overview-panel-card" shadow="never">
    <!-- 1. 全局统计区 (数据来自 props) -->
    <!-- <div class="global-stats">
      <div class="stat-item">
        <span class="stat-title">知识库实体总数</span>
        <span class="stat-value">{{ totalNodes }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-title">知识库关系总数</span>
        <span class="stat-value">{{ totalEdges }}</span>
      </div>
    </div>
    <el-divider v-if=" rawData.nodes.length > 0" /> -->

    <!-- 2. 分类概览区 (数据可视化升级) -->
    <div class="overview-container">
      <el-collapse v-model="activeCollapseNames">
        <!-- 节点概览 -->
        <el-collapse-item name="nodes">
          <template #title>
            <span class="collapse-title">当前查询节点 ({{ rawData.nodes.length }})</span>
          </template>
          <div 
            v-for="[category, items] in overview.nodes" 
            :key="category" 
            class="overview-item-pro"
            :class="{ active: editorTargetName === category }" 
            @click="emit('show-editor', { type: 'nodes', name: category, event: $event })"
            :title="`占比: ${((items.length / rawData.nodes.length) * 100).toFixed(1)}%`"
          >
            <component :is="iconMap[category] || iconMap.defaultNode" class="item-icon" :size="18" />
            <div class="item-label">
              {{ entityCategoryLabels[category] || category }} ({{ items.length }})
            </div>
            <el-progress 
              :percentage="(items.length / rawData.nodes.length) * 100" 
              :show-text="false"
              :stroke-width="6"
              class="item-progress"
            />
          </div>
        </el-collapse-item>

        <!-- 关系概览 -->
        <el-collapse-item name="edges" v-if="overview.edges.size > 0">
          <template #title>
            <span class="collapse-title">当前查询关系 ({{ rawData.links.length }})</span>
          </template>
           <div 
            v-for="[type, items] in overview.edges" 
            :key="type" 
            class="overview-item-pro"
            :class="{ active: editorTargetName === type }" 
            @click="emit('show-editor', { type: 'edges', name: type, event: $event })"
            :title="`占比: ${((items.length / rawData.links.length) * 100).toFixed(1)}%`"
          >
            <component :is="iconMap[type] || iconMap.defaultEdge" class="item-icon" :size="18" />
            <div class="item-label">
              {{ edgeTypeLabels[type] || type }} ({{ items.length }})
            </div>
            <el-progress 
              :percentage="(items.length / rawData.links.length) * 100" 
              :show-text="false"
              :stroke-width="6"
              class="item-progress"
            />
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
    
    <div v-if="!isLoading && rawData.nodes.length === 0" class="no-data-placeholder">
      <p>当前查询无结果</p>
      <p>请尝试其他查询</p>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed } from 'vue';
import { ElCard, ElCollapse, ElCollapseItem, ElDivider, ElProgress } from 'element-plus';
// 引入图标库
import { Users, Building, Swords, School, Link, GitMerge, UserCheck, Handshake, Briefcase, Box, Share2 } from 'lucide-vue-next';

// 定义 Props，增加 totalNodes 和 totalEdges
const props = defineProps({
  isLoading: Boolean,
  overview: { type: Object, required: true },
  rawData: { type: Object, required: true },
  editorTargetName: String,
  entityCategoryLabels: Object,
  edgeTypeLabels: Object,
  totalNodes: { type: Number, default: 0 }, // 新增：全局节点总数
  totalEdges: { type: Number, default: 0 }, // 新增：全局关系总数
});

const emit = defineEmits(['show-editor']);

// 默认展开
const activeCollapseNames = ref(['nodes', 'edges']);

// 图标映射
const iconMap = {
  Person: Users,
  Event: Building,
  教育和工作经历: Building,
  参加的战役战斗: Swords,

  Grandparent: Users,
  Parent: Users,
  Child: Users,
  革命事件: Building,
  战役事件: Swords,
  生平事件: School,

  PARTICIPATED_IN: UserCheck,
  COMRADE_WITH: GitMerge,
  PARTICIPATED_IN_ORG: Briefcase,
  POSSIBLE_SAME_AS: Swords,
  
  COLLEAGUE_OF: Handshake,
  ATTENDED: School,
  RELATED_TO: Link,
  FRIEND_OF: Handshake,
  WORKED_AT: Briefcase,
  defaultNode: Box,
  defaultEdge: Share2,
};
</script>

<style scoped>
.overview-panel-card {
  border: none;
  background-color: transparent;
}
:deep(.el-card__body) {
  padding: 5px 10px;
}

/* 全局统计区样式 */
.global-stats {
  display: flex;
  justify-content: space-around;
  text-align: center;
}
.stat-item {
  display: flex;
  flex-direction: column;
}
.stat-title {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 4px;
}
.stat-value {
  font-size: 26px;
  font-weight: 600;
  color: var(--text-primary);
}
.el-divider {
  margin: 16px 0;
}

/* 折叠面板样式 */
.collapse-title {
  font-weight: 500;
  font-size: 1em;
  color: var(--text-primary);
}
:deep(.el-collapse) {
  border: none;
}
:deep(.el-collapse-item__header), :deep(.el-collapse-item__wrap) {
  border: none;
}
:deep(.el-collapse-item__content) {
  padding-bottom: 5px;
}

/* 升级后的列表项样式 */
.overview-item-pro {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 8px;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.2s, color 0.2s;
}
.overview-item-pro:hover {
  background-color: var(--bg-hover);
}
.overview-item-pro.active {
  background-color: var(--accent-color-light);
  color: var(--accent-color);
  font-weight: 500;
}
.item-icon {
  color: var(--text-secondary);
  flex-shrink: 0;
}
.overview-item-pro.active .item-icon {
  color: var(--accent-color);
}
.item-label {
  flex-grow: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.9em;
}
.item-progress {
  width: 80px;
  flex-shrink: 0;
}
:deep(.el-progress-bar__inner) {
  background-color: var(--accent-color-light);
  transition: width 0.5s ease-in-out;
}
.overview-item-pro.active :deep(.el-progress-bar__inner) {
  background-color: var(--accent-color);
}

.no-data-placeholder {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 0;
  font-size: 0.9em;
}
.no-data-placeholder p {
  margin: 5px 0;
}
</style>
