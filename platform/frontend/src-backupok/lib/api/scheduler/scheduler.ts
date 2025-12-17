/**
 * Scheduler API Client
 */
import { api } from '../shared/client'
import type {
  ScheduledScan,
  CreateScheduledScanData,
  ScheduledScansResponse,
  ApiResponse
} from './types'

const BASE_URL = '/advanced'

export const schedulerAPI = {
  /**
   * List all scheduled scans
   */
  listScheduledScans: async (): Promise<ScheduledScan[]> => {
    const response = await api.get<ScheduledScansResponse>(
      `${BASE_URL}/scheduled-scans`
    )
    return response.data.scheduled_scans
  },

  /**
   * Create new scheduled scan
   */
  createScheduledScan: async (
    scanData: CreateScheduledScanData
  ): Promise<ScheduledScan> => {
    const response = await api.post<ScheduledScan>(
      `${BASE_URL}/scheduled-scans`,
      scanData
    )
    return response.data
  },

  /**
   * Get specific scheduled scan
   */
  getScheduledScan: async (scanId: string): Promise<ScheduledScan> => {
    const response = await api.get<ScheduledScan>(
      `${BASE_URL}/scheduled-scans/${scanId}`
    )
    return response.data
  },

  /**
   * Cancel scheduled scan
   */
  cancelScheduledScan: async (scanId: string): Promise<ApiResponse> => {
    const response = await api.delete<ApiResponse>(
      `${BASE_URL}/scheduled-scans/${scanId}`
    )
    return response.data
  },

  /**
   * Preview scheduled scan (without creating)
   */
  previewScheduledScan: async (
    scanData: Omit<CreateScheduledScanData, 'scan_id'>
  ): Promise<any> => {
    const response = await api.post<any>(
      `${BASE_URL}/scheduled-scans/preview`,
      scanData
    )
    return response.data
  }
}

