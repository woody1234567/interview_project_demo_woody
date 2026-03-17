<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const items: NavigationMenuItem[] = [
  {
    label: 'StudyWithWoody',
    to: 'https://studywithwoody.site',
    target: '_blank'
  },
]
</script>

<template>
  <UFooter>
    <template #left>
      <p class="text-muted text-sm">Copyright © StudyWithWoody {{ new Date().getFullYear() }}</p>
    </template>

    <UNavigationMenu :items="items" variant="link" />

    <template #right>
      <UButton
        icon="i-simple-icons-youtube"
        color="neutral"
        variant="ghost"
        to="https://www.youtube.com/@Woodyhsu-vlog"
        target="_blank"
        aria-label="Youtube"
      />
      <UButton
        icon="i-simple-icons-linkedin"
        color="neutral"
        variant="ghost"
        to="https://www.linkedin.com/in/chun-wei-hsu19990703/"
        target="_blank"
        aria-label="LinkedIn"
      />
      <UButton
        icon="i-simple-icons-github"
        color="neutral"
        variant="ghost"
        to="https://github.com/woody1234567"
        target="_blank"
        aria-label="GitHub"
      />
    </template>
  </UFooter>
</template>
