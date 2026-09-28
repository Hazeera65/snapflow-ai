import { create } from 'zustand'
import axios from 'axios'

export interface Hardware {
  platform: string
  architecture: string
  processor: string
  is_snapdragon: boolean
  snapdragon_model: string | null
  available_backends: string[]
  preferred_backend: string
  mode: string
  npu_available: boolean
  gpu_available: boolean
  total_memory_gb: number | null
  timestamp: string
}

interface HardwareStore {
  hardware: Hardware | null
  loading: boolean
  error: string | null
  fetchHardware: () => Promise<void>
}

export const useHardwareStore = create<HardwareStore>((set) => ({
  hardware: null,
  loading: false,
  error: null,
  
  fetchHardware: async () => {
    set({ loading: true, error: null })
    try {
      const response = await axios.get('/api/hardware/status')
      set({ hardware: response.data, loading: false })
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch hardware info',
        loading: false 
      })
    }
  }
}))
