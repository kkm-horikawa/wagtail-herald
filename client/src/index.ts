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

// Auto-init for non-Telepath usage (when DOM is ready)
if (typeof document !== 'undefined') {
  const init = () => {
    const elements = document.querySelectorAll<HTMLElement>(
      '[data-schema-widget]',
    )
    for (const el of elements) {
      // Skip if already initialized
      if (el.dataset.schemaWidgetInitialized) continue
      el.dataset.schemaWidgetInitialized = 'true'
      initSchemaWidget(el)
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init)
  } else {
    init()
  }
}
