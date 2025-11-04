<!-- src/App.vue -->
<template>
  <div id="app-container">
    <!-- Header 在最顶部,占据100%宽度 -->
    <header class="app-header">
      <MainHeader v-model:currentView="currentView" :theme="theme" @toggle-theme="toggleTheme" @run-query="runQuery"
        @set-force-label-show="value => forceLabelShow = value" />
    </header>

    <!-- 主体区域 -->
    <div class="app-body">
            <!-- 右侧边栏 -->
      <aside class="sidebar">
        <!-- 查询面板 -->
        <QueryPanel :is-loading="isLoading" @run-query="runQuery"  :initial-query="initialQuery" />

        <!-- 中间可滚动区域 -->
        <div class="scrollable-area">
          <OverviewPanel :is-loading="isLoading" :overview="overview" :raw-data="rawData"
            :editor-target-name="editor.targetName" :entity-category-labels="entityCategoryLabels"
            :edge-type-labels="edgeTypeLabels" :total-nodes="globalStats.totalNodes" :total-edges="globalStats.totalEdges"
            @show-editor="handleShowEditor" />
        </div>

        <!-- 底部固定区域 -->
        <div class="fixed-bottom">

          <!-- 条件渲染面板 -->
          <transition name="panel-fade" mode="out-in">
            <StatsPanel v-if="showStats" :total-nodes="globalStats.totalNodes"
          :total-person-nodes="globalStats.totalPersonNodes" :total-battle-nodes="globalStats.totalBattleNodes"
          :total-event-nodes="globalStats.totalEventNodes" :total-edges="globalStats.totalEdges"
          :total-comrade-edges="globalStats.totalComradeEdges"
          :total-participated-edges="globalStats.totalParticipatedEdges"
          :total-family-edges="globalStats.totalFamilyEdges"
          @run-query="runQuery"
          />
            <LayoutPanel v-else v-model:layout-config="layoutConfig" />
          </transition>

                    <!-- 切换按钮 -->
          <div class="toggle-button-container">
            <button class="toggle-button" @click="togglePanel" :title="showStats ? '切换到布局设置' : '切换到统计信息'">
              <!-- <BarChart3 v-if="!showStats" :size="12" /> -->
              <!-- <Layout v-else :size="12" /> -->
              <span>{{ showStats ? '切换到布局设置' : '切换到统计信息' }}</span>
            </button>
          </div>
        </div>
      </aside>
      <!-- 主内容区 -->
      <main class="main-content">
        <SystemIntroduction />

        <!-- 主内容区 -->
        <div v-if="!isLoading && currentView === 'graph'" class="graph-wrapper">
          <GraphChart :graph-data="filteredData" :style-config="styleConfig" :layout-config="layoutConfig"
            :force-label-show="forceLabelShow" :key="chartKey" :entityCategoryLabels="entityCategoryLabels"
            :edgeTypeLabels="edgeTypeLabels" @legend-select-changed="handleLegendChange"
            @query-related-nodes="handleRelatedNodesQuery" @node-select="handleNodeSelect" @edge-select="handleEdgeSelect"
            @clear-select="handleClearSelect" />

          <TimeSlider v-if="TimeSliderCurrentView" :min-date="minGraphDate" :max-date="maxGraphDate"
            :time-period-labels="timePeriodMap" v-model:selected-range="currentSelectedRange" />
        </div>
        <div v-if="!isLoading && currentView === 'table'" class="table-view">
          <TableView :table-data="tableData" />
        </div>

        <div v-if="!isLoading && currentView === 'ai'" class="ai-view">
          <AIChat @graph-query-result="handleAIGraphQuery" />
        </div>

        <div v-if="isLoading" class="loading-overlay">
          <p>加载中...</p>
        </div>

        <!-- 右边属性区 -->
        <div class="info-panel" v-if="currentView !== 'ai'">
          <InfoPanel :selected-item="selectedItem" :nodes="rawData.nodes" :entity-category-labels="entityCategoryLabels"
            :edge-type-labels="edgeTypeLabels" :property-labels="propertyLabels" />
        </div>
      </main>

    </div>

    <!-- 样式编辑器 -->
    <StyleEditor :visible="editor.visible" :position="editor.position" :target-type="editor.targetType"
      :target-name="editor.targetName" :config="activeEditorConfig" :available-props="availableLabelProps"
      :entityCategoryLabels="entityCategoryLabels" :edgeTypeLabels="edgeTypeLabels" @close="editor.visible = false"
      @update-style="handleStyleUpdate" @update-position="handleEditorMove" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useDark, useToggle } from '@vueuse/core';

