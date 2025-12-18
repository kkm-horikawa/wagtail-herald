/**
 * Wagtail Telepath adapter for SchemaWidget
 *
 * This module provides StreamField integration for the schema widget,
 * allowing widgets to be dynamically created when blocks are added.
 */

import {
  type SchemaWidgetInstance,
  type SchemaWidgetState,
  initSchemaWidget,
} from './widget'

/**
 * Bound widget instance returned by render()
 * Implements Wagtail's BoundWidget interface
 */
class BoundSchemaWidget {
  private container: HTMLElement
  private hiddenInput: HTMLInputElement
  private widget: SchemaWidgetInstance | null = null

  constructor(
    container: HTMLElement,
    hiddenInput: HTMLInputElement,
    initialState: SchemaWidgetState,
  ) {
    this.container = container
    this.hiddenInput = hiddenInput

    try {
      // Mark container as initialized to prevent autoInit from resetting it
      container.dataset.schemaWidgetInitialized = 'true'

      this.widget = initSchemaWidget(container, initialState)
      this.setupSync()
      this.syncToHiddenInput()
    } catch (error) {
      console.error('WagtailHerald: Failed to initialize schema widget', error)
    }
  }

  /**
   * Set up event listeners to sync widget state to hidden input
   */
  private setupSync(): void {
    // Sync on any checkbox change
    this.container.addEventListener('change', (e) => {
      const target = e.target as HTMLElement
      if (target.tagName === 'INPUT') {
        this.syncToHiddenInput()
      }
    })

    // Sync on textarea input for real-time updates
    // Note: widget.ts handles JSON parsing on input, so state is always up-to-date
    this.container.addEventListener('input', (e) => {
      const target = e.target as HTMLElement
      if (target.tagName === 'TEXTAREA') {
        this.syncToHiddenInput()
      }
    })

    // Sync before form submission to ensure latest state is saved
    const form = this.hiddenInput.closest('form')
    if (form) {
      form.addEventListener('submit', () => {
        this.syncToHiddenInput()
      })
    }
  }

  /**
   * Sync widget state to hidden input for form submission
   */
  private syncToHiddenInput(): void {
    const state = this.widget?.getState()
    if (state) {
      this.hiddenInput.value = JSON.stringify(state)
    }
  }

  /**
   * Get the HTML ID for label association
   */
  get idForLabel(): string | null {
    return this.hiddenInput.id || null
  }

  /**
   * Get the current value for form submission
   */
  getValue(): string {
    return this.hiddenInput.value
  }

  /**
   * Get the current state for re-initialization
   */
  getState(): SchemaWidgetState {
    return this.widget?.getState() ?? { types: [], properties: {} }
  }

  /**
   * Set a new state value
   */
  setState(newState: SchemaWidgetState): void {
    this.widget?.setState(newState)
    this.syncToHiddenInput()
  }

  /**
   * Focus the first input in the widget
   */
  focus(): void {
    const firstInput = this.container.querySelector('input')
    if (firstInput) {
      firstInput.focus()
    }
  }
}

/**
 * Widget definition for Wagtail Telepath
 * Creates and manages SchemaWidget instances
 */
class SchemaWidgetDefinition {
  private html: string

  constructor(html: string) {
    this.html = html
  }

  /**
   * Render the widget into the page
   */
  render(
    placeholder: HTMLElement,
    name: string,
    id: string,
    initialState: SchemaWidgetState | string,
  ): BoundSchemaWidget {
    // Replace placeholders in the HTML template
    const renderedHtml = this.html
      .replace(/__NAME__/g, name)
      .replace(/__ID__/g, id)

    // Insert the HTML
    placeholder.outerHTML = renderedHtml

    // Find elements
    const container = document.getElementById(`${id}-container`)
    const hiddenInput = document.getElementById(id) as HTMLInputElement

    if (!container || !hiddenInput) {
      throw new Error(`WagtailHerald: Elements not found for id "${id}"`)
    }

    // Parse initial state if string
    let state: SchemaWidgetState
    if (typeof initialState === 'string') {
      try {
        state = JSON.parse(initialState || '{"types":[],"properties":{}}')
      } catch {
        state = { types: [], properties: {} }
      }
    } else {
      state = initialState ?? { types: [], properties: {} }
    }

    // Return bound widget
    return new BoundSchemaWidget(container, hiddenInput, state)
  }
}

// Register with Wagtail Telepath when available
declare global {
  interface Window {
    telepath?: {
      register: (name: string, cls: unknown) => void
    }
  }
}

if (typeof window !== 'undefined' && window.telepath) {
  window.telepath.register(
    'wagtail_herald.widgets.SchemaWidget',
    SchemaWidgetDefinition,
  )
}

export { SchemaWidgetDefinition, BoundSchemaWidget }
