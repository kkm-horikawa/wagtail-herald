/**
 * Schema Widget - Core implementation
 *
 * A widget for selecting Schema.org types and configuring their properties.
 */

import {
  SCHEMA_TEMPLATES,
  type SchemaTemplate,
  getTemplatesByCategory,
  getDefaultOnTemplates,
} from './schema-templates'

/**
 * Widget state containing selected types and their properties
 */
export interface SchemaWidgetState {
  types: string[]
  properties: Record<string, Record<string, unknown>>
}

/**
 * Widget instance with state management methods
 */
export interface SchemaWidgetInstance {
  getState(): SchemaWidgetState
  setState(state: SchemaWidgetState): void
  destroy(): void
}

/**
 * Category display configuration
 */
const CATEGORY_LABELS: Record<string, { en: string; ja: string }> = {
  'site-wide': { en: 'Site-wide', ja: 'サイト全体' },
  content: { en: 'Content', ja: 'コンテンツ' },
  business: { en: 'Business', ja: 'ビジネス' },
  interactive: { en: 'Interactive', ja: 'インタラクティブ' },
  events: { en: 'Events', ja: 'イベント' },
  people: { en: 'People', ja: '人物' },
  specialized: { en: 'Specialized', ja: '特殊' },
}

/**
 * Category display order
 */
const CATEGORY_ORDER = [
  'site-wide',
  'content',
  'business',
  'interactive',
  'events',
  'people',
  'specialized',
]

/**
 * Detect if the current locale is Japanese
 */
function isJapaneseLocale(): boolean {
  if (typeof document === 'undefined') return false
  const htmlLang = document.documentElement.lang
  return htmlLang?.startsWith('ja') ?? false
}

/**
 * Create default state with default-on types selected
 */
function createDefaultState(): SchemaWidgetState {
  const state: SchemaWidgetState = { types: [], properties: {} }
  const defaultOnTemplates = getDefaultOnTemplates()
  for (const template of defaultOnTemplates) {
    state.types.push(template.type)
    state.properties[template.type] = { ...template.placeholder }
  }
  return state
}

/**
 * Initialize the Schema Widget on a container element
 */
export function initSchemaWidget(
  container: HTMLElement,
  initialState?: SchemaWidgetState,
): SchemaWidgetInstance {
  // Add default-on types only when no initial state is provided
  const state: SchemaWidgetState = initialState
    ? { types: [...initialState.types], properties: { ...initialState.properties } }
    : createDefaultState()

  const isJa = isJapaneseLocale()

  // Initial render
  render(container, state, isJa)

  return {
    getState: () => ({
      types: [...state.types],
      properties: JSON.parse(JSON.stringify(state.properties)),
    }),
    setState: (newState) => {
      state.types = [...newState.types]
      state.properties = JSON.parse(JSON.stringify(newState.properties))
      render(container, state, isJa)
    },
    destroy: () => {
      container.innerHTML = ''
    },
  }
}

/**
 * Render the widget UI
 */
function render(
  container: HTMLElement,
  state: SchemaWidgetState,
  isJa: boolean,
): void {
  container.innerHTML = `
    <div class="schema-widget">
      <div class="schema-widget__types">
        ${renderTypeCheckboxes(state.types, isJa)}
      </div>
      <div class="schema-widget__properties">
        ${renderPropertyEditors(state, isJa)}
      </div>
    </div>
  `

  attachEventListeners(container, state, isJa)
}

/**
 * Render checkboxes grouped by category
 */
function renderTypeCheckboxes(selectedTypes: string[], isJa: boolean): string {
  const categories = getTemplatesByCategory()

  return CATEGORY_ORDER.map((category) => {
    const templates = categories[category]
    if (!templates || templates.length === 0) return ''

    const categoryLabel = CATEGORY_LABELS[category]
    const displayLabel = isJa ? categoryLabel.ja : categoryLabel.en

    return `
      <fieldset class="schema-widget__category">
        <legend>${escapeHtml(displayLabel)}</legend>
        <div class="schema-widget__category-types">
          ${templates
            .map((t) => {
              const label = isJa ? t.labelJa : t.label
              const isChecked = selectedTypes.includes(t.type)
              const isDefaultOn = t.defaultOn === true

              return `
              <label class="schema-widget__type${isDefaultOn ? ' schema-widget__type--default' : ''}">
                <input type="checkbox"
                       name="schema_type"
                       value="${escapeHtml(t.type)}"
                       ${isChecked ? 'checked' : ''}>
                <span class="schema-widget__type-label">${escapeHtml(label)}</span>
                ${isDefaultOn ? '<span class="schema-widget__type-badge">Auto</span>' : ''}
              </label>
            `
            })
            .join('')}
        </div>
      </fieldset>
    `
  }).join('')
}