// 导入子组件
import GraphChart from './components/GraphChart.vue';
import TableView from './components/TableView.vue';
import StyleEditor from './components/StyleEditor.vue';
import QueryPanel from './components/QueryPanel.vue';
import MainHeader from './components/MainHeader.vue';
import OverviewPanel from './components/OverviewPanel.vue';
import InfoPanel from './components/InfoPanel.vue';
import LayoutPanel from './components/LayoutPanel.vue';
import TimeSlider from './components/TimeSlider.vue';
import AIChat from './components/AIChat.vue';
import SystemIntroduction from './components/SystemIntroduction.vue'
import StatsPanel from './components/StatsPanel.vue';


// 导入工具函数
import { formatProperty } from './utils/formatters.js';

// 模式层定义
const entityCategoryLabels = {
  Person: '人物',
  前辈: '前辈',
  后代: '后代',
  后代二代: '后代二代',
  后代三代: '后代三代',
  Event: '事件',
  教育和工作经历: '教育和工作经历',
  参加的战役战斗: '参加的战役战斗',
  战役战斗: '战役战斗',
  // Battle: '重要战役',

  一代: '一代',
  后代: '后代',
  生平事件: '教育和工 作经历',
  革命事件: '教育和工作经历',
  战役事件: '参加的战役战斗',

};

// 控制左侧边栏的文本展示
const edgeTypeLabels = {
  PARTICIPATED_IN: '参与关系',
  COMRADE_WITH: '战友关系',
  COMRADE: '战友关系',
  FAMILY_WITH: '亲友关系',
  INVOLVED_IN_BATTLE: '参与关系',

  POSSIBLE_SAME_AS: '可能是同一人',
  INFERRED_PARTICIPATED_IN: '推断参与关系',
  INFERRED_COMRADE_WITH: '推断战友关系',
};

const propertyLabels = {
  aliases: '曾用名',
  gender: '性别',
  category: '类别',
  generation: '代际',
  new_fourth_army_fifth_division: '五师前辈',
  join_party_date: '入党时间',
  join_revolution_date: '参加革命时间',
  person_category: '人物类别',

  birth_date: '出生日期',
  death_date: '逝世日期',
  birth_place: '籍贯',


  probability: '概率',
  relationship: '关系',
  relationship_type: '关系类型',
  relationship_verb: '同事关系',
  time_period: '时期',
  time_value: '时间',
  time_start: '开始时间',
  time_end: '结束时间',
  location: '地点',
  organization: '组织',
  institution: '机构',
  position: '职位',
  event_name: '事件名称',
  relationship_description: '关系描述',
  relationship_to_event: '与事件的关系',
  is_family_member: '是否亲属',


  background: '背景',
  belligerents: '交战方',
  key_figures: '主要领导',
  impact: '影响',
  time_details: '时间',
  location_details: '地点',
  process_and_tactics: '战术',
  result: '结果',
  updated_at: '合并更新时间',
  new_fourth_army_battle: '五师战役',

  contribution: '贡献',
  role: '角色',

  battle_time:'作战时间',
  battle_area:'作战地区',
  our_forces:'我军参战部队',
  enemy_forces:'敌军参战部队',
  battle_process:'作战经过',
  battle_result:'作战结果',

  inference_confidence: '推理置信度',
  inference_metadata: '推理元数据',
  inference_reasoning: '推理过程',
  inference_source: '推理来源',

  battle_event_id: '战役事件ID',
  battle_event_name: '战役事件名称',
  source_type: '溯源类型',


  source_info: '溯源信息',
  source_text: '溯源文本',
  created_at: '创建时间',
};

// 定义时期-时间段映射表
// 注意：日期字符串必须是 Date 可解析的格式，例如 'YYYY-MM-DD'
const timePeriodMap = {
  '早期革命时期': { start: '1921-07-01', end: '1927-10-01' },  // 从中共一大开始
  '土地革命战争时期': { start: '1927-10-02', end: '1937-07-06' },  // 南昌起义后
  '抗日战争时期': { start: '1937-07-07', end: '1945-09-02' },  // 卢沟桥事变至日本投降
  '解放战争时期': { start: '1945-09-03', end: '1949-09-30' },  // 抗战结束至新中国成立前

  '新中国成立初期': { start: '1949-10-01', end: '1956-12-31' },  // 建国到三大改造完成
  '社会主义建设探索时期': { start: '1957-01-01', end: '1966-05-15' },  // 探索期至文革前
  '文化大革命时期': { start: '1966-05-16', end: '1976-10-06' },  // 文革开始至粉碎四人帮
  '改革开放初期': { start: '1976-10-07', end: '1992-01-01' },  // 改革开放准备阶段
  '改革开放深化时期': { start: '1992-01-02', end: '2012-11-14' },  // 南方谈话至十八大前
  '新时代': { start: '2012-11-15', end: '2025-01-01' },  // 十八大至今

  '中华人民共和国成立后': { start: '1949-10-01', end: '2025-12-31' }  // 完整建国后时期

};


