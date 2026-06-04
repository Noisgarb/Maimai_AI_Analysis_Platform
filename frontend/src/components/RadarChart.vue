<script setup>
import { computed } from "vue";

const props = defineProps({
  dimensions: {
    type: Array,
    default: () => []
  },
  size: {
    type: Number,
    default: 420
  }
});

const points = computed(() => {
  const dims = props.dimensions;
  if (!dims.length) return "";
  const cx = props.size / 2;
  const cy = props.size / 2;
  const radius = props.size * 0.35;
  return dims
    .map((d, i) => {
      const angle = (Math.PI * 2 * i) / dims.length - Math.PI / 2;
      const r = radius * (Number(d.score) / 100);
      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;
      return `${x},${y}`;
    })
    .join(" ");
});

const axis = computed(() => {
  const dims = props.dimensions;
  const cx = props.size / 2;
  const cy = props.size / 2;
  const radius = props.size * 0.35;
  return dims.map((d, i) => {
    const angle = (Math.PI * 2 * i) / dims.length - Math.PI / 2;
    return {
      x: cx + Math.cos(angle) * radius,
      y: cy + Math.sin(angle) * radius,
      name: d.name,
      score: d.score
    };
  });
});
</script>

<template>
  <div class="radar-wrap">
    <svg :width="size" :height="size" class="radar">
      <circle
        v-for="r in [0.2, 0.4, 0.6, 0.8, 1]"
        :key="r"
        :cx="size / 2"
        :cy="size / 2"
        :r="size * 0.35 * r"
        class="grid"
      />
      <line
        v-for="item in axis"
        :key="item.name"
        :x1="size / 2"
        :y1="size / 2"
        :x2="item.x"
        :y2="item.y"
        class="axis"
      />
      <polygon :points="points" class="shape" />
      <circle
        v-for="item in axis"
        :key="`${item.name}-dot`"
        :cx="item.x"
        :cy="item.y"
        r="4"
        class="dot"
      />
      <text
        v-for="item in axis"
        :key="`${item.name}-text`"
        :x="item.x"
        :y="item.y"
        class="label"
      >
        {{ item.name }} {{ Number(item.score).toFixed(0) }}
      </text>
    </svg>
  </div>
</template>

<style scoped>
.radar-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
}

.radar {
  background:
    radial-gradient(circle at 30% 25%, rgba(98, 171, 255, 0.12), transparent 40%),
    radial-gradient(circle at 80% 75%, rgba(192, 93, 255, 0.14), transparent 45%),
    radial-gradient(circle at center, #111629 0%, #0b1021 100%);
  border-radius: 16px;
  border: 1px solid rgba(102, 130, 215, 0.26);
}

.grid {
  fill: none;
  stroke: #2e3758;
  stroke-width: 1;
}

.axis {
  stroke: #3f4b77;
  stroke-width: 1;
}

.shape {
  fill: rgba(115, 165, 255, 0.32);
  stroke: #88b8ff;
  stroke-width: 2;
}

.dot {
  fill: #9ed0ff;
}

.label {
  fill: #e4edff;
  font-size: 11px;
  paint-order: stroke;
  stroke: rgba(8, 14, 30, 0.8);
  stroke-width: 2px;
  stroke-linejoin: round;
}
</style>
