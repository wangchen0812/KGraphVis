// 日期格式化
export const formatDate = (dateStr) => {
  if (!dateStr) return '';
  
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr;
    
    // 检查是否包含时间信息
    const hasTime = dateStr.includes('T');
    
    if (hasTime) {
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    } else {
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    }
  } catch {
    return dateStr;
  }
};

// 修改溯源信息格式化函数，优化显示效果
// const formatSourceInfo = (sourceInfo) => {
//   try {
//     const info = typeof sourceInfo === 'string' ? JSON.parse(sourceInfo) : sourceInfo;
    
//     // 处理多来源格式
//     if (typeof info === 'object' && !info.source_file && !info.source_type) {
//       const sources = [];
//       const circleNumbers = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩'];
//       let index = 0;
      
//       for (const key in info) {
//         if (info.hasOwnProperty(key) && info[key] && typeof info[key] === 'object') {
//           const source = info[key];
//           const sourceFile = source.source_file || '';
//           const sourceType = source.source_type ? `-${source.source_type}` : '';
//           if (sourceFile) {
//             const number = circleNumbers[index] || `[${index+1}]`;
//             sources.push(`${number} ${sourceFile}${sourceType}`);
//             index++;
//           }
//         }
//       }
//       return sources.join('\n');
//     }
//     // 处理单来源格式
//     else {
//       const sourceFile = info.source_file ? `${info.source_file}` : '';
//       const sourceType = info.source_type ? `-${info.source_type}` : '';
//       return [sourceFile, sourceType].filter(item => item).join('\n');
//     }
//   } catch (e) {
//     return typeof sourceInfo === 'string' ? sourceInfo : '';
//   }
// };



