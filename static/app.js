// TokenViewer Pro - Frontend Architecture & High-Performance Visualization

(function() {
  'use strict';

  // Comprehensive i18n Dictionary
  const I18N = {
    zh: {
      dashboard: "仪表盘",
      modelMonitor: "模型监控",
      tokenUsage: "Token 消耗",
      apiLogs: "调用日志",
      settings: "系统设置",
      liveStatus: "实时状态",
      connected: "已连接",
      offline: "离线",
      connecting: "连接中...",
      searchPlaceholder: "搜索模型名",
      searchModelsTitle: "模型统计检索",
      resultsUnit: "个结果",
      noMatchingModels: "未找到匹配模型",
      allAgents: "All Agents",
      allAgentsOption: "All Agents",
      online: "连接中",
      changeAvatar: "更换自定义头像...",
      resetAvatar: "恢复默认头像",
      agentFilterTitle: "Agent 过滤",
      timeToday: "今天",
      time24h: "24小时",
      time7d: "7天",
      time30d: "30天",
      timeAll: "全部",
      activeModels: "活跃模型",
      noActiveModels: "暂无活跃模型",
      totalTokensUsed: "Token 消耗总量",
      usageTrend: "消耗趋势",
      hrsToday: "今日",
      hrs24: "24 小时",
      days7: "7 天",
      days30: "30 天",
      allTime: "全部时间",
      activeProjects: "活跃项目",
      projectsUnit: "个项目",
      tokenConsumption: "Token 消耗量",
      refreshRate: "刷新:",
      timelineToday: "用量时间线（今日 00:00 至今）",
      timeline24h: "用量时间线（最近 24 小时）",
      timeline7d: "用量时间线（最近 7 天）",
      timeline30d: "用量时间线（最近 30 天）",
      timelineAll: "用量时间线（全部历史）",
      currentRate: "当前用量:",
      rateUnit: "Tokens",
      peak: "峰值:",
      costOverview: "费用概览",
      estimated: "预估开销:",
      projectBreakdown: "项目占比",
      // Model monitor
      modelMonitorDesc: "详细模型调用频次、Token 吞吐、缓存命中率与单价成本",
      thModel: "模型名称",
      thRequests: "调用次数",
      thTokens: "Token 消耗 ▾",
      thCacheRate: "缓存率",
      thCost: "预估金额",
      noModelData: "无匹配模型数据",
      // Token usage
      tokenUsageDesc: "输入、输出、上下文缓存写入与读取全量分析",
      kpiFreshTitle: "全新输入 Token (Fresh)",
      kpiFreshSub: "全新计算上下文输入",
      kpiCacheTitle: "缓存读取 Token (Cache Read)",
      kpiCacheSub: "命中缓存上下文读取",
      kpiOutputTitle: "输出生成 Token (Output)",
      kpiOutputSub: "模型生成内容与推理 Token",
      kpiHitRateTitle: "综合缓存命中率",
      kpiHitRateSub: "节省的重复计算比例",
      // API Logs
      apiLogsDesc: "按会话或工作目录归集的调用历史流",
      thSession: "会话 / 工作目录",
      thLastActive: "最近活动时间",
      noLogData: "无匹配记录",
      // Settings
      settingsDesc: "语言切换、界面缩放、订阅套餐链接与模型定价基准维护",
      langTitle: "界面语言 / Language",
      langSub: "切换软件显示语言（默认简体中文）",
      subUrlTitle: "套餐订阅链接",
      subUrlSub: "外部额度控制台或套餐管理直达入口",
      btnSaveUrl: "保存链接",
      pricingTitle: "模型定价维护（USD / 每百万 Token）",
      pricingSub: "维护单价后点击保存将立即重新核算全部历史开销",
      btnAddModel: "+ 新增模型",
      btnSavePrice: "保存并重算",
      msgUrlSaved: "订阅链接已保存！",
      msgSavingPrice: "正在重算历史开销并保存...",
      msgPriceSaved: "定价保存成功，全量历史数据已更新！",
      msgPriceDel: "已删除模型并重新核算开销",
      subDirect: "订阅套餐",
      subDirectTitle: "直达订阅套餐 / 打开外部控制台",
      thPriceModel: "模型名称",
      thPriceFresh: "全新输入 ($/1M)",
      thPriceCache: "缓存读取 ($/1M)",
      thPriceOutput: "输出生成 ($/1M)",
      thPriceAction: "操作",
      msgConfigureUrlFirst: "请先在此处配置您的订阅套餐链接",
      zoomTitle: "界面缩放比例",
      zoomSub: "调整界面显示大小，适配 2K / 4K 高分屏（快捷键 Ctrl + +/-/0）",
      winCapsule: "桌面灵动胶囊 (全场景置顶 / 点击直接拖拽)",
      winMin: "最小化",
      winMax: "全屏 (F11)",
      winRestore: "还原窗口 (F11)",
      winFullscreen: "全屏 (F11)",
      winClose: "关闭",
      activeModelsTip: "查看模型监控明细",
      activeProjectsTip: "查看项目与调用日志",
      costOverviewTip: "查看模型费用明细",
      projectBreakdownTip: "查看项目调用日志 / 点击项目快速过滤",
      splashAnimTitle: "开机流体过渡",
      splashAnimSub: "开启或关闭软件启动时的黑水晶毛玻璃平滑过渡",
      animOn: "开启",
      animOff: "关闭"
    },
    en: {
      dashboard: "Dashboard",
      modelMonitor: "Model Monitor",
      tokenUsage: "Token Usage",
      apiLogs: "API Logs",
      settings: "Settings",
      liveStatus: "Live Status",
      connected: "Connected",
      offline: "Offline",
      connecting: "Connecting...",
      searchPlaceholder: "Search models",
      searchModelsTitle: "Model Statistics",
      resultsUnit: "results",
      noMatchingModels: "No matching models found",
      allAgents: "All Agents",
      allAgentsOption: "All Agents",
      online: "Connecting...",
      changeAvatar: "Change Avatar...",
      resetAvatar: "Reset to Default",
      agentFilterTitle: "Agent Filter",
      timeToday: "Today",
      time24h: "24h",
      time7d: "7d",
      time30d: "30d",
      timeAll: "All",
      activeModels: "Active Models",
      noActiveModels: "No active models",
      totalTokensUsed: "Total Tokens Used",
      usageTrend: "Usage",
      hrsToday: "Today",
      hrs24: "24 hrs",
      days7: "7 days",
      days30: "30 days",
      allTime: "all time",
      activeProjects: "Active Projects",
      projectsUnit: "projects",
      tokenConsumption: "Token Consumption",
      refreshRate: "Refresh:",
      timelineToday: "Usage Timeline (Today from 00:00)",
      timeline24h: "Usage Timeline (Last 24 Hours)",
      timeline7d: "Usage Timeline (Last 7 Days)",
      timeline30d: "Usage Timeline (Last 30 Days)",
      timelineAll: "Usage Timeline (All Recorded History)",
      currentRate: "Current Usage:",
      rateUnit: "Tokens",
      peak: "Peak:",
      costOverview: "Cost Overview",
      estimated: "Estimated:",
      projectBreakdown: "Project Breakdown",
      // Model monitor
      modelMonitorDesc: "Detailed model requests, token throughput, cache rate, and cost",
      thModel: "Model Name",
      thRequests: "Requests",
      thTokens: "Tokens ▾",
      thCacheRate: "Cache Rate",
      thCost: "Est. Cost",
      noModelData: "No matching models",
      // Token usage
      tokenUsageDesc: "Fresh input, cache read, output, and context cache analytics",
      kpiFreshTitle: "Fresh Input Tokens",
      kpiFreshSub: "Fresh context computation",
      kpiCacheTitle: "Cache Read Tokens",
      kpiCacheSub: "Cache hit context read",
      kpiOutputTitle: "Output Tokens",
      kpiOutputSub: "Model generation & reasoning",
      kpiHitRateTitle: "Overall Cache Hit Rate",
      kpiHitRateSub: "Saved computation percentage",
      // API Logs
      apiLogsDesc: "Invocation history grouped by session or workspace directory",
      thSession: "Session / Directory",
      thLastActive: "Last Active",
      noLogData: "No matching records",
      // Settings
      settingsDesc: "Language, UI scaling, subscription URL, and pricing benchmark maintenance",
      langTitle: "Interface Language",
      langSub: "Select interface language (Default: Simplified Chinese)",
      subUrlTitle: "Subscription URL",
      subUrlSub: "Direct portal to external quota management console",
      btnSaveUrl: "Save URL",
      pricingTitle: "Model Pricing Benchmark (USD / Million Tokens)",
      pricingSub: "Updating pricing will immediately recalculate all historical costs",
      btnAddModel: "+ Add Model",
      btnSavePrice: "Save & Recompute",
      msgUrlSaved: "Subscription URL saved!",
      msgSavingPrice: "Recalculating costs and saving...",
      msgPriceSaved: "Pricing saved and history recalculated!",
      msgPriceDel: "Model deleted and costs recomputed",
      subDirect: "Subscription",
      subDirectTitle: "Direct to Subscription / Open Console",
      thPriceModel: "Model Name",
      thPriceFresh: "Input ($/1M)",
      thPriceCache: "Cache ($/1M)",
      thPriceOutput: "Output ($/1M)",
      thPriceAction: "Action",
      msgConfigureUrlFirst: "Please configure your subscription URL here first",
      zoomTitle: "UI Scaling / Zoom",
      zoomSub: "Adjust interface size for 2K / 4K high-res displays (Ctrl + +/-/0)",
      winCapsule: "Dynamic Island Capsule (Always-on-top / Click & drag)",
      winMin: "Minimize",
      winMax: "Fullscreen (F11)",
      winRestore: "Restore Window (F11)",
      winFullscreen: "Fullscreen (F11)",
      winClose: "Close",
      activeModelsTip: "View model monitor details",
      activeProjectsTip: "View project & session logs",
      costOverviewTip: "View model cost breakdown",
      projectBreakdownTip: "View project logs / Click to filter",
      splashAnimTitle: "Startup Glass Transition",
      splashAnimSub: "Enable or disable smooth liquid glass startup transition",
      animOn: "Enabled",
      animOff: "Disabled"
    }
  };

  // State Management (Default language is Chinese 'zh')
  const state = {
    lang: new URLSearchParams(window.location.search).get('lang') || localStorage.getItem('tokenviewer_lang') || 'zh',
    view: 'dashboard',
    range: localStorage.getItem('tokenviewer_range') || 'today',
    agent: '',
    searchQuery: '',
    refreshInterval: parseInt(localStorage.getItem('tokenviewer_refresh') || '60', 10),
    dashboardData: null,
    modelsData: [],
    sessionsData: [],
    pricingList: [],
    subscriptionUrl: '',
    zoom: parseInt(localStorage.getItem('tokenviewer_zoom') || '100', 10),
    isMax: false,
    isFull: false,
    sort: {
      models: { key: 'tokens', asc: false },
      sessions: { key: 'tokens', asc: false }
    }
  };
  window.appState = state;

  function t(key) {
    const dict = I18N[state.lang] || I18N.zh;
    return dict[key] !== undefined ? dict[key] : (I18N.zh[key] || key);
  }

  // Chart instances & Timers
  let consumptionChart = null;
  let miniSparklineChart = null;
  let miniCostChart = null;
  let breakdownDonutChart = null;
  let currentBreakdownItems = [];
  let currentBreakdownTotal = 1;
  let currentBreakdownColors = [];
  let dashboardTimer = null;
  let moveRaf = null;

  // Peak Annotation Plugin - ONLY for consumptionChart
  const peakAnnotationPlugin = {
    id: 'peakAnnotation',
    afterDatasetsDraw(chart) {
      if (!chart.canvas || chart.canvas.id !== 'consumptionChart') return;

      const { ctx } = chart;
      const meta = chart.getDatasetMeta(0);
      if (!meta || !meta.data || meta.data.length === 0) return;

      const dataset = chart.data.datasets[0];
      const values = dataset.data;
      if (!values || values.length === 0) return;

      let maxVal = -1;
      let maxIdx = -1;
      for (let i = 0; i < values.length; i++) {
        const val = typeof values[i] === 'number' ? values[i] : 0;
        if (val > maxVal) {
          maxVal = val;
          maxIdx = i;
        }
      }

      if (maxIdx === -1 || maxVal <= 0) return;

      const point = meta.data[maxIdx];
      if (!point) return;

      const px = point.x;
      const py = point.y;

      ctx.save();

      // Outer luminous glow ring
      ctx.beginPath();
      ctx.arc(px, py, 4.5, 0, 2 * Math.PI);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
      ctx.lineWidth = 2.5;
      ctx.strokeStyle = '#38bdf8';
      ctx.stroke();

      // Dashed vertical connector
      const badgeY = Math.max(18, py - 30);
      ctx.beginPath();
      ctx.setLineDash([2, 2]);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
      ctx.lineWidth = 1;
      ctx.moveTo(px, py - 5);
      ctx.lineTo(px, badgeY + 11);
      ctx.stroke();
      ctx.setLineDash([]);

      // Badge Capsule
      const peakPrefix = t('peak');
      const peakStr = `${peakPrefix} ${formatTokens(maxVal)}`;
      ctx.font = '600 10.5px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
      const textWidth = ctx.measureText(peakStr).width;

      const pillW = textWidth + 20;
      const pillH = 20;
      let pillX = px - pillW / 2;
      if (pillX < 8) pillX = 8;
      if (pillX + pillW > chart.width - 8) pillX = chart.width - pillW - 8;

      ctx.shadowColor = 'rgba(0, 0, 0, 0.35)';
      ctx.shadowBlur = 10;
      ctx.shadowOffsetY = 3;
      ctx.beginPath();
      ctx.roundRect(pillX, badgeY, pillW, pillH, 10);
      ctx.fillStyle = '#ffffff';
      ctx.fill();
      ctx.shadowColor = 'transparent';

      // Cyan accent dot inside pill
      ctx.beginPath();
      ctx.arc(pillX + 9, badgeY + pillH / 2, 3, 0, 2 * Math.PI);
      ctx.fillStyle = '#0284c7';
      ctx.fill();

      // Text
      ctx.fillStyle = '#0f172a';
      ctx.fillText(peakStr, pillX + 16, badgeY + 14);

      ctx.restore();
    }
  };

  if (window.Chart) {
    Chart.register(peakAnnotationPlugin);
  }

  // Number & Currency Formatters
  function formatTokens(val) {
    if (!val || val === 0) return '0';
    if (val >= 1e9) return (val / 1e9).toFixed(2) + 'B';
    if (val >= 1e6) return (val / 1e6).toFixed(1) + 'M';
    if (val >= 1e3) return (val / 1e3).toFixed(1) + 'k';
    return Math.round(val).toLocaleString();
  }

  function formatCost(val) {
    if (val === undefined || val === null || val === 0) return '$0.00';
    if (val < 0.01) return '$' + val.toFixed(4);
    return '$' + val.toFixed(2);
  }

  function formatPct(val) {
    if (!val && val !== 0) return '0%';
    return (val * 100).toFixed(0) + '%';
  }

  // Smooth number counter without flickering
  function animateNumber(element, targetValue, formatter, duration = 450) {
    if (!element) return;
    const rawVal = parseFloat(targetValue) || 0;
    const prevVal = parseFloat(element.getAttribute('data-num'));
    if (!isNaN(prevVal) && Math.abs(prevVal - rawVal) < 0.0001) {
      element.textContent = formatter(rawVal);
      return;
    }
    const start = isNaN(prevVal) ? 0 : prevVal;
    const startTime = performance.now();

    function step(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // easeOutCubic
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = start + (rawVal - start) * ease;
      element.textContent = formatter(current);
      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        element.textContent = formatter(rawVal);
        element.setAttribute('data-num', rawVal);
      }
    }
    element.setAttribute('data-num', rawVal);
    requestAnimationFrame(step);
  }

  // DOM Elements
  const el = {
    winClose: document.getElementById('winClose'),
    winMin: document.getElementById('winMin'),
    winMax: document.getElementById('winMax'),
    iconMaximize: document.querySelector('.icon-maximize'),
    iconRestore: document.querySelector('.icon-restore'),
    proZoomSeg: document.getElementById('proZoomSeg'),
    sidebar: document.getElementById('appSidebar'),
    sidebarToggleBtn: document.getElementById('sidebarToggleBtn'),
    sidebarSearchBtn: document.getElementById('sidebarSearchBtn'),
    navItems: document.querySelectorAll('.nav-item'),
    viewPanels: document.querySelectorAll('.view-panel'),
    globalSearch: document.getElementById('globalSearch'),
    searchClearBtn: document.getElementById('searchClearBtn'),
    searchResultsFlyout: document.getElementById('searchResultsFlyout'),
    searchFlyoutList: document.getElementById('searchFlyoutList'),
    searchMatchCount: document.getElementById('searchMatchCount'),
    agentSelectorBtn: document.getElementById('agentSelectorBtn'),
    agentDropdown: document.getElementById('agentDropdown'),
    currentAgentName: document.getElementById('currentAgentName'),
    userAvatarContainer: document.getElementById('userAvatarContainer'),
    userCustomAvatar: document.getElementById('userCustomAvatar'),
    userDefaultAvatarSvg: document.getElementById('userDefaultAvatarSvg'),
    avatarFileInput: document.getElementById('avatarFileInput'),
    dropdownChangeAvatar: document.getElementById('dropdownChangeAvatar'),
    dropdownResetAvatar: document.getElementById('dropdownResetAvatar'),
    userProfileInfo: document.getElementById('userProfileInfo'),
    agentChevron: document.getElementById('agentChevron'),
    timeBtns: document.querySelectorAll('.time-btn'),
    connDot: document.getElementById('connDot'),
    connText: document.getElementById('connText'),
    liveCard: document.getElementById('liveCard'),
    topHeader: document.querySelector('.top-header'),
    
    // Dashboard elements
    openModelsCard: document.getElementById('openModelsCard'),
    openProjectsCard: document.getElementById('openProjectsCard'),
    openCostCard: document.getElementById('openCostCard'),
    openBreakdownCard: document.getElementById('openBreakdownCard'),
    subDirectBtn: document.getElementById('subDirectBtn'),
    activeModelsList: document.getElementById('activeModelsList'),
    dashTotalTokens: document.getElementById('dashTotalTokens'),
    tokenTimeLabel: document.getElementById('tokenTimeLabel'),
    dashActiveProjects: document.getElementById('dashActiveProjects'),
    consumptionSubtitle: document.getElementById('consumptionSubtitle'),
    currentRate: document.getElementById('currentRate'),
    dashTotalCost: document.getElementById('dashTotalCost'),
    breakdownLegend: document.getElementById('breakdownLegend'),
    
    // Token usage KPIs
    kpiFresh: document.getElementById('kpiFresh'),
    kpiCacheRead: document.getElementById('kpiCacheRead'),
    kpiOutput: document.getElementById('kpiOutput'),
    kpiHitRate: document.getElementById('kpiHitRate'),
    
    // Tables
    modelsTable: document.querySelector('#modelsTable tbody'),
    sessionsTable: document.querySelector('#sessionsTable tbody'),
    modelsThs: document.querySelectorAll('#modelsTable th'),
    sessionsThs: document.querySelectorAll('#sessionsTable th'),
    
    // Settings
    proLangSeg: document.getElementById('proLangSeg'),
    proSubUrl: document.getElementById('proSubUrl'),
    proUrlSave: document.getElementById('proUrlSave'),
    proPriceList: document.getElementById('proPriceList'),
    proPriceAdd: document.getElementById('proPriceAdd'),
    proPriceSave: document.getElementById('proPriceSave'),
    proPriceStatus: document.getElementById('proPriceStatus'),

    // Apple 灵动岛风格桌面胶囊
    winCapsuleBtn: document.getElementById('winCapsuleBtn'),
    dynamicIslandWrapper: document.getElementById('dynamicIslandWrapper'),
    dynamicIsland: document.getElementById('dynamicIsland'),
    islandGlowDot: document.getElementById('islandGlowDot'),
    islandTodayTokens: document.getElementById('islandTodayTokens'),
    islandTodayCost: document.getElementById('islandTodayCost'),
    islandRestoreBtn: document.getElementById('islandRestoreBtn'),

    // 开机黑水晶毛玻璃平滑过渡 (Liquid Glass Startup Transition)
    appGlassVeil: document.getElementById('appGlassVeil'),
    proSplashSeg: document.getElementById('proSplashSeg'),
    appWindow: document.getElementById('appWindow')
  };

  // ==========================================================================
  // 纯正黑水晶毛玻璃开机丝滑过渡 (Liquid Glass Startup Transition)
  // 无假自检、无假进度条，纯物理光学消融 (~400ms)
  // ==========================================================================
  function setupStartupTransition() {
    if (!el.appGlassVeil) return;

    // 检查用户是否在设置中关闭了开机动效
    const splashDisabled = localStorage.getItem('tokenviewer_splash_disabled') === '1';

    // 初始化设置面板中的切换按钮
    if (el.proSplashSeg) {
      const btns = el.proSplashSeg.querySelectorAll('button');
      btns.forEach(b => {
        const val = b.getAttribute('data-splash');
        if ((splashDisabled && val === 'off') || (!splashDisabled && val === 'on')) {
          b.classList.add('active');
        } else {
          b.classList.remove('active');
        }
        b.addEventListener('click', () => {
          btns.forEach(x => x.classList.remove('active'));
          b.classList.add('active');
          const isOff = val === 'off';
          localStorage.setItem('tokenviewer_splash_disabled', isOff ? '1' : '0');
        });
      });
    }

    // 若用户主动关闭了启动动效，直接瞬时移除
    if (splashDisabled) {
      el.appGlassVeil.style.display = 'none';
      if (el.appWindow) {
        el.appWindow.classList.remove('app-entering');
        el.appWindow.classList.add('app-ready');
      }
      return;
    }

    let dismissed = false;
    function dismissVeil() {
      if (dismissed) return;
      dismissed = true;

      if (el.appGlassVeil) {
        el.appGlassVeil.classList.add('veil-dismissed');
      }
      if (el.appWindow) {
        el.appWindow.classList.remove('app-entering');
        el.appWindow.classList.add('app-ready');
      }
      setTimeout(() => {
        if (el.appGlassVeil) {
          el.appGlassVeil.style.display = 'none';
        }
      }, 440);
    }

    // 首屏数据返回与消融触发（保持轻柔呼吸约 360ms，最长 1200ms 强制进入）
    const startTime = Date.now();
    window.notifyAppReady = () => {
      const elapsed = Date.now() - startTime;
      const minDisplay = 360;
      if (elapsed < minDisplay) {
        setTimeout(dismissVeil, minDisplay - elapsed);
      } else {
        dismissVeil();
      }
    };

    // 最长 1.2s 超时兜底消融
    setTimeout(dismissVeil, 1200);
  }

  function init() {
    setupStartupTransition();
    setupLanguage();
    setupAvatar();
    setupSidebar();
    setupWindowControls();
    setupDrag();
    setupNavigation();
    setupAgentFilter();
    setupTimeRange();
    setupRefreshRate();
    setupSubscriptionDirect();
    setupSearch();
    setupTheme();
    setupTableSorting();
    setupSettings();
    setupKeyboardAndZoom();
    setupDynamicIsland();

    // Load initial settings and fetch
    loadSettings();
    refreshAll().finally(() => {
      if (typeof window.notifyAppReady === 'function') {
        window.notifyAppReady();
      }
    });

    // Heartbeat check for connection status
    setInterval(pollStatus, 4000);
  }

  // Apple Music Style Sidebar Controller (Dual-mode: Collapsed & Expanded)
  function setupSidebar() {
    const savedCollapsed = localStorage.getItem('tokenviewer_sidebar_collapsed');
    // 默认折叠状态 (首次打开或未设置时为 true)
    const isCollapsed = savedCollapsed === null ? true : savedCollapsed === '1';
    if (el.sidebar) {
      if (isCollapsed) el.sidebar.classList.add('collapsed');
      else el.sidebar.classList.remove('collapsed');
    }

    if (el.sidebarToggleBtn) {
      el.sidebarToggleBtn.addEventListener('click', () => {
        if (!el.sidebar) return;
        const nowCollapsed = el.sidebar.classList.toggle('collapsed');
        localStorage.setItem('tokenviewer_sidebar_collapsed', nowCollapsed ? '1' : '0');
        if (nowCollapsed || !(el.globalSearch && el.globalSearch.value.trim())) {
          hideSearchFlyout();
        }
        onSidebarResize();
      });
    }

    if (el.sidebarSearchBtn) {
      el.sidebarSearchBtn.addEventListener('click', () => {
        if (!el.sidebar) return;
        el.sidebar.classList.remove('collapsed');
        localStorage.setItem('tokenviewer_sidebar_collapsed', '0');
        onSidebarResize();
        setTimeout(() => {
          if (el.globalSearch) {
            el.globalSearch.focus();
            if (el.globalSearch.value.trim()) {
              handleGlobalSearch(el.globalSearch.value.trim());
            }
          }
        }, 120);
      });
    }
  }

  function onSidebarResize() {
    setTimeout(() => {
      if (consumptionChart) consumptionChart.resize();
      if (miniSparklineChart) miniSparklineChart.resize();
      if (miniCostChart) miniCostChart.resize();
      if (breakdownDonutChart) breakdownDonutChart.resize();
      window.dispatchEvent(new Event('resize'));
    }, 250);
  }

  // 1. Language System (Default Chinese, Switchable to English)
  function setupLanguage() {
    applyLanguage(state.lang);

    if (el.proLangSeg) {
      el.proLangSeg.querySelectorAll('button').forEach(btn => {
        if (btn.getAttribute('data-lang') === state.lang) btn.classList.add('active');
        else btn.classList.remove('active');

        btn.addEventListener('click', () => {
          el.proLangSeg.querySelectorAll('button').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          const lang = btn.getAttribute('data-lang');
          setLanguage(lang);
        });
      });
    }
  }

  function setLanguage(lang) {
    state.lang = lang;
    localStorage.setItem('tokenviewer_lang', lang);
    applyLanguage(lang);
    fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language: lang })
    }).catch(() => {});
    refreshAll();
  }

  function applyLanguage(lang) {
    document.documentElement.setAttribute('data-lang', lang);
    document.documentElement.setAttribute('lang', lang);

    // Update all text nodes with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(elem => {
      const key = elem.getAttribute('data-i18n');
      elem.textContent = t(key);
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-ph]').forEach(elem => {
      const key = elem.getAttribute('data-i18n-ph');
      elem.placeholder = t(key);
    });

    // Update title tooltips
    document.querySelectorAll('[data-i18n-title]').forEach(elem => {
      const key = elem.getAttribute('data-i18n-title');
      elem.title = t(key);
    });

    // Update Agent label
    if (!state.agent) {
      el.currentAgentName.textContent = t('allAgents');
    }

    // Update timeline subtitle
    updateTimelineLabel();

    // Update time token label
    updateTokenTimeLabel();

    // Rebuild charts with localized labels
    rebuildCharts();
  }

  function updateTimelineLabel() {
    const map = {
      'today': t('timelineToday'),
      '1d': t('timeline24h'),
      '7d': t('timeline7d'),
      '30d': t('timeline30d'),
      'all': t('timelineAll')
    };
    if (el.consumptionSubtitle) {
      el.consumptionSubtitle.textContent = map[state.range] || map['today'];
    }
  }

  function updateTokenTimeLabel() {
    const map = {
      'today': t('hrsToday'),
      '1d': t('hrs24'),
      '7d': t('days7'),
      '30d': t('days30'),
      'all': t('allTime')
    };
    if (el.tokenTimeLabel) {
      el.tokenTimeLabel.textContent = map[state.range] || map['today'];
    }
  }

  // 2. Windows-Native Window Controls (Top Right) & State Sync
  function updateWindowState(isMax, isFull) {
    const active = !!(isMax || isFull);
    state.isMax = !!isMax;
    state.isFull = !!isFull;
    document.body.classList.toggle('is-maximized', active);
    document.body.classList.toggle('is-fullscreen', !!isFull);

    if (el.iconMaximize && el.iconRestore) {
      if (active) {
        el.iconMaximize.style.display = 'none';
        el.iconRestore.style.display = 'inline-block';
        if (el.winMax) el.winMax.setAttribute('title', t('winRestore'));
      } else {
        el.iconMaximize.style.display = 'inline-block';
        el.iconRestore.style.display = 'none';
        if (el.winMax) el.winMax.setAttribute('title', t('winFullscreen') || t('winMax'));
      }
    }
  }
  window.onWindowStateChanged = updateWindowState;

  async function toggleFullscreen() {
    try {
      if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.toggle_fullscreen_or_maximize === 'function') {
        const isFull = await window.pywebview.api.toggle_fullscreen_or_maximize();
        updateWindowState(isFull, isFull);
      } else if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.toggle_fullscreen === 'function') {
        const isFull = await window.pywebview.api.toggle_fullscreen();
        updateWindowState(isFull, isFull);
      } else {
        const d = await fetch('/api/window/fullscreen', { method: 'POST' }).then(r => r.json()).catch(() => ({}));
        if (d.fullscreen) {
          updateWindowState(true, true);
        } else if (d.maximized) {
          updateWindowState(true, false);
        } else if (document.fullscreenElement) {
          if (document.exitFullscreen) await document.exitFullscreen();
          updateWindowState(false, false);
        } else if (document.documentElement.requestFullscreen) {
          await document.documentElement.requestFullscreen();
          updateWindowState(true, true);
        } else {
          const active = !state.isFull;
          updateWindowState(active, active);
        }
      }
    } catch (e) {
      console.error('toggleFullscreen error:', e);
    }
  }
  window.toggleFullscreen = toggleFullscreen;

  function setupWindowControls() {
    if (el.winClose) {
      el.winClose.addEventListener('click', () => {
        if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.exit_app === 'function') {
          window.pywebview.api.exit_app();
        } else {
          fetch('/api/window/close', { method: 'POST' }).catch(() => window.close());
        }
      });
    }
    if (el.winMin) {
      el.winMin.addEventListener('click', () => {
        if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.minimize === 'function') {
          window.pywebview.api.minimize();
        } else {
          fetch('/api/window/minimize', { method: 'POST' });
        }
      });
    }
    if (el.winMax) {
      el.winMax.addEventListener('click', async () => {
        await toggleFullscreen();
      });
    }
    if (el.topHeader) {
      el.topHeader.addEventListener('dblclick', (e) => {
        if (e.target.closest('input, button, a, .window-controls, .search-wrap, .time-pills')) return;
        if (el.winMax) el.winMax.click();
      });
    }

    // Query initial window state
    fetch('/api/window/state')
      .then(r => r.json())
      .then(d => {
        updateWindowState(d.maximized, d.fullscreen);
        if (typeof d.pinned !== 'undefined') updatePinState(d.pinned);
      })
      .catch(() => {});

    // Listen to resize with debounce
    let resizeTimer = null;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        fetch('/api/window/state')
          .then(r => r.json())
          .then(d => {
            updateWindowState(d.maximized, d.fullscreen);
            if (typeof d.pinned !== 'undefined') updatePinState(d.pinned);
          })
          .catch(() => {});
      }, 100);
    });
  }

  function setupDrag() {
    document.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return;
      if (!(window.pywebview && window.pywebview.api)) return;
      if (e.target.closest('button, a, input, textarea, select, .pricing-table-wrap, .pro-table, canvas, .dropdown-item, .window-controls, #dynamicIslandWrapper, #dynamicIsland')) return;
      window.pywebview.api.drag_begin();
      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
    });
  }

  function onMouseMove() {
    if (moveRaf) return;
    moveRaf = requestAnimationFrame(() => {
      moveRaf = null;
      if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.drag_move();
      }
    });
  }

  function onMouseUp() {
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.drag_end();
    }
  }

  // 3. Navigation
  function setupNavigation() {
    el.navItems.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetView = btn.getAttribute('data-view');
        switchView(targetView);
      });
    });

    if (el.openModelsCard) {
      el.openModelsCard.addEventListener('click', () => {
        state.sort.models = { key: 'tokens', asc: false };
        if (el.modelsThs) {
          el.modelsThs.forEach(th => {
            const k = th.getAttribute('data-key');
            th.classList.toggle('active', k === 'tokens');
            if (k === 'tokens') {
              th.textContent = `${t('thTokens')} ▾`;
            } else {
              const i18nKey = th.getAttribute('data-i18n');
              th.textContent = t(i18nKey);
            }
          });
        }
        switchView('models');
      });
    }
    if (el.openProjectsCard) {
      el.openProjectsCard.addEventListener('click', () => switchView('logs'));
    }
    if (el.openCostCard) {
      el.openCostCard.addEventListener('click', () => {
        state.sort.models = { key: 'cost', asc: false };
        if (el.modelsThs) {
          el.modelsThs.forEach(th => {
            const k = th.getAttribute('data-key');
            th.classList.toggle('active', k === 'cost');
            if (k === 'cost') {
              th.textContent = `${t('thCost')} ▾`;
            } else {
              const i18nKey = th.getAttribute('data-i18n');
              th.textContent = t(i18nKey);
            }
          });
        }
        switchView('models');
      });
    }
    if (el.openBreakdownCard) {
      el.openBreakdownCard.addEventListener('click', (e) => {
        if (e.target.closest('.legend-item')) return;
        switchView('logs');
      });
    }
    if (el.liveCard) {
      el.liveCard.addEventListener('click', () => refreshAll());
    }
  }

  function switchView(viewName) {
    state.view = viewName;
    el.navItems.forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-view') === viewName);
    });
    el.viewPanels.forEach(panel => {
      panel.classList.toggle('active', panel.id === `view-${viewName}`);
    });

    if (viewName === 'models') loadModelsTable();
    else if (viewName === 'logs') loadSessionsTable();
    else if (viewName === 'settings') loadSettings();
    else if (viewName === 'dashboard') {
      setTimeout(rebuildCharts, 40);
    }
  }

  // 4. Custom Avatar Management & Persistence
  function setupAvatar() {
    const savedAvatar = localStorage.getItem('tokenviewer_avatar');
    if (savedAvatar) {
      applyAvatar(savedAvatar);
    }

    if (el.userAvatarContainer) {
      el.userAvatarContainer.addEventListener('click', (e) => {
        e.stopPropagation();
        if (el.avatarFileInput) el.avatarFileInput.click();
      });
    }

    if (el.dropdownChangeAvatar) {
      el.dropdownChangeAvatar.addEventListener('click', (e) => {
        e.stopPropagation();
        if (el.agentDropdown) el.agentDropdown.hidden = true;
        if (el.avatarFileInput) el.avatarFileInput.click();
      });
    }

    if (el.dropdownResetAvatar) {
      el.dropdownResetAvatar.addEventListener('click', (e) => {
        e.stopPropagation();
        resetAvatar();
        if (el.agentDropdown) el.agentDropdown.hidden = true;
      });
    }

    if (el.avatarFileInput) {
      el.avatarFileInput.addEventListener('change', (e) => {
        const file = e.target.files && e.target.files[0];
        if (!file) return;
        if (!file.type.startsWith('image/')) {
          alert(state.lang === 'zh' ? '请选择图片文件 (PNG, JPG, WebP等)' : 'Please select an image file');
          return;
        }

        const reader = new FileReader();
        reader.onload = (evt) => {
          const img = new Image();
          img.onload = () => {
            // Compress & square crop to 256x256 max
            const canvas = document.createElement('canvas');
            const size = 256;
            canvas.width = size;
            canvas.height = size;
            const ctx = canvas.getContext('2d');
            
            const minSide = Math.min(img.width, img.height);
            const sx = (img.width - minSide) / 2;
            const sy = (img.height - minSide) / 2;
            
            ctx.drawImage(img, sx, sy, minSide, minSide, 0, 0, size, size);
            const dataUrl = canvas.toDataURL('image/png');
            
            applyAvatar(dataUrl);
            localStorage.setItem('tokenviewer_avatar', dataUrl);
            
            fetch('/api/settings', {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ avatar: dataUrl })
            }).catch(() => {});
          };
          img.src = evt.target.result;
        };
        reader.readAsDataURL(file);
        e.target.value = '';
      });
    }
  }

  function applyAvatar(dataUrl) {
    if (!dataUrl) {
      resetAvatar();
      return;
    }
    if (el.userCustomAvatar) {
      el.userCustomAvatar.src = dataUrl;
      el.userCustomAvatar.style.display = 'block';
    }
    if (el.userDefaultAvatarSvg) {
      el.userDefaultAvatarSvg.style.display = 'none';
    }
    if (el.dropdownResetAvatar) {
      el.dropdownResetAvatar.style.display = 'flex';
    }
  }

  function resetAvatar() {
    localStorage.removeItem('tokenviewer_avatar');
    if (el.userCustomAvatar) {
      el.userCustomAvatar.src = '';
      el.userCustomAvatar.style.display = 'none';
    }
    if (el.userDefaultAvatarSvg) {
      el.userDefaultAvatarSvg.style.display = 'flex';
    }
    if (el.dropdownResetAvatar) {
      el.dropdownResetAvatar.style.display = 'none';
    }
    fetch('/api/settings', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ avatar: "" })
    }).catch(() => {});
  }

  // 4.1 Agent Selector Filter
  function setAgentFilter(agentId) {
    state.agent = agentId || '';
    if (el.agentDropdown) {
      el.agentDropdown.querySelectorAll('.dropdown-item[data-agent]').forEach(d => {
        d.classList.toggle('active', (d.getAttribute('data-agent') || '') === state.agent);
      });
    }
    if (!state.agent) {
      if (el.currentAgentName) el.currentAgentName.textContent = t('allAgents');
    } else {
      const match = el.agentDropdown ? el.agentDropdown.querySelector(`.dropdown-item[data-agent="${state.agent}"]`) : null;
      if (el.currentAgentName) {
        el.currentAgentName.textContent = match ? match.textContent.split('(')[0].trim() : state.agent;
      }
    }
    refreshAll();
  }

  function setupAgentFilter() {
    if (!el.agentSelectorBtn) return;

    el.agentSelectorBtn.addEventListener('click', (e) => {
      // If user clicked the avatar container, that handles file upload
      if (e.target.closest('#userAvatarContainer')) return;
      e.stopPropagation();
      el.agentDropdown.hidden = !el.agentDropdown.hidden;
    });

    document.addEventListener('click', (e) => {
      if (!el.agentSelectorBtn.contains(e.target)) {
        el.agentDropdown.hidden = true;
      }
    });

    el.agentDropdown.querySelectorAll('.dropdown-item[data-agent]').forEach(item => {
      item.addEventListener('click', (e) => {
        e.stopPropagation();
        const agent = item.getAttribute('data-agent') || '';
        setAgentFilter(agent);
        el.agentDropdown.hidden = true;
      });
    });
  }

  // 5. Time Range Filter
  function setupTimeRange() {
    el.timeBtns.forEach(btn => {
      const r = btn.getAttribute('data-range');
      if (r === state.range) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }

      btn.addEventListener('click', () => {
        el.timeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.range = btn.getAttribute('data-range') || 'today';
        localStorage.setItem('tokenviewer_range', state.range);
        updateTimelineLabel();
        updateTokenTimeLabel();
        refreshAll();
      });
    });
  }

  // 5.1 Auto-Refresh Rate Control (3s / 30s / 60s, Default 60s)
  function setupRefreshRate() {
    const container = document.getElementById('refreshPills');
    if (!container) return;

    function updateActiveBtn(sec) {
      container.querySelectorAll('.refresh-btn').forEach(btn => {
        const bSec = parseInt(btn.getAttribute('data-refresh'), 10);
        if (bSec === sec) {
          btn.classList.add('active');
        } else {
          btn.classList.remove('active');
        }
      });
    }

    function applyInterval(sec) {
      state.refreshInterval = sec;
      localStorage.setItem('tokenviewer_refresh', sec.toString());
      updateActiveBtn(sec);

      if (dashboardTimer) {
        clearInterval(dashboardTimer);
      }
      dashboardTimer = setInterval(() => {
        if (state.view === 'dashboard') {
          fetchDashboard();
        }
      }, sec * 1000);
    }

    container.querySelectorAll('.refresh-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const sec = parseInt(btn.getAttribute('data-refresh'), 10);
        applyInterval(sec);
      });
    });

    applyInterval(state.refreshInterval || 60);
  }

  // 5.2 Direct Subscription Button Controller (放在主页直达套餐)
  function setupSubscriptionDirect() {
    if (!el.subDirectBtn) return;
    el.subDirectBtn.addEventListener('click', () => {
      const url = state.subscriptionUrl || (el.proSubUrl ? el.proSubUrl.value.trim() : '');
      if (url) {
        if (window.pywebview && window.pywebview.api && window.pywebview.api.open_subscription) {
          try {
            window.pywebview.api.open_subscription();
            return;
          } catch (e) {}
        }
        window.open(url, '_blank');
      } else {
        switchView('settings');
        if (el.proSubUrl) {
          el.proSubUrl.focus();
          el.proSubUrl.scrollIntoView({ behavior: 'smooth', block: 'center' });
          showPriceStatus(t('msgConfigureUrlFirst'));
        }
      }
    });
  }

  // Helper for vendor badge in search results
  function getVendorBadge(modelName) {
    const raw = (modelName || '').trim();
    const clean = (raw.includes('/') ? raw.split('/').pop() : raw).toLowerCase();
    if (clean.startsWith('claude')) return 'Anthropic';
    if (clean.startsWith('gpt') || clean.startsWith('o1') || clean.startsWith('o3')) return 'OpenAI';
    if (clean.startsWith('gemini')) return 'Google';
    if (clean.startsWith('deepseek')) return 'DeepSeek';
    if (clean.startsWith('qwen')) return 'Qwen';
    if (clean.startsWith('grok')) return 'xAI';
    if (clean.startsWith('glm')) return 'Zhipu';
    if (clean.startsWith('doubao')) return 'ByteDance';
    if (clean.startsWith('moonshot') || clean.startsWith('kimi')) return 'Moonshot';
    return 'AI Model';
  }

  function escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // Unified models cache for search
  let searchModelsCache = null;
  let searchCacheKey = '';
  let searchDebounceTimer = null;

  function currentSearchCacheKey() {
    return `${state.range}|${state.agent || ''}`;
  }

  async function fetchAllSearchModels() {
    try {
      let modelsUrl = `/api/models?range=${state.range}`;
      if (state.agent) modelsUrl += `&agent=${state.agent}`;
      const [modelsRes, pricingRes] = await Promise.all([
        fetch(modelsUrl).then(r => r.json()).catch(() => []),
        fetch('/api/pricing').then(r => r.json()).catch(() => [])
      ]);

      const map = new Map();
      (modelsRes || []).forEach(m => {
        const name = m.model || m.display_name || '';
        if (!name) return;
        map.set(name.toLowerCase(), {
          model: name,
          display_name: m.display_name || name,
          agent_type: m.agent_type || '',
          request_count: m.request_count || 0,
          tokens: m.tokens || 0,
          cache_hit_rate: m.cache_hit_rate || 0,
          cost: m.cost || 0
        });
      });

      (pricingRes || []).forEach(p => {
        const name = p.model || p.display_name || '';
        if (!name) return;
        const key = name.toLowerCase();
        if (!map.has(key)) {
          map.set(key, {
            model: name,
            display_name: p.display_name || name,
            agent_type: '',
            request_count: 0,
            tokens: 0,
            cache_hit_rate: 0,
            cost: 0
          });
        }
      });

      searchModelsCache = Array.from(map.values());
      searchCacheKey = currentSearchCacheKey();
      return searchModelsCache;
    } catch (err) {
      console.error('Failed to load search models:', err);
      return [];
    }
  }

  function hideSearchFlyout() {
    if (el.searchResultsFlyout) {
      el.searchResultsFlyout.hidden = true;
      el.searchResultsFlyout.style.display = 'none';
      el.searchResultsFlyout.classList.remove('active');
    }
  }

  function showSearchFlyout() {
    if (el.searchResultsFlyout) {
      el.searchResultsFlyout.hidden = false;
      el.searchResultsFlyout.style.display = 'flex';
      el.searchResultsFlyout.classList.add('active');
    }
  }

  async function handleGlobalSearch(query) {
    const q = (query || '').trim().toLowerCase();
    if (!q) {
      hideSearchFlyout();
      if (el.searchClearBtn) el.searchClearBtn.style.display = 'none';
      return;
    }

    if (el.searchClearBtn) el.searchClearBtn.style.display = 'flex';

    if (!searchModelsCache || searchCacheKey !== currentSearchCacheKey()) {
      await fetchAllSearchModels();
    }
    const models = searchModelsCache || [];

    // Fuzzy matching
    const matches = models.filter(m => {
      const target = `${m.model} ${m.display_name} ${getVendorBadge(m.model)}`.toLowerCase();
      const parts = q.split(/\s+/);
      return parts.every(p => target.includes(p));
    });

    matches.sort((a, b) => {
      if (b.tokens !== a.tokens) return b.tokens - a.tokens;
      if (b.request_count !== a.request_count) return b.request_count - a.request_count;
      return a.model.localeCompare(b.model);
    });

    if (el.searchMatchCount) {
      el.searchMatchCount.textContent = `${matches.length} ${t('resultsUnit') || '个结果'}`;
    }

    if (matches.length === 0) {
      el.searchFlyoutList.innerHTML = `
        <div class="search-no-result">
          <div style="font-size:12.5px; font-weight:600; color:var(--text-secondary); margin-bottom:4px;">${t('noMatchingModels') || '未找到匹配模型'}</div>
          <div style="font-size:11px; color:var(--text-muted);">"${escapeHtml(q)}"</div>
        </div>
      `;
      showSearchFlyout();
      return;
    }

    let html = '';
    matches.slice(0, 10).forEach(m => {
      const vendor = getVendorBadge(m.model);
      const reqFmt = (m.request_count || 0).toLocaleString();
      const tokenFmt = formatTokens(m.tokens || 0);
      const cacheFmt = formatPct(m.cache_hit_rate || 0);
      const costFmt = formatCost(m.cost || 0);

      html += `
        <div class="search-result-item" data-model="${escapeHtml(m.model)}">
          <div class="search-item-top">
            <span class="search-item-name">
              <b>${escapeHtml(m.display_name || m.model)}</b>
            </span>
            <span class="search-item-badge">${vendor}</span>
          </div>
          <div class="search-metrics-grid">
            <div class="search-metric-cell">
              <span class="search-m-lbl">${t('thRequests')}</span>
              <span class="search-m-val highlight">${reqFmt}</span>
            </div>
            <div class="search-metric-cell">
              <span class="search-m-lbl">${t('thTokens').replace(/[▾▴]/g, '').trim()}</span>
              <span class="search-m-val">${tokenFmt}</span>
            </div>
            <div class="search-metric-cell">
              <span class="search-m-lbl">${t('thCacheRate')}</span>
              <span class="search-m-val">${cacheFmt}</span>
            </div>
            <div class="search-metric-cell">
              <span class="search-m-lbl">${t('thCost')}</span>
              <span class="search-m-val highlight">${costFmt}</span>
            </div>
          </div>
        </div>
      `;
    });

    el.searchFlyoutList.innerHTML = html;
    showSearchFlyout();

    el.searchFlyoutList.querySelectorAll('.search-result-item').forEach(item => {
      item.addEventListener('click', () => {
        const modelName = item.getAttribute('data-model');
        hideSearchFlyout();
        switchView('models');
        if (el.globalSearch) {
          el.globalSearch.value = modelName;
          state.searchQuery = modelName.toLowerCase();
          renderModelsTable();
        }
      });
    });
  }

  // 6. Search
  function setupSearch() {
    if (!el.globalSearch) return;

    // 初始状态强制隐藏，仅输入文本后才展示
    hideSearchFlyout();

    el.globalSearch.addEventListener('input', (e) => {
      const val = e.target.value.trim();
      state.searchQuery = val.toLowerCase();
      if (state.view === 'models') renderModelsTable();
      else if (state.view === 'logs') renderSessionsTable();

      if (!val) {
        hideSearchFlyout();
        if (el.searchClearBtn) el.searchClearBtn.style.display = 'none';
        clearTimeout(searchDebounceTimer);
        return;
      }

      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        handleGlobalSearch(val);
      }, 100);
    });

    el.globalSearch.addEventListener('focus', () => {
      const val = el.globalSearch.value.trim();
      if (val) {
        handleGlobalSearch(val);
      } else {
        hideSearchFlyout();
      }
    });

    if (el.searchClearBtn) {
      el.searchClearBtn.addEventListener('click', () => {
        el.globalSearch.value = '';
        state.searchQuery = '';
        el.searchClearBtn.style.display = 'none';
        hideSearchFlyout();
        if (state.view === 'models') renderModelsTable();
        else if (state.view === 'logs') renderSessionsTable();
      });
    }

    document.addEventListener('click', (e) => {
      if (!e.target.closest('.search-expanded-box')) {
        hideSearchFlyout();
      }
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        hideSearchFlyout();
      }
    });
  }

  // 7. Theme System (Exclusively High-End Dark Obsidian Acrylic)
  function setupTheme() {
    localStorage.setItem('tokenviewer_theme', 'dark');
    applyTheme('dark');
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', 'dark');
  }

  // 8. Table Sorting
  function setupTableSorting() {
    el.modelsThs.forEach(th => {
      th.addEventListener('click', () => {
        const key = th.getAttribute('data-key');
        if (!key) return;
        if (state.sort.models.key === key) {
          state.sort.models.asc = !state.sort.models.asc;
        } else {
          state.sort.models.key = key;
          state.sort.models.asc = false;
        }
        updateThSortStyles(el.modelsThs, state.sort.models);
        renderModelsTable();
      });
    });

    el.sessionsThs.forEach(th => {
      th.addEventListener('click', () => {
        const key = th.getAttribute('data-key');
        if (!key) return;
        if (state.sort.sessions.key === key) {
          state.sort.sessions.asc = !state.sort.sessions.asc;
        } else {
          state.sort.sessions.key = key;
          state.sort.sessions.asc = false;
        }
        updateThSortStyles(el.sessionsThs, state.sort.sessions);
        renderSessionsTable();
      });
    });
  }

  function updateThSortStyles(ths, sortState) {
    ths.forEach(th => {
      const k = th.getAttribute('data-key');
      if (k === sortState.key) {
        th.classList.add('active');
        const text = th.textContent.replace(/[▾▴]/g, '').trim();
        th.textContent = `${text} ${sortState.asc ? '▴' : '▾'}`;
      } else {
        th.classList.remove('active');
        th.textContent = th.textContent.replace(/[▾▴]/g, '').trim();
      }
    });
  }

  // Data Refresh
  async function refreshAll() {
    await Promise.all([
      fetchDashboard(),
      pollStatus()
    ]);
    if (state.view === 'models') loadModelsTable();
    if (state.view === 'logs') loadSessionsTable();
  }

  async function pollStatus() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      // 顶栏精简后不再有状态指示元素，仅保留心跳探测
      if (el.connDot && el.connText) {
        if (data.is_alive) {
          el.connDot.className = 'pulse-dot on';
          el.connText.textContent = t('connected');
        } else {
          el.connDot.className = 'pulse-dot';
          el.connText.textContent = t('offline');
        }
      }
    } catch (e) {
      if (el.connDot && el.connText) {
        el.connDot.className = 'pulse-dot';
        el.connText.textContent = t('connecting');
      }
    }
  }

  async function fetchDashboard() {
    try {
      let url = `/api/dashboard?range=${state.range}`;
      if (state.agent) url += `&agent=${state.agent}`;
      const res = await fetch(url);
      const data = await res.json();
      state.dashboardData = data;
      renderDashboard(data);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
    }
  }

  function renderDashboard(data) {
    if (!data) return;

    // 1. Total Tokens
    const totalTokens = data.total_tokens || 0;
    animateNumber(el.dashTotalTokens, totalTokens, (v) => formatTokens(v));

    // 2. Active Projects
    const activeProjectsCount = (data.projects_breakdown || []).length || (data.active_projects_count || 1);
    animateNumber(el.dashActiveProjects, activeProjectsCount, (v) => Math.round(v));

    // 3. Cost Overview
    const totalCost = data.total_cost || 0;
    animateNumber(el.dashTotalCost, totalCost, (v) => formatCost(v));

    // 4. Rate
    if (data.timeline && data.timeline.length > 0) {
      let maxRate = 0;
      data.timeline.forEach(t => { if (t.tokens > maxRate) maxRate = t.tokens; });
      el.currentRate.textContent = `${formatTokens(maxRate)} ${t('rateUnit')}`;
    } else {
      el.currentRate.textContent = `0 ${t('rateUnit')}`;
    }

    // 5. Active Models Top 3
    renderActiveModels(data.models_breakdown || []);

    // 6. Token Usage KPIs
    renderTokenUsageKPIs(data);

    // 7. Charts
    renderConsumptionChart(data.timeline || []);
    renderSparkline(data.timeline || []);
    renderMiniCostChart(data.timeline || []);
    renderBreakdownDonut(data.projects_breakdown || []);
  }

  function renderActiveModels(models) {
    if (!models || models.length === 0) {
      el.activeModelsList.innerHTML = `<div class="model-line" style="color:var(--text-muted)">${t('noActiveModels')}</div>`;
      return;
    }

    const totalTokens = models.reduce((acc, m) => acc + (m.tokens || 0), 0) || 1;
    const top3 = models.slice(0, 3);
    const colors = ['cyan', 'indigo', 'purple'];

    let html = '';
    top3.forEach((m, idx) => {
      const pct = formatPct(m.tokens / totalTokens);
      const colorClass = colors[idx % colors.length];
      let displayName = m.label || m.name || 'Unknown';
      displayName = displayName.replace(/^models\//, '');
      html += `
        <div class="model-line">
          <div class="model-name-group">
            <span class="model-dot ${colorClass}"></span>
            <span title="${displayName}">${displayName}</span>
          </div>
          <span class="model-pct">${pct}</span>
        </div>
      `;
    });

    el.activeModelsList.innerHTML = html;
  }

  function renderTokenUsageKPIs(data) {
    const fresh = data.input_fresh || 0;
    const cacheRead = data.cache_read || 0;
    const output = data.output || 0;
    const hitRate = (fresh + cacheRead) > 0 ? (cacheRead / (fresh + cacheRead)) : 0;

    animateNumber(el.kpiFresh, fresh, (v) => formatTokens(v));
    animateNumber(el.kpiCacheRead, cacheRead, (v) => formatTokens(v));
    animateNumber(el.kpiOutput, output, (v) => formatTokens(v));
    animateNumber(el.kpiHitRate, hitRate * 100, (v) => formatPct(v / 100));
  }

  // Chart 1: Token Consumption Bar Chart (Smooth in-place updates)
  function renderConsumptionChart(timeline) {
    const canvas = document.getElementById('consumptionChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let labels = [];
    let dataPoints = [];

    // Map time string to tokens from timeline
    const tokenMap = {};
    if (timeline && Array.isArray(timeline)) {
      timeline.forEach(t => {
        if (t.time) tokenMap[t.time] = (tokenMap[t.time] || 0) + (t.tokens || 0);
      });
    }

    if (state.range === 'today') {
      // 00:00 to 23:00 for today (实时统计当日消耗量)
      for (let h = 0; h < 24; h++) {
        const hStr = (h < 10 ? '0' : '') + h + ':00';
        labels.push(hStr);
        dataPoints.push(tokenMap[hStr] || 0);
      }
    } else if (state.range === '1d') {
      // Rolling last 24 hours
      const nowH = new Date().getHours();
      for (let i = 23; i >= 0; i--) {
        const h = (nowH - i + 24) % 24;
        const hStr = (h < 10 ? '0' : '') + h + ':00';
        labels.push(hStr);
        dataPoints.push(tokenMap[hStr] || 0);
      }
    } else {
      // 7d, 30d, all
      if (timeline && timeline.length > 0) {
        labels = timeline.map(t => t.time || '');
        dataPoints = timeline.map(t => t.tokens || 0);
      } else {
        labels = ['--'];
        dataPoints = [0];
      }
    }

    const gridColor = 'rgba(255, 255, 255, 0.04)';
    const textColor = '#64748b';

    // Vertical gradient for bars: refined restrained steel-cyan to soft translucent base
    const barGradient = ctx.createLinearGradient(0, 0, 0, 160);
    barGradient.addColorStop(0, 'rgba(56, 189, 248, 0.88)');
    barGradient.addColorStop(1, 'rgba(56, 189, 248, 0.16)');

    const hoverGradient = ctx.createLinearGradient(0, 0, 0, 160);
    hoverGradient.addColorStop(0, '#38bdf8');
    hoverGradient.addColorStop(1, 'rgba(56, 189, 248, 0.35)');

    if (consumptionChart) {
      // In-place smooth dataset update - zero flicker!
      consumptionChart.data.labels = labels;
      consumptionChart.data.datasets[0].data = dataPoints;
      consumptionChart.update();
      return;
    }

    consumptionChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          data: dataPoints,
          backgroundColor: barGradient,
          hoverBackgroundColor: hoverGradient,
          borderRadius: 4,
          borderSkipped: false,
          maxBarThickness: 32,
          barPercentage: 0.65,
          categoryPercentage: 0.78
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 450,
          easing: 'easeOutQuart'
        },
        interaction: {
          intersect: false,
          mode: 'index'
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(15, 20, 32, 0.92)',
            titleColor: '#f8fafc',
            bodyColor: '#cbd5e1',
            borderColor: 'rgba(255, 255, 255, 0.12)',
            borderWidth: 1,
            padding: 8,
            cornerRadius: 8,
            displayColors: false,
            callbacks: {
              label: (ctx) => `Tokens: ${Math.round(ctx.parsed.y).toLocaleString()}`
            }
          }
        },
        scales: {
          x: {
            grid: { color: gridColor, drawBorder: false },
            ticks: { color: textColor, font: { size: 9.5 }, maxTicksLimit: 12 }
          },
          y: {
            grid: { color: gridColor, drawBorder: false, borderDash: [3, 3] },
            ticks: {
              color: textColor,
              font: { size: 9.5 },
              callback: (v) => formatTokens(v),
              maxTicksLimit: 4
            }
          }
        }
      }
    });
  }

  // Chart 2: Mini Sparkline
  function renderSparkline(timeline) {
    const canvas = document.getElementById('miniSparkline');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let finalData = [0, 0];
    if (timeline && timeline.length > 0) {
      finalData = timeline.map(t => t.tokens || 0);
      if (finalData.length === 1) finalData = [0, finalData[0]];
    }

    if (miniSparklineChart) {
      miniSparklineChart.data.labels = finalData.map((_, i) => i);
      miniSparklineChart.data.datasets[0].data = finalData;
      miniSparklineChart.update();
      return;
    }

    const fillGrad = ctx.createLinearGradient(0, 0, 0, 52);
    fillGrad.addColorStop(0, 'rgba(56, 189, 248, 0.36)');
    fillGrad.addColorStop(0.5, 'rgba(56, 189, 248, 0.12)');
    fillGrad.addColorStop(1, 'rgba(56, 189, 248, 0.00)');

    miniSparklineChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: finalData.map((_, i) => i),
        datasets: [{
          data: finalData,
          borderColor: '#38bdf8',
          borderWidth: 2,
          tension: 0.42,
          fill: true,
          backgroundColor: fillGrad,
          pointRadius: (context) => {
            const index = context.dataIndex;
            const count = context.dataset.data.length;
            return index === count - 1 ? 3 : 0;
          },
          pointBackgroundColor: '#ffffff',
          pointBorderColor: '#38bdf8',
          pointBorderWidth: 2,
          pointHoverRadius: 4,
          pointHoverBackgroundColor: '#38bdf8',
          pointHoverBorderColor: '#ffffff',
          pointHoverBorderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 350 },
        layout: {
          padding: { top: 4, bottom: 2, left: 2, right: 6 }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            displayColors: false,
            callbacks: {
              title: () => '',
              label: (ctx) => `${formatTokens(ctx.parsed.y)} tokens`
            },
            padding: 5,
            bodyFont: { size: 10.5, family: 'inherit', weight: '600' },
            cornerRadius: 5,
            backgroundColor: 'rgba(15, 23, 42, 0.92)',
            borderColor: 'rgba(56, 189, 248, 0.35)',
            borderWidth: 1
          }
        },
        scales: {
          x: { display: false },
          y: {
            display: false,
            grace: '12%'
          }
        }
      }
    });
  }

  // Chart 3: Mini Cost Wave Chart
  function renderMiniCostChart(timeline) {
    const canvas = document.getElementById('miniCostChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let costData = [0, 0];
    if (timeline && timeline.length > 0) {
      costData = timeline.map(t => t.cost || 0);
      if (costData.length === 1) costData = [0, costData[0]];
    }

    if (miniCostChart) {
      miniCostChart.data.labels = costData.map((_, i) => i);
      miniCostChart.data.datasets[0].data = costData;
      miniCostChart.update();
      return;
    }

    const strokeGrad = '#38bdf8';
    const fillGrad = ctx.createLinearGradient(0, 0, 0, 36);
    fillGrad.addColorStop(0, 'rgba(56, 189, 248, 0.22)');
    fillGrad.addColorStop(1, 'rgba(56, 189, 248, 0.0)');

    miniCostChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: costData.map((_, i) => i),
        datasets: [{
          data: costData,
          borderColor: strokeGrad,
          borderWidth: 1.8,
          pointRadius: 0,
          tension: 0.4,
          fill: true,
          backgroundColor: fillGrad
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 350 },
        plugins: { legend: { display: false }, tooltip: { enabled: false } },
        scales: {
          x: { display: false },
          y: { display: false }
        }
      }
    });
  }

  function handleDonutExternalTooltip(context) {
    let tooltipEl = document.getElementById('donutFloatingTooltip');
    if (!tooltipEl) {
      tooltipEl = document.createElement('div');
      tooltipEl.id = 'donutFloatingTooltip';
      tooltipEl.className = 'donut-floating-tooltip';
      document.body.appendChild(tooltipEl);
    }

    const tooltipModel = context.tooltip;
    if (!tooltipModel || tooltipModel.opacity === 0 || !tooltipModel.dataPoints || tooltipModel.dataPoints.length === 0) {
      tooltipEl.classList.remove('visible');
      if (el.breakdownLegend) {
        el.breakdownLegend.querySelectorAll('.legend-item').forEach(li => {
          li.classList.remove('highlighted', 'dimmed');
        });
      }
      return;
    }

    const idx = tooltipModel.dataPoints[0].dataIndex;
    const item = (currentBreakdownItems && currentBreakdownItems[idx]) || {
      name: tooltipModel.dataPoints[0].label,
      label: tooltipModel.dataPoints[0].label,
      tokens: tooltipModel.dataPoints[0].parsed
    };
    const total = currentBreakdownTotal || 1;
    const pct = total > 0 ? ((item.tokens / total) * 100).toFixed(0) + '%' : '0%';
    const color = (currentBreakdownColors && currentBreakdownColors[idx]) || '#38bdf8';
    const tokensStr = formatTokens(item.tokens || 0);
    const costStr = (item.cost && item.cost > 0) ? formatCost(item.cost) : null;

    tooltipEl.innerHTML = `
      <div class="dtt-row-top">
        <span class="dtt-dot" style="background:${color}"></span>
        <span class="dtt-title">${escapeHtml(item.label || item.name)}</span>
        <span class="dtt-pct">${pct}</span>
      </div>
      <div class="dtt-row-bottom">
        <span class="dtt-tokens">${tokensStr} Tokens</span>
        ${costStr ? `<span class="dtt-divider">·</span><span class="dtt-cost">${costStr}</span>` : ''}
      </div>
    `;

    const canvas = context.chart.canvas;
    const rect = canvas.getBoundingClientRect();
    const left = rect.left + rect.width / 2;
    const top = rect.top - 8;

    tooltipEl.style.left = `${left}px`;
    tooltipEl.style.top = `${top}px`;
    tooltipEl.classList.add('visible');

    if (el.breakdownLegend) {
      el.breakdownLegend.querySelectorAll('.legend-item').forEach((li) => {
        const itemIdx = parseInt(li.getAttribute('data-index'), 10);
        if (itemIdx === idx) {
          li.classList.add('highlighted');
          li.classList.remove('dimmed');
        } else {
          li.classList.add('dimmed');
          li.classList.remove('highlighted');
        }
      });
    }
  }

  // Chart 4: Project Breakdown Donut
  function renderBreakdownDonut(projects) {
    const canvas = document.getElementById('breakdownChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const toolColors = {
      'antigravity': '#38bdf8',
      'claude': '#f43f5e',
      'codex': '#8b5cf6',
      'zcode': '#10b981',
      'pi': '#f59e0b',
      'other': '#94a3b8'
    };

    let items = projects && projects.length > 0 ? projects : [
      { name: 'antigravity', label: 'Antigravity', tokens: 78 },
      { name: 'claude', label: 'Claude Code', tokens: 16 },
      { name: 'codex', label: 'Codex', tokens: 6 },
      { name: 'zcode', label: 'Zcode', tokens: 4 },
      { name: 'pi', label: 'Pi', tokens: 2 }
    ];

    const totalTokens = items.reduce((sum, item) => sum + (item.tokens || 0), 0) || 1;
    const labels = items.map(i => i.label || i.name);
    const data = items.map(i => i.tokens || 0);
    const bgColors = items.map(i => toolColors[(i.name || '').toLowerCase()] || '#818cf8');

    currentBreakdownItems = items;
    currentBreakdownTotal = totalTokens;
    currentBreakdownColors = bgColors;

    const hoverBorderColor = 'rgba(255, 255, 255, 0.6)';

    let legendHtml = '';
    items.forEach((item, idx) => {
      const pct = formatPct(item.tokens / totalTokens);
      const color = bgColors[idx];
      const isSelected = (state.agent && state.agent.toLowerCase() === (item.name || '').toLowerCase());
      legendHtml += `
        <div class="legend-item ${isSelected ? 'selected' : ''}" data-index="${idx}" data-agent="${escapeHtml(item.name || '')}" title="点击过滤 ${escapeHtml(item.label || item.name)}">
          <div class="legend-label">
            <span class="legend-dot" style="background:${color}"></span>
            <span>${escapeHtml(item.label || item.name)}</span>
          </div>
          <span class="legend-val">${pct}</span>
        </div>
      `;
    });
    if (el.breakdownLegend) {
      el.breakdownLegend.innerHTML = legendHtml;
      el.breakdownLegend.querySelectorAll('.legend-item').forEach(itemEl => {
        itemEl.addEventListener('click', (e) => {
          e.stopPropagation();
          const targetAgent = itemEl.getAttribute('data-agent') || '';
          if (state.agent && state.agent.toLowerCase() === targetAgent.toLowerCase()) {
            setAgentFilter('');
          } else {
            setAgentFilter(targetAgent);
          }
        });
        itemEl.addEventListener('mouseenter', () => {
          const idx = parseInt(itemEl.getAttribute('data-index'), 10);
          if (breakdownDonutChart) {
            breakdownDonutChart.setActiveElements([{ datasetIndex: 0, index: idx }]);
            breakdownDonutChart.tooltip.setActiveElements([{ datasetIndex: 0, index: idx }]);
            breakdownDonutChart.update();
          }
        });
        itemEl.addEventListener('mouseleave', () => {
          if (breakdownDonutChart) {
            breakdownDonutChart.setActiveElements([]);
            breakdownDonutChart.tooltip.setActiveElements([]);
            breakdownDonutChart.update();
          }
        });
      });
    }

    canvas.onclick = (e) => {
      if (!breakdownDonutChart) return;
      const points = breakdownDonutChart.getElementsAtEventForMode(e, 'nearest', { intersect: true }, true);
      if (points && points.length > 0) {
        e.stopPropagation();
        const idx = points[0].index;
        const item = currentBreakdownItems && currentBreakdownItems[idx];
        if (item) {
          const targetAgent = item.name || '';
          if (state.agent && state.agent.toLowerCase() === targetAgent.toLowerCase()) {
            setAgentFilter('');
          } else {
            setAgentFilter(targetAgent);
          }
        }
      }
    };

    if (breakdownDonutChart) {
      breakdownDonutChart.data.labels = labels;
      breakdownDonutChart.data.datasets[0].data = data;
      breakdownDonutChart.data.datasets[0].backgroundColor = bgColors;
      breakdownDonutChart.data.datasets[0].hoverBorderColor = hoverBorderColor;
      breakdownDonutChart.update();
      return;
    }

    breakdownDonutChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: bgColors,
          borderWidth: 0,
          hoverOffset: 0,
          hoverBorderWidth: 1.5,
          hoverBorderColor: hoverBorderColor
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 350 },
        cutout: '72%',
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: false,
            external: handleDonutExternalTooltip
          }
        }
      }
    });
  }

  function rebuildCharts() {
    if (consumptionChart) {
      consumptionChart.destroy();
      consumptionChart = null;
    }
    if (miniSparklineChart) {
      miniSparklineChart.destroy();
      miniSparklineChart = null;
    }
    if (miniCostChart) {
      miniCostChart.destroy();
      miniCostChart = null;
    }
    if (breakdownDonutChart) {
      breakdownDonutChart.destroy();
      breakdownDonutChart = null;
    }
    const tEl = document.getElementById('donutFloatingTooltip');
    if (tEl) tEl.classList.remove('visible');

    if (state.dashboardData) {
      renderConsumptionChart(state.dashboardData.timeline || []);
      renderSparkline(state.dashboardData.timeline || []);
      renderMiniCostChart(state.dashboardData.timeline || []);
      renderBreakdownDonut(state.dashboardData.projects_breakdown || []);
    }
  }

  // Model Monitor Table
  async function loadModelsTable() {
    try {
      let url = `/api/models?range=${state.range}`;
      if (state.agent) url += `&agent=${state.agent}`;
      const res = await fetch(url);
      const data = await res.json();
      state.modelsData = data || [];
      renderModelsTable();
    } catch (e) {
      console.error('Failed to load models table:', e);
    }
  }

  function renderModelsTable() {
    let list = [...state.modelsData];
    if (state.searchQuery) {
      list = list.filter(m => (m.display_name || m.model || '').toLowerCase().includes(state.searchQuery));
    }

    const { key, asc } = state.sort.models;
    list.sort((a, b) => {
      let va = a[key] !== undefined ? a[key] : '';
      let vb = b[key] !== undefined ? b[key] : '';
      if (key === '_label') {
        va = a.display_name || a.model || '';
        vb = b.display_name || b.model || '';
      }
      if (typeof va === 'number' && typeof vb === 'number') {
        return asc ? va - vb : vb - va;
      }
      return asc ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va));
    });

    let html = '';
    list.forEach(m => {
      const name = escapeHtml(m.display_name || m.model || 'Unknown');
      html += `
        <tr>
          <td title="${name}"><b>${name}</b></td>
          <td class="r">${(m.request_count || 0).toLocaleString()}</td>
          <td class="r">${formatTokens(m.tokens || 0)}</td>
          <td class="r">${formatPct(m.cache_hit_rate || 0)}</td>
          <td class="r">${formatCost(m.cost || 0)}</td>
        </tr>
      `;
    });

    el.modelsTable.innerHTML = html || `<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-muted)">${t('noModelData')}</td></tr>`;
  }

  // Sessions Table
  async function loadSessionsTable() {
    try {
      let url = `/api/sessions?range=${state.range}`;
      if (state.agent) url += `&agent=${state.agent}`;
      const res = await fetch(url);
      const data = await res.json();
      state.sessionsData = data || [];
      renderSessionsTable();
    } catch (e) {
      console.error('Failed to load sessions table:', e);
    }
  }

  function renderSessionsTable() {
    let list = [...state.sessionsData];
    if (state.searchQuery) {
      list = list.filter(s => (s.display_name || s.session_id || '').toLowerCase().includes(state.searchQuery));
    }

    const { key, asc } = state.sort.sessions;
    list.sort((a, b) => {
      let va = a[key] !== undefined ? a[key] : '';
      let vb = b[key] !== undefined ? b[key] : '';
      if (key === '_label') {
        va = a.display_name || a.session_id || '';
        vb = b.display_name || b.session_id || '';
      }
      if (typeof va === 'number' && typeof vb === 'number') {
        return asc ? va - vb : vb - va;
      }
      return asc ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va));
    });

    function formatTime(val) {
      if (!val) return '--';
      const d = typeof val === 'number' ? new Date(val > 1e11 ? val : val * 1000) : new Date(val);
      return isNaN(d.getTime()) ? String(val) : d.toLocaleString();
    }

    let html = '';
    list.forEach(s => {
      const rawName = s.cwd ? (s.cwd + ' (' + (s.display_name || s.session_id || '').substring(0, 8) + '...)') : (s.display_name || s.session_id || 'Session');
      const fullName = escapeHtml(s.cwd ? `${s.cwd} [${s.session_id}]` : (s.display_name || s.session_id || ''));
      const name = escapeHtml(rawName);
      const timeStr = formatTime(s.last_ts);
      html += `
        <tr>
          <td title="${fullName}"><b>${name}</b></td>
          <td class="r">${timeStr}</td>
          <td class="r">${formatTokens(s.tokens || 0)}</td>
          <td class="r">${formatPct(s.cache_hit_rate || 0)}</td>
          <td class="r">${formatCost(s.cost || 0)}</td>
        </tr>
      `;
    });

    el.sessionsTable.innerHTML = html || `<tr><td colspan="5" style="text-align:center;padding:20px;color:var(--text-muted)">${t('noLogData')}</td></tr>`;
  }

  // Settings
  async function loadSettings() {
    try {
      const [settingsRes, priceRes] = await Promise.all([
        fetch('/api/settings'),
        fetch('/api/pricing')
      ]);
      const settingsData = await settingsRes.json();
      const priceData = await priceRes.json();

      el.proSubUrl.value = settingsData.subscription_url || '';
      state.subscriptionUrl = settingsData.subscription_url || '';
      const urlLang = new URLSearchParams(window.location.search).get('lang');
      if (!urlLang && !localStorage.getItem('tokenviewer_lang') && settingsData.language) {
        state.lang = settingsData.language;
        applyLanguage(state.lang);
      }
      if (settingsData.avatar) {
        applyAvatar(settingsData.avatar);
      }
      state.pricingList = priceData || [];
      renderPricingTable();
    } catch (e) {
      console.error('Failed to load settings:', e);
    }
  }

  function renderPricingTable() {
    let html = '';
    state.pricingList.forEach(item => {
      const m = escapeHtml(item.model || '');
      html += `
        <div class="pricing-row" data-model="${m}">
          <input type="text" class="p-model-name" value="${m}" readonly title="${m}">
          <input type="number" step="any" min="0" class="p-fresh" value="${item.input_per_million || 0}" placeholder="0.00" title="${t('thPriceFresh')}">
          <input type="number" step="any" min="0" class="p-cache" value="${item.cache_read_per_million || 0}" placeholder="0.00" title="${t('thPriceCache')}">
          <input type="number" step="any" min="0" class="p-output" value="${item.output_per_million || 0}" placeholder="0.00" title="${t('thPriceOutput')}">
          <button class="pricing-del-btn" title="${t('thPriceAction') || '删除'}">✕</button>
        </div>
      `;
    });
    el.proPriceList.innerHTML = html || `<div style="color:var(--text-muted);padding:14px;text-align:center;font-size:12px;">暂无定价配置</div>`;

    el.proPriceList.querySelectorAll('.pricing-del-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const row = e.target.closest('.pricing-row');
        const model = row.getAttribute('data-model');
        if (model) {
          try {
            await fetch(`/api/pricing/${encodeURIComponent(model)}`, { method: 'DELETE' });
            row.remove();
            showPriceStatus(t('msgPriceDel'));
            refreshAll();
          } catch (err) {
            showPriceStatus('删除失败 / Delete failed');
          }
        } else {
          row.remove();
        }
      });
    });
  }

  function setupSettings() {
    if (el.proUrlSave) {
      el.proUrlSave.addEventListener('click', async () => {
        const url = el.proSubUrl.value.trim();
        if (url && !/^https?:\/\//i.test(url)) {
          showPriceStatus(state.lang === 'zh' ? '链接需以 http:// 或 https:// 开头' : 'URL must start with http:// or https://');
          return;
        }
        try {
          await fetch('/api/settings', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ subscription_url: url })
          });
          state.subscriptionUrl = url;
          showPriceStatus(t('msgUrlSaved'));
        } catch (e) {
          showPriceStatus('保存失败 / Save failed');
        }
      });
    }

    if (el.proPriceAdd) {
      el.proPriceAdd.addEventListener('click', () => {
        const row = document.createElement('div');
        row.className = 'pricing-row';
        row.innerHTML = `
          <input type="text" class="p-model-name" placeholder="模型标识 (如 gpt-5)" title="模型标识">
          <input type="number" step="any" min="0" class="p-fresh" value="0.00" placeholder="0.00" title="${t('thPriceFresh')}">
          <input type="number" step="any" min="0" class="p-cache" value="0.00" placeholder="0.00" title="${t('thPriceCache')}">
          <input type="number" step="any" min="0" class="p-output" value="0.00" placeholder="0.00" title="${t('thPriceOutput')}">
          <button class="pricing-del-btn" title="删除">✕</button>
        `;
        row.querySelector('.pricing-del-btn').addEventListener('click', () => row.remove());
        el.proPriceList.prepend(row);
        const nameInput = row.querySelector('.p-model-name');
        if (nameInput) nameInput.focus();
      });
    }

    if (el.proPriceSave) {
      el.proPriceSave.addEventListener('click', async () => {
        const rows = el.proPriceList.querySelectorAll('.pricing-row');
        showPriceStatus(t('msgSavingPrice'));

        try {
          const items = [];
          rows.forEach(r => {
            const model = r.querySelector('.p-model-name').value.trim();
            if (!model) return;
            items.push({
              model: model,
              display_name: model,
              input_per_million: parseFloat(r.querySelector('.p-fresh').value) || 0,
              cache_read_per_million: parseFloat(r.querySelector('.p-cache').value) || 0,
              cache_creation_per_million: 0,
              output_per_million: parseFloat(r.querySelector('.p-output').value) || 0,
              multiplier: 1.0
            });
          });
          if (items.length > 0) {
            await fetch('/api/pricing/batch', {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ items })
            });
          }
          showPriceStatus(t('msgPriceSaved'));
          refreshAll();
        } catch (e) {
          showPriceStatus('保存失败 / Save failed: ' + e.message);
        }
      });
    }

    if (el.proZoomSeg) {
      el.proZoomSeg.addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;
        const z = parseInt(btn.getAttribute('data-zoom'), 10);
        if (!isNaN(z)) applyZoom(z);
      });
    }
  }

  function applyZoom(percent) {
    percent = Math.min(Math.max(percent, 80), 180);
    state.zoom = percent;
    localStorage.setItem('tokenviewer_zoom', percent.toString());
    document.documentElement.style.zoom = (percent / 100).toString();

    if (el.proZoomSeg) {
      el.proZoomSeg.querySelectorAll('button').forEach(btn => {
        btn.classList.toggle('active', parseInt(btn.getAttribute('data-zoom'), 10) === percent);
      });
    }

    setTimeout(() => {
      if (typeof rebuildCharts === 'function') rebuildCharts();
    }, 60);
  }

  function setupKeyboardAndZoom() {
    // 1. 设置 Chart.js 默认 Retina 高像素比渲染，图表绝对清晰不模糊
    if (typeof Chart !== 'undefined' && Chart.defaults) {
      Chart.defaults.devicePixelRatio = Math.max(window.devicePixelRatio || 1, 1.5);
    }

    // 2. 应用保存或初始缩放
    applyZoom(state.zoom);

    // 3. 全局快捷键：F11 切全屏，Ctrl + / - / 0 缩放
    window.addEventListener('keydown', (e) => {
      if (e.key === 'F11') {
        e.preventDefault();
        toggleFullscreen();
        return;
      }
      if (e.ctrlKey || e.metaKey) {
        if (e.key === '=' || e.key === '+') {
          e.preventDefault();
          applyZoom(state.zoom + 10);
        } else if (e.key === '-' || e.key === '_') {
          e.preventDefault();
          applyZoom(state.zoom - 10);
        } else if (e.key === '0') {
          e.preventDefault();
          applyZoom(100);
        }
      }
    });

    // 4. Ctrl + 鼠标滚轮缩放
    window.addEventListener('wheel', (e) => {
      if (e.ctrlKey) {
        e.preventDefault();
        const delta = e.deltaY < 0 ? 5 : -5;
        applyZoom(state.zoom + delta);
      }
    }, { passive: false });
  }

  function showPriceStatus(msg) {
    el.proPriceStatus.textContent = msg;
    setTimeout(() => {
      if (el.proPriceStatus.textContent === msg) {
        el.proPriceStatus.textContent = '';
      }
    }, 4000);
  }

  // ==========================================================================
  // Apple 灵动岛风格桌面胶囊系统 (Apple Dynamic Island Desktop Capsule)
  // ==========================================================================
  function setupDynamicIsland() {
    if (!el.dynamicIsland || !el.dynamicIslandWrapper) return;

    let islandPollInterval = null;
    let isDragging = false;
    let startMouseX = 0;
    let startMouseY = 0;
    let islandMoveRaf = null;

    async function setWindowCapsuleMode(isCapsule) {
      // 优先通过 pywebview 原生 JS API 切换
      try {
        if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.set_capsule_mode === 'function') {
          return await window.pywebview.api.set_capsule_mode(isCapsule);
        }
      } catch (e) {
        console.warn('pywebview set_capsule_mode error:', e);
      }
      // 兜底 HTTP 接口调用
      try {
        const res = await fetch('/api/window/capsule', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_capsule: isCapsule })
        });
        const d = await res.json();
        return d.ok;
      } catch (e) {
        console.error('fetch /api/window/capsule error:', e);
      }
      return false;
    }

    async function enterCapsuleMode() {
      // 1. 先触发主窗口平滑向内收聚形变动效 (200ms)
      if (el.appWindow) {
        el.appWindow.classList.add('morphing-to-capsule');
      }
      await new Promise(r => setTimeout(r, 200));

      state.isCapsuleMode = true;
      document.body.classList.add('capsule-mode');
      el.dynamicIslandWrapper.style.display = 'flex';

      // 2. 灵动岛弹性展开涌现动效 (220ms)
      el.dynamicIsland.classList.add('island-emerging');
      setTimeout(() => {
        el.dynamicIsland.classList.remove('island-emerging');
      }, 260);

      if (el.appWindow) {
        el.appWindow.classList.remove('morphing-to-capsule');
      }

      await setWindowCapsuleMode(true);
      await pollIslandStatus();

      if (!islandPollInterval) {
        islandPollInterval = setInterval(pollIslandStatus, 1500);
      }
    }

    async function exitCapsuleMode() {
      // 1. 灵动岛向外虚化扩散动画 (160ms)
      el.dynamicIsland.classList.add('island-expanding');
      await new Promise(r => setTimeout(r, 160));

      state.isCapsuleMode = false;
      document.body.classList.remove('capsule-mode');
      el.dynamicIslandWrapper.style.display = 'none';
      el.dynamicIsland.classList.remove('island-expanding');

      if (islandPollInterval) {
        clearInterval(islandPollInterval);
        islandPollInterval = null;
      }

      // 2. 主窗口如花瓣般从灵动岛盛开绽放 (window-blooming)
      if (el.appWindow) {
        el.appWindow.classList.add('window-blooming');
        setTimeout(() => {
          el.appWindow.classList.remove('window-blooming');
        }, 320);
      }

      await setWindowCapsuleMode(false);

      setTimeout(() => {
        refreshAll();
        if (typeof rebuildCharts === 'function') rebuildCharts();
        window.dispatchEvent(new Event('resize'));
      }, 150);
    }

    async function pollIslandStatus() {
      try {
        const res = await fetch('/api/live_status');
        if (!res.ok) return;
        const data = await res.json();

        // 1. 当日 Token 消耗总量
        const tokens = data.today_tokens || 0;
        if (el.islandTodayTokens) {
          el.islandTodayTokens.textContent = formatTokens(tokens);
        }

        // 2. 当日总消费金额
        const cost = data.today_cost || 0;
        if (el.islandTodayCost) {
          el.islandTodayCost.textContent = formatCost(cost);
        }

        // 3. Apple 呼吸状态微珠：idle 翡翠绿 / active 科技天蓝 / burst 预警金橙
        if (el.islandGlowDot) {
          el.islandGlowDot.className = 'island-gem-core';
          if (data.status === 'burst') {
            el.islandGlowDot.classList.add('pulse-burst');
          } else if (data.status === 'active' || data.is_active || (data.speed_tokens_per_sec && data.speed_tokens_per_sec > 0)) {
            el.islandGlowDot.classList.add('pulse-active');
          } else {
            el.islandGlowDot.classList.add('pulse-idle');
          }
        }
      } catch (e) {
        // 静默捕获
      }
    }

    // 核心交互：【点击直接拖拽移动（无需长按）】
    // 使用 Pointer Events + setPointerCapture 确保即使鼠标高速移出胶囊窗体，拖拽依然极速响应且绝不丢帧
    el.dynamicIsland.addEventListener('pointerdown', (e) => {
      if (e.button !== 0) return;
      // 点击右侧还原按钮时不触发拖动
      if (e.target.closest('#islandRestoreBtn')) return;

      e.preventDefault();
      isDragging = true;
      el.dynamicIsland.classList.add('dragging-active');

      try {
        el.dynamicIsland.setPointerCapture(e.pointerId);
      } catch (_) {}

      if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.drag_begin === 'function') {
        window.pywebview.api.drag_begin();
      }
    });

    el.dynamicIsland.addEventListener('pointermove', (e) => {
      if (!isDragging) return;
      e.preventDefault();

      if (islandMoveRaf) return;
      islandMoveRaf = requestAnimationFrame(() => {
        islandMoveRaf = null;
        if (isDragging && window.pywebview && window.pywebview.api && typeof window.pywebview.api.drag_move === 'function') {
          window.pywebview.api.drag_move();
        }
      });
    });

    const onIslandPointerUp = (e) => {
      if (!isDragging) return;
      isDragging = false;
      el.dynamicIsland.classList.remove('dragging-active');

      if (islandMoveRaf) {
        cancelAnimationFrame(islandMoveRaf);
        islandMoveRaf = null;
      }

      try {
        if (e && typeof e.pointerId !== 'undefined' && el.dynamicIsland.hasPointerCapture(e.pointerId)) {
          el.dynamicIsland.releasePointerCapture(e.pointerId);
        }
      } catch (_) {}

      if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.drag_end === 'function') {
        window.pywebview.api.drag_end();
      }
    };

    el.dynamicIsland.addEventListener('pointerup', onIslandPointerUp);
    el.dynamicIsland.addEventListener('pointercancel', onIslandPointerUp);

    // 双击灵动岛：还原完整仪表盘大屏
    el.dynamicIsland.addEventListener('dblclick', (e) => {
      if (e.target.closest('#islandRestoreBtn')) return;
      exitCapsuleMode();
    });

    // 点击右上还原按钮
    if (el.islandRestoreBtn) {
      el.islandRestoreBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        exitCapsuleMode();
      });
    }

    // 顶栏胶囊切换按钮
    if (el.winCapsuleBtn) {
      el.winCapsuleBtn.addEventListener('click', () => {
        enterCapsuleMode();
      });
    }

    // 全局导出方法
    window.enterCapsuleMode = enterCapsuleMode;
    window.exitCapsuleMode = exitCapsuleMode;
  }

  window.addEventListener('DOMContentLoaded', init);
})();
