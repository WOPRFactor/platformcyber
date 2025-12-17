// ===== COMPONENTE DE CAMPO DE FORMULARIO REUTILIZABLE =====

import React, { forwardRef, InputHTMLAttributes, TextareaHTMLAttributes, SelectHTMLAttributes } from 'react'
import { AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react'

export interface BaseFieldProps {
  label?: string
  error?: string | null
  success?: boolean
  required?: boolean
  helperText?: string
  className?: string
  labelClassName?: string
  inputClassName?: string
  errorClassName?: string
  disabled?: boolean
  isDirty?: boolean
}

// ===== INPUT TEXT =====

interface TextInputProps extends BaseFieldProps, Omit<InputHTMLAttributes<HTMLInputElement>, 'className'> {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search'
  showPasswordToggle?: boolean
}

export const TextInput = forwardRef<HTMLInputElement, TextInputProps>(({
  label,
  error,
  success,
  required,
  helperText,
  className = '',
  labelClassName = '',
  inputClassName = '',
  errorClassName = '',
  type = 'text',
  showPasswordToggle = false,
  isDirty,
  ...props
}, ref) => {
  const [showPassword, setShowPassword] = React.useState(false)

  const inputType = type === 'password' && showPassword ? 'text' : type

  const baseInputClasses = `
    w-full px-4 py-3 border rounded-xl font-medium transition-all duration-200
    bg-white border-gray-200 text-gray-900 placeholder-gray-400
    focus:outline-none focus:ring-2 focus:border-transparent
    disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed
  `

  const getInputClasses = () => {
    if (error && isDirty) {
      return `${baseInputClasses} border-red-500 focus:ring-red-500/20`
    }
    if (success && isDirty) {
      return `${baseInputClasses} border-gray-200 focus:ring-red-500/20`
    }
    return `${baseInputClasses} focus:ring-red-500/20 focus:border-red-500`
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <label className={`block text-sm font-medium text-gray-600 ${labelClassName}`}>
          {label}
          {required && <span className="text-red-600 ml-1">*</span>}
        </label>
      )}

      <div className="relative">
        <input
          ref={ref}
          type={inputType}
          className={`${getInputClasses()} ${inputClassName}`}
          {...props}
        />

        {/* Toggle para mostrar/ocultar contraseña */}
        {type === 'password' && showPasswordToggle && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-600 transition-colors"
          >
            {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
          </button>
        )}

        {/* Iconos de estado */}
        {isDirty && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            {error ? (
              <AlertCircle size={20} className="text-red-600" />
            ) : success ? (
              <CheckCircle size={20} className="text-gray-900" />
            ) : null}
          </div>
        )}
      </div>

      {/* Texto de ayuda */}
      {helperText && !error && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}

      {/* Mensaje de error */}
      {error && isDirty && (
        <p className={`text-sm ${errorClassName || 'text-red-600'} flex items-center space-x-2`}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </p>
      )}
    </div>
  )
})

TextInput.displayName = 'TextInput'

// ===== TEXTAREA =====

interface TextAreaProps extends BaseFieldProps, Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'className'> {
  rows?: number
  resize?: 'none' | 'vertical' | 'horizontal' | 'both'
}

export const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(({
  label,
  error,
  success,
  required,
  helperText,
  className = '',
  labelClassName = '',
  inputClassName = '',
  errorClassName = '',
  rows = 4,
  resize = 'vertical',
  isDirty,
  ...props
}, ref) => {
  const baseTextareaClasses = `
    w-full px-4 py-3 border rounded-xl font-medium transition-all duration-200
    bg-white border-gray-200 text-gray-900 placeholder-gray-400
    focus:outline-none focus:ring-2 focus:border-transparent
    disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed
  `

  const getTextareaClasses = () => {
    if (error && isDirty) {
      return `${baseTextareaClasses} border-red-500 focus:ring-red-500/20`
    }
    if (success && isDirty) {
      return `${baseTextareaClasses} border-gray-200 focus:ring-red-500/20`
    }
    return `${baseTextareaClasses} focus:ring-red-500/20 focus:border-red-500`
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <label className={`block text-sm font-medium text-gray-600 ${labelClassName}`}>
          {label}
          {required && <span className="text-red-600 ml-1">*</span>}
        </label>
      )}

      <div className="relative">
        <textarea
          ref={ref}
          rows={rows}
          style={{ resize }}
          className={`${getTextareaClasses()} ${inputClassName}`}
          {...props}
        />

        {/* Iconos de estado */}
        {isDirty && (
          <div className="absolute right-3 top-3">
            {error ? (
              <AlertCircle size={20} className="text-red-600" />
            ) : success ? (
              <CheckCircle size={20} className="text-gray-900" />
            ) : null}
          </div>
        )}
      </div>

      {/* Texto de ayuda */}
      {helperText && !error && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}

      {/* Mensaje de error */}
      {error && isDirty && (
        <p className={`text-sm ${errorClassName || 'text-red-600'} flex items-center space-x-2`}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </p>
      )}
    </div>
  )
})

