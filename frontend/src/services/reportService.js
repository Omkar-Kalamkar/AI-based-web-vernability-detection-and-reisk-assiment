import { apiDownload, apiRequest } from './api'

export const reportService = {
  preview: (scanId) => apiRequest(`/api/reports/${scanId}/preview`),
  downloadPdf: (scanId) => apiDownload(`/api/reports/${scanId}/pdf`, 'secureai-report.pdf'),
  downloadCsv: (scanId) => apiDownload(`/api/reports/${scanId}/csv`, 'secureai-report.csv'),
}