// 格式化溯源信息
// 该函数将输入的 sourceInfo 格式化为树形结构或字符串
// 支持两种格式：
// 1. 数组格式，包含多个来源信息
// 2. 单个对象格式，包含单一来源信息
// 返回值为一个对象，包含 value（格式化后的值）和 isTree（是否为树形结构）
export const formatSourceInfo = (sourceInfo) => {
  // 1. 安全解析输入数据，确保其为 JavaScript 对象或数组
  let data;
  try {
    data = typeof sourceInfo === 'string' ? JSON.parse(sourceInfo) : sourceInfo;
  } catch (e) {
    // 解析失败，返回原始值
    return {
      value: sourceInfo,
      isTree: false,
    };
  }

  // 2. 判断是否为数组格式
  if (Array.isArray(data) && data.length > 0) {
    const treeData = [];

    data.forEach((item) => {
      if (!item) {
        return;
      }

      const sourceNode = {
        label: '未知来源',
        children: [],
      };

      const detailsChildren = [];

      // --- 核心逻辑：根据 item 的结构判断是人物还是战役 ---
      
      // 检查 item 是否包含 source_info 字段，这是人物格式的特征
      const isPersonItem = item.source_info && item.source_info.source_file;
      
      // 检查 item 是否包含 source_file 和 category，这是战役格式的特征
      const isBattleItem = item.source_file && item.category === '战役事件';

      if (isPersonItem) {
        // --- 人物处理逻辑 ---
        sourceNode.label = `${item.source_info.source_file}${item.source_info.source_type ? `-${item.source_info.source_type}` : ''}`;

        if (item.name) detailsChildren.push({ label: `◽姓名：${item.name}` });
        if (item.aliases && item.aliases.length > 0) detailsChildren.push({ label: `◽别名：${item.aliases.join(', ')}` });
        if (item.gender) detailsChildren.push({ label: `◽性别：${item.gender}` });
        if (item.birth_date) detailsChildren.push({ label: `◽出生日期：${item.birth_date}` });
        if (item.death_date) detailsChildren.push({ label: `◽逝世日期：${item.death_date}` });
        if (item.birth_place) detailsChildren.push({ label: `◽出生地：${item.birth_place}` });
        
      } else if (isBattleItem) {
        // --- 战役处理逻辑 ---
        sourceNode.label = `${item.source_file || '未知文件'}${item.source_type ? `-${item.source_type}` : ''}`;
        
        if (item.name) detailsChildren.push({ label: `◽【名称】: ${item.name}` });
        if (item.background) detailsChildren.push({ label: `◽【背景】: ${item.background}` });
        if (item.time_details) detailsChildren.push({ label: `◽【时间】: ${item.time_details.description || '无'}` });
        if (item.location_details) detailsChildren.push({ label: `◽【地点】: ${item.location_details.description || '无'}` });
        
        if (item.belligerents && item.belligerents.length > 0) {
          const belligerentsInfo = item.belligerents
            .map((side) => `${side.side}: ${side.units?.join(', ') || '无部队'}`)
            .join('; ');
          detailsChildren.push({ label: `◽【参战方】: ${belligerentsInfo}` });
        }
        
        if (item.result) detailsChildren.push({ label: `◽【结果】: ${item.result.outcome || '无'}` });
        if (item.impact) detailsChildren.push({ label: `◽【影响】: ${item.impact}` });
        if (item.process_and_tactics) detailsChildren.push({ label: `◽【战术】: ${item.process_and_tactics}` });
      } else {
          // 如果是其他未知格式，仅使用 source_file 作为来源
          if (item.source_file) {
              sourceNode.label = `${item.source_file}${item.source_type ? `-${item.source_type}` : ''}`;
          }
      }

      // 如果有子节点，将其添加到 sourceNode
      if (detailsChildren.length > 0) {
        sourceNode.children = detailsChildren;
      }

      // 如果有详细信息或者仅仅是来源文件，都将它添加到树中
      if (detailsChildren.length > 0 || sourceNode.label !== '未知来源') {
        treeData.push(sourceNode);
      }
    });

    return {
      value: treeData,
      isTree: true,
    };
  }

  // 3. 处理非数组的其他格式（单对象或未知格式）
  if (typeof data === 'object' && data !== null) {
    const sources = [];
    const circleNumbers = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩'];
    let index = 0;

    // 格式0处理逻辑
    if (data.source_file) {
      const sourceFile = data.source_file || '';
      const sourceType = data.source_type ? `-${data.source_type}` : '';
      sources.push(`${sourceFile}${sourceType}`);
    } else {
      // 格式1处理逻辑
      for (const key in data) {
        if (Object.prototype.hasOwnProperty.call(data, key) && data[key] && typeof data[key] === 'object') {
          const source = data[key];
          const sourceFile = source.source_file || '';
          const sourceType = source.source_type ? `-${source.source_type}` : '';
          if (sourceFile) {
            const number = circleNumbers[index] || `[${index + 1}]`;
            sources.push(`\n${number} ${sourceFile}${sourceType}`);
            index++;
          }
        }
      }
    }
    
    return {
      value: sources.join('\n'),
      isTree: false,
    };
  }

  // 4. 处理其他未知格式或空值
  return {
    value: '',
    isTree: false,
  };
};

const propertyOrder = {
  // 人物
  'generation': -1,
  '代际': -1,
  'new_fourth_army_fifth_division': 0,
  '五师前辈': 0,
  '性别': 1,
  'gender': 1,
  '曾用名': 2,
  'aliases': 2,
  '籍贯': 3,
  'birth_place': 3,
  '出生日期': 4,
  'birth_date': 4,
  '逝世日期': 5,
  'death_date': 5,
  'join_revolution_date': 6,
  '参加革命时间': 6,
  'join_party_date': 7,
  '入党时间': 7,
    'is_family_member':8,
   '是否亲属':8,
  'person_category': 9,
  '人物类别': 9,


  // 事件
  // '类别':1, 
  // 'category':1,

  // 事件-战役
  'new_fourth_army_battle': 1,
  '五师战役': 1,
  'background': 2,
  '背景':2,
  'time_details': 3,
  '时间': 3,
  'location_details': 4,
  '地点': 4,
  'belligerents': 5,
  '交战方': 5,
  'key_figures': 6,
  '主要领导': 6,

  'process_and_tactics': 7,
  '战术': 7,
  'result':8, 
  '结果': 8,
  'impact': 9, 
  '影响': 9,

  'battle_time':1,
  '作战时间':1,
  'battle_area':2,
  '作战地区':2,
  'our_forces':3,
  '我军参战部队':3,
  'enemy_forces':4,
  '敌军参战部队':4,
  'battle_process':5,
  '作战经过':5,
  'battle_result':6,
  '作战结果':6,



  'updated_at': 300,
  '合并更新时间':300,

  // 人物-人物关系
  '关系描述':1,
  'relationship_description':1,
  '事件名称':2,
  'event_name':2,
  '关系类型':3,
  'relationship_type':3,


  // 人物-事件关系
  '关系' : 1,
  'relationship': 1,
  '组织': 2,
  'organization': 2,
  '机构': 2,
  'institution': 2,
  '职位': 3,
  'position': 3,
  '地点': 4,
  'location': 4,
  '同事关系':5,
  'relationship_verb':5,
  '发生时间': 6,
  'time_value': 6,
  '发生时期':7,
  'time_period':7,
  '开始时间': 8,
  'time_start': 8,
  '结束时间': 9,
  'time_end': 9,


  // 人物-战役战斗
  'inference_confidence': 10,
  '推理置信度':10,
  'inference_metadata': 11,
  '推理元数据':11,
  'inference_reasoning': 12,
  '推理过程':12,
  'inference_source': 13,
  '推理来源':13,


  '溯源信息': 100,
  'source_info': 100,
  '溯源文本': 100,
  'source_text': 100,

  '创建时间': 200,
  'created_at': 200,

};