// --- STATE MANAGEMENT --- 
const rawData = reactive({ nodes: [], links: [] });
const tableData = reactive({ headers: [], rows: [] });
const currentView = ref('graph');
const TimeSliderCurrentView = ref(false);
// const theme = ref('dark');
// const theme = ref('light');

// 控制底部面板显示的状态
const showStats = ref(true); // true 显示统计，false 显示布局
// 切换显示面板
const togglePanel = () => {
  showStats.value = !showStats.value;
};

const chartKey = ref(0);
const editor = reactive({ visible: false, position: { top: 0, left: 0 }, targetType: null, targetName: null });
const styleConfig = reactive({ nodes: {}, edges: {} });
const layoutConfig = reactive({ repulsion: 400, edgeLength: 200 });
const forceLabelShow = ref('on');
const isLoading = ref(true);
const selectedItem = ref(null);


const globalStats = reactive({
  totalNodes: 0,
  totalPersonNodes: 0,
  totalBattleNodes: 0,
  totalEventNodes: 0,
  totalEdges: 0,
  totalComradeEdges: 0,
  totalParticipatedEdges: 0,
  totalFamilyEdges: 0
});
// const initialQuery = "MATCH Path=(p:Person {name: '李先念'})-[*1]-(b:Person {name: '任质斌'} ) RETURN Path";
// const initialQuery = 'MATCH (n:Person {name:"刘少卿"})-[r]->(m) RETURN n,r,m LIMIT 150';
// const initialQuery = 'MATCH (n1:Person {name:"刘少卿"})-[r]->(m) RETURN n1, r, m, labels(m) as m_labels UNION ALL MATCH (n2:Person {name:"李先念"})-[r]->(m) RETURN n2 as n1, r, m, labels(m) as m_labels';
const initialQuery = 'MATCH (n:Person) RETURN n';

// 时间轴相关状态
// 时间轴长度默认值，会在数据加载后更新为图谱实际的时间范围
const minGraphDate = ref(new Date('1900-01-01'));
const maxGraphDate = ref(new Date('2025-12-31'));
// 时间轴默认选中值
const minCurrentSelected = ref(new Date('1941-01-01'));
const maxCurrentSelected = ref(new Date('1945-10-01'));
const currentSelectedRange = ref([minCurrentSelected.value, maxCurrentSelected.value]); // 默认选中全部范围

// --- API & DATA HANDLING ---
async function runQuery(cypher) {
  isLoading.value = true;
  editor.visible = false;
  handleClearSelect();
  try {
    console.log("查询Cypher语句:", cypher);
    const apiUrl = import.meta.env.VITE_API_URL;
    const response = await fetch(`${apiUrl}/graph`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cypher: cypher }),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    const result = await response.json();
    if (result.error) throw new Error(result.error);
    console.log("查询结果类型 result.type:", result.type);

    if (result.type === 'graph') {
      // —— 把 Event 节点 category 换成 properties.category ——
      // —— 把 Person 节点 category 换成 properties.generation ——
      const nodes = result.data.nodes || [];
      nodes.forEach(n => {
        // if ((n.category === 'Event') && n.properties?.category) {
        if ((n.category === 'Event' || n.category === 'Battle') && n.properties?.category) {
          n.category = n.properties.category;
        }
        if ((n.category === 'Person') && n.properties?.generation) {
          n.category = n.properties.generation;
        }
      });
      rawData.nodes = nodes;
      rawData.links = result.data.links || [];
      // ———————————————————————————————————————

      // rawData.nodes = result.data.nodes || [];
      // rawData.links = result.data.links || [];

      tableData.headers = [];
      tableData.rows = [];
      initializeStyleConfig();
      currentView.value = 'graph';

      //更新图谱时间范围
      updateGraphDateRange();
    } else {
      tableData.headers = result.data.headers || [];
      tableData.rows = result.data.rows || [];
      rawData.nodes = []; rawData.links = [];
      currentView.value = 'table';
    }
    console.log("查询结果:", result);

  } catch (e) {
    console.error("查询或处理数据时出错:", e);
    // alert(`查询失败: ${e.message}`);
  } finally {
    isLoading.value = false;
    chartKey.value++;
  }
}

