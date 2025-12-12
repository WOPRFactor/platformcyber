# Cursor AI Prompt for Factor X Style Migration

## Quick Prompt (Copy & Paste)

```
Continue updating this component to match the new enterprise design system. The project has been migrated from a dark cyberpunk theme to a light enterprise theme.

Key changes needed:
- bg-gray-800/900 → bg-white or bg-gray-50
- border-green-* → border-gray-200
- text-green-* → text-gray-900 (headings) or text-gray-500 (descriptions)
- Buttons: bg-green-* → bg-red-600 hover:bg-red-700
- Active tabs: border-green-* text-green-* → border-red-500 text-red-600
- Focus rings: focus:ring-green-* → focus:ring-red-500/20
- Cards should have: bg-white border border-gray-200 rounded-xl shadow-sm
- Remove any glow effects or neon styling

Reference the STYLE_GUIDE.md for complete patterns. Look at src/pages/Scanning.tsx as a reference for the correct style.
```

---

## Detailed Prompt for Batch Updates

```
I need you to update the styling of React components in this project. The design has been migrated from a dark cyberpunk theme (green on black) to a professional enterprise light theme.

## Style Rules:

### Backgrounds
- Page/section backgrounds: bg-gray-50 or bg-slate-50
- Cards and panels: bg-white
- Input backgrounds: bg-gray-50
- NO dark backgrounds (bg-gray-800, bg-gray-900) except for code blocks

### Borders
- All borders: border-gray-200 or border-gray-100
- NO colored borders (border-green-*, border-blue-500, etc.)
- Cards: border border-gray-200

### Text Colors
- Headings: text-gray-900
- Body text: text-gray-700 or text-gray-600
- Descriptions/secondary: text-gray-500
- Muted: text-gray-400
- NO green text (text-green-*)

### Buttons
- Primary: bg-red-600 hover:bg-red-700 text-white
- Secondary: bg-gray-100 hover:bg-gray-200 text-gray-700
- Ghost: text-gray-600 hover:bg-gray-100

### Active/Selected States
- Tab active: border-red-500 text-red-600
- Tab inactive: border-transparent text-gray-500 hover:text-gray-700

### Focus States
- focus:ring-2 focus:ring-red-500/20 focus:border-red-500

### Cards Structure
```jsx
<div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
  <h2 className="text-lg font-semibold text-gray-900">Title</h2>
  <p className="text-gray-500 text-sm mt-1">Description</p>
  {/* content */}
</div>
```

### Remove
- All glow effects (shadow-green-*, shadow-*-glow)
- Neon/cyberpunk styling
- font-mono except for actual code
- Emojis in UI text (use Lucide icons instead)

## Reference Files
Look at these already-updated files for the correct patterns:
- src/pages/Scanning.tsx
- src/pages/Exploitation.tsx
- src/components/Layout.tsx
- src/index.css (has all CSS variables)

Please update the component following these guidelines while preserving all functionality.
```

---

## Single File Update Prompt

```
Update this component to the new enterprise style:

1. Change backgrounds: bg-gray-800 → bg-white, bg-gray-900 → bg-gray-50
2. Change borders: border-green-* → border-gray-200
3. Change text: text-green-* → text-gray-900/500, text-white → text-gray-900
4. Change buttons: bg-green-* → bg-red-600
5. Change active states: border-green-* text-green-* → border-red-500 text-red-600
6. Add shadow-sm to cards
7. Use rounded-xl for cards
8. Keep all functionality intact

Reference: src/pages/Scanning.tsx for the correct style patterns.
```

---

## Bulk Migration Prompt

```
I need to migrate multiple components from dark theme to light enterprise theme. For each file:

FROM (old dark theme):
- bg-gray-800, bg-gray-900 → backgrounds
- border-green-500, border-green-400 → borders  
- text-green-400, text-green-500 → headings
- text-green-600 → descriptions
- Active: border-green-*, text-green-*

TO (new enterprise theme):
- bg-white, bg-gray-50 → backgrounds
- border-gray-200 → borders
- text-gray-900 → headings
- text-gray-500 → descriptions
- Active: border-red-500, text-red-600
- Buttons: bg-red-600 hover:bg-red-700 text-white

Apply these changes to all .tsx files in the specified directory while keeping the logic unchanged.
```

---

## Component-Specific Prompts

### For Tool Section Components (Nmap, Nikto, etc.)
```
Update this tool section component:
- Card wrapper: bg-white border border-gray-200 rounded-xl p-6 shadow-sm
- Section title: text-lg font-semibold text-gray-900
- Description: text-gray-500 text-sm
- Input fields: bg-gray-50 border-gray-200 rounded-lg focus:ring-red-500/20
- Execute button: bg-red-600 hover:bg-red-700 text-white rounded-lg
- Secondary buttons: bg-gray-100 hover:bg-gray-200 text-gray-700
```

### For Tab Components
```
Update the tabs styling:
- Container: border-b border-gray-200
- Active tab: border-b-2 border-red-500 text-red-600
- Inactive tab: border-transparent text-gray-500 hover:text-gray-700
- Add transition-colors to buttons
```

### For Modal Components
```
Update modal styling:
- Overlay: bg-black/50 backdrop-blur-sm
- Modal container: bg-white rounded-xl shadow-xl
- Header: border-b border-gray-200 p-4
- Title: text-lg font-semibold text-gray-900
- Body: p-6
- Footer: border-t border-gray-100 p-4 bg-gray-50
- Close button: text-gray-400 hover:text-gray-600
```

### For Form Components
```
Update form styling:
- Labels: text-sm font-medium text-gray-700 mb-1
- Inputs: w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-red-500/20 focus:border-red-500
- Select: same as inputs
- Checkbox/Radio: accent-red-600
- Error text: text-sm text-red-600 mt-1
```

---

## Validation Checklist

After updating, verify:
- [ ] No bg-gray-800 or bg-gray-900 (except sidebar/terminal)
- [ ] No border-green-* classes
- [ ] No text-green-* classes
- [ ] All buttons use red-600 for primary actions
- [ ] Active tabs use border-red-500 text-red-600
- [ ] Cards have shadow-sm and rounded-xl
- [ ] Focus states use red-500
- [ ] All functionality still works