// 导出获取属性顺序的函数
export const getPropertyOrder = (key) => {

  return propertyOrder[key] || 80; // 未定义顺序的属性放到最后
};


// ----------------------------战役--------------------------------------------------
// 安全地将JSON字符串解析为对象
const safeJSONParse = (str) => {
  if (typeof str === 'string' && (str.trim().startsWith('[') || str.trim().startsWith('{'))) {
    try {
      return JSON.parse(str);
    } catch (e) {
      console.error('JSON解析失败:', e);
    }
  }
  return str;
};

// 格式化交战方
const formatBelligerents = (belligerents) => {
  if (!Array.isArray(belligerents) || belligerents.length === 0) {
    return '无';
  }
  
  return belligerents.map(side => {
    const sideInfo = [];
    // 使用 style 属性直接应用颜色，并使用 class 方便样式调整
    const sideNameHtml = `<span style="color: var(--accent-error); font-weight: bold;">🚩${side.side || '未知方'}</span>`;
    
    sideInfo.push(`${sideNameHtml}`);
    // 使用 style 属性加粗
    if (side.units?.length > 0) {
      sideInfo.push(`<span style="color: var(--text-secondary);">[部队]</span>: ${side.units.join(', ')}`);
    }
    if (side.strength) {
      sideInfo.push(`<span style="color: var(--text-secondary);">[兵力]</span>: ${side.strength}`);
    }
    if (side.commanders?.length > 0) {
      sideInfo.push(`<span style="color: var(--text-secondary);">[指挥官]</span>: ${side.commanders.map(c => `${c.name} (${c.position})`).join('; ')}`);
    }
    return sideInfo.join('<br>'); 
  }).join('<br><br>');
};


// 格式化结果
const formatResult = (result) => {
  if (!result || typeof result !== 'object' || Object.keys(result).length === 0) {
    return '无';
  }
  const parts = [];
  if (result.outcome) {
    parts.push(`<span style="color: var(--accent-error);">🚩${result.outcome}</span>`);
  }
  if (result.casualties_and_captives) {
    parts.push(`<span style="color: var(--text-secondary);">[伤亡和俘虏]</span>: ${result.casualties_and_captives}`);
  }
  if (result.spoils_of_war) {
    parts.push(`<span style="color: var(--text-secondary);">[战利品]</span>: ${result.spoils_of_war}`);
  }
  return parts.length > 0 ? parts.join('<br>') : '无';
};

// 格式化主要领导（key_figures）
const formatKeyFigures = (keyFigures) => {
  if (!Array.isArray(keyFigures) || keyFigures.length === 0) {
  return '无';
  }
  return keyFigures.map(fig => {
  const nameHtml = `<span style="color: var(--accent-error); font-weight: bold;">${fig.name || '未知人物'}</span>`;
  const roleHtml = fig.role ? `<span style="color: var(--text-secondary);">[角色]</span>: ${fig.role}` : '';
  const contributionHtml = fig.contribution ? `<span style="color: var(--text-secondary);">[贡献]</span>: ${fig.contribution}` : '';
  return [nameHtml, roleHtml, contributionHtml].filter(Boolean).join('<br>');
  }).join('<br><br>');
};