function initializeStyleConfig() {

  const nodeCategories = [...new Set(rawData.nodes.map(n => n.category))];
  const edgeTypes = [...new Set(rawData.links.map(l => l.name))];


  const categoryColors = {
    'Person': '#F47F72',
    '前辈': '#F47F72',
    '后代': '#BDBADB',
    '子辈': '#E4BEBE',
    '孙辈': '#8DD1C6',
    'Event': '#F2C94C',
    '教育和工作经历': '#FBB463',
    '参加的战役战斗': '#80B1D3',
    '战役战斗': '#C0B1D3',

    'Grandparent': '#F47F72',
    'Organization': '#FBF8B4',

    'Battle': '#80B1D3',
    'EducationalInstitution': '#BDBADB',
    'Child': '#8DD1C6',
    'Parent': '#FBB463'
  };

  const defaultColors = ['#8be9fd', '#50fa7b', '#ff79c6', '#bd93f9', '#ff6e6e', '#f1fa8c'];
  const newNodesConfig = {};
  nodeCategories.forEach((cat, i) => {
    const color = categoryColors[cat] || defaultColors[i % defaultColors.length];
    newNodesConfig[cat] = { visible: true, color: color, size: 50, labelProp: 'name', labelFormatter: (n) => n.name };
  });

  styleConfig.nodes = newNodesConfig;
  const newEdgesConfig = {};

  edgeTypes.forEach((type) => {

    newEdgesConfig[type] = {
      visible: true,
      color: '#6272a4',
      width: 1.5,
      labelProp: 'dynamic', // 表示动态选择
      labelFormatter: (l) => {
        // 按优先级选择第一个存在的属性
        return l.properties.relationship ||
          l.properties.relationship_type ||
          l.properties.relationship_to_event ||
          l.properties.relationship_verb ||
          l.properties.role ||
          l.properties.type;
      }
    };


  });
  styleConfig.edges = newEdgesConfig;
}

// 获取数据库全局统计数据的函数
async function fetchGlobalStats() {
  try {
    const apiUrl = import.meta.env.VITE_API_URL;
    const [nodesResponse, nodesPersonResponse, nodesBattleResponse, nodesEventResponse, edgesResponse, edgesComradeResponse, edgesParticipatedResponse, edgesFamilyResponse] = await Promise.all([
      fetch(`${apiUrl}/graph`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cypher: 'MATCH (n) RETURN count(n) AS total' }),
      }),
      fetch(`${apiUrl}/graph`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cypher: 'MATCH (n:Person) RETURN count(n) AS total' }),
      }),
      fetch(`${apiUrl}/graph`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // body: JSON.stringify({ cypher: 'MATCH (n:Event {category:"参加的战役战斗"}) RETURN count(n) AS total' }),
        body: JSON.stringify({ cypher: 'MATCH (n:Event) WHERE n.category IN ["参加的战役战斗", "战役战斗"] RETURN count(n) AS total' }),
      }),
      fetch(`${apiUrl}/graph`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cypher: 'MATCH (n:Event {category:"教育和工作经历"}) RETURN count(n) AS total' }),
      }),
      fetch(`${apiUrl}/graph`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cypher: 'MATCH ()-[r]->() RETURN count(r) AS total' }),
      }),
      fetch(`${apiUrl}/graph`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cypher: 'MATCH ()-[r:COMRADE_WITH|COMRADE|INFERRED_COMRADE_WITH]->() RETURN count(r) AS total' }),
      }),
      fetch(`${apiUrl}/graph`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cypher: 'MATCH ()-[r:PARTICIPATED_IN|INVOLVED_IN_BATTLE|INFERRED_PARTICIPATED_IN]->() RETURN count(r) AS total' }),
      }),
      fetch(`${apiUrl}/graph`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cypher: 'MATCH ()-[r:FAMILY_WITH]->() RETURN count(r) AS total' }),
      })
    ]);

    if (!nodesResponse.ok || !nodesPersonResponse.ok || !nodesBattleResponse.ok || !nodesEventResponse.ok || !edgesResponse.ok || !edgesComradeResponse.ok || !edgesParticipatedResponse.ok || !edgesFamilyResponse.ok) {
      throw new Error('Failed to fetch global stats');
    }

    const nodesResult = await nodesResponse.json();
    const nodesPersonResult = await nodesPersonResponse.json();
    const nodesBattleResult = await nodesBattleResponse.json();
    const nodesEventResult = await nodesEventResponse.json();
    const edgesResult = await edgesResponse.json();
    const edgesComradeResult = await edgesComradeResponse.json();
    const edgesParticipatedResult = await edgesParticipatedResponse.json();
    const edgesFamilyResult = await edgesFamilyResponse.json();

    // 从对象数组的第一项中，通过属性名 'total' 来获取计数值
    globalStats.totalNodes = nodesResult.data?.rows[0]?.total || 0;
    globalStats.totalPersonNodes = nodesPersonResult.data?.rows[0]?.total || 0;
    globalStats.totalBattleNodes = nodesBattleResult.data?.rows[0]?.total || 0;
    globalStats.totalEventNodes = nodesEventResult.data?.rows[0]?.total || 0;

    globalStats.totalEdges = edgesResult.data?.rows[0]?.total || 0;
    globalStats.totalComradeEdges = edgesComradeResult.data?.rows[0]?.total || 0;
    globalStats.totalParticipatedEdges = edgesParticipatedResult.data?.rows[0]?.total || 0;
    globalStats.totalFamilyEdges = edgesFamilyResult.data?.rows[0]?.total || 0;



  } catch (e) {
    console.error("获取全局统计数据失败:", e);
    globalStats.totalNodes = 0;
    globalStats.totalPersonNodes = 0;
    globalStats.totalBattleNodes = 0;
    globalStats.totalEventNodes = 0;
    globalStats.totalEdges = 0;
    globalStats.totalComradeEdges = 0;
    globalStats.totalParticipatedEdges = 0;
    globalStats.totalFamilyEdges = 0;
  }
}

