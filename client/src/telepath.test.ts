import { beforeEach, describe, expect, it, vi } from 'vitest'

// Mock window.telepath before importing telepath module
const mockRegister = vi.fn()

describe('Telepath adapter', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
    mockRegister.mockClear()
  })

  describe('SchemaWidgetDefinition', () => {
    it('should render widget from HTML template', async () => {
      // Import after setting up mocks
      const { SchemaWidgetDefinition } = await import('./telepath')

      const html = `
        <div class="schema-widget-wrapper">
          <input type="hidden" name="__NAME__" id="__ID__" value="">
          <div id="__ID__-container" data-schema-widget></div>
        </div>
      `

      const definition = new SchemaWidgetDefinition(html)

      // Create placeholder
      const placeholder = document.createElement('div')
      document.body.appendChild(placeholder)

      const boundWidget = definition.render(
        placeholder,
        'schema_data',
        'id_schema_data',
        { types: ['Article'], properties: {} },
      )

      expect(boundWidget).toBeDefined()
      expect(boundWidget.idForLabel).toBe('id_schema_data')
    })

    it('should parse string initial state', async () => {
      const { SchemaWidgetDefinition } = await import('./telepath')

      const html = `
        <div class="schema-widget-wrapper">
          <input type="hidden" name="__NAME__" id="__ID__" value="">
          <div id="__ID__-container" data-schema-widget></div>
        </div>
      `

      const definition = new SchemaWidgetDefinition(html)
      const placeholder = document.createElement('div')
      document.body.appendChild(placeholder)

      const boundWidget = definition.render(
        placeholder,
        'schema_data',
        'id_schema_data',
        '{"types":["Product"],"properties":{}}',
      )

      const state = boundWidget.getState()
      expect(state.types).toContain('Product')
    })

    it('should handle invalid JSON gracefully', async () => {
      const { SchemaWidgetDefinition } = await import('./telepath')

      const html = `
        <div class="schema-widget-wrapper">
          <input type="hidden" name="__NAME__" id="__ID__" value="">
          <div id="__ID__-container" data-schema-widget></div>
        </div>
      `

      const definition = new SchemaWidgetDefinition(html)
      const placeholder = document.createElement('div')
      document.body.appendChild(placeholder)

      const boundWidget = definition.render(
        placeholder,
        'schema_data',
        'id_schema_data',
        '{ invalid json }',
      )

      const state = boundWidget.getState()
      expect(state.types).toEqual([])
      expect(state.properties).toEqual({})
    })

    it('should throw error when elements not found', async () => {
      const { SchemaWidgetDefinition } = await import('./telepath')

      // HTML without proper ID structure
      const html = '<div>Invalid HTML</div>'

      const definition = new SchemaWidgetDefinition(html)
      const placeholder = document.createElement('div')
      document.body.appendChild(placeholder)

      expect(() => {
        definition.render(placeholder, 'schema_data', 'id_schema_data', {
          types: [],
          properties: {},
        })
      }).toThrow('WagtailHerald: Elements not found')
    })
  })

  describe('BoundSchemaWidget', () => {
    it('should sync state to hidden input on checkbox change', async () => {
      const { SchemaWidgetDefinition } = await import('./telepath')

      const html = `
        <div class="schema-widget-wrapper">
          <input type="hidden" name="__NAME__" id="__ID__" value="">
          <div id="__ID__-container" data-schema-widget></div>
        </div>
      `

      const definition = new SchemaWidgetDefinition(html)
      const placeholder = document.createElement('div')
      document.body.appendChild(placeholder)

      definition.render(
        placeholder,
        'schema_data',
        'id_schema_data',
        { types: [], properties: {} },
      )

      // Find and check a checkbox
      const container = document.getElementById('id_schema_data-container')
      const checkbox = container?.querySelector(
        'input[value="Article"]',
      ) as HTMLInputElement
      expect(checkbox).not.toBeNull()

      checkbox.checked = true
      checkbox.dispatchEvent(new Event('change', { bubbles: true }))

      // Hidden input should be updated
      const hiddenInput = document.getElementById(
        'id_schema_data',
      ) as HTMLInputElement
      const value = JSON.parse(hiddenInput.value)
      expect(value.types).toContain('Article')
    })

    it('should return current state via getState', async () => {
      const { SchemaWidgetDefinition } = await import('./telepath')

      const html = `
        <div class="schema-widget-wrapper">
          <input type="hidden" name="__NAME__" id="__ID__" value="">
          <div id="__ID__-container" data-schema-widget></div>
        </div>
      `

      const definition = new SchemaWidgetDefinition(html)
      const placeholder = document.createElement('div')
      document.body.appendChild(placeholder)

      const boundWidget = definition.render(
        placeholder,
        'schema_data',
        'id_schema_data',
        { types: ['FAQPage'], properties: { FAQPage: { mainEntity: [] } } },
      )

      const state = boundWidget.getState()
      expect(state.types).toEqual(['FAQPage'])
      expect(state.properties.FAQPage).toBeDefined()
    })

    it('should update widget via setState', async () => {
      const { SchemaWidgetDefinition } = await import('./telepath')

      const html = `
        <div class="schema-widget-wrapper">
          <input type="hidden" name="__NAME__" id="__ID__" value="">
          <div id="__ID__-container" data-schema-widget></div>
        </div>
      `

      const definition = new SchemaWidgetDefinition(html)
      const placeholder = document.createElement('div')
      document.body.appendChild(placeholder)

      const boundWidget = definition.render(
        placeholder,
        'schema_data',
        'id_schema_data',
        { types: [], properties: {} },
      )

      boundWidget.setState({
        types: ['Event'],
        properties: { Event: { startDate: '2025-01-01' } },
      })

      const state = boundWidget.getState()
      expect(state.types).toEqual(['Event'])

      // Hidden input should also be updated
      const hiddenInput = document.getElementById(
        'id_schema_data',
      ) as HTMLInputElement
      expect(hiddenInput.value).toContain('Event')
    })

    it('should focus first input via focus()', async () => {
      const { SchemaWidgetDefinition } = await import('./telepath')

      const html = `
        <div class="schema-widget-wrapper">
          <input type="hidden" name="__NAME__" id="__ID__" value="">
          <div id="__ID__-container" data-schema-widget></div>
        </div>
      `

      const definition = new SchemaWidgetDefinition(html)
      const placeholder = document.createElement('div')
      document.body.appendChild(placeholder)

      const boundWidget = definition.render(
        placeholder,
        'schema_data',
        'id_schema_data',
        { types: [], properties: {} },
      )

      // Focus should not throw
      expect(() => boundWidget.focus()).not.toThrow()
    })

    it('should return hidden input value via getValue()', async () => {
      const { SchemaWidgetDefinition } = await import('./telepath')

      const html = `
        <div class="schema-widget-wrapper">
          <input type="hidden" name="__NAME__" id="__ID__" value="">
          <div id="__ID__-container" data-schema-widget></div>
        </div>
      `

      const definition = new SchemaWidgetDefinition(html)
      const placeholder = document.createElement('div')
      document.body.appendChild(placeholder)

      const boundWidget = definition.render(
        placeholder,
        'schema_data',
        'id_schema_data',
        { types: ['Article'], properties: {} },
      )

      const value = boundWidget.getValue()
      expect(value).toContain('Article')
    })
  })
})

describe('Telepath registration', () => {
  it('should register with window.telepath when available', async () => {
    // Set up window.telepath mock
    ;(
      window as unknown as { telepath: { register: typeof mockRegister } }
    ).telepath = {
      register: mockRegister,
    }

    // Reset modules to trigger registration
    vi.resetModules()

    // Import module
    await import('./telepath')

    expect(mockRegister).toHaveBeenCalledWith(
      'wagtail_herald.widgets.SchemaWidget',
      expect.any(Function),
    )

    // Cleanup
    ;(window as unknown as { telepath?: unknown }).telepath = undefined
  })
})
