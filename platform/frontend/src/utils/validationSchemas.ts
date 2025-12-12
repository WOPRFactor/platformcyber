// ===== ESQUEMAS DE VALIDACIÓN PARA FORMULARIOS =====

export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: string, formData?: any) => boolean
  customMessage?: string
  type?: 'email' | 'url' | 'ip' | 'domain' | 'number' | 'text'
}

export interface ValidationSchema {
  [key: string]: ValidationRule
}

// ===== VALIDADORES PREDEFINIDOS =====

export const validators = {
  email: (value: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(value)
  },

  url: (value: string): boolean => {
    try {
      new URL(value.startsWith('http') ? value : `http://${value}`)
      return true
    } catch {
      return false
    }
  },

  ip: (value: string): boolean => {
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
    return ipRegex.test(value)
  },

  domain: (value: string): boolean => {
    const domainRegex = /^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$/
    return domainRegex.test(value)
  },

  number: (value: string): boolean => {
    return !isNaN(Number(value)) && !isNaN(parseFloat(value))
  },

  port: (value: string): boolean => {
    const port = parseInt(value)
    return port >= 1 && port <= 65535
  },

  cidr: (value: string): boolean => {
    const cidrRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(?:[0-9]|[1-2][0-9]|3[0-2])$/
    return cidrRegex.test(value)
  },

  noSpecialChars: (value: string): boolean => {
    const specialCharsRegex = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/
    return !specialCharsRegex.test(value)
  },

  alphanumeric: (value: string): boolean => {
    const alphanumericRegex = /^[a-zA-Z0-9]+$/
    return alphanumericRegex.test(value)
  },

  strongPassword: (value: string): boolean => {
    // Al menos 8 caracteres, una mayúscula, una minúscula, un número
    const strongPasswordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/
    return strongPasswordRegex.test(value)
  }
}

// ===== ESQUEMAS DE VALIDACIÓN POR FORMULARIO =====

