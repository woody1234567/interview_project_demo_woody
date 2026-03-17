<script setup lang="ts">
import type { PredictionInput } from '~/components/TransactionForm.vue'

type PredictResp = {
  fraud_prob: number
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH'
  thresholds?: { t_mid: number; t_high: number }
  model_used?: string
}

const config = useRuntimeConfig()
const featureApiBase = config.public.featureApiBase
const modelApiBase = config.public.modelApiBase

const featureStatus = ref<'idle' | 'loading' | 'ok' | 'fail'>('idle')
const modelStatus = ref<'idle' | 'loading' | 'ok' | 'fail'>('idle')

const loading = ref(false)
const errorMsg = ref('')
const result = ref<PredictResp | null>(null)

async function checkConnections() {
  featureStatus.value = 'loading'
  modelStatus.value = 'loading'
  
  try {
    const feature = await $fetch<{ status: string }>(`${featureApiBase}/health`)
    featureStatus.value = feature.status === 'ok' ? 'ok' : 'fail'
  } catch {
    featureStatus.value = 'fail'
  }

  try {
    const model = await $fetch<{ status: string }>(`${modelApiBase}/health`)
    modelStatus.value = model.status === 'ok' ? 'ok' : 'fail'
  } catch {
    modelStatus.value = 'fail'
  }
}

async function runPrediction(payload: PredictionInput) {
  loading.value = true
  errorMsg.value = ''
  result.value = null

  try {
    const featureResp = await $fetch<any>(`${featureApiBase}/v1/features/transform`, {
      method: 'POST',
      body: payload.transaction,
    })

    const predictResp = await $fetch<PredictResp>(`${modelApiBase}/v1/model/predict`, {
      method: 'POST',
      body: {
        ...featureResp,
        model_name: payload.model_name,
      },
    })

    result.value = predictResp
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || err?.message || 'Prediction failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="space-y-10">
    <section class="max-w-2xl">
      <h1 class="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-5xl">
        Fraud Detection <span class="text-primary">Analysis</span>
      </h1>
      <p class="mt-4 text-lg text-gray-500 dark:text-gray-400">
        Input transaction details to analyze risk levels using our advanced AI models. 
        Our system transforms features and predicts fraud probability in real-time.
      </p>

      <div class="mt-8 flex flex-wrap items-center gap-4 bg-gray-50 dark:bg-gray-800/50 p-4 rounded-xl border border-gray-100 dark:border-gray-800">
        <UButton 
          icon="i-heroicons-bolt" 
          variant="subtle" 
          color="neutral" 
          size="sm" 
          label="Check Connection" 
          :loading="featureStatus === 'loading' || modelStatus === 'loading'"
          @click="checkConnections"
        />
        
        <div class="flex items-center gap-6 ml-auto">
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-gray-400 uppercase tracking-wider">Feature API</span>
            <UBadge 
              v-if="featureStatus !== 'idle'" 
              :color="featureStatus === 'ok' ? 'success' : 'error'" 
              variant="subtle" 
              size="sm"
              class="min-w-15 justify-center"
            >
              <template #leading>
                <span class="w-2 h-2 rounded-full animate-pulse" :class="featureStatus === 'ok' ? 'bg-success-500' : 'bg-error-500'" />
              </template>
              {{ featureStatus === 'ok' ? 'OK' : 'fail' }}
            </UBadge>
            <span v-else class="text-xs text-gray-400 italic">Not checked</span>
          </div>

          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-gray-400 uppercase tracking-wider">Model API</span>
            <UBadge 
              v-if="modelStatus !== 'idle'" 
              :color="modelStatus === 'ok' ? 'success' : 'error'" 
              variant="subtle" 
              size="sm"
              class="min-w-15 justify-center"
            >
              <template #leading>
                <span class="w-2 h-2 rounded-full animate-pulse" :class="modelStatus === 'ok' ? 'bg-success-500' : 'bg-error-500'" />
              </template>
              {{ modelStatus === 'ok' ? 'OK' : 'fail' }}
            </UBadge>
            <span v-else class="text-xs text-gray-400 italic">Not checked</span>
          </div>
        </div>
      </div>
    </section>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-10 items-start">
      <section>
        <TransactionForm @submit="runPrediction" />
      </section>

      <section class="space-y-6">
        <div v-if="loading" class="flex flex-col items-center justify-center p-12 border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-2xl">
          <UIcon name="i-heroicons-arrow-path" class="w-10 h-10 animate-spin text-primary mb-4" />
          <p class="text-gray-500 font-medium">Analyzing transaction data...</p>
        </div>

        <UAlert
          v-if="errorMsg"
          icon="i-heroicons-exclamation-triangle"
          color="error"
          variant="subtle"
          title="Analysis Failed"
          :description="errorMsg"
        />

        <PredictionCard
          v-if="result"
          :fraud-prob="result.fraud_prob"
          :risk-level="result.risk_level"
          :t-mid="result.thresholds?.t_mid"
          :t-high="result.thresholds?.t_high"
          :model-used="result.model_used"
        />

        <div v-if="!result && !loading && !errorMsg" class="h-full flex flex-col items-center justify-center p-12 bg-gray-50 dark:bg-gray-800/20 rounded-2xl border border-gray-100 dark:border-gray-800">
          <UIcon name="i-heroicons-shield-check" class="w-12 h-12 text-gray-300 dark:text-gray-700 mb-4" />
          <p class="text-gray-400 text-center text-sm max-w-xs">
            Submit the form on the left to see the fraud risk analysis result here.
          </p>
        </div>
      </section>
    </div>
  </div>
</template>
