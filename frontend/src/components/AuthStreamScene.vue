<template>
  <section class="auth-stream-scene" aria-hidden="true">
    <div class="scene-grid"></div>
    <div class="scene-copy">
      <span class="stream-copy stream-copy-title" :style="copyStyle(title, zeroDelay)">
        {{ title }}
      </span>
      <span
        v-for="(line, index) in descriptionLines"
        :key="`${index}-${line}`"
        class="stream-copy stream-copy-description"
        :style="copyStyle(line, `${0.85 + index * 0.7}s`)"
      >
        {{ line }}
      </span>
    </div>
    <span
      v-for="item in keywordNodes"
      :key="item.text"
      class="scene-keyword"
      :style="item.style"
    >
      {{ item.text }}
    </span>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  descriptionLines: {
    type: Array,
    default: () => [],
  },
  keywords: {
    type: Array,
    default: () => [],
  },
})

const zeroDelay = '0s'
const viewportWidth = ref(typeof window === 'undefined' ? 1440 : window.innerWidth)
const keywordSlots = [
  {
    desktop: { left: 'clamp(208px, 24vw, 340px)', top: '41%' },
    tablet: { left: '164px', top: '40%' },
    mobile: null,
  },
  {
    desktop: { left: 'clamp(228px, 26vw, 368px)', bottom: 'clamp(62px, 13vh, 110px)' },
    tablet: { left: '182px', bottom: '50px' },
    mobile: null,
  },
  {
    desktop: { right: 'clamp(198px, 24vw, 340px)', top: 'clamp(96px, 17vh, 160px)' },
    tablet: { right: '168px', top: '40px' },
    mobile: null,
  },
  {
    desktop: { right: 'clamp(224px, 26vw, 376px)', top: '47%' },
    tablet: { right: '186px', bottom: '116px' },
    mobile: { right: '44px', bottom: '32px' },
  },
  {
    desktop: { right: 'clamp(208px, 24vw, 342px)', bottom: 'clamp(56px, 12vh, 98px)' },
    tablet: null,
    mobile: null,
  },
  {
    desktop: { left: 'clamp(246px, 28vw, 392px)', top: '58%' },
    tablet: null,
    mobile: null,
  },
]

function updateViewportWidth() {
  viewportWidth.value = window.innerWidth
}

onMounted(() => {
  updateViewportWidth()
  window.addEventListener('resize', updateViewportWidth)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateViewportWidth)
})

function estimateWidth(text) {
  let width = 0
  for (const char of text) {
    width += /[A-Za-z0-9 ]/.test(char) ? 0.72 : 1.06
  }
  return `${Math.max(width + 1.5, 10)}em`
}

function copyStyle(text, delay) {
  return {
    '--stream-width': estimateWidth(text),
    '--stream-delay': delay,
  }
}

function hashText(text) {
  let hash = 0
  for (const char of text) {
    hash = ((hash << 5) - hash) + char.charCodeAt(0)
    hash |= 0
  }
  return Math.abs(hash)
}

function shuffledSlots(seed) {
  const pool = [...keywordSlots]
  let state = (seed || 1) % 2147483647
  if (state <= 0) state += 2147483646

  for (let index = pool.length - 1; index > 0; index -= 1) {
    state = (state * 48271) % 2147483647
    const swapIndex = state % (index + 1)
    ;[pool[index], pool[swapIndex]] = [pool[swapIndex], pool[index]]
  }
  return pool
}

const keywordNodes = computed(() => {
  const width = viewportWidth.value
  const stage = width <= 920 ? 'mobile' : width <= 1260 ? 'tablet' : 'desktop'
  const slots = shuffledSlots(hashText(`${props.title}-${props.keywords.join('|')}`))
  const availableSlots = slots.filter((slot) => slot[stage])
  return props.keywords.slice(0, 4).map((text, index) => {
    const slot = availableSlots[index % Math.max(availableSlots.length, 1)]?.[stage]
    if (!slot) {
      return {
        text,
        style: {
          display: 'none',
        },
      }
    }
    return {
      text,
      style: {
        '--stream-width': estimateWidth(text),
        '--stream-delay': `${2.6 + index * 0.7}s`,
        left: slot.left ?? 'auto',
        right: slot.right ?? 'auto',
        top: slot.top ?? 'auto',
        bottom: slot.bottom ?? 'auto',
      },
    }
  })
})
</script>

