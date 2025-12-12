/**
 * Workspace Files Console
 * =======================
 * 
 * Componente para visualizar y explorar archivos generados en un workspace.
 * Muestra archivos organizados por categoría (recon, scans, enumeration, etc.)
 */

import React, { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { workspacesAPI, WorkspaceFile } from '../lib/api/workspaces/workspaces'
import { useWorkspace } from '../contexts/WorkspaceContext'
import { 
  Folder, 
  FileText, 
  Download,
  Search,
  X,
  ChevronRight,
  Home,
  Trash2
} from 'lucide-react'
import { toast } from 'sonner'

interface WorkspaceFilesConsoleProps {
  isOpen: boolean
  onClose: () => void
}

const CATEGORIES = [
  { id: 'all', name: 'Todos', icon: '📁' },
  { id: 'recon', name: 'Reconocimiento', icon: '🔍' },
  { id: 'scans', name: 'Escaneos', icon: '📡' },
  { id: 'enumeration', name: 'Enumeración', icon: '🔎' },
  { id: 'vuln_scans', name: 'Vulnerabilidades', icon: '⚠️' },
  { id: 'exploitation', name: 'Explotación', icon: '💥' },
  { id: 'postexploit', name: 'Post-Explotación', icon: '🔓' },
  { id: 'ad_scans', name: 'Active Directory', icon: '🏢' },
  { id: 'cloud_scans', name: 'Cloud', icon: '☁️' }
]

export const WorkspaceFilesConsole: React.FC<WorkspaceFilesConsoleProps> = ({ isOpen, onClose }) => {
  const { currentWorkspace } = useWorkspace()
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [currentPath, setCurrentPath] = useState<string>('')  // Path relativo dentro de la categoría
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFile, setSelectedFile] = useState<WorkspaceFile | null>(null)
  const [fileContent, setFileContent] = useState<string | null>(null)
  const [isLoadingContent, setIsLoadingContent] = useState(false)

  // Query para obtener archivos y directorios
  const { data: filesData, isLoading, refetch } = useQuery({
    queryKey: ['workspace-files', currentWorkspace?.id, selectedCategory, currentPath],
    queryFn: async () => {
      if (!currentWorkspace) return null
      const category = selectedCategory === 'all' ? undefined : selectedCategory
      const path = currentPath || undefined
      return await workspacesAPI.getWorkspaceFiles(currentWorkspace.id, category, path)
    },
    enabled: isOpen && !!currentWorkspace,
    staleTime: 30000, // 30 segundos
  })

  // Resetear path cuando cambia la categoría
  useEffect(() => {
    setCurrentPath('')
    setSelectedFile(null)
    setFileContent(null)
  }, [selectedCategory])

  // Filtrar items (archivos y directorios) por búsqueda
  const filteredItems = filesData?.items?.filter(item => 
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.category.toLowerCase().includes(searchQuery.toLowerCase())
  ) || []

  // Navegar a un directorio
  const navigateToDirectory = (dir: WorkspaceFile) => {
    // El path del directorio es relativo al workspace, necesitamos extraer el path relativo a la categoría
    const pathParts = dir.path.split('/')
    if (pathParts.length >= 2) {
      // pathParts[0] es la categoría, pathParts[1+] es el subdirectorio
      const subPath = pathParts.slice(1).join('/')
      setCurrentPath(subPath)
      setSelectedFile(null)
      setFileContent(null)
    } else {
      // Si solo tiene un nivel, usar el nombre del directorio
      setCurrentPath(dir.name)
      setSelectedFile(null)
      setFileContent(null)
    }
  }

  // Navegar hacia atrás
  const navigateBack = () => {
    if (currentPath) {
      const pathParts = currentPath.split('/')
      if (pathParts.length > 1) {
        setCurrentPath(pathParts.slice(0, -1).join('/'))
      } else {
        setCurrentPath('')
      }
      setSelectedFile(null)
      setFileContent(null)
    }
  }

  // Obtener breadcrumbs
  const getBreadcrumbs = () => {
    const crumbs = []
    if (selectedCategory !== 'all') {
      crumbs.push({ name: CATEGORIES.find(c => c.id === selectedCategory)?.name || selectedCategory, path: '' })
    }
    if (currentPath) {
      const pathParts = currentPath.split('/')
      pathParts.forEach((part, index) => {
        crumbs.push({
          name: part,
          path: pathParts.slice(0, index + 1).join('/')
        })
      })
    }
    return crumbs
  }

  // Cargar contenido del archivo
  const loadFileContent = async (file: WorkspaceFile) => {
    if (!currentWorkspace) return
    
    setSelectedFile(file)
    setIsLoadingContent(true)
    setFileContent(null)

    try {
      const content = await workspacesAPI.getWorkspaceFileContent(
        currentWorkspace.id,
        file.path,
        false
      ) as any

      if (content.is_binary) {
        setFileContent(null)
      } else {
        setFileContent(content.content || '')
      }
    } catch (error) {
      console.error('Error loading file content:', error)
      setFileContent('Error al cargar el archivo')
    } finally {
      setIsLoadingContent(false)
    }
  }

  // Descargar archivo
  const downloadFile = async (file: WorkspaceFile) => {
    if (!currentWorkspace) return

    try {
      const blob = await workspacesAPI.getWorkspaceFileContent(
        currentWorkspace.id,
        file.path,
        true
      ) as Blob

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading file:', error)
      toast.error('Error al descargar el archivo')
    }
  }

  // Eliminar archivo individual
  const deleteFile = async (file: WorkspaceFile) => {
    if (!currentWorkspace) return

    // Confirmación
    const confirmed = window.confirm(
      `¿Estás seguro de que deseas eliminar "${file.name}"?\n\nEsta acción no se puede deshacer.`
    )

    if (!confirmed) return

    try {
      await workspacesAPI.deleteWorkspaceFile(currentWorkspace.id, file.path)
      toast.success(`Archivo "${file.name}" eliminado correctamente`)
      
      // Si el archivo eliminado estaba seleccionado, limpiar la selección
      if (selectedFile?.path === file.path) {
        setSelectedFile(null)
        setFileContent(null)
      }
      
      // Refrescar la lista
      refetch()
    } catch (error: any) {
      console.error('Error deleting file:', error)
      toast.error(`Error al eliminar el archivo: ${error.response?.data?.message || error.message || 'Error desconocido'}`)
    }
  }

  // Eliminar todos los archivos
  const deleteAllFiles = async () => {
    if (!currentWorkspace) return

    const categoryName = selectedCategory === 'all' 
      ? 'todas las categorías' 
      : CATEGORIES.find(c => c.id === selectedCategory)?.name || selectedCategory

    // Confirmación
    const confirmed = window.confirm(
      `¿Estás seguro de que deseas eliminar TODOS los archivos de "${categoryName}"?\n\n` +
      `Esta acción eliminará ${filesData?.total_files || 0} archivo(s) y ${filesData?.total_directories || 0} directorio(s).\n\n` +
      `Esta acción NO se puede deshacer.`
    )

    if (!confirmed) return

    try {
      const category = selectedCategory === 'all' ? undefined : selectedCategory
      const result = await workspacesAPI.deleteAllWorkspaceFiles(currentWorkspace.id, category)
      
      toast.success(
        `Eliminados ${result.deleted_files} archivo(s) y ${result.deleted_directories} directorio(s) correctamente`
      )
      
      // Limpiar selección
      setSelectedFile(null)
      setFileContent(null)
      
      // Refrescar la lista
      refetch()
    } catch (error: any) {
      console.error('Error deleting all files:', error)
      toast.error(`Error al eliminar los archivos: ${error.response?.data?.message || error.message || 'Error desconocido'}`)
    }
  }

  // Formatear fecha
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-gray-50 border border-gray-200 rounded-xl shadow-2xl w-[90vw] h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 flex-shrink-0">
          <div className="flex items-center gap-3">
            <Folder className="w-6 h-6 text-gray-900" />
            <div>
              <h2 className="text-xl font-bold text-white">
                Archivos del Workspace
              </h2>
              <p className="text-sm text-gray-500">
                {currentWorkspace?.name || 'Sin workspace seleccionado'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex flex-1 overflow-hidden">
          {/* Sidebar - Categorías */}
          <div className="w-64 border-r border-gray-200 bg-white overflow-y-auto flex-shrink-0">
            <div className="p-4">
              <h3 className="text-sm font-semibold text-gray-500 mb-3">Categorías</h3>
              <div className="space-y-1">
                {CATEGORIES.map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => {
                      setSelectedCategory(cat.id)
                      setSelectedFile(null)
                      setFileContent(null)
                    }}
                    className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                      selectedCategory === cat.id
                        ? 'bg-red-600 text-white'
                        : 'text-gray-600 hover:bg-gray-700'
                    }`}
                  >
                    <span className="mr-2">{cat.icon}</span>
                    {cat.name}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Breadcrumbs */}
            {(currentPath || selectedCategory !== 'all') && (
              <div className="p-4 border-b border-gray-200 flex-shrink-0">
                <div className="flex items-center gap-2 text-sm">
                  <button
                    onClick={() => {
                      setCurrentPath('')
                      setSelectedFile(null)
                      setFileContent(null)
                    }}
                    className="flex items-center gap-1 text-gray-500 hover:text-gray-900 transition-colors"
                  >
                    <Home className="w-4 h-4" />
                    <span>Inicio</span>
                  </button>
                  {getBreadcrumbs().map((crumb, index) => (
                    <React.Fragment key={index}>
                      <ChevronRight className="w-4 h-4 text-gray-500" />
                      {index === getBreadcrumbs().length - 1 ? (
                        <span className="text-gray-900 font-medium">{crumb.name}</span>
                      ) : (
                        <button
                          onClick={() => {
                            setCurrentPath(crumb.path)
                            setSelectedFile(null)
                            setFileContent(null)
                          }}
                          className="text-gray-500 hover:text-gray-900 transition-colors"
                        >
                          {crumb.name}
                        </button>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            )}

            {/* Search Bar */}
            <div className="p-4 border-b border-gray-200 flex-shrink-0">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  placeholder="Buscar archivos..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-gray-200"
                />
              </div>
            </div>

            {/* Files and Directories List */}
            <div className="flex-1 overflow-y-auto p-4">
              {isLoading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-gray-500">Cargando archivos...</div>
                </div>
              ) : filteredItems.length === 0 ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center text-gray-500">
                    <Folder className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>No se encontraron archivos</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredItems.map((item) => {
                    if (item.type === 'directory') {
                      const dir = item as WorkspaceFile
                      return (
                        <div
                          key={dir.path}
                          onClick={() => navigateToDirectory(dir)}
                          className="p-3 rounded-md border cursor-pointer transition-colors bg-white border-gray-200 hover:border-gray-200 hover:bg-red-600/10"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3 flex-1 min-w-0">
                              <Folder className="w-5 h-5 text-blue-400 flex-shrink-0" />
                              <div className="flex-1 min-w-0">
                                <div className="text-white font-medium truncate">{dir.name}</div>
                                <div className="text-sm text-gray-500">
                                  {dir.file_count || 0} archivo{(dir.file_count || 0) !== 1 ? 's' : ''} • {formatDate(dir.modified)}
                                </div>
                              </div>
                            </div>
                            <ChevronRight className="w-5 h-5 text-gray-500 flex-shrink-0" />
                          </div>
                        </div>
                      )
                    } else {
                      const file = item as WorkspaceFile
                      return (
                        <div
                          key={file.path}
                          onClick={() => loadFileContent(file)}
                          className={`p-3 rounded-md border cursor-pointer transition-colors ${
                            selectedFile?.path === file.path
                              ? 'bg-red-600/20 border-gray-200'
                              : 'bg-white border-gray-200 hover:border-gray-200'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3 flex-1 min-w-0">
                              <FileText className="w-5 h-5 text-gray-500 flex-shrink-0" />
                              <div className="flex-1 min-w-0">
                                <div className="text-white font-medium truncate">{file.name}</div>
                                <div className="text-sm text-gray-500">
                                  {file.category} • {file.size_human} • {formatDate(file.modified)}
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-1 ml-2">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  downloadFile(file)
                                }}
                                className="p-2 text-gray-500 hover:text-gray-900 transition-colors flex-shrink-0"
                                title="Descargar archivo"
                              >
                                <Download className="w-5 h-5" />
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  deleteFile(file)
                                }}
                                className="p-2 text-gray-500 hover:text-red-400 transition-colors flex-shrink-0"
                                title="Eliminar archivo"
                              >
                                <Trash2 className="w-5 h-5" />
                              </button>
                            </div>
                          </div>
                        </div>
                      )
                    }
                  })}
                </div>
              )}
            </div>

            {/* File Content Viewer */}
            {selectedFile && (
              <div className="border-t border-gray-200 h-64 flex flex-col flex-shrink-0">
                <div className="p-3 border-b border-gray-200 bg-white flex items-center justify-between">
                  <div className="text-white font-medium">{selectedFile.name}</div>
                  <button
                    onClick={() => {
                      setSelectedFile(null)
                      setFileContent(null)
                    }}
                    className="text-gray-500 hover:text-white"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <div className="flex-1 overflow-auto p-4 bg-gray-50">
                  {isLoadingContent ? (
                    <div className="text-gray-500">Cargando contenido...</div>
                  ) : fileContent === null ? (
                    <div className="text-gray-500">
                      Archivo binario. Usa el botón de descarga para obtenerlo.
                    </div>
                  ) : (
                    <pre className="text-sm text-gray-600 whitespace-pre-wrap font-mono">
                      {fileContent}
                    </pre>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-white flex items-center justify-between flex-shrink-0">
          <div className="text-sm text-gray-500">
            {filesData ? (
              <>
                {filesData.total_files} archivo{filesData.total_files !== 1 ? 's' : ''}
                {filesData.total_directories > 0 && (
                  <> • {filesData.total_directories} directorio{filesData.total_directories !== 1 ? 's' : ''}</>
                )}
              </>
            ) : (
              'Cargando...'
            )}
          </div>
          <div className="flex items-center gap-2">
            {currentPath && (
              <button
                onClick={navigateBack}
                className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-md transition-colors text-sm"
              >
                ← Atrás
              </button>
            )}
            <button
              onClick={deleteAllFiles}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors text-sm flex items-center gap-2"
              title={`Eliminar todos los archivos de ${selectedCategory === 'all' ? 'todas las categorías' : CATEGORIES.find(c => c.id === selectedCategory)?.name || selectedCategory}`}
            >
              <Trash2 className="w-4 h-4" />
              Eliminar Todos
            </button>
            <button
              onClick={() => refetch()}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors text-sm"
            >
              Actualizar
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

