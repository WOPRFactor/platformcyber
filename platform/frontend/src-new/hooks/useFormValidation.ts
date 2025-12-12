// ===== HOOK DE VALIDACIÓN DE FORMULARIOS =====

import { useState, useCallback, useEffect } from 'react'
import { ValidationSchema, ValidationRule, validators, getValidationErrorMessage, sanitizeInput } from '../utils/validationSchemas'

export interface ValidationErrors {
  [key: string]: string
}

export interface ValidationState {
  errors: ValidationErrors
  isValid: boolean
  isDirty: { [key: string]: boolean }
}

export interface FormValues {
  [key: string]: any
}

// ===== HOOK PRINCIPAL =====

export const useFormValidation = (schema: ValidationSchema) => {
  const [errors, setErrors] = useState<ValidationErrors>({})
  const [isValid, setIsValid] = useState(false)
  const [isDirty, setIsDirty] = useState<{ [key: string]: boolean }>({})

  // Función para validar un campo individual
  const validateField = useCallback((fieldName: string, value: any, formData?: FormValues): string | null => {
    const rule = schema[fieldName]
    if (!rule) return null

    // Sanitizar input
    const sanitizedValue = typeof value === 'string' ? sanitizeInput(value) : value
    const stringValue = String(sanitizedValue || '')

    // Validación requerida
    if (rule.required && (!sanitizedValue || stringValue.trim() === '')) {
      return getValidationErrorMessage(fieldName, { required: true })
    }

    // Si no es requerido y está vacío, es válido
    if (!rule.required && (!sanitizedValue || stringValue.trim() === '')) {
      return null
    }

    // Validación de longitud mínima
    if (rule.minLength && stringValue.length < rule.minLength) {
      return getValidationErrorMessage(fieldName, { minLength: rule.minLength })
    }

    // Validación de longitud máxima
    if (rule.maxLength && stringValue.length > rule.maxLength) {
      return getValidationErrorMessage(fieldName, { maxLength: rule.maxLength })
    }

    // Validación de patrón regex
    if (rule.pattern && !rule.pattern.test(stringValue)) {
      return rule.customMessage || `${fieldName} no cumple con el formato requerido`
    }

    // Validación por tipo
    if (rule.type) {
      let isValidType = false

      switch (rule.type) {
        case 'email':
          isValidType = validators.email(stringValue)
          break
        case 'url':
          isValidType = validators.url(stringValue)
          break
        case 'ip':
          isValidType = validators.ip(stringValue)
          break
        case 'domain':
          isValidType = validators.domain(stringValue)
          break
        case 'number':
          isValidType = validators.number(stringValue)
          break
        default:
          isValidType = true
      }

      if (!isValidType) {
        return getValidationErrorMessage(fieldName, { type: rule.type })
      }
    }

    // Validación personalizada
    if (rule.custom && !rule.custom(stringValue, formData)) {
      return rule.customMessage || `${fieldName} es inválido`
    }

    return null
  }, [schema])

  // Función para validar todo el formulario
  const validateForm = useCallback((formData: FormValues): ValidationErrors => {
    const newErrors: ValidationErrors = {}

    Object.keys(schema).forEach(fieldName => {
      const error = validateField(fieldName, formData[fieldName], formData)
      if (error) {
        newErrors[fieldName] = error
      }
    })

    setErrors(newErrors)
    const formIsValid = Object.keys(newErrors).length === 0
    setIsValid(formIsValid)

    return newErrors
  }, [schema, validateField])

  // Función para validar un campo específico (para validación en tiempo real)
  const validateSingleField = useCallback((fieldName: string, value: any, formData?: FormValues): boolean => {
    const rule = schema[fieldName]
    if (!rule) return true

    const sanitizedValue = typeof value === 'string' ? sanitizeInput(value) : value
    const stringValue = String(sanitizedValue || '')

    // Validación requerida
    if (rule.required && (!sanitizedValue || stringValue.trim() === '')) {
      const error = getValidationErrorMessage(fieldName, { required: true })
      setErrors(prev => ({ ...prev, [fieldName]: error }))
      setIsDirty(prev => ({ ...prev, [fieldName]: true }))
      return false
    }

    // Si no es requerido y está vacío, es válido
    if (!rule.required && (!sanitizedValue || stringValue.trim() === '')) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[fieldName]
        return newErrors
      })
      setIsDirty(prev => ({ ...prev, [fieldName]: true }))
      return true
    }

    // Validación de longitud mínima
    if (rule.minLength && stringValue.length < rule.minLength) {
      const error = getValidationErrorMessage(fieldName, { minLength: rule.minLength })
      setErrors(prev => ({ ...prev, [fieldName]: error }))
      setIsDirty(prev => ({ ...prev, [fieldName]: true }))
      return false
    }

    // Validación de longitud máxima
    if (rule.maxLength && stringValue.length > rule.maxLength) {
      const error = getValidationErrorMessage(fieldName, { maxLength: rule.maxLength })
      setErrors(prev => ({ ...prev, [fieldName]: error }))
      setIsDirty(prev => ({ ...prev, [fieldName]: true }))
      return false
    }

    // Validación por tipo
    if (rule.type) {
      let isValidType = false

      switch (rule.type) {
        case 'email':
          isValidType = validators.email(stringValue)
          break
        case 'url':
          isValidType = validators.url(stringValue)
          break
        case 'ip':
          isValidType = validators.ip(stringValue)
          break
        case 'domain':
          isValidType = validators.domain(stringValue)
          break
        case 'number':
          isValidType = validators.number(stringValue)
          break
        default:
          isValidType = true
      }

      if (!isValidType) {
        const error = getValidationErrorMessage(fieldName, { type: rule.type })
        setErrors(prev => ({ ...prev, [fieldName]: error }))
        setIsDirty(prev => ({ ...prev, [fieldName]: true }))
        return false
      }
    }

    // Validación personalizada
    if (rule.custom && !rule.custom(stringValue, formData)) {
      const error = rule.customMessage || `${fieldName} es inválido`
      setErrors(prev => ({ ...prev, [fieldName]: error }))
      setIsDirty(prev => ({ ...prev, [fieldName]: true }))
      return false
    }

    // Si llega aquí, es válido
    setErrors(prev => {
      const newErrors = { ...prev }
      delete newErrors[fieldName]
      return newErrors
    })
    setIsDirty(prev => ({ ...prev, [fieldName]: true }))

    return true
  }, [schema])

  // Función para limpiar errores
  const clearErrors = useCallback(() => {
    setErrors({})
    setIsValid(false)
    setIsDirty({})
  }, [])

  // Función para marcar campo como "sucio" (modificado por el usuario)
  const markFieldAsDirty = useCallback((fieldName: string) => {
    setIsDirty(prev => ({ ...prev, [fieldName]: true }))
  }, [])

  // Función para resetear validación
  const resetValidation = useCallback(() => {
    clearErrors()
  }, [clearErrors])

  // Efecto para recalcular isValid cuando cambian los errores
  useEffect(() => {
    const formIsValid = Object.keys(errors).length === 0
    setIsValid(formIsValid)
  }, [errors])

  return {
    errors,
    isValid,
    isDirty,
    validateForm,
    validateField,
    validateSingleField,
    clearErrors,
    resetValidation,
    markFieldAsDirty,
    // Función helper para obtener el error de un campo específico
    getFieldError: (fieldName: string) => errors[fieldName] || null,
    // Función helper para saber si un campo tiene error
    hasFieldError: (fieldName: string) => !!errors[fieldName],
    // Función helper para saber si un campo está "sucio"
    isFieldDirty: (fieldName: string) => isDirty[fieldName] || false
  }
}