/**
 * Schema types that are fully auto-generated (no JSON editor needed)
 */
const AUTO_GENERATED_TYPES = ['WebSite', 'Organization', 'BreadcrumbList', 'WebPage']

/**
 * Render property editors for selected types
 */
function renderPropertyEditors(
  state: SchemaWidgetState,
  isJa: boolean,
): string {
  if (state.types.length === 0) {
    const emptyMessage = isJa
      ? 'スキーマタイプを選択してプロパティを設定してください'
      : 'Select schema types above to configure properties'

    return `<div class="schema-widget__empty">${escapeHtml(emptyMessage)}</div>`
  }

  return state.types
    .map((type) => {
      const template = SCHEMA_TEMPLATES[type]
      if (!template) return ''

      // Use placeholder if properties is empty or doesn't exist
      const savedProps = state.properties[type]
      const properties = (savedProps && Object.keys(savedProps).length > 0)
        ? savedProps
        : template.placeholder
      const label = isJa ? template.labelJa : template.label
      const helpText = isJa ? template.helpTextJa : template.helpText
      const isAutoGenerated = AUTO_GENERATED_TYPES.includes(type)

      const autoFieldsLabel = isJa ? '自動入力' : 'Auto-filled'
      const exampleLabel = isJa ? '例' : 'Example'
      const requiredLabel = isJa ? '必須項目' : 'Required'
      const optionalLabel = isJa ? 'オプション' : 'Optional'

      const autoFieldsList =
        template.autoFields.length > 0
          ? template.autoFields.map((f) => f.schemaProperty).join(', ')
          : isJa
            ? 'なし'
            : 'None'

      // Auto-generated types don't need JSON editor
      if (isAutoGenerated) {
        const fullyAutoMessage = isJa
          ? '※ このスキーマは完全自動生成されます。カスタマイズは不要です。'
          : '※ This schema is fully auto-generated. No customization needed.'

        return `
        <details class="schema-widget__editor">
          <summary class="schema-widget__editor-header">
            <span class="schema-widget__editor-title">${escapeHtml(label)}</span>
            <a href="${escapeHtml(template.googleDocsUrl)}"
               target="_blank"
               rel="noopener noreferrer"
               class="schema-widget__docs-link"
               title="View documentation">?</a>
          </summary>
          <div class="schema-widget__editor-content">
            <div class="schema-widget__help">${escapeHtml(helpText)}</div>
            <div class="schema-widget__auto-fields">
              <strong>${escapeHtml(autoFieldsLabel)}:</strong> ${escapeHtml(autoFieldsList)}
            </div>
            <div class="schema-widget__fully-auto">${escapeHtml(fullyAutoMessage)}</div>
          </div>
        </details>
      `
      }

      return `
      <details class="schema-widget__editor" open>
        <summary class="schema-widget__editor-header">
          <span class="schema-widget__editor-title">${escapeHtml(label)}</span>
          <a href="${escapeHtml(template.googleDocsUrl)}"
             target="_blank"
             rel="noopener noreferrer"
             class="schema-widget__docs-link"
             title="View documentation">?</a>
        </summary>
        <div class="schema-widget__editor-content">
          <div class="schema-widget__help">${escapeHtml(helpText)}</div>

          <div class="schema-widget__auto-fields">
            <strong>${escapeHtml(autoFieldsLabel)}:</strong> ${escapeHtml(autoFieldsList)}
          </div>

          ${renderFieldInfo(template, requiredLabel, optionalLabel)}

          <div class="schema-widget__json-container">
            <label class="schema-widget__json-label">
              ${isJa ? 'カスタムプロパティ (JSON)' : 'Custom Properties (JSON)'}
            </label>
            <textarea
              class="schema-widget__json"
              data-schema-type="${escapeHtml(type)}"
              rows="6"
              spellcheck="false"
            >${escapeHtml(JSON.stringify(properties, null, 2))}</textarea>
          </div>

          ${
            (() => {
              const example = isJa && Object.keys(template.exampleJa).length > 0 ? template.exampleJa : template.example
              return Object.keys(example).length > 0
                ? `
            <details class="schema-widget__example">
              <summary class="schema-widget__example-header">${escapeHtml(exampleLabel)}</summary>
              <code>${escapeHtml(JSON.stringify(example, null, 2))}</code>
            </details>
          `
                : ''
            })()
          }
        </div>
      </details>
    `
    })
    .join('')
}