// // 辅助函数：将关系的各种时间属性规范化为 [startDate: Date, endDate: Date]
// function normalizeLinkTime(link) {
//   const properties = link.properties || {};
//   let startDate = null;
//   let endDate = null;

//   if (properties.time_start && properties.time_end) {
//     startDate = new Date(properties.time_start);
//     endDate = new Date(properties.time_end);
//   } else if (properties.time_value) {
//     // 处理 'YYYY-MM' 格式，使其覆盖整个月
//     const timeVal = String(properties.time_value);
//     if (timeVal.match(/^\d{4}-\d{2}$/)) { // 匹配 'YYYY-MM'
//       startDate = new Date(timeVal + '-01');
//       endDate = new Date(startDate.getFullYear(), startDate.getMonth() + 1, 0); // 月份的最后一天
//     } else {
//       startDate = new Date(timeVal);
//       endDate = new Date(timeVal); // 对于精确到天的日期，视为一个点
//     }
//   } else if (properties.time_period && timePeriodMap[properties.time_period]) {
//     const period = timePeriodMap[properties.time_period];
//     startDate = new Date(period.start);
//     endDate = new Date(period.end);
//   }

//   // 确保日期有效，如果解析失败则设为 null
//   startDate = isNaN(startDate?.getTime()) ? null : startDate;
//   endDate = isNaN(endDate?.getTime()) ? null : endDate;

//   // 如果只有开始日期没有结束日期，可以默认一个结束日期（例如，开始日期 + 1天）
//   if (startDate && !endDate) {
//     endDate = new Date(startDate);
//     endDate.setDate(startDate.getDate() + 1); // 默认一天跨度
//   }
//   // 如果只有结束日期没有开始日期，同理
//   if (endDate && !startDate) {
//     startDate = new Date(endDate);
//     startDate.setDate(endDate.getDate() - 1); // 默认一天跨度
//   }

//   return [startDate, endDate];
// }
// 辅助函数：将关系的各种时间属性规范化为 [startDate: Date, endDate: Date]
function normalizeLinkTime(link) {
  const properties = link.properties || {};
  let dateString = properties.time_start || properties.time_end || properties.time_value;
  let startDate = null;
  let endDate = null;

  // --- 新增：中文日期解析逻辑 ---
  if (dateString) {
    // 匹配 "YYYY年M月" 或 "YYYY年" 格式
    const matchYearMonth = String(dateString).match(/(\d{4})年(\d{1,2})月/);
    const matchYear = String(dateString).match(/(\d{4})年/);

    if (matchYearMonth) {
      // 匹配到年和月 (如 "1943年5月")
      const year = parseInt(matchYearMonth[1]);
      const month = parseInt(matchYearMonth[2]);
      // 创建月份的第一天作为开始日期
      startDate = new Date(year, month - 1, 1);
      // 创建月份的最后一天作为结束日期
      endDate = new Date(year, month, 0); 
    } else if (matchYear) {
      // 匹配到年 (如 "1943年")
      const year = parseInt(matchYear[1]);
      startDate = new Date(year, 0, 1); // 年初
      endDate = new Date(year, 11, 31); // 年底
    }
    // 如果是 time_start 和 time_end 两个属性，需要分别处理以覆盖时间段
    if (properties.time_start && properties.time_end) {
        // 由于 time_start/time_end 可能是中文日期，使用上面的逻辑分别解析
        const startMatch = String(properties.time_start).match(/(\d{4})年(\d{1,2})月?/);
        const endMatch = String(properties.time_end).match(/(\d{4})年(\d{1,2})月?/);
        
        // 尝试解析 time_start
        if (startMatch) {
            const year = parseInt(startMatch[1]);
            const month = startMatch[2] ? parseInt(startMatch[2]) : 1;
            startDate = new Date(year, month - 1, 1);
        }

        // 尝试解析 time_end
        if (endMatch) {
            const year = parseInt(endMatch[1]);
            // 如果有月，找到该月最后一天；如果没有月，找到年底
            const month = endMatch[2] ? parseInt(endMatch[2]) : 12;
            endDate = endMatch[2] 
                      ? new Date(year, month, 0) // 月份的最后一天
                      : new Date(year, 11, 31); // 年底
        }
    }
  } 
  // --- 原始逻辑：处理标准格式 time_value/time_period ---
  
  if (!startDate && !endDate) {
      // time_start/time_end/time_value 如果是标准格式日期字符串 (如 'YYYY-MM-DD')
      if (properties.time_start && properties.time_end) {
        startDate = new Date(properties.time_start);
        endDate = new Date(properties.time_end);
      } else if (properties.time_value) {
        // 处理 'YYYY-MM' 格式，使其覆盖整个月
        const timeVal = String(properties.time_value);
        if (timeVal.match(/^\d{4}-\d{2}$/)) { // 匹配 'YYYY-MM'
          startDate = new Date(timeVal + '-01');
          endDate = new Date(startDate.getFullYear(), startDate.getMonth() + 1, 0); // 月份的最后一天
        } else {
          startDate = new Date(timeVal);
          endDate = new Date(timeVal); // 对于精确到天的日期，视为一个点
        }
      } else if (properties.time_period && timePeriodMap[properties.time_period]) {
        const period = timePeriodMap[properties.time_period];
        startDate = new Date(period.start);
        endDate = new Date(period.end);
      }
  }


  // 确保日期有效，如果解析失败则设为 null
  startDate = isNaN(startDate?.getTime()) ? null : startDate;
  endDate = isNaN(endDate?.getTime()) ? null : endDate;

  // 如果只有开始日期没有结束日期，可以默认一个结束日期（例如，开始日期 + 1天）
  if (startDate && !endDate) {
    endDate = new Date(startDate);
    endDate.setDate(startDate.getDate() + 1); // 默认一天跨度
  }
  // 如果只有结束日期没有开始日期，同理
  if (endDate && !startDate) {
    startDate = new Date(endDate);
    startDate.setDate(endDate.getDate() - 1); // 默认一天跨度
  }
  
  // 最终如果仍无法解析，返回 null/null
  if (!startDate && !endDate) {
     console.warn("无法解析时间属性:", properties);
  }

  return [startDate, endDate];
}