<style scoped>
.auth-stream-scene {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  --scene-side-padding: var(--auth-scene-side-padding, clamp(28px, 4vw, 72px));
  --scene-safe-lane-width: min(var(--auth-safe-lane-width, 620px), calc(100% - (var(--scene-side-padding) * 2)));
  --scene-left-width: calc((100% - var(--scene-safe-lane-width)) / 2);
  background:
    linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.16) 0%,
      rgba(255, 255, 255, 0.16) calc(50% - (var(--scene-safe-lane-width) / 2) - 30px),
      rgba(255, 255, 255, 0.68) calc(50% - (var(--scene-safe-lane-width) / 2) + 24px),
      rgba(255, 255, 255, 0.68) calc(50% + (var(--scene-safe-lane-width) / 2) - 24px),
      rgba(255, 255, 255, 0.16) calc(50% + (var(--scene-safe-lane-width) / 2) + 30px),
      rgba(255, 255, 255, 0.16) 100%
    ),
    radial-gradient(circle at 12% 14%, rgba(95, 156, 255, 0.2), transparent 24%),
    radial-gradient(circle at 78% 72%, rgba(95, 156, 255, 0.16), transparent 26%),
    linear-gradient(135deg, rgba(248, 251, 255, 0.98) 0%, rgba(236, 244, 255, 0.98) 52%, rgba(251, 253, 255, 0.98) 100%);
}

.auth-stream-scene::before,
.auth-stream-scene::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.auth-stream-scene::before {
  background:
    linear-gradient(115deg, transparent 0%, rgba(93, 154, 255, 0.06) 28%, transparent 54%),
    linear-gradient(295deg, transparent 0%, rgba(93, 154, 255, 0.05) 34%, transparent 62%);
  animation: sceneGlowShift 16s linear infinite;
}

.auth-stream-scene::after {
  background:
    repeating-linear-gradient(
      118deg,
      rgba(68, 130, 246, 0) 0 24px,
      rgba(68, 130, 246, 0.045) 24px 27px,
      rgba(255, 255, 255, 0.018) 27px 48px
    );
  opacity: 0.72;
  animation: sceneLineShift 22s linear infinite;
}

.scene-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(111, 149, 211, 0.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(111, 149, 211, 0.08) 1px, transparent 1px);
  background-size: 110px 110px;
  mask-image: radial-gradient(circle at center, rgba(0, 0, 0, 0.95), transparent 92%);
  opacity: 0.38;
}

.scene-copy {
  position: absolute;
  top: clamp(78px, 14vh, 132px);
  left: clamp(72px, 7vw, 136px);
  width: clamp(360px, calc(var(--scene-left-width) - 84px), 560px);
  display: flex;
  flex-direction: column;
  gap: 14px;
  z-index: 1;
}

.stream-copy,
.scene-keyword {
  display: inline-block;
  width: 0;
  max-width: 100%;
  overflow: hidden;
  white-space: nowrap;
  border-right: 1px solid rgba(77, 126, 207, 0.28);
  text-shadow: 0 0 18px rgba(102, 160, 255, 0.12);
  opacity: 0;
  animation: streamTyping 7.2s steps(36) infinite;
  animation-delay: var(--stream-delay);
}