// 格式化地点详情，返回 HTML 字符串
const formatLocationDetails = (locationDetails) => {
  if (!locationDetails || typeof locationDetails !== 'object' || Object.keys(locationDetails).length === 0) {
    return '无';
  }
  
  const parts = [];
  const fullAddress = [
    locationDetails.province,
    locationDetails.city,
    locationDetails.district,
    locationDetails.specific_area
  ].filter(Boolean).join('');
  
  if (fullAddress) {
    parts.push(`<span style="color: var(--text-secondary);">[具体位置]</span>: ${fullAddress}`);
  }
  if (locationDetails.description) {
    parts.push(`<span style="color: var(--text-secondary);">[地点描述]</span>: ${locationDetails.description}`);
  }
  
  return parts.length > 0 ? parts.join('<br>') : '无';
};

// 格式化时间详情，返回 HTML 字符串
const formatTimeDetails = (timeDetails) => {
  if (!timeDetails || typeof timeDetails !== 'object' || Object.keys(timeDetails).length === 0) {
    return '无';
  }
  
  const parts = [];
  if (timeDetails.description) {
    parts.push(`<span style="color: var(--text-secondary);">[时间描述]</span>: ${timeDetails.description}`);
  }
  if (timeDetails.start_date) {
    parts.push(`<span style="color: var(--text-secondary);">[起始日期]</span>: ${timeDetails.start_date}`);
  }
  if (timeDetails.end_date) {
    parts.push(`<span style="color: var(--text-secondary);">[结束日期]</span>: ${timeDetails.end_date}`);
  }
  
  return parts.length > 0 ? parts.join('<br>') : '无';
};

// 格式化推理元数据 (inference_metadata)
const formatInferenceMetadata = (metadata) => {
  if (!metadata || typeof metadata !== 'object' || Object.keys(metadata).length === 0) {
    return '无';
  }

  const parts = [];
  
  // 推理时间
  if (metadata.inferred_at) {
    parts.push(`<span style="color: var(--text-secondary);">[推理时间]</span>: ${formatDate(metadata.inferred_at)}`);
  }
  // 模型
  if (metadata.model) {
    parts.push(`<span style="color: var(--text-secondary);">[使用模型]</span>: ${metadata.model}`);
  }
  // 相似度分数
  if (metadata.name_similarity !== undefined) {
    parts.push(`<span style="color: var(--text-secondary);">[名称相似度]</span>: ${metadata.name_similarity}`);
  }

  // 证据详情 (evidence)
  if (metadata.evidence && typeof metadata.evidence === 'object') {
    const evidenceParts = [];
    // ✅ 解决方案：将 Markdown **替换为 <strong> 标签进行加粗
    evidenceParts.push('<strong>匹配证据</strong>：'); 
    
    // 使用小圆点或短横线展示证据列表
    if (metadata.evidence.name_match !== undefined) evidenceParts.push(`- 名称匹配: ${metadata.evidence.name_match ? '是' : '否'}`);
    if (metadata.evidence.time_match !== undefined) evidenceParts.push(`- 时间匹配: ${metadata.evidence.time_match ? '是' : '否'}`);
    if (metadata.evidence.location_match !== undefined) evidenceParts.push(`- 地点匹配: ${metadata.evidence.location_match ? '是' : '否'}`);
    if (metadata.evidence.description) evidenceParts.push(`- 描述: ${metadata.evidence.description}`);
    
    parts.push(evidenceParts.join('<br>'));
  }

  return parts.length > 0 ? parts.join('<br>') : '无';
};

