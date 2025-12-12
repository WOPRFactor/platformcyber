/**
 * DatePicker Component
 * ====================
 * 
 * Componente de calendario desplegable para seleccionar fechas.
 */

import React, { useState, useRef, useEffect } from 'react'
import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react'
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, getDay } from 'date-fns'
import { es } from 'date-fns/locale'

interface DatePickerProps {
  value: string
  onChange: (date: string) => void
  placeholder?: string
  label?: string
  minDate?: string
  maxDate?: string
}

const DatePicker: React.FC<DatePickerProps> = ({
  value,
  onChange,
  placeholder = 'dd/mm/yyyy',
  label,
  minDate,
  maxDate
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [currentMonth, setCurrentMonth] = useState(value ? new Date(value) : new Date())
  const pickerRef = useRef<HTMLDivElement>(null)

  // Cerrar cuando se hace click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (pickerRef.current && !pickerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const selectedDate = value ? new Date(value) : null
  const minDateObj = minDate ? new Date(minDate) : null
  const maxDateObj = maxDate ? new Date(maxDate) : null

  const monthStart = startOfMonth(currentMonth)
  const monthEnd = endOfMonth(currentMonth)
  const daysInMonth = eachDayOfInterval({ start: monthStart, end: monthEnd })
  
  // Días de la semana
  const weekDays = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
  
  // Días vacíos al inicio del mes
  const firstDayOfWeek = getDay(monthStart)
  const emptyDays = Array(firstDayOfWeek).fill(null)

  const handleDateSelect = (date: Date) => {
    const dateString = format(date, 'yyyy-MM-dd')
    onChange(dateString)
    setIsOpen(false)
  }

  const handlePrevMonth = () => {
    setCurrentMonth(subMonths(currentMonth, 1))
  }

  const handleNextMonth = () => {
    setCurrentMonth(addMonths(currentMonth, 1))
  }

  const isDateDisabled = (date: Date): boolean => {
    if (minDateObj && date < minDateObj) return true
    if (maxDateObj && date > maxDateObj) return true
    return false
  }

  const displayValue = value ? format(new Date(value), 'dd/MM/yyyy') : ''

  return (
    <div className="relative" ref={pickerRef}>
      {label && (
        <label className="block text-sm font-medium text-gray-900 mb-2">
          {label}
        </label>
      )}
      <div className="relative">
        <input
          type="text"
          value={displayValue}
          placeholder={placeholder}
          readOnly
          onClick={() => setIsOpen(!isOpen)}
          className="w-full bg-gray-50 border border-gray-200 rounded px-3 py-2 text-gray-900 cursor-pointer focus:outline-none focus:ring-2 focus:ring-red-500 pr-10"
        />
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-900 hover:text-gray-700"
        >
          <Calendar className="w-5 h-5" />
        </button>
      </div>

      {isOpen && (
        <div className="absolute z-50 mt-2 bg-white border border-gray-200 rounded-xl shadow-xl p-4 min-w-[300px]">
          {/* Header del calendario */}
          <div className="flex items-center justify-between mb-4">
            <button
              type="button"
              onClick={handlePrevMonth}
              className="p-1 hover:bg-gray-700 rounded text-gray-900 hover:text-gray-700"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <h3 className="text-lg font-semibold text-gray-900">
              {format(currentMonth, 'MMMM yyyy', { locale: es })}
            </h3>
            <button
              type="button"
              onClick={handleNextMonth}
              className="p-1 hover:bg-gray-700 rounded text-gray-900 hover:text-gray-700"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>

          {/* Días de la semana */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {weekDays.map((day) => (
              <div
                key={day}
                className="text-center text-xs font-medium text-gray-500 py-1"
              >
                {day}
              </div>
            ))}
          </div>

          {/* Días del mes */}
          <div className="grid grid-cols-7 gap-1">
            {emptyDays.map((_, index) => (
              <div key={`empty-${index}`} className="h-8" />
            ))}
            {daysInMonth.map((day) => {
              const isSelected = selectedDate && isSameDay(day, selectedDate)
              const isCurrentMonth = isSameMonth(day, currentMonth)
              const isDisabled = isDateDisabled(day)
              const isToday = isSameDay(day, new Date())

              return (
                <button
                  key={day.toString()}
                  type="button"
                  onClick={() => !isDisabled && handleDateSelect(day)}
                  disabled={isDisabled}
                  className={`
                    h-8 w-8 rounded text-sm
                    ${isSelected
                      ? 'bg-red-600 text-white font-semibold'
                      : isToday
                      ? 'bg-green-900 text-gray-700 font-semibold'
                      : isDisabled
                      ? 'text-gray-600 cursor-not-allowed'
                      : 'text-gray-600 hover:bg-gray-700 hover:text-gray-900'
                    }
                    ${!isCurrentMonth ? 'opacity-50' : ''}
                  `}
                >
                  {format(day, 'd')}
                </button>
              )
            })}
          </div>

          {/* Botón para limpiar */}
          {value && (
            <button
              type="button"
              onClick={() => {
                onChange('')
                setIsOpen(false)
              }}
              className="mt-3 w-full text-sm text-red-400 hover:text-red-300 py-1"
            >
              Limpiar
            </button>
          )}
        </div>
      )}
    </div>
  )
}

export default DatePicker

