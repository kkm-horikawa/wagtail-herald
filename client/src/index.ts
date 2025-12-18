/**
 * wagtail-herald Schema Widget
 *
 * A TypeScript-powered widget for managing Schema.org structured data
 * in Wagtail CMS pages.
 */

import './styles.css'
import {
  type SchemaWidgetInstance,
  type SchemaWidgetState,
  initSchemaWidget,
} from './widget'

export const VERSION = '0.2.0'

export { initSchemaWidget }
export type { SchemaWidgetInstance, SchemaWidgetState }

// Re-export schema templates for external use
export {
  SCHEMA_TEMPLATES,
  getTemplate,
  getTemplatesByCategory,
  getAllTypes,
  getDefaultOnTemplates,
  type SchemaTemplate,
  type AutoField,
  type FieldDef,
} from './schema-templates'

/**
 * Public API exposed to window for IIFE builds
 */
export const WagtailHeraldSchema = {
  VERSION,
  initSchemaWidget,
}

// Expose to window for IIFE usage
if (typeof window !== 'undefined') {
  ;(
    window as unknown as { WagtailHeraldSchema: typeof WagtailHeraldSchema }
  ).WagtailHeraldSchema = WagtailHeraldSchema
}

/**
 * Auto-initialize all schema widgets in the document
 * @internal Exported for testing purposes
 */
export function autoInit(): void {
  const elements = document.querySelectorAll<HTMLElement>(
    '[data-schema-widget]',
  )
  for (const el of elements) {
    // Skip if already initialized
    if (el.dataset.schemaWidgetInitialized) continue
    el.dataset.schemaWidgetInitialized = 'true'

    // Read initial state from data attribute if available
    let initialState: SchemaWidgetState | undefined
    const initialStateJson = el.dataset.initialState
    if (initialStateJson) {
      try {
        initialState = JSON.parse(initialStateJson)
      } catch {
        // Invalid JSON, use default state
      }
    }

    const widget = initSchemaWidget(el, initialState)

    // Find the associated hidden input and set up sync
    // The hidden input should be a sibling with matching ID (container ID minus '-container')
    const containerId = el.id
    if (containerId?.endsWith('-container')) {
      const hiddenInputId = containerId.replace(/-container$/, '')
      const hiddenInput = document.getElementById(
        hiddenInputId,
      ) as HTMLInputElement | null
      if (hiddenInput) {
        // Sync initial state to hidden input
        hiddenInput.value = JSON.stringify(widget.getState())

        // Set up sync on changes
        el.addEventListener('change', () => {
          hiddenInput.value = JSON.stringify(widget.getState())
        })

        el.addEventListener('input', (e) => {
          const target = e.target as HTMLElement
          if (target.tagName === 'TEXTAREA') {
            hiddenInput.value = JSON.stringify(widget.getState())
          }
        })

        // Sync before form submission
        const form = hiddenInput.closest('form')
        if (form) {
          form.addEventListener('submit', () => {
            hiddenInput.value = JSON.stringify(widget.getState())
          })
        }
      }
    }
  }
}

// Auto-init for non-Telepath usage (when DOM is ready)
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInit)
  } else {
    autoInit()
  }
}

// Import telepath adapter to ensure it's registered
import './telepath'