// ===== HOOK PARA CAMPOS INDIVIDUALES =====

export const useFieldValidation = (
  fieldName: string,
  rule: ValidationRule,
  formData?: FormValues
) => {
  const [error, setError] = useState<string | null>(null)
  const [isDirty, setIsDirty] = useState(false)

  const validate = useCallback((value: any) => {
    const schema = { [fieldName]: rule }
    const mockHook = useFormValidation(schema)
    const fieldError = mockHook.validateField(fieldName, value, formData)

    setError(fieldError)
    setIsDirty(true)

    return !fieldError
  }, [fieldName, rule, formData])

  const clear = useCallback(() => {
    setError(null)
    setIsDirty(false)
  }, [])

  return {
    error,
    isDirty,
    isValid: !error,
    validate,
    clear
  }
}

// ===== HOOK PARA VALIDACIÓN ASÍNCRONA =====

export const useAsyncValidation = (schema: ValidationSchema) => {
  const [isValidating, setIsValidating] = useState(false)
  const [asyncErrors, setAsyncErrors] = useState<ValidationErrors>({})

  const validateAsync = useCallback(async (formData: FormValues): Promise<ValidationErrors> => {
    setIsValidating(true)
    setAsyncErrors({})

    const newErrors: ValidationErrors = {}

    // Ejecutar validaciones asíncronas en paralelo
    const validationPromises = Object.keys(schema).map(async (fieldName) => {
      const rule = schema[fieldName]
      if (rule.custom && typeof rule.custom === 'function') {
        try {
          // Aquí podrías hacer llamadas API para validación asíncrona
          // Por ejemplo: validar si un username ya existe
          const isValid = await Promise.resolve(rule.custom(formData[fieldName] as string, formData))
          if (!isValid) {
            newErrors[fieldName] = rule.customMessage || `${fieldName} es inválido`
          }
        } catch (error) {
          newErrors[fieldName] = `Error validando ${fieldName}`
        }
      }
    })

    await Promise.all(validationPromises)

    setAsyncErrors(newErrors)
    setIsValidating(false)

    return newErrors
  }, [schema])

  return {
    asyncErrors,
    isValidating,
    validateAsync,
    clearAsyncErrors: () => setAsyncErrors({})
  }
}

// ===== UTILIDADES ADICIONALES =====

export const createValidationSchema = (fields: { [key: string]: ValidationRule }): ValidationSchema => {
  return fields
}

export const mergeValidationSchemas = (...schemas: ValidationSchema[]): ValidationSchema => {
  return Object.assign({}, ...schemas)
}

export const extendValidationSchema = (baseSchema: ValidationSchema, extensions: ValidationSchema): ValidationSchema => {
  return { ...baseSchema, ...extensions }
}