// 格式化推理来源 (inference_source)
const formatInferenceSource = (source) => {
  if (!source || typeof source !== 'object' || Object.keys(source).length === 0) {
    return '无';
  }
  
  const parts = [];
  // 定义加粗样式，使用 <strong> 或 <span>
  const boldStyle = 'font-weight: bold;';

  // 原始事件 (通常是当前事件)
  if (source.original_event_name || source.original_event_id) {
    // ✅ 解决方案：将 Markdown **替换为 <span> + style 进行加粗
    const name = source.original_event_name ? `<span style="${boldStyle}">${source.original_event_name}</span>` : '未知名称';
    const id = source.original_event_id ? `(${source.original_event_id})` : '';
    parts.push(`<span style="color: var(--text-secondary);">[原始事件]</span>: ${name} ${id}`);
  }

  // 匹配的战役事件 (用于融合的另一个事件)
  if (source.battle_event_name || source.battle_event_id) {
    // ✅ 解决方案：将 Markdown **替换为 <span> + style 进行加粗
    const name = source.battle_event_name ? `<span style="${boldStyle}">${source.battle_event_name}</span>` : '未知名称';
    const id = source.battle_event_id ? `(${source.battle_event_id})` : '';
    parts.push(`<span style="color: var(--text-secondary);">[匹配事件]</span>: ${name} ${id}`);
  }

  return parts.length > 0 ? parts.join('<br>') : '无';
};

// 格式化推理过程 (inference_reasoning)
const formatInferenceReasoning = (reasoning) => {
  // 推理过程直接返回字符串，但可以进行简单的 HTML 包装以统一风格
  if (!reasoning || typeof reasoning !== 'string') {
    return '无';
  }
  
  return `<span style="color: var(--text-primary);">${reasoning}</span>`;
};


//--------------------------end 战役-------------------------


// 属性格式化
export const formatProperty = (key, value) => {
  // console.log(`格式化属性 ${key} 的值: ${value}`);

  if (value === null || value === undefined) return '';
  
  // 空值处理
  if (value === '' ) return '无';

  // 首先，安全地将任何JSON字符串解析为JavaScript对象
  const parsedValue = safeJSONParse(value);

  // 检查空值，但放在解析后进行，以避免将空JSON字符串误判为无
  if (parsedValue === null || parsedValue === undefined || parsedValue === '') {
    return '无';
  }

  if (key === '交战方' || key === 'belligerents') {
    return formatBelligerents(parsedValue);
  } 
  if (key === '结果' || key === 'result') {
    return formatResult(parsedValue);
  } 
  if (key === '时间详情' || key === 'time_details') {
    return formatTimeDetails(parsedValue);
  } 
  if (key === '地点详情' || key === 'location_details') {
    return formatLocationDetails(parsedValue);
  } 
  if (key === 'key_figures' || key === '主要领导') {
    return formatKeyFigures(parsedValue);
  }

  // --- 新增推理属性格式化 ---
  if (key === 'inference_confidence' || key === '推理置信度') {
    // 简单字符串，使用颜色强调
    const confidenceMap = {
      'high': '高',
      'medium': '中',
      'low': '低',
      'unknown': '未知'
    };
    const displayValue = confidenceMap[String(value).toLowerCase()] || String(value);
    return `<span style="color: var(--accent-success); font-weight: bold;">${displayValue}</span>`;
  }
  if (key === 'inference_metadata' || key === '推理元数据') {
    return formatInferenceMetadata(parsedValue);
  }
  if (key === 'inference_reasoning' || key === '推理过程') {
    return formatInferenceReasoning(String(value)); // 推理过程总是作为字符串处理
  }
  if (key === 'inference_source' || key === '推理来源') {
    return formatInferenceSource(parsedValue);
  }

  // 日期类型处理
  if ( key.toLowerCase().includes('created_at') || key.toLowerCase().includes('updated_at') ) {
    // console.log(`格式化日期属性 ${key} 的值: ${value}`);
    return formatDate(value);
  }
  
  // 性别处理
  if (key === 'Gender' || key === '性别') {
    return value === '男' ? '男' : '女';
  }

  // 别名处理
  if (key === '别名' || key === 'aliases') {
    if (Array.isArray(value)) {
      return value.length > 0 ? value.join(', ') : '无';
    } else if (typeof value === 'string') {
      return value ? value : '无'; 
    }
  }
  
  // 布尔值处理
  if (typeof value === 'boolean') {
    return value ? '是' : '否';
  }

  // 数组处理（通用）
  if (Array.isArray(value)) {
    return value.join(', ');
  }
  if (typeof value === 'object') {
    return JSON.stringify(value); 
  }

  // console.log(`格式化属性 ${key} 的结果: ${value}`);
  
  return value;
};



