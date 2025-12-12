# Factor X - Enterprise Design System Guide

## Overview

This project has been redesigned from a dark cyberpunk theme (green on black) to a professional enterprise security platform style (light theme with dark sidebar), inspired by Splunk, CrowdStrike, and similar enterprise security tools.

## Color Palette

### Brand Colors
- **Primary (Red)**: `#dc2626` (red-600) - Main brand color, used for CTAs and active states
- **Primary Dark**: `#991b1b` (red-700) - Hover states
- **Primary Light**: `#fef2f2` (red-50) - Light backgrounds

### Backgrounds
- **Page Background**: `#f8fafc` (slate-50) or `#f9fafb` (gray-50)
- **Cards/Panels**: `#ffffff` (white)
- **Sidebar**: `#0f172a` (slate-900) - Dark sidebar
- **Sidebar Hover**: `#1e293b` (slate-800)

### Text Colors
- **Headings**: `#111827` (gray-900)
- **Body Text**: `#374151` (gray-700)
- **Secondary Text**: `#6b7280` (gray-500)
- **Muted Text**: `#9ca3af` (gray-400)
- **Sidebar Text**: `#94a3b8` (slate-400)
- **Sidebar Text Active**: `#ffffff` (white)

### Borders
- **Default**: `#e5e7eb` (gray-200)
- **Light**: `#f3f4f6` (gray-100)
- **Focus Ring**: `#dc2626` with 20% opacity

### Severity Colors (for vulnerabilities/alerts)
- **Critical**: `#dc2626` (red-600) / bg: `#fef2f2` (red-50)
- **High**: `#ea580c` (orange-600) / bg: `#fff7ed` (orange-50)
- **Medium**: `#d97706` (amber-600) / bg: `#fffbeb` (amber-50)
- **Low**: `#2563eb` (blue-600) / bg: `#eff6ff` (blue-50)
- **Info**: `#6b7280` (gray-500) / bg: `#f9fafb` (gray-50)

### Status Colors
- **Success**: `#10b981` (emerald-500)
- **Warning**: `#f59e0b` (amber-500)
- **Error**: `#ef4444` (red-500)
- **Info**: `#3b82f6` (blue-500)

## Component Patterns

### Page Layout Structure
```tsx
<div className="space-y-6">
  {/* Page Header */}
  <div className="flex items-center justify-between">
    <div>
      <h1 className="text-2xl font-semibold text-gray-900">Page Title</h1>
      <p className="text-gray-500 mt-1">Page description goes here</p>
    </div>
    <div className="flex items-center gap-2 px-3 py-1.5 bg-{color}-50 text-{color}-600 rounded-lg text-sm font-medium">
      <Icon className="w-4 h-4" />
      Status Badge
    </div>
  </div>

  {/* Content Cards */}
  <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
    {/* Card content */}
  </div>
</div>
```

### Card Component
```tsx
<div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
  <div className="mb-4">
    <h2 className="text-lg font-semibold text-gray-900">Card Title</h2>
    <p className="text-gray-500 text-sm mt-1">Card description</p>
  </div>
  {/* Card content */}
</div>
```

### Tabs Navigation
```tsx
<div className="flex border-b border-gray-200 mb-4 overflow-x-auto">
  <button
    className={`flex items-center gap-2 px-4 py-2 border-b-2 whitespace-nowrap transition-colors ${
      isActive
        ? 'border-red-500 text-red-600'
        : 'border-transparent text-gray-500 hover:text-gray-700'
    }`}
  >
    <Icon className="w-4 h-4" />
    Tab Label
  </button>
</div>
```

### Primary Button
```tsx
<button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors">
  Button Text
</button>
```

### Secondary Button
```tsx
<button className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors">
  Button Text
</button>
```

### Ghost Button
```tsx
<button className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium transition-colors">
  Button Text
</button>
```

### Input Field
```tsx
<input
  type="text"
  className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all"
  placeholder="Placeholder text"
/>
```

### Select Field
```tsx
<select className="px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 transition-all">
  <option>Option 1</option>
</select>
```

### Badge/Tag
```tsx
// Status badges
<span className="px-2.5 py-1 text-xs font-medium rounded-full bg-emerald-50 text-emerald-700">
  Active
</span>

// Severity badges
<span className="px-2.5 py-1 text-xs font-medium rounded-full bg-red-50 text-red-700">
  Critical
</span>
```

### Warning/Alert Box
```tsx
<div className="border border-amber-200 bg-amber-50 p-4 rounded-xl">
  <div className="flex items-center gap-2 mb-2">
    <AlertTriangle className="w-5 h-5 text-amber-600" />
    <h3 className="font-semibold text-amber-800">Warning Title</h3>
  </div>
  <p className="text-amber-700 text-sm">Warning message content</p>
</div>
```