// 更新图谱的时间范围
function updateGraphDateRange() {
  let tempMinDate = null;
  let tempMaxDate = null;

  rawData.links.forEach(link => {
    const [linkStart, linkEnd] = normalizeLinkTime(link);
    if (linkStart && (!tempMinDate || linkStart < tempMinDate)) {
      tempMinDate = linkStart;
    }
    if (linkEnd && (!tempMaxDate || linkEnd > tempMaxDate)) {
      tempMaxDate = linkEnd;
    }
  });

  // 如果图谱中没有任何带时间属性的链接，可以设置一个默认的宽泛时间范围
  if (tempMinDate && tempMaxDate) {
    minGraphDate.value = tempMinDate;
    maxGraphDate.value = tempMaxDate;
  } else {
    minGraphDate.value = new Date('1941-01-01');
    maxGraphDate.value = new Date('1945-10-01');
  }
  //初始选中范围
  currentSelectedRange.value = [minGraphDate.value, maxGraphDate.value];
}

// --- UI INTERACTION HANDLERS ---
// 新的事件处理器，用于响应 OverviewPanel 的事件
function handleShowEditor({ type, name, event }) {
  const rect = event.currentTarget.getBoundingClientRect();
  editor.targetType = type;
  editor.targetName = name;
  editor.position = { top: rect.top, left: rect.right + 10 };
  editor.visible = true;
}

function handleStyleUpdate({ key, value }) {
  if (!editor.targetName) return;
  const config = styleConfig[editor.targetType]?.[editor.targetName];
  if (config) {
    config[key] = value;
    if (key === 'labelProp') {
      if (editor.targetType === 'nodes') {
        config.labelFormatter = (node) => node.properties[value] || node[value] || '';
      } else {
        config.labelFormatter = (link) => (value === 'none') ? '' : link.properties[value] || '';
      }
    }
  }
}

function handleEditorMove(newPosition) {
  editor.position.top = newPosition.top;
  editor.position.left = newPosition.left;
}

function handleLegendChange(selected) {
  Object.keys(selected).forEach(categoryName => {
    if (styleConfig.nodes[categoryName]) {
      styleConfig.nodes[categoryName].visible = selected[categoryName];
    }
  });
}

async function handleRelatedNodesQuery(nodeName) {
  isLoading.value = true;
  try {
    const cypher = `MATCH p= (n)-[*1]-(x) WHERE n.name='${nodeName}' RETURN p`;
    console.log("查询关联节点的Cypher语句:", cypher);
    runQuery(cypher);
  } catch (e) {
    console.error("查询关联节点时出错:", e);
    alert(`查询失败: ${e.message}`);
  } finally {
    isLoading.value = false;
  }
}

// 处理节点被选中的事件
function handleNodeSelect(nodeData) {
  if (!nodeData || !nodeData.id) return;
  const fullNode = rawData.nodes.find(n => n.id === nodeData.id);
  if (!fullNode) return;

  // 如果再次点击同一个节点，则取消选中（可选功能，体验更好）
  if (selectedItem.value?.data?.id === fullNode.id) {
    selectedItem.value = null;
  } else {
    selectedItem.value = {
      dataType: 'node',
      data: { ...fullNode, properties: fullNode.properties || {} }
    };
  }
}

