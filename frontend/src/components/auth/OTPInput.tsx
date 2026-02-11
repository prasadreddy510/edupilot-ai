'use client'

import { useState, useRef, KeyboardEvent, ClipboardEvent } from 'react'
import { cn } from '@/lib/utils'

interface OTPInputProps {
  length?: number
  onComplete: (otp: string) => void
  disabled?: boolean
}

export function OTPInput({ length = 6, onComplete, disabled = false }: OTPInputProps) {
  const [otp, setOtp] = useState<string[]>(Array(length).fill(''))
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  const handleChange = (index: number, value: string) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) return

    const newOtp = [...otp]
    newOtp[index] = value

    setOtp(newOtp)

    // Move to next input if value entered
    if (value && index < length - 1) {
      inputRefs.current[index + 1]?.focus()
    }

    // Check if OTP is complete
    if (newOtp.every((digit) => digit !== '')) {
      onComplete(newOtp.join(''))
    }
  }

  const handleKeyDown = (index: number, e: KeyboardEvent<HTMLInputElement>) => {
    // Move to previous input on backspace
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handlePaste = (e: ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault()
    const pastedData = e.clipboardData.getData('text/plain').slice(0, length)

    // Only allow digits
    if (!/^\d+$/.test(pastedData)) return

    const newOtp = pastedData.split('')
    while (newOtp.length < length) {
      newOtp.push('')
    }

    setOtp(newOtp)

    // Focus last filled input or last input
    const lastFilledIndex = Math.min(pastedData.length, length) - 1
    inputRefs.current[lastFilledIndex]?.focus()

    // Check if OTP is complete
    if (newOtp.every((digit) => digit !== '')) {
      onComplete(newOtp.join(''))
    }
  }

  return (
    <div className="flex gap-2 justify-center">
      {otp.map((digit, index) => (
        <input
          key={index}
          ref={(el) => {
            inputRefs.current[index] = el
          }}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={digit}
          onChange={(e) => handleChange(index, e.target.value)}
          onKeyDown={(e) => handleKeyDown(index, e)}
          onPaste={handlePaste}
          disabled={disabled}
          className={cn(
            'h-12 w-12 rounded-lg border-2 text-center text-lg font-semibold',
            'focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200',
            'disabled:bg-gray-100 disabled:cursor-not-allowed',
            digit ? 'border-blue-500' : 'border-gray-300'
          )}
          autoComplete="off"
        />
      ))}
    </div>
  )
}
