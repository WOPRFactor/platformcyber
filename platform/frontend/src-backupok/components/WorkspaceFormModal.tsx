import React, { useState, useEffect } from 'react';
import { X, Briefcase, User, Target, Calendar, FileText, Save, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface WorkspaceFormData {
  name: string;
  description: string;
  client_name: string;
  client_contact: string;
  target_domain: string;
  target_ip: string;
  target_type: 'web' | 'api' | 'mobile' | 'network' | 'other' | '';
  in_scope: string;
  out_of_scope: string;
  start_date: string;
  end_date: string;
  notes: string;
}

interface WorkspaceFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: WorkspaceFormData) => Promise<void>;
  initialData?: Partial<WorkspaceFormData>;
  mode: 'create' | 'edit';
}

const WorkspaceFormModal: React.FC<WorkspaceFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialData,
  mode = 'create'
}) => {
  const [formData, setFormData] = useState<WorkspaceFormData>({
    name: '',
    description: '',
    client_name: '',
    client_contact: '',
    target_domain: '',
    target_ip: '',
    target_type: '',
    in_scope: '',
    out_of_scope: '',
    start_date: '',
    end_date: '',
    notes: ''
  });

  const [errors, setErrors] = useState<Partial<Record<keyof WorkspaceFormData, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Cargar datos iniciales si están disponibles
  useEffect(() => {
    if (initialData) {
      setFormData(prev => ({
        ...prev,
        ...initialData,
        target_type: initialData.target_type || ''
      }));
    }
  }, [initialData]);

  // Limpiar formulario al cerrar
  useEffect(() => {
    if (!isOpen) {
      setFormData({
        name: '',
        description: '',
        client_name: '',
        client_contact: '',
        target_domain: '',
        target_ip: '',
        target_type: '',
        in_scope: '',
        out_of_scope: '',
        start_date: '',
        end_date: '',
        notes: ''
      });
      setErrors({});
    }
  }, [isOpen]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Limpiar error del campo cuando el usuario empieza a escribir
    if (errors[name as keyof WorkspaceFormData]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name as keyof WorkspaceFormData];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof WorkspaceFormData, string>> = {};

    // Validaciones requeridas
    if (!formData.name.trim()) {
      newErrors.name = 'El nombre del workspace es requerido';
    }

    if (!formData.client_name.trim()) {
      newErrors.client_name = 'El nombre del cliente es requerido';
    }

    if (!formData.target_domain.trim()) {
      newErrors.target_domain = 'El dominio/URL principal es requerido';
    }

    // Validación de email si se proporciona
    if (formData.client_contact && !formData.client_contact.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      newErrors.client_contact = 'Ingrese un email válido';
    }

    // Validación de fechas
    if (formData.start_date && formData.end_date) {
      const start = new Date(formData.start_date);
      const end = new Date(formData.end_date);
      if (end < start) {
        newErrors.end_date = 'La fecha de fin debe ser posterior a la fecha de inicio';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error('Por favor, corrija los errores en el formulario');
      return;
    }

    setIsSubmitting(true);

    try {
      // Filtrar campos vacíos y preparar datos para envío
      const dataToSubmit = {
        ...formData,
        target_type: formData.target_type || undefined,
        start_date: formData.start_date || null,
        end_date: formData.end_date || null
      };

      await onSubmit(dataToSubmit as WorkspaceFormData);
      toast.success(mode === 'create' ? 'Workspace creado exitosamente' : 'Workspace actualizado exitosamente');
      onClose();
    } catch (error: any) {
      console.error('Error al guardar workspace:', error);
      toast.error(error?.message || 'Error al guardar el workspace');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[10000] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/70 backdrop-blur-sm z-[10001]"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-gray-50 border border-gray-200/30 rounded-xl shadow-2xl z-[10002]">
        {/* Header */}
        <div className="sticky top-0 z-10 bg-gray-50 border-b border-gray-200/30 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Briefcase className="w-6 h-6 text-gray-900" />
              <h2 className="text-2xl font-bold text-gray-900">
                {mode === 'create' ? 'Crear Nuevo Workspace' : 'Editar Workspace'}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-900 transition-colors"
              disabled={isSubmitting}
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-8">
          {/* Sección 1: Información del Proyecto */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Briefcase className="w-5 h-5" />
              Información del Proyecto
            </h3>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Nombre del Workspace <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className={`w-full bg-white border ${errors.name ? 'border-red-500' : 'border-gray-200'} rounded-xl px-4 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500`}
                  placeholder="Ej: Proyecto Acme Corp - Pentesting Web"
                  disabled={isSubmitting}
                />
                {errors.name && <p className="text-red-400 text-sm mt-1">{errors.name}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Descripción
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={3}
                  className="w-full bg-white border border-gray-200 rounded-xl px-4 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 resize-none"
                  placeholder="Descripción general del proyecto..."
                  disabled={isSubmitting}
                />
              </div>
            </div>
          </div>

          {/* Sección 2: Información del Cliente */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <User className="w-5 h-5" />
              Información del Cliente
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Nombre del Cliente <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  name="client_name"
                  value={formData.client_name}
                  onChange={handleChange}
                  className={`w-full bg-white border ${errors.client_name ? 'border-red-500' : 'border-gray-200'} rounded-xl px-4 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500`}
                  placeholder="Ej: Acme Corporation"
                  disabled={isSubmitting}
                />
                {errors.client_name && <p className="text-red-400 text-sm mt-1">{errors.client_name}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Contacto del Cliente (Email)
                </label>
                <input
                  type="email"
                  name="client_contact"
                  value={formData.client_contact}
                  onChange={handleChange}
                  className={`w-full bg-white border ${errors.client_contact ? 'border-red-500' : 'border-gray-200'} rounded-xl px-4 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500`}
                  placeholder="contacto@cliente.com"
                  disabled={isSubmitting}
                />
                {errors.client_contact && <p className="text-red-400 text-sm mt-1">{errors.client_contact}</p>}
              </div>
            </div>
          </div>

          {/* Sección 3: Target Principal */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Target className="w-5 h-5" />
              Target Principal
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Dominio/URL Principal <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  name="target_domain"
                  value={formData.target_domain}
                  onChange={handleChange}
                  className={`w-full bg-white border ${errors.target_domain ? 'border-red-500' : 'border-gray-200'} rounded-xl px-4 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500`}
                  placeholder="Ej: example.com, https://app.example.com"
                  disabled={isSubmitting}
                />
                {errors.target_domain && <p className="text-red-400 text-sm mt-1">{errors.target_domain}</p>}
                <p className="text-xs text-gray-500 mt-1">
                  Este será el target por defecto en todos los scans
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  IP del Target (Opcional)
                </label>
                <input
                  type="text"
                  name="target_ip"
                  value={formData.target_ip}
                  onChange={handleChange}
                  className="w-full bg-white border border-gray-200 rounded-xl px-4 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
                  placeholder="Ej: 192.168.1.100"
                  disabled={isSubmitting}
                />
              </div>

              <div className="md:col-span-3">
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Tipo de Aplicación
                </label>
                <select
                  name="target_type"
                  value={formData.target_type}
                  onChange={handleChange}
                  className="w-full bg-white border border-gray-200 rounded-xl px-4 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
                  disabled={isSubmitting}
                >
                  <option value="">Seleccionar tipo...</option>
                  <option value="web">Web Application</option>
                  <option value="api">REST API</option>
                  <option value="mobile">Mobile Backend</option>
                  <option value="network">Network Infrastructure</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          {/* Sección 4: Scope del Proyecto */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Scope del Proyecto
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  In Scope
                </label>
                <textarea
                  name="in_scope"
                  value={formData.in_scope}
                  onChange={handleChange}
                  rows={4}
                  className="w-full bg-white border border-gray-200 rounded-xl px-4 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 resize-none"
                  placeholder="- Aplicación web principal&#10;- API REST en /api/*&#10;- Subdominios *.example.com&#10;- Direcciones IP: 192.168.1.0/24"
                  disabled={isSubmitting}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Elementos dentro del alcance del proyecto
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Out of Scope
                </label>
                <textarea
                  name="out_of_scope"
                  value={formData.out_of_scope}
                  onChange={handleChange}
                  rows={4}
                  className="w-full bg-white border border-gray-200 rounded-xl px-4 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 resize-none"
                  placeholder="- Servidores de producción activos&#10;- Bases de datos de usuarios reales&#10;- Sistemas de terceros"
                  disabled={isSubmitting}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Elementos fuera del alcance del proyecto
                </p>
              </div>
            </div>
          </div>

          {/* Sección 5: Fechas */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Fechas del Proyecto
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Fecha de Inicio
                </label>
                <input
                  type="date"
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleChange}
                  className="w-full bg-white border border-gray-200 rounded-xl px-4 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
                  disabled={isSubmitting}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-600 mb-2">
                  Fecha Límite
                </label>
                <input
                  type="date"
                  name="end_date"
                  value={formData.end_date}
                  onChange={handleChange}
                  className={`w-full bg-white border ${errors.end_date ? 'border-red-500' : 'border-gray-200'} rounded-xl px-4 py-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500`}
                  disabled={isSubmitting}
                />
                {errors.end_date && <p className="text-red-400 text-sm mt-1">{errors.end_date}</p>}
              </div>
            </div>
          </div>

          {/* Sección 6: Notas */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Notas Adicionales
            </h3>
            <div>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleChange}
                rows={4}
                className="w-full bg-white border border-gray-200 rounded-xl px-4 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 resize-none"
                placeholder="Notas, requisitos especiales, metodología acordada, etc..."
                disabled={isSubmitting}
              />
            </div>
          </div>

          {/* Footer con botones */}
          <div className="flex justify-end gap-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors font-medium"
              disabled={isSubmitting}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-red-600 hover:bg-red-600 text-white rounded-xl transition-colors font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Guardando...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  {mode === 'create' ? 'Crear Workspace' : 'Guardar Cambios'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default WorkspaceFormModal;

