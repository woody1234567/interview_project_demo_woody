<script setup lang="ts">
const items = [
  { label: 'Home', icon: 'i-heroicons-home', to: '/' }
]

const colorMode = useColorMode()
const isDark = computed({
  get () {
    return colorMode.value === 'dark'
  },
  set () {
    colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'
  }
})
</script>

<template>
  <nav class="border-b border-gray-200 dark:border-gray-800 bg-white/75 dark:bg-gray-900/75 backdrop-blur-md sticky top-0 z-50">
    <UContainer>
      <div class="flex h-16 items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <NuxtLink to="/" class="flex items-center gap-2">
            <UIcon name="i-heroicons-shield-check" class="w-8 h-8 text-primary-500" />
            <span class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-500 to-primary-700">
              FraudRisk
            </span>
          </NuxtLink>
        </div>

        <div class="hidden md:flex items-center gap-x-8">
          <NuxtLink 
            v-for="item in items" 
            :key="item.label" 
            :to="item.to"
            class="text-sm font-medium text-gray-600 hover:text-primary-500 dark:text-gray-400 dark:hover:text-primary-400 transition-colors"
          >
            {{ item.label }}
          </NuxtLink>
        </div>

        <div class="flex items-center gap-3">
          <UButton
            :icon="isDark ? 'i-heroicons-moon-20-solid' : 'i-heroicons-sun-20-solid'"
            color="neutral"
            variant="ghost"
            aria-label="Theme"
            @click="isDark = !isDark"
          />
          <UButton
            label="Get Started"
            trailing-icon="i-heroicons-arrow-right-20-solid"
            color="primary"
            class="hidden sm:flex"
          />
        </div>
      </div>
    </UContainer>
  </nav>
</template>