### Security Warning Box (for dangerous tools)
```tsx
<div className="border border-red-200 bg-red-50 p-6 rounded-xl">
  <div className="flex items-center gap-2 mb-4">
    <AlertTriangle className="w-6 h-6 text-red-600" />
    <h2 className="text-lg font-semibold text-red-800">SECURITY WARNING</h2>
  </div>
  <div className="text-red-700 space-y-2 text-sm">
    <p>• Warning point 1</p>
    <p>• Warning point 2</p>
  </div>
</div>
```

### Table
```tsx
<div className="overflow-x-auto">
  <table className="w-full">
    <thead>
      <tr className="border-b border-gray-200">
        <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900">Header</th>
      </tr>
    </thead>
    <tbody>
      <tr className="border-b border-gray-100 hover:bg-gray-50">
        <td className="py-3 px-4 text-sm text-gray-700">Cell content</td>
      </tr>
    </tbody>
  </table>
</div>
```

### List Item (for history/sessions)
```tsx
<div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100">
  <div>
    <div className="font-medium text-gray-900">Item Title</div>
    <div className="text-sm text-gray-500">Item description</div>
  </div>
  <div className="flex items-center gap-2">
    <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-emerald-50 text-emerald-700">
      Status
    </span>
  </div>
</div>
```

## Migration Patterns

### Old → New Mapping

| Old (Cyberpunk) | New (Enterprise) |
|-----------------|------------------|
| `bg-gray-900` | `bg-gray-50` or page background |
| `bg-gray-800` | `bg-white` |
| `bg-gray-700` | `bg-gray-50` |
| `border-green-500` | `border-gray-200` |
| `border-green-400` | `border-gray-200` |
| `text-green-400` | `text-gray-900` (headings) |
| `text-green-500` | `text-gray-800` |
| `text-green-600` | `text-gray-500` |
| `text-green-300` | `text-gray-700` |
| `text-gray-400` | `text-gray-500` |
| `text-gray-300` | `text-gray-600` |
| `text-white` | `text-gray-900` |
| `hover:bg-green-*` | `hover:bg-red-*` |
| `focus:ring-green-500` | `focus:ring-red-500` |
| `bg-green-600` (buttons) | `bg-red-600` |
| `rounded-lg` | `rounded-xl` (cards) |
| `font-mono` (general text) | Remove or use only for code |

### Icon Colors
- Active/Selected: `text-red-500` or `text-red-600`
- Default: `text-gray-400` or `text-gray-500`
- On dark sidebar: `text-slate-400`, active: `text-white`

## Typography

### Headings
- **Page Title**: `text-2xl font-semibold text-gray-900`
- **Section Title**: `text-lg font-semibold text-gray-900`
- **Card Title**: `text-base font-semibold text-gray-900`
- **Subsection**: `text-sm font-medium text-gray-900`

### Body Text
- **Primary**: `text-sm text-gray-700` or `text-gray-600`
- **Secondary**: `text-sm text-gray-500`
- **Muted**: `text-xs text-gray-400`

## Spacing

- Page padding: Applied by Layout component
- Card padding: `p-6`
- Section spacing: `space-y-6`
- Inner spacing: `space-y-4` or `gap-4`
- Compact spacing: `space-y-2` or `gap-2`

## Shadows

- Cards: `shadow-sm`
- Dropdowns/Modals: `shadow-lg` or `shadow-xl`
- Hover effects: `hover:shadow-md`

## Transitions

- Default: `transition-colors` or `transition-all`
- Duration: Default (150ms) or `duration-200`

## Files Already Updated

These files are already converted to the new style and can be used as reference:

- `src/index.css` - Complete design system
- `src/components/Layout.tsx` - Main layout with sidebar
- `src/pages/Login.tsx` - Login page
- `src/pages/DashboardEnhanced.tsx` - Dashboard
- `src/pages/Scanning.tsx` - Scanning page
- `src/pages/VulnerabilityAssessment.tsx` - Vulnerability page
- `src/pages/Reconnaissance.tsx` - Reconnaissance page
- `src/pages/Exploitation.tsx` - Exploitation page
- `src/pages/PostExploitation.tsx` - Post-exploitation page
- `src/pages/Cloud.tsx` - Cloud security page
- `src/pages/Container.tsx` - Container security page
- `src/pages/ActiveDirectory.tsx` - AD page
- `src/pages/Reporting.tsx` - Reporting page
- `src/components/WorkspaceSelector.tsx` - Workspace selector
- `src/components/LoadingSpinner.tsx` - Loading spinner
- `src/components/charts/StatCard.tsx` - Stat cards
- `src/components/charts/ChartContainer.tsx` - Chart wrapper

## Files That Need Updating

All component files in these directories need to be updated:

- `src/pages/*/components/**/*.tsx`
- `src/components/exploitation/*.tsx`
- `src/components/postExploitation/*.tsx`
- `src/components/cloud/*.tsx`
- `src/components/container/*.tsx`
- `src/components/activeDirectory/*.tsx`
- `src/components/scanning/*.tsx`
- `src/components/systemMonitor/*.tsx`
- `src/components/charts/*.tsx` (except StatCard and ChartContainer)
- Modal components