/**
 * Render required and optional field information
 */
function renderFieldInfo(
  template: SchemaTemplate,
  requiredLabel: string,
  optionalLabel: string,
): string {
  const parts: string[] = []

  if (template.requiredFields.length > 0) {
    const fields = template.requiredFields
      .map((f) => `${f.name} (${f.type})`)
      .join(', ')
    parts.push(`
      <div class="schema-widget__fields schema-widget__fields--required">
        <strong>${escapeHtml(requiredLabel)}:</strong> ${escapeHtml(fields)}
      </div>
    `)
  }

  if (template.optionalFields.length > 0) {
    const fields = template.optionalFields
      .map((f) => `${f.name} (${f.type})`)
      .join(', ')
    parts.push(`
      <div class="schema-widget__fields schema-widget__fields--optional">
        <strong>${escapeHtml(optionalLabel)}:</strong> ${escapeHtml(fields)}
      </div>
    `)
  }

  return parts.join('')
}

/**
 * Attach event listeners to the widget
 */
function attachEventListeners(
  container: HTMLElement,
  state: SchemaWidgetState,
  isJa: boolean,
): void {
  // Handle checkbox changes
  const checkboxes = container.querySelectorAll<HTMLInputElement>(
    'input[name="schema_type"]',
  )
  for (const checkbox of checkboxes) {
    checkbox.addEventListener('change', () => {
      handleCheckboxChange(container, state, checkbox, isJa)
    })
  }

  // Handle JSON textarea changes (input for real-time sync, blur as fallback)
  const textareas = container.querySelectorAll<HTMLTextAreaElement>(
    '.schema-widget__json',
  )
  for (const textarea of textareas) {
    textarea.addEventListener('input', () => {
      handleJsonChange(state, textarea)
    })
  }
}

/**
 * Handle checkbox state changes
 */
function handleCheckboxChange(
  container: HTMLElement,
  state: SchemaWidgetState,
  checkbox: HTMLInputElement,
  isJa: boolean,
): void {
  const type = checkbox.value

  if (checkbox.checked) {
    if (!state.types.includes(type)) {
      state.types.push(type)
      // Initialize with placeholder if no properties exist
      if (!state.properties[type]) {
        const template = SCHEMA_TEMPLATES[type]
        if (template) {
          state.properties[type] = { ...template.placeholder }
        }
      }
    }
  } else {
    const index = state.types.indexOf(type)
    if (index > -1) {
      state.types.splice(index, 1)
    }
    // Keep properties in case user re-enables
  }

  // Re-render only the properties section
  const propertiesContainer = container.querySelector(
    '.schema-widget__properties',
  )
  if (propertiesContainer) {
    propertiesContainer.innerHTML = renderPropertyEditors(state, isJa)
    // Re-attach JSON textarea listeners
    const textareas = propertiesContainer.querySelectorAll<HTMLTextAreaElement>(
      '.schema-widget__json',
    )
    for (const textarea of textareas) {
      textarea.addEventListener('input', () => {
        handleJsonChange(state, textarea)
      })
    }
  }
}

/**
 * Handle JSON textarea changes
 */
function handleJsonChange(
  state: SchemaWidgetState,
  textarea: HTMLTextAreaElement,
): void {
  const type = textarea.dataset.schemaType
  if (!type) return

  try {
    const parsed = JSON.parse(textarea.value) as Record<string, unknown>
    state.properties[type] = parsed
    textarea.classList.remove('schema-widget__json--error')
  } catch {
    textarea.classList.add('schema-widget__json--error')
  }
}

/**
 * Escape HTML special characters
 */
function escapeHtml(str: string): string {
  const htmlEscapes: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }
  return str.replace(/[&<>"']/g, (char) => htmlEscapes[char])
}