// 处理关系被选中的事件
function handleEdgeSelect(edgeData) {
  if (!edgeData || !edgeData.source || !edgeData.target) return;
  const fullLink = rawData.links.find(l =>
    l.source === edgeData.source &&
    l.target === edgeData.target &&
    l.name === edgeData.name &&
    l.properties.event_name === edgeData.properties.event_name
  );
  if (!fullLink) return;

  if (selectedItem.value?.dataType === 'edge') {

  } else {
    selectedItem.value = {
      dataType: 'edge',
      data: { ...fullLink, properties: fullLink.properties || {} }
    };
  }

}

// 处理清空选中的事件（当点击图表空白处时）
function handleClearSelect() {
  selectedItem.value = null;
}


// 处理AI图谱查询结果
function handleAIGraphQuery(result) {
  if (result.type === 'graph' && result.data) {
    // 处理Event节点category
    const nodes = result.data.nodes || [];
    nodes.forEach(n => {
      if (n.category === 'Event' && n.properties?.category) {
        n.category = n.properties.category;
      }
    });

    rawData.nodes = nodes;
    rawData.links = result.data.links || [];

    tableData.headers = [];
    tableData.rows = [];
    initializeStyleConfig();

    // 切换到图谱视图
    currentView.value = 'graph';

    // 更新图谱时间范围
    updateGraphDateRange();

    // 刷新图表
    chartKey.value++;
  }
}
// --- COMPUTED PROPERTIES ---

const theme = computed(() => isDark.value ? 'dark' : 'light')


const overview = computed(() => {
  const nodes = new Map();
  if (rawData.nodes) {
    rawData.nodes.forEach(n => { if (!nodes.has(n.category)) nodes.set(n.category, []); nodes.get(n.category).push(n); });
  }
  const edges = new Map();
  if (rawData.links) {
    rawData.links.forEach(l => { if (!edges.has(l.name)) edges.set(l.name, []); edges.get(l.name).push(l); });
  }
  return { nodes, edges };
});

const activeEditorConfig = computed(() => {
  if (!editor.targetName || !styleConfig[editor.targetType] || !styleConfig[editor.targetType][editor.targetName]) return {};
  return styleConfig[editor.targetType][editor.targetName];
});

const availableLabelProps = computed(() => {
  if (!editor.targetName) return [];
  const { targetType, targetName } = editor;
  if (targetType === 'nodes') {
    const sampleNode = rawData.nodes?.find(n => n.category === targetName);
    if (!sampleNode) return ['name', 'id', 'category'];
    return [...new Set(['name', 'id', 'category', ...Object.keys(sampleNode.properties || {})])];
  } else {
    const sampleLink = rawData.links?.find(l => l.name === targetName);
    if (!sampleLink) return ['type'];
    return [...new Set(['type', ...Object.keys(sampleLink.properties || {})])];
  }
});