.stream-copy {
  color: rgba(17, 39, 74, 0.88);
  font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.stream-copy-title {
  display: block;
  font-size: clamp(38px, 4.1vw, 60px);
  line-height: 1.08;
  font-weight: 750;
  letter-spacing: -0.04em;
  white-space: nowrap;
}

.stream-copy-description {
  display: block;
  font-size: clamp(15px, 1.15vw, 18px);
  line-height: 1.66;
  color: rgba(63, 95, 145, 0.9);
}

.scene-keyword {
  position: absolute;
  z-index: 1;
  color: rgba(77, 126, 207, 0.28);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: clamp(16px, 1.25vw, 22px);
  letter-spacing: 0.12em;
}

@keyframes streamTyping {
  0% {
    width: 0;
    opacity: 0;
    transform: translate3d(0, 10px, 0);
  }
  8% {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
  42% {
    width: min(var(--stream-width), 100%);
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
  58% {
    width: min(var(--stream-width), 100%);
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
  82% {
    width: 0;
    opacity: 0;
    transform: translate3d(0, -2px, 0);
  }
  100% {
    width: 0;
    opacity: 0;
    transform: translate3d(0, -2px, 0);
  }
}

@keyframes streamFadeMobile {
  0% {
    opacity: 0;
    transform: translate3d(0, 8px, 0);
  }
  12% {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
  68% {
    opacity: 1;
    transform: translate3d(0, 0, 0);
  }
  100% {
    opacity: 0;
    transform: translate3d(0, -4px, 0);
  }
}

@media (max-width: 1400px) {
  .scene-copy {
    width: clamp(320px, calc(var(--scene-left-width) - 72px), 500px);
  }
}

@media (max-width: 1260px) {
  .scene-copy {
    top: 28px;
    left: 36px;
    width: min(420px, calc(100% - 540px));
  }

  .scene-keyword {
    font-size: 14px;
  }
}

@media (max-width: 920px) {
  .scene-copy {
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: min(420px, calc(100% - 32px));
    gap: 10px;
  }

  .scene-keyword {
    font-size: 13px;
    right: 22px !important;
    left: auto !important;
  }

  .stream-copy-title {
    font-size: 30px;
  }

  .stream-copy-description {
    font-size: 14px;
    line-height: 1.6;
  }
}

@media (max-width: 640px) {
  .scene-copy {
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    width: calc(100% - 24px);
    gap: 8px;
  }

  .scene-keyword {
    display: none;
  }

  .stream-copy-title {
    font-size: 26px;
    line-height: 1.12;
  }

  .stream-copy-description {
    font-size: 13px;
    line-height: 1.55;
  }

  .stream-copy {
    width: 100%;
    white-space: normal;
    overflow: visible;
    border-right: none;
    animation: streamFadeMobile 7.2s ease-in-out infinite;
  }
}

@media (max-width: 480px) {
  .scene-copy {
    top: 14px;
    width: calc(100% - 20px);
  }
}

@keyframes sceneGlowShift {
  0% {
    transform: translate3d(-5%, -3%, 0);
  }
  50% {
    transform: translate3d(4%, 4%, 0);
  }
  100% {
    transform: translate3d(-5%, -3%, 0);
  }
}

@keyframes sceneLineShift {
  0% {
    transform: translate3d(-6%, -4%, 0);
  }
  100% {
    transform: translate3d(8%, 5%, 0);
  }
}

:global(:root[data-theme='dark'] .auth-stream-scene) {
  background:
    linear-gradient(
      90deg,
      rgba(14, 24, 38, 0.2) 0%,
      rgba(14, 24, 38, 0.2) calc(50% - (var(--scene-safe-lane-width) / 2) - 30px),
      rgba(20, 33, 53, 0.62) calc(50% - (var(--scene-safe-lane-width) / 2) + 24px),
      rgba(20, 33, 53, 0.62) calc(50% + (var(--scene-safe-lane-width) / 2) - 24px),
      rgba(14, 24, 38, 0.2) calc(50% + (var(--scene-safe-lane-width) / 2) + 30px),
      rgba(14, 24, 38, 0.2) 100%
    ),
    radial-gradient(circle at 12% 14%, rgba(112, 182, 255, 0.18), transparent 24%),
    radial-gradient(circle at 78% 72%, rgba(112, 182, 255, 0.14), transparent 26%),
    linear-gradient(135deg, rgba(15, 27, 43, 0.98) 0%, rgba(10, 19, 31, 0.98) 52%, rgba(14, 24, 38, 0.98) 100%);
}

:global(:root[data-theme='dark'] .stream-copy-title) {
  color: rgba(236, 244, 255, 0.92);
}

:global(:root[data-theme='dark'] .stream-copy-description) {
  color: rgba(165, 191, 236, 0.9);
}

:global(:root[data-theme='dark'] .scene-keyword) {
  color: rgba(127, 180, 255, 0.34);
}
</style>
