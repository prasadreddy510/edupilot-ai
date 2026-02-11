import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export function formatTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  } else {
    return `${secs}s`
  }
}

export function calculatePercentage(value: number, total: number): number {
  if (total === 0) return 0
  return Math.round((value / total) * 100)
}

export function getGradeLabel(grade: number): string {
  const gradeMap: { [key: number]: string } = {
    3: 'Grade 3',
    4: 'Grade 4',
    5: 'Grade 5',
    6: 'Grade 6',
    7: 'Grade 7',
    8: 'Grade 8',
    9: 'Grade 9',
    10: 'Grade 10',
  }
  return gradeMap[grade] || `Grade ${grade}`
}

export function getMasteryColor(masteryLevel: number): string {
  if (masteryLevel >= 80) return 'text-green-600'
  if (masteryLevel >= 60) return 'text-blue-600'
  if (masteryLevel >= 40) return 'text-yellow-600'
  return 'text-red-600'
}

export function getMasteryLabel(masteryLevel: number): string {
  if (masteryLevel >= 80) return 'Excellent'
  if (masteryLevel >= 60) return 'Good'
  if (masteryLevel >= 40) return 'Fair'
  return 'Needs Improvement'
}