const filteredData = computed(() => {
  // 基础检查：如果没有任何节点或样式配置，直接返回空数据。
  if (!rawData.nodes || rawData.nodes.length === 0 || !styleConfig.nodes || Object.keys(styleConfig.nodes).length === 0) {
    return { nodes: [], links: [] };
  }


  // 检查是否存在含有时间属性的链接，并且时间属性多于一种
  const hasTimeBasedLinks = (() => {
    const uniqueTimeValues = new Set(); // 存储所有时间值（自动去重）
    let hasTime = false; // 是否至少有一个链接包含时间属性

    // 遍历所有链接
    rawData.links.forEach((link) => {
      const properties = link.properties || {};

      // 检查并记录时间属性
      if (properties.time_start != null) {
        uniqueTimeValues.add(properties.time_start);
        hasTime = true;
      }
      if (properties.time_end != null) {
        uniqueTimeValues.add(properties.time_end);
        hasTime = true;
      }
      if (properties.time_value != null) {
        uniqueTimeValues.add(properties.time_value);
        hasTime = true;
      }
      if (properties.time_period != null) {
        uniqueTimeValues.add(properties.time_period);
        hasTime = true;
      }
    });

    // console.log('uniqueTimeValues:', uniqueTimeValues);

    // 返回：是否有时间属性 && 去重后的时间值数量 > 1
    return hasTime && uniqueTimeValues.size > 1;
  })();


  // 定义基础的节点可见性过滤
  const visibleNodeCategories = Object.keys(styleConfig.nodes).filter(cat => styleConfig.nodes[cat]?.visible);

  let finalNodes = [];
  let finalLinks = [];

  if (hasTimeBasedLinks) {
    // 场景1：存在包含多个时间属性的链接，启用时间过滤器
    TimeSliderCurrentView.value = true;
    const [rangeStart, rangeEnd] = currentSelectedRange.value;

    // 1. 分离链接：有时间属性和无时间属性
    const timeBasedLinks = [];
    const nonTimeBasedLinks = [];

    rawData.links.forEach(link => {
      const properties = link.properties || {};
      // 判断是否有任何时间属性
      if (properties.time_start || properties.time_end || properties.time_value || properties.time_period) {
        timeBasedLinks.push(link);
      } else {
        nonTimeBasedLinks.push(link);
      }
    });

    // 2. 根据时间范围过滤有时间属性的链接
    const filteredTimeBasedLinks = timeBasedLinks.filter(link => {
      const [linkStart, linkEnd] = normalizeLinkTime(link);
      // 判断时间段重叠
      return (linkStart <= rangeEnd) && (linkEnd >= rangeStart);
    });

    // 3. 将过滤后的有时间属性的链接和所有无时间属性的链接合并
    const combinedLinks = [...filteredTimeBasedLinks, ...nonTimeBasedLinks];

    // 4. 根据合并后的链接，确定最终可见的节点ID
    const visibleNodeIdsAfterTimeFilter = new Set();
    combinedLinks.forEach(link => {
      visibleNodeIdsAfterTimeFilter.add(link.source);
      visibleNodeIdsAfterTimeFilter.add(link.target);
    });

    // 5. 过滤节点：只保留在 visibleNodeIdsAfterTimeFilter 中，并应用样式过滤
    finalNodes = rawData.nodes.filter(n =>
      visibleNodeIdsAfterTimeFilter.has(n.id) &&
      visibleNodeCategories.includes(n.category)
    );

    const finalNodeIds = new Set(finalNodes.map(n => n.id));

    // 6. 过滤链接：只保留连接最终可见节点的链接，并应用样式配置可见性
    finalLinks = combinedLinks.filter(l =>
      finalNodeIds.has(l.source) &&
      finalNodeIds.has(l.target) &&
      (styleConfig.edges[l.name]?.visible !== false)
    );
  }

  else {
    // 场景2：不存在时间属性的链接（或链接数量为0），只进行样式过滤

    TimeSliderCurrentView.value = false;
    // 1. 过滤节点：仅根据样式配置进行过滤
    finalNodes = rawData.nodes.filter(n => visibleNodeCategories.includes(n.category));

    const finalNodeIds = new Set(finalNodes.map(n => n.id));

    // 2. 过滤链接：保留所有连接最终可见节点的原始链接
    finalLinks = rawData.links.filter(l =>
      finalNodeIds.has(l.source) &&
      finalNodeIds.has(l.target) &&
      (styleConfig.edges[l.name]?.visible !== false)
    );

  }

  console.log('filteredData:', { nodes: finalNodes, links: finalLinks });
  return { nodes: finalNodes, links: finalLinks };
});


// const isDark = useDark();
// const toggleDark = useToggle(isDark);

// function toggleTheme() {
//   toggleDark();
//   theme.value = theme.value === 'dark' ? 'light' : 'dark';
//   document.body.className = theme.value + '-theme';
//   chartKey.value++;
// }

// onMounted(() => {
//   document.body.className = theme.value + '-theme';
//   runQuery(initialQuery);
//   fetchGlobalStats();
//   updateGraphDateRange();
// });




const isDark = useDark()
const toggleDark = useToggle(isDark)



function toggleTheme() {
  toggleDark()
  document.body.className = theme.value + '-theme'
  chartKey.value++
}

onMounted(() => {
  document.body.className = theme.value + '-theme'
  runQuery(initialQuery)
  fetchGlobalStats()
  updateGraphDateRange()
})


</script>




<style scoped>
/* 整体容器改为纵向布局 */
#app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

/* Header 区域 - 占据100%宽度 */
.app-header {
  width: 100%;
  flex-shrink: 0;
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  z-index: 100;
}

/* 主体区域 - 横向布局 */
.app-body {
  display: flex;
  flex: 1;
  overflow: hidden;
  flex-direction: row;
}

/* 主内容区 - 占据剩余空间 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 右侧边栏 */
.sidebar {
  width: 288px;
  flex-shrink: 0;
  background-color: var(--bg-secondary);
  border-right: 2px solid var(--border-color);
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.scrollable-area {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.fixed-bottom {
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
}

.toggle-button-container {
  padding: 4px;
}

.toggle-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 4px 6px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-button:hover {
  background-color: var(--bg-hover);
}

/* 面板切换动画 */
.panel-fade-enter-active,
.panel-fade-leave-active {
  transition: opacity 0.2s;
}

.panel-fade-enter-from,
.panel-fade-leave-to {
  opacity: 0;
}

.graph-wrapper,
.table-view,
.ai-view {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.table-view {
  padding: 24px;
}

.ai-view {
  padding: 16px;
}

.loading-overlay {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.5rem;
  color: var(--text-muted);
}

/* 信息面板 */
.info-panel {
  position: fixed;
  top: 80px; 
  right: 10px; 
  width: 350px;
}
</style>