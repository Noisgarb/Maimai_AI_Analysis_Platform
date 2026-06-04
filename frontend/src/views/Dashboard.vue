<script setup>
import { computed, onBeforeUnmount, ref } from "vue";
import axios from "axios";
import html2canvas from "html2canvas";
import RadarChart from "../components/RadarChart.vue";

const apiBase = ref("http://127.0.0.1:8000");
const username = ref("");
const qq = ref("");
const loading = ref(false);
const error = ref("");
const result = ref(null);
const recommendLoading = ref(false);
const recommendError = ref("");
const recommendData = ref(null);
const activeTab = ref("overview");
const queryProgress = ref(0);
const b50Tab = ref("B35");
const exportLoading = ref(false);
const exportTarget = ref(null);
let progressTimer = null;

const dimensionRank = computed(() => {
  const dims = result.value?.radar?.dimensions || [];
  return [...dims].sort((a, b) => Number(b.score) - Number(a.score));
});

const b50Items = computed(() => result.value?.b50 || []);
const b35Items = computed(() => result.value?.b35 || []);
const b15Items = computed(() => result.value?.b15 || []);
const currentBItems = computed(() => (b50Tab.value === "B15" ? b15Items.value : b35Items.value));

function startProgress() {
  queryProgress.value = 8;
  if (progressTimer) clearInterval(progressTimer);
  progressTimer = setInterval(() => {
    if (queryProgress.value < 92) {
      queryProgress.value += Math.floor(Math.random() * 8) + 2;
    }
    if (queryProgress.value > 92) {
      queryProgress.value = 92;
    }
  }, 260);
}

function finishProgress() {
  if (progressTimer) {
    clearInterval(progressTimer);
    progressTimer = null;
  }
  queryProgress.value = 100;
  setTimeout(() => {
    queryProgress.value = 0;
  }, 500);
}

async function submitAnalyze() {
  error.value = "";
  result.value = null;
  recommendError.value = "";
  recommendData.value = null;
  if (!username.value && !qq.value) {
    error.value = "请至少输入用户名或QQ号";
    return;
  }
  loading.value = true;
  startProgress();
  try {
    const payload = { b50: "1" };
    if (username.value) payload.username = username.value;
    if (qq.value) payload.qq = qq.value;
    const resp = await axios.post(`${apiBase.value}/analysis/b50`, payload);
    result.value = resp.data;
    await fetchRecommend(payload);
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || "分析失败";
  } finally {
    finishProgress();
    loading.value = false;
  }
}

async function fetchRecommend(payload = null) {
  recommendError.value = "";
  recommendLoading.value = true;
  try {
    const reqPayload = payload || { b50: "1" };
    if (!payload) {
      if (username.value) reqPayload.username = username.value;
      if (qq.value) reqPayload.qq = qq.value;
    }
    const resp = await axios.post(`${apiBase.value}/analysis/recommend`, reqPayload);
    recommendData.value = resp.data;
  } catch (e) {
    recommendError.value = e?.response?.data?.detail || e.message || "获取推荐失败";
  } finally {
    recommendLoading.value = false;
  }
}

onBeforeUnmount(() => {
  if (progressTimer) clearInterval(progressTimer);
});

function difficultyClass(levelLabel) {
  if (!levelLabel) return "diff-unknown";
  const lv = String(levelLabel).toLowerCase();
  if (lv.includes("basic")) return "diff-basic";
  if (lv.includes("advance")) return "diff-advanced";
  if (lv.includes("expert")) return "diff-expert";
  if (lv.includes("master")) return "diff-master";
  if (lv.includes("re:master") || lv.includes("remaster")) return "diff-remaster";
  if (lv.includes("14+") || lv.includes("15")) return "diff-remaster";
  if (lv.includes("13") || lv.includes("14")) return "diff-master";
  if (lv.includes("12")) return "diff-expert";
  if (lv.includes("10") || lv.includes("11")) return "diff-advanced";
  return "diff-basic";
}

function rateClass(rate) {
  const r = String(rate || "").toLowerCase();
  if (r.includes("sss+")) return "rate-ssspp";
  if (r.includes("sss")) return "rate-sss";
  if (r.includes("ss+")) return "rate-sspp";
  if (r.includes("ss")) return "rate-ss";
  if (r.includes("s+")) return "rate-spp";
  if (r.includes("s")) return "rate-s";
  return "rate-default";
}

function rateLabel(rate) {
  const r = String(rate || "").toLowerCase();
  const map = {
    d: "D",
    c: "C",
    b: "B",
    bb: "BB",
    bbb: "BBB",
    a: "A",
    aa: "AA",
    aaa: "AAA",
    s: "S",
    sp: "S+",
    ss: "SS",
    ssp: "SS+",
    sss: "SSS",
    sssp: "SSS+"
  };
  return map[r] || String(rate || "-").toUpperCase();
}

async function exportB50Image() {
  if (!exportTarget.value || !result.value) return;
  exportLoading.value = true;
  try {
    const canvas = await html2canvas(exportTarget.value, {
      backgroundColor: "#070b18",
      scale: 2,
      useCORS: true
    });
    const link = document.createElement("a");
    const name = result.value.player_id || "player";
    link.download = `b50-overview-${name}.png`;
    link.href = canvas.toDataURL("image/png");
    link.click();
  } finally {
    exportLoading.value = false;
  }
}
</script>

<template>
  <div class="page">
    <header class="top card">
      <p class="eyebrow">MAIMAI ANALYSIS STATION</p>
      <h1>舞萌 B50 六维分析平台</h1>
      <p>接入水鱼查分器，自动产出六维能力图、短板定位与阶段训练建议</p>
    </header>

    <section class="card form">
      <div class="form-grid">
        <label>后端地址</label>
        <input v-model="apiBase" placeholder="http://127.0.0.1:8000" />
        <label>水鱼用户名</label>
        <input v-model="username" placeholder="例如：player_name" />
        <label>QQ号</label>
        <input v-model="qq" placeholder="例如：123456789" />
      </div>
      <button :disabled="loading" @click="submitAnalyze">
        {{ loading ? "分析中..." : "开始分析" }}
      </button>
      <div v-if="loading" class="progress-wrap">
        <div class="progress-bar">
          <div class="progress-inner" :style="{ width: `${queryProgress}%` }"></div>
        </div>
        <p class="progress-text">正在查询并分析 B50 数据... {{ queryProgress }}%</p>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </section>

    <section v-if="error && !result" class="card empty-tip">
      <h3>暂时没有查到可用数据</h3>
      <p>可能原因：</p>
      <ul>
        <li>玩家关闭了查分器隐私，或未绑定/未同步成绩</li>
        <li>用户名或 QQ 号输入有误</li>
        <li>水鱼接口临时限流或网络波动</li>
      </ul>
      <p>建议：检查账号信息后重试，或稍后再查询。</p>
    </section>

    <section v-if="result" class="layout">
      <div class="card">
        <div class="title-row">
          <h3>六维实力图</h3>
          <span class="rating-chip">RATING {{ result.rating ?? "-" }}</span>
        </div>
        <RadarChart :dimensions="result.radar.dimensions" />
      </div>
      <div class="card">
        <h3>能力摘要</h3>
        <p>玩家：{{ result.player_id }}</p>
        <p>强项：{{ result.radar.strengths.join(" / ") }}</p>
        <p>短板：{{ result.radar.shortfalls.join(" / ") }}</p>
        <div class="tabs">
          <button :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">
            维度排行
          </button>
          <button :class="{ active: activeTab === 'advice' }" @click="activeTab = 'advice'">
            提升建议
          </button>
        </div>
        <div v-if="activeTab === 'overview'" class="dimension-list">
          <article v-for="item in dimensionRank" :key="item.key" class="dimension-item">
            <p>{{ item.name }}</p>
            <strong>{{ Number(item.score).toFixed(1) }}</strong>
          </article>
        </div>
        <div v-else>
        <article v-for="item in result.advice" :key="item.horizon" class="advice">
          <h5>{{ item.title }}</h5>
          <p>{{ item.detail }}</p>
          <p class="songs">推荐标签：{{ item.songs.join("、") || "无" }}</p>
        </article>
        </div>
      </div>
    </section>

    <section v-if="result" ref="exportTarget" class="card b50-card">
      <div class="title-row">
        <h3>B50 总览</h3>
        <div class="b50-actions">
          <span class="rating-chip">共 {{ b50Items.length }} 首</span>
          <button class="export-btn" :disabled="exportLoading" @click="exportB50Image">
            {{ exportLoading ? "导出中..." : "导出总览图" }}
          </button>
        </div>
      </div>
      <div class="tabs b50-tabs">
        <button :class="{ active: b50Tab === 'B35' }" @click="b50Tab = 'B35'">
          B35（旧曲）{{ b35Items.length }}
        </button>
        <button :class="{ active: b50Tab === 'B15' }" @click="b50Tab = 'B15'">
          B15（新曲）{{ b15Items.length }}
        </button>
      </div>
      <div v-if="currentBItems.length" class="b50-grid">
        <article v-for="(item, idx) in currentBItems" :key="`${item.song_id}-${idx}`" class="b50-item">
          <img
            class="cover"
            :src="item.cover_url || 'https://www.diving-fish.com/covers/0.png'"
            :alt="item.title"
            loading="lazy"
          />
          <div class="b50-body">
            <h4>
              <span class="rank">#{{ idx + 1 }}</span>
              <span class="song-title">{{ item.title }}</span>
            </h4>
            <p class="meta">
              <span class="badge badge-type">{{ item.type || "-" }}</span>
              <span class="badge" :class="difficultyClass(item.level_label)">{{ item.level_label || "-" }}</span>
              <span class="badge badge-segment">{{ item.segment || b50Tab }}</span>
              <span>DS {{ item.ds ?? "-" }}</span>
              <span>RA {{ item.ra ?? "-" }}</span>
            </p>
            <p class="meta">
              <span>达成率 {{ item.achievements ?? "-" }}%</span>
              <span class="badge" :class="rateClass(item.rate)">评价 {{ rateLabel(item.rate) }}</span>
              <span>DX {{ item.dx_score ?? "-" }}</span>
            </p>
            <p class="meta">
              <span class="badge badge-fc">FC {{ item.fc || "-" }}</span>
              <span class="badge badge-fs">FS {{ item.fs || "-" }}</span>
            </p>
          </div>
        </article>
      </div>
      <div v-else class="b50-empty">
        <p>该玩家当前没有可展示的 {{ b50Tab }} 明细。</p>
        <p>请确认已同步成绩，且未开启“禁止他人查询成绩”等隐私设置。</p>
      </div>
    </section>

    <section v-if="result" class="card recommend-card">
      <div class="title-row">
        <h3>训练推荐</h3>
        <button class="export-btn" :disabled="recommendLoading" @click="fetchRecommend()">
          {{ recommendLoading ? "刷新中..." : "刷新推荐" }}
        </button>
      </div>
      <p v-if="recommendError" class="error">{{ recommendError }}</p>
      <div v-else-if="recommendData">
        <p class="recommend-head">
          短板维度：{{ (recommendData.shortfalls || []).join(" / ") || "-" }}
          <span class="recommend-source">来源：{{ recommendData.source || "-" }}</span>
        </p>
        <div class="recommend-grid">
          <article
            v-for="(item, idx) in recommendData.items || []"
            :key="`${item.song_id}-${idx}`"
            class="recommend-item"
          >
            <strong>{{ idx + 1 }}. {{ item.title }}</strong>
            <p>{{ item.difficulty }} / {{ item.level }} / DS {{ item.ds }}</p>
          </article>
        </div>
        <p v-if="recommendData.warning" class="recommend-warning">
          提示：{{ recommendData.warning }}
        </p>
      </div>
      <p v-else class="recommend-empty">暂无推荐结果，点击“刷新推荐”获取。</p>
    </section>
  </div>