export const validationSchemas = {
  // ===== AUTENTICACIÓN =====
  login: {
    username: {
      required: true,
      minLength: 3,
      maxLength: 50,
      custom: validators.noSpecialChars,
      customMessage: 'El nombre de usuario no puede contener caracteres especiales'
    },
    password: {
      required: true,
      minLength: 6,
      maxLength: 100
    }
  } as ValidationSchema,

  // ===== RECONOCIMIENTO =====
  dnsLookup: {
    target: {
      required: true,
      type: 'domain'
    }
  } as ValidationSchema,

  portScan: {
    target: {
      required: true,
      type: 'ip'
    },
    ports: {
      required: false,
      pattern: /^(\d+(-\d+)?)(,\s*\d+(-\d+)?)*$/,
      customMessage: 'Formato: 80,443 o 1-1024'
    },
    timeout: {
      required: false,
      type: 'number',
      custom: (value) => parseInt(value) >= 1 && parseInt(value) <= 30,
      customMessage: 'Timeout debe estar entre 1 y 30 segundos'
    }
  } as ValidationSchema,

  // ===== VULNERABILITY ASSESSMENT =====
  vulnScan: {
    target: {
      required: true,
      type: 'ip'
    },
    scanType: {
      required: true
    },
    depth: {
      required: false,
      type: 'number',
      custom: (value) => parseInt(value) >= 1 && parseInt(value) <= 5,
      customMessage: 'Profundidad debe estar entre 1 y 5'
    }
  } as ValidationSchema,

  // ===== OWASP AUDITOR =====
  owaspAudit: {
    target: {
      required: true,
      custom: (value) => validators.url(value) || validators.ip(value),
      customMessage: 'Debe ser una URL válida o dirección IP'
    }
  } as ValidationSchema,

  // ===== MITRE ATTACKS =====
  mitreSimulation: {
    target: {
      required: true,
      custom: (value) => validators.ip(value) || validators.domain(value),
      customMessage: 'Debe ser una IP o dominio válido'
    },
    technique: {
      required: true
    }
  } as ValidationSchema,

  // ===== REPORTING =====
  reportGeneration: {
    title: {
      required: true,
      minLength: 5,
      maxLength: 100
    },
    target: {
      required: true,
      custom: (value) => validators.url(value) || validators.ip(value) || validators.domain(value),
      customMessage: 'Debe ser una URL, IP o dominio válido'
    },
    startDate: {
      required: false,
      custom: (value) => !isNaN(Date.parse(value)),
      customMessage: 'Fecha inválida'
    },
    endDate: {
      required: false,
      custom: (value) => !isNaN(Date.parse(value)),
      customMessage: 'Fecha inválida'
    }
  } as ValidationSchema,

  // ===== IA ANALYSIS =====
  aiAnalysis: {
    query: {
      required: true,
      minLength: 10,
      maxLength: 1000
    },
    context: {
      required: false,
      maxLength: 5000
    },
    model: {
      required: false
    }
  } as ValidationSchema,

  // ===== EXPLOITATION =====
  exploitConfig: {
    target: {
      required: true,
      custom: (value) => validators.ip(value) || validators.domain(value),
      customMessage: 'Debe ser una IP o dominio válido'
    },
    port: {
      required: false,
      custom: validators.port,
      customMessage: 'Puerto debe estar entre 1 y 65535'
    },
    exploit: {
      required: true
    },
    payload: {
      required: false
    }
  } as ValidationSchema,

  // ===== CONFIGURACIÓN =====
  userProfile: {
    username: {
      required: true,
      minLength: 3,
      maxLength: 30,
      custom: validators.alphanumeric,
      customMessage: 'Solo letras y números'
    },
    email: {
      required: true,
      type: 'email'
    },
    currentPassword: {
      required: true,
      minLength: 6
    },
    newPassword: {
      required: false,
      custom: validators.strongPassword,
      customMessage: 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número'
    },
    confirmPassword: {
      required: false,
      custom: (value, formData) => value === formData?.newPassword,
      customMessage: 'Las contraseñas no coinciden'
    }
  } as ValidationSchema,

  // ===== NETWORK SCANNING =====
  networkScan: {
    network: {
      required: true,
      custom: validators.cidr,
      customMessage: 'Debe ser una red en formato CIDR (ej: 192.168.1.0/24)'
    },
    scanType: {
      required: true
    },
    timing: {
      required: false,
      custom: (value) => ['T1', 'T2', 'T3', 'T4', 'T5'].includes(value),
      customMessage: 'Timing debe ser T1, T2, T3, T4 o T5'
    }
  } as ValidationSchema,

  // ===== WEB APPLICATION SCANNING =====
  webScan: {
    url: {
      required: true,
      type: 'url'
    },
    scanProfile: {
      required: true
    },
    userAgent: {
      required: false,
      maxLength: 200
    },
    cookie: {
      required: false,
      maxLength: 500
    }
  } as ValidationSchema,

  // ===== API TESTING =====
  apiTest: {
    endpoint: {
      required: true,
      type: 'url'
    },
    method: {
      required: true,
      custom: (value) => ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].includes(value.toUpperCase()),
      customMessage: 'Método HTTP inválido'
    },
    headers: {
      required: false,
      custom: (value) => {
        if (!value) return true
        try {
          JSON.parse(value)
          return true
        } catch {
          return false
        }
      },
      customMessage: 'Headers debe ser JSON válido'
    },
    body: {
      required: false,
      custom: (value) => {
        if (!value) return true
        try {
          JSON.parse(value)
          return true
        } catch {
          return false
        }
      },
      customMessage: 'Body debe ser JSON válido'
    }
  } as ValidationSchema,

  // ===== SCHEDULED TASKS =====
  scheduledTask: {
    name: {
      required: true,
      minLength: 3,
      maxLength: 100,
      custom: validators.noSpecialChars,
      customMessage: 'El nombre no puede contener caracteres especiales'
    },
    function: {
      required: true
    },
    type: {
      required: true,
      custom: (value) => ['cron', 'interval', 'date'].includes(value),
      customMessage: 'Tipo debe ser cron, interval o date'
    },
    trigger: {
      required: true,
      custom: (value, formData) => {
        if (!formData?.type) return false
        try {
          const trigger = JSON.parse(value)
          if (formData.type === 'cron') {
            return trigger.hour !== undefined || trigger.minute !== undefined || trigger.day_of_week !== undefined
          }
          if (formData.type === 'interval') {
            return trigger.hours !== undefined || trigger.minutes !== undefined || trigger.days !== undefined
          }
          if (formData.type === 'date') {
            return trigger.run_date !== undefined
          }
          return false
        } catch {
          return false
        }
      },
      customMessage: 'Configuración de trigger inválida para el tipo seleccionado'
    }
  } as ValidationSchema
}

// ===== FUNCIONES DE UTILIDAD =====

export const sanitizeInput = (value: string): string => {
  // Eliminar caracteres potencialmente peligrosos
  return value
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<[^>]*>/g, '')
    .trim()
}

export const getValidationErrorMessage = (field: string, rule: ValidationRule): string => {
  if (rule.customMessage) return rule.customMessage

  if (rule.required) return `${field} es requerido`
  if (rule.minLength) return `${field} debe tener al menos ${rule.minLength} caracteres`
  if (rule.maxLength) return `${field} no puede tener más de ${rule.maxLength} caracteres`
  if (rule.type === 'email') return `${field} debe ser un email válido`
  if (rule.type === 'url') return `${field} debe ser una URL válida`
  if (rule.type === 'ip') return `${field} debe ser una IP válida`
  if (rule.type === 'domain') return `${field} debe ser un dominio válido`

  return `${field} es inválido`
}
