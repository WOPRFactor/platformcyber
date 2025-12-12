/**
 * useDragResize Hook
 * ===================
 * 
 * Hook para manejar drag & resize de ventanas modales.
 */

import { useState, useRef, useCallback, useEffect } from 'react'

interface UseDragResizeOptions {
  initialPosition?: { x: number; y: number }
  initialSize?: { width: number; height: number }
  minWidth?: number
  minHeight?: number
  onBringToFront?: () => void
}

export const useDragResize = (options: UseDragResizeOptions = {}) => {
  const {
    initialPosition = { x: 100, y: 100 },
    initialSize = { width: 1200, height: 700 },
    minWidth = 800,
    minHeight = 500,
    onBringToFront
  } = options

  const [isDragging, setIsDragging] = useState(false)
  const [isResizing, setIsResizing] = useState(false)
  const [position, setPosition] = useState(initialPosition)
  const [size, setSize] = useState(initialSize)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 })
  const modalRef = useRef<HTMLDivElement>(null)

  const handleMouseDown = (e: React.MouseEvent) => {
    if (onBringToFront) {
      onBringToFront()
    }

    if (e.target === e.currentTarget || (e.target as HTMLElement).closest('.modal-header')) {
      setIsDragging(true)
      setDragStart({
        x: e.clientX - position.x,
        y: e.clientY - position.y
      })
    }
  }

  const handleResizeMouseDown = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsResizing(true)
    setResizeStart({
      x: e.clientX,
      y: e.clientY,
      width: size.width,
      height: size.height
    })
  }

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging) {
      const newX = e.clientX - dragStart.x
      const newY = e.clientY - dragStart.y

      const maxX = window.innerWidth - size.width
      const maxY = window.innerHeight - size.height

      setPosition({
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      })
    }

    if (isResizing) {
      const newWidth = Math.max(minWidth, resizeStart.width + (e.clientX - resizeStart.x))
      const newHeight = Math.max(minHeight, resizeStart.height + (e.clientY - resizeStart.y))

      setSize({
        width: newWidth,
        height: newHeight
      })
    }
  }, [isDragging, isResizing, dragStart, resizeStart, size.width, size.height, minWidth, minHeight])

  const handleMouseUp = useCallback(() => {
    setIsDragging(false)
    setIsResizing(false)
  }, [])

  useEffect(() => {
    if (isDragging || isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = isDragging ? 'grabbing' : 'nw-resize'
      document.body.style.userSelect = 'none'
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }
  }, [isDragging, isResizing, handleMouseMove, handleMouseUp])

  return {
    modalRef,
    position,
    size,
    isDragging,
    isResizing,
    handleMouseDown,
    handleResizeMouseDown
  }
}