</template>

<style scoped>
.page {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px;
  color: #f2f5ff;
  background:
    radial-gradient(circle at 20% 10%, #1f3f78 0%, transparent 30%),
    radial-gradient(circle at 85% 20%, #57257a 0%, transparent 35%),
    #070b18;
  min-height: 100vh;
  font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 12px;
  letter-spacing: 1.2px;
  color: #9cb9ff;
}

.top h1 {
  margin: 0 0 8px;
  font-size: 36px;
  letter-spacing: 0.4px;
}

.top p {
  color: #c9d7ff;
  margin: 0;
}

.card {
  background: linear-gradient(155deg, rgba(18, 25, 50, 0.88), rgba(13, 19, 41, 0.93));
  border: 1px solid rgba(114, 139, 212, 0.32);
  border-radius: 18px;
  padding: 18px;
  margin-top: 16px;
  box-shadow: 0 14px 35px rgba(0, 0, 0, 0.32);
}

.form {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

label {
  font-size: 13px;
  color: #a8beff;
}

input {
  height: 40px;
  border-radius: 10px;
  border: 1px solid #354b8b;
  background: rgba(10, 16, 34, 0.7);
  color: #edf2ff;
  padding: 0 12px;
}

button {
  margin-top: 10px;
  height: 42px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(90deg, #3a8dff, #7d53ff 58%, #d24fff);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(81, 129, 255, 0.35);
}

button:disabled {
  opacity: 0.7;
}

.layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.rating-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 12px;
  border: 1px solid #4c72d8;
  border-radius: 999px;
  font-size: 12px;
  color: #b8cdff;
  background: rgba(16, 35, 80, 0.6);
}

.tabs {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.tabs button {
  margin-top: 0;
  height: 34px;
  padding: 0 14px;
  border: 1px solid #38539c;
  border-radius: 999px;
  background: rgba(21, 33, 65, 0.9);
  color: #bdd0ff;
  box-shadow: none;
}

.tabs button.active {
  background: linear-gradient(90deg, #3d7aff, #7f58ff);
  border-color: transparent;
  color: #fff;
}

.dimension-list {
  margin-top: 10px;
}

.dimension-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #2f437f;
  background: rgba(8, 15, 35, 0.7);
}

.dimension-item p {
  margin: 0;
  color: #d8e4ff;
}

.advice {
  margin-top: 10px;
  padding: 12px;
  background: rgba(13, 20, 48, 0.9);
  border-radius: 10px;
  border: 1px solid #2d3a63;
}

.advice h5,
.advice p {
  margin: 6px 0;
}

.songs {
  color: #9fb7ff;
}

.error {
  color: #ff8f8f;
  margin: 0;
}

.progress-wrap {
  margin-top: 8px;
}

.progress-bar {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  background: rgba(30, 45, 86, 0.85);
  border: 1px solid #3554a5;
  overflow: hidden;
}

.progress-inner {
  height: 100%;
  background: linear-gradient(90deg, #33b1ff, #7378ff, #d84eff);
  transition: width 0.25s ease;
}

.progress-text {
  margin: 6px 0 0;
  font-size: 12px;
  color: #aecaFF;
}

.empty-tip h3 {
  margin: 0 0 8px;
}

.empty-tip p {
  margin: 6px 0;
}

.empty-tip ul {
  margin: 6px 0 8px;
  padding-left: 18px;
  color: #c8d8ff;
}

.b50-card {
  margin-top: 18px;
}

.b50-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.export-btn {
  margin-top: 0;
  height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid #4e66ab;
  background: rgba(17, 28, 59, 0.95);
  color: #d7e4ff;
  font-size: 12px;
}

.b50-tabs {
  margin-top: 12px;
}

.b50-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.b50-item {
  display: flex;
  gap: 12px;
  border: 1px solid #2f437f;
  background: rgba(8, 15, 35, 0.8);
  border-radius: 12px;
  padding: 10px;
}

.cover {
  width: 88px;
  height: 88px;
  object-fit: cover;
  border-radius: 10px;
  border: 1px solid #3d5397;
  background: #111;
}

.b50-body {
  min-width: 0;
}

.b50-body h4 {
  margin: 0 0 6px;
  font-size: 14px;
  line-height: 1.3;
  display: flex;
  align-items: center;
  gap: 8px;
}

.rank {
  display: inline-flex;
  min-width: 38px;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid #3b56a3;
  background: rgba(16, 30, 68, 0.85);
  color: #9fc2ff;
  font-size: 12px;
  padding: 2px 6px;
}

.song-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta {
  margin: 4px 0 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  color: #b9c9f6;
  font-size: 12px;
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid #44588f;
  padding: 1px 8px;
  background: rgba(20, 28, 54, 0.8);
}

.badge-type {
  border-color: #4e6ebf;
  color: #b9ceff;
}

.badge-segment {
  border-color: #7d66dc;
  color: #d0beff;
}

.badge-fc {
  border-color: #3fa989;
  color: #8ff7d7;
}

.badge-fs {
  border-color: #4a95c9;
  color: #9fdaff;
}

.diff-basic {
  border-color: #4ea0ff;
  color: #b8dbff;
}

.diff-advanced {
  border-color: #5cc68d;
  color: #c8ffe1;
}

.diff-expert {
  border-color: #f08a3e;
  color: #ffd4b0;
}

.diff-master {
  border-color: #b26bff;
  color: #e1caff;
}

.diff-remaster {
  border-color: #ff6aa8;
  color: #ffc8df;
}

.diff-unknown {
  border-color: #68779d;
  color: #c3cde0;
}

.rate-ssspp,
.rate-sss {
  border-color: #ffd76a;
  color: #ffe8a3;
}

.rate-sspp,
.rate-ss {
  border-color: #7eb8ff;
  color: #cde4ff;
}

.rate-spp,
.rate-s {
  border-color: #8ad9a3;
  color: #d4ffe1;
}

.rate-default {
  border-color: #8491ae;
  color: #c3cee2;
}

.b50-empty {
  margin-top: 12px;
  border: 1px dashed #39509a;
  background: rgba(10, 18, 42, 0.7);
  border-radius: 12px;
  padding: 14px;
  color: #c9d8ff;
}

.b50-empty p {
  margin: 6px 0;
}

.recommend-card {
  margin-top: 16px;
}

.recommend-head {
  margin: 10px 0;
  color: #c9d8ff;
}

.recommend-source {
  margin-left: 12px;
  color: #98b1ff;
  font-size: 12px;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.recommend-item {
  border: 1px solid #2f437f;
  background: rgba(8, 15, 35, 0.78);
  border-radius: 10px;
  padding: 10px 12px;
}

.recommend-item strong {
  font-size: 13px;
}

.recommend-item p {
  margin: 6px 0 0;
  color: #b9c9f6;
  font-size: 12px;
}

.recommend-warning {
  margin: 10px 0 0;
  color: #ffcf9e;
  font-size: 12px;
}

.recommend-empty {
  margin: 10px 0 0;
  color: #b9c9f6;
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .b50-grid {
    grid-template-columns: 1fr;
  }

  .recommend-grid {
    grid-template-columns: 1fr;
  }
}
</style>