TextArea.displayName = 'TextArea'

// ===== SELECT =====

interface SelectOption {
  value: string | number
  label: string
  disabled?: boolean
}

interface SelectProps extends BaseFieldProps, Omit<SelectHTMLAttributes<HTMLSelectElement>, 'className'> {
  options?: SelectOption[]
  placeholder?: string
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(({
  label,
  error,
  success,
  required,
  helperText,
  className = '',
  labelClassName = '',
  inputClassName = '',
  errorClassName = '',
  options,
  placeholder,
  isDirty,
  ...props
}, ref) => {
  const baseSelectClasses = `
    w-full px-4 py-3 border rounded-xl font-medium transition-all duration-200
    bg-white border-gray-200 text-gray-900
    focus:outline-none focus:ring-2 focus:border-transparent
    disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed
  `

  const getSelectClasses = () => {
    if (error && isDirty) {
      return `${baseSelectClasses} border-red-500 focus:ring-red-500/20`
    }
    if (success && isDirty) {
      return `${baseSelectClasses} border-gray-200 focus:ring-red-500/20`
    }
    return `${baseSelectClasses} focus:ring-red-500/20 focus:border-red-500`
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <label className={`block text-sm font-medium text-gray-600 ${labelClassName}`}>
          {label}
          {required && <span className="text-red-600 ml-1">*</span>}
        </label>
      )}

      <div className="relative">
        <select
          ref={ref}
          className={`${getSelectClasses()} ${inputClassName}`}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options?.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>

        {/* Iconos de estado */}
        {isDirty && (
          <div className="absolute right-8 top-1/2 transform -translate-y-1/2">
            {error ? (
              <AlertCircle size={20} className="text-red-600" />
            ) : success ? (
              <CheckCircle size={20} className="text-gray-900" />
            ) : null}
          </div>
        )}
      </div>

      {/* Texto de ayuda */}
      {helperText && !error && (
        <p className="text-sm text-gray-500">{helperText}</p>
      )}

      {/* Mensaje de error */}
      {error && isDirty && (
        <p className={`text-sm ${errorClassName || 'text-red-600'} flex items-center space-x-2`}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </p>
      )}
    </div>
  )
})

Select.displayName = 'Select'

// ===== CHECKBOX =====

interface CheckboxProps extends BaseFieldProps, Omit<InputHTMLAttributes<HTMLInputElement>, 'className' | 'type'> {
  checkboxLabel?: string
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(({
  label,
  checkboxLabel,
  error,
  required,
  helperText,
  className = '',
  labelClassName = '',
  errorClassName = '',
  isDirty,
  ...props
}, ref) => {
  return (
    <div className={`space-y-2 ${className}`}>
      {label && (
        <label className={`block text-sm font-medium text-gray-600 ${labelClassName}`}>
          {label}
          {required && <span className="text-red-600 ml-1">*</span>}
        </label>
      )}

      <label className="flex items-center space-x-3 cursor-pointer">
        <input
          ref={ref}
          type="checkbox"
          className="
            w-4 h-4 text-red-600 bg-white border-gray-200 rounded
            focus:ring-red-500 focus:ring-2 focus:ring-offset-0
            checked:bg-red-600 checked:border-red-600
          "
          {...props}
        />
        <span className="text-gray-600 text-sm">{checkboxLabel}</span>
      </label>

      {/* Texto de ayuda */}
      {helperText && !error && (
        <p className="text-sm text-gray-500 ml-7">{helperText}</p>
      )}

      {/* Mensaje de error */}
      {error && isDirty && (
        <p className={`text-sm ${errorClassName || 'text-red-600'} flex items-center space-x-2 ml-7`}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </p>
      )}
    </div>
  )
})

Checkbox.displayName = 'Checkbox'

// ===== COMPONENTE FORM FIELD GENÉRICO =====

interface FormFieldProps extends BaseFieldProps {
  type: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search' | 'textarea' | 'select' | 'checkbox'
  // Props específicos por tipo
  textProps?: Partial<TextInputProps>
  textareaProps?: Partial<TextAreaProps>
  selectProps?: Partial<SelectProps>
  checkboxProps?: Partial<CheckboxProps>
}

export const FormField: React.FC<FormFieldProps> = ({
  type,
  textProps,
  textareaProps,
  selectProps,
  checkboxProps,
  ...baseProps
}) => {
  switch (type) {
    case 'textarea':
      return <TextArea {...baseProps} {...textareaProps} />
    case 'select':
      return <Select {...baseProps} {...selectProps} />
    case 'checkbox':
      return <Checkbox {...baseProps} {...checkboxProps} />
    default:
      return <TextInput type={type as any} {...baseProps} {...textProps} />
  }
}

// ===== EXPORTACIONES =====

export type { TextInputProps, TextAreaProps, SelectProps, CheckboxProps, FormFieldProps }
