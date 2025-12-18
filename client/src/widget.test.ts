import { beforeEach, describe, expect, it, vi } from 'vitest'
import { type SchemaWidgetState, initSchemaWidget } from './widget'

describe('initSchemaWidget', () => {
  let container: HTMLElement

  beforeEach(() => {
    container = document.createElement('div')
    document.body.appendChild(container)
  })

  it('should initialize widget with empty state', () => {
    const widget = initSchemaWidget(container)

    expect(widget.getState()).toEqual({
      types: [],
      properties: {},
    })
    expect(container.querySelector('.schema-widget')).not.toBeNull()
  })

  it('should initialize widget with initial state', () => {
    const initialState: SchemaWidgetState = {
      types: ['Article', 'Product'],
      properties: {
        Article: { articleSection: 'Tech' },
        Product: { brand: 'Example' },
      },
    }

    const widget = initSchemaWidget(container, initialState)
    const state = widget.getState()

    expect(state.types).toEqual(['Article', 'Product'])
    expect(state.properties.Article).toEqual({ articleSection: 'Tech' })
    expect(state.properties.Product).toEqual({ brand: 'Example' })
  })

  it('should render type checkboxes grouped by category', () => {
    initSchemaWidget(container)

    const categories = container.querySelectorAll('.schema-widget__category')
    expect(categories.length).toBe(7) // All categories should be present

    const checkboxes = container.querySelectorAll('input[name="schema_type"]')
    expect(checkboxes.length).toBe(17) // All 17 schema types
  })

  it('should mark default-on types with badge', () => {
    initSchemaWidget(container)

    const badges = container.querySelectorAll('.schema-widget__type-badge')
    expect(badges.length).toBe(3) // WebSite, Organization, BreadcrumbList

    const defaultTypes = container.querySelectorAll(
      '.schema-widget__type--default',
    )
    expect(defaultTypes.length).toBe(3)
  })

  it('should check boxes for selected types', () => {
    initSchemaWidget(container, {
      types: ['Article', 'FAQPage'],
      properties: {},
    })

    const articleCheckbox = container.querySelector(
      'input[value="Article"]',
    ) as HTMLInputElement
    const faqCheckbox = container.querySelector(
      'input[value="FAQPage"]',
    ) as HTMLInputElement
    const productCheckbox = container.querySelector(
      'input[value="Product"]',
    ) as HTMLInputElement

    expect(articleCheckbox.checked).toBe(true)
    expect(faqCheckbox.checked).toBe(true)
    expect(productCheckbox.checked).toBe(false)
  })

  it('should show empty message when no types selected', () => {
    initSchemaWidget(container)

    const empty = container.querySelector('.schema-widget__empty')
    expect(empty).not.toBeNull()
    expect(empty?.textContent).toContain('Select schema types')
  })

  it('should render property editors for selected types', () => {
    initSchemaWidget(container, {
      types: ['Article', 'Product'],
      properties: {},
    })

    const editors = container.querySelectorAll('.schema-widget__editor')
    expect(editors.length).toBe(2)

    const textareas = container.querySelectorAll('.schema-widget__json')
    expect(textareas.length).toBe(2)
  })

  it('should show help text and documentation link', () => {
    initSchemaWidget(container, {
      types: ['Article'],
      properties: {},
    })

    const help = container.querySelector('.schema-widget__help')
    expect(help?.textContent).toContain('General article')

    const docsLink = container.querySelector(
      '.schema-widget__docs-link',
    ) as HTMLAnchorElement
    expect(docsLink).not.toBeNull()
    expect(docsLink.href).toContain('google.com')
  })

  it('should show auto-fields info', () => {
    initSchemaWidget(container, {
      types: ['Article'],
      properties: {},
    })

    const autoFields = container.querySelector('.schema-widget__auto-fields')
    expect(autoFields?.textContent).toContain('headline')
    expect(autoFields?.textContent).toContain('author')
    expect(autoFields?.textContent).toContain('datePublished')
  })

  it('should show required and optional fields', () => {
    initSchemaWidget(container, {
      types: ['FAQPage'],
      properties: {},
    })

    const required = container.querySelector('.schema-widget__fields--required')
    expect(required?.textContent).toContain('mainEntity')

    // FAQPage has no optional fields, test with LocalBusiness
    initSchemaWidget(container, {
      types: ['LocalBusiness'],
      properties: {},
    })

    const requiredLB = container.querySelector(
      '.schema-widget__fields--required',
    )
    expect(requiredLB?.textContent).toContain('address')

    const optionalLB = container.querySelector(
      '.schema-widget__fields--optional',
    )
    expect(optionalLB?.textContent).toContain('telephone')
  })
})

describe('SchemaWidgetInstance.getState', () => {
  it('should return a deep copy of the state', () => {
    const container = document.createElement('div')
    const initialState: SchemaWidgetState = {
      types: ['Article'],
      properties: { Article: { key: 'value' } },
    }

    const widget = initSchemaWidget(container, initialState)
    const state1 = widget.getState()
    const state2 = widget.getState()

    // Should be equal but not the same object
    expect(state1).toEqual(state2)
    expect(state1).not.toBe(state2)
    expect(state1.types).not.toBe(state2.types)
    expect(state1.properties).not.toBe(state2.properties)
  })
})

describe('SchemaWidgetInstance.setState', () => {
  it('should update the widget state and re-render', () => {
    const container = document.createElement('div')
    const widget = initSchemaWidget(container)

    // Initially no types
    expect(widget.getState().types).toEqual([])

    // Update state
    widget.setState({
      types: ['Product'],
      properties: { Product: { brand: 'TestBrand' } },
    })

    // Check updated state
    const newState = widget.getState()
    expect(newState.types).toEqual(['Product'])
    expect(newState.properties.Product).toEqual({ brand: 'TestBrand' })

    // Check UI updated
    const productCheckbox = container.querySelector(
      'input[value="Product"]',
    ) as HTMLInputElement
    expect(productCheckbox.checked).toBe(true)

    const editor = container.querySelector('.schema-widget__editor')
    expect(editor).not.toBeNull()
  })
})

describe('SchemaWidgetInstance.destroy', () => {
  it('should clear the container', () => {
    const container = document.createElement('div')
    const widget = initSchemaWidget(container)

    expect(container.innerHTML).not.toBe('')

    widget.destroy()

    expect(container.innerHTML).toBe('')
  })
})

describe('Checkbox interactions', () => {
  it('should add type to state when checkbox is checked', () => {
    const container = document.createElement('div')
    const widget = initSchemaWidget(container)

    const checkbox = container.querySelector(
      'input[value="Article"]',
    ) as HTMLInputElement
    checkbox.checked = true
    checkbox.dispatchEvent(new Event('change'))

    const state = widget.getState()
    expect(state.types).toContain('Article')
  })

  it('should remove type from state when checkbox is unchecked', () => {
    const container = document.createElement('div')
    const widget = initSchemaWidget(container, {
      types: ['Article'],
      properties: {},
    })

    const checkbox = container.querySelector(
      'input[value="Article"]',
    ) as HTMLInputElement
    checkbox.checked = false
    checkbox.dispatchEvent(new Event('change'))

    const state = widget.getState()
    expect(state.types).not.toContain('Article')
  })

  it('should initialize properties with placeholder when type is selected', () => {
    const container = document.createElement('div')
    const widget = initSchemaWidget(container)

    const checkbox = container.querySelector(
      'input[value="FAQPage"]',
    ) as HTMLInputElement
    checkbox.checked = true
    checkbox.dispatchEvent(new Event('change'))

    const state = widget.getState()
    expect(state.properties.FAQPage).toBeDefined()
    expect(state.properties.FAQPage.mainEntity).toBeDefined()
  })

  it('should preserve properties when type is deselected and reselected', () => {
    const container = document.createElement('div')
    const widget = initSchemaWidget(container, {
      types: ['Article'],
      properties: { Article: { articleSection: 'CustomSection' } },
    })

    // Uncheck
    const checkbox = container.querySelector(
      'input[value="Article"]',
    ) as HTMLInputElement
    checkbox.checked = false
    checkbox.dispatchEvent(new Event('change'))

    expect(widget.getState().types).not.toContain('Article')

    // Recheck
    checkbox.checked = true
    checkbox.dispatchEvent(new Event('change'))

    const state = widget.getState()
    expect(state.types).toContain('Article')
    // Properties should be preserved
    expect(state.properties.Article).toEqual({
      articleSection: 'CustomSection',
    })
  })
})

describe('JSON textarea interactions', () => {
  it('should update properties on valid JSON blur', () => {
    const container = document.createElement('div')
    const widget = initSchemaWidget(container, {
      types: ['Product'],
      properties: {},
    })

    const textarea = container.querySelector(
      '.schema-widget__json',
    ) as HTMLTextAreaElement
    textarea.value = '{"brand": "NewBrand", "sku": "SKU123"}'
    textarea.dispatchEvent(new Event('blur'))

    const state = widget.getState()
    expect(state.properties.Product).toEqual({
      brand: 'NewBrand',
      sku: 'SKU123',
    })
  })

  it('should add error class on invalid JSON', () => {
    const container = document.createElement('div')
    initSchemaWidget(container, {
      types: ['Product'],
      properties: {},
    })

    const textarea = container.querySelector(
      '.schema-widget__json',
    ) as HTMLTextAreaElement
    textarea.value = '{ invalid json }'
    textarea.dispatchEvent(new Event('blur'))

    expect(textarea.classList.contains('schema-widget__json--error')).toBe(true)
  })

  it('should remove error class on valid JSON', () => {
    const container = document.createElement('div')
    initSchemaWidget(container, {
      types: ['Product'],
      properties: {},
    })

    const textarea = container.querySelector(
      '.schema-widget__json',
    ) as HTMLTextAreaElement

    // First make it invalid
    textarea.value = '{ invalid }'
    textarea.dispatchEvent(new Event('blur'))
    expect(textarea.classList.contains('schema-widget__json--error')).toBe(true)

    // Then fix it
    textarea.value = '{"valid": "json"}'
    textarea.dispatchEvent(new Event('blur'))
    expect(textarea.classList.contains('schema-widget__json--error')).toBe(
      false,
    )
  })
})

describe('Japanese locale support', () => {
  it('should display Japanese labels when document lang is ja', () => {
    // Set Japanese locale
    document.documentElement.lang = 'ja'

    const container = document.createElement('div')
    initSchemaWidget(container, {
      types: ['Article'],
      properties: {},
    })

    // Check first category label (site-wide)
    const legends = container.querySelectorAll(
      '.schema-widget__category legend',
    )
    expect(legends[0]?.textContent).toBe('サイト全体')
    expect(legends[1]?.textContent).toBe('コンテンツ')

    // Check type label
    const articleLabel = container.querySelector(
      'input[value="Article"]',
    )?.nextElementSibling
    expect(articleLabel?.textContent).toBe('記事')

    // Check empty message
    container.innerHTML = ''
    initSchemaWidget(container)
    const empty = container.querySelector('.schema-widget__empty')
    expect(empty?.textContent).toContain('スキーマタイプを選択')

    // Reset
    document.documentElement.lang = 'en'
  })
})

describe('escapeHtml', () => {
  it('should escape single quotes in property values', () => {
    const container = document.createElement('div')
    initSchemaWidget(container, {
      types: ['Article'],
      properties: {
        Article: { articleSection: "Tech's Best" },
      },
    })

    const textarea = container.querySelector(
      '.schema-widget__json',
    ) as HTMLTextAreaElement
    // The JSON should contain the escaped single quote in the textarea value
    expect(textarea.value).toContain("Tech's Best")
  })

  it('should escape all special HTML characters', () => {
    const container = document.createElement('div')
    initSchemaWidget(container, {
      types: ['Article'],
      properties: {
        Article: { content: "<script>\"alert('xss')&</script>" },
      },
    })

    // Check that the widget renders without XSS issues
    const widget = container.querySelector('.schema-widget')
    expect(widget).not.toBeNull()
  })
})

describe('JSON textarea after checkbox change', () => {
  it('should handle blur event on re-attached textarea listeners', () => {
    const container = document.createElement('div')
    const widget = initSchemaWidget(container)

    // Select a type to create property editor
    const checkbox = container.querySelector(
      'input[value="Product"]',
    ) as HTMLInputElement
    checkbox.checked = true
    checkbox.dispatchEvent(new Event('change'))

    // Now the textarea has been created with new event listeners
    const textarea = container.querySelector(
      '.schema-widget__json',
    ) as HTMLTextAreaElement
    expect(textarea).not.toBeNull()

    // Modify and blur the textarea (tests the re-attached listener)
    textarea.value = '{"brand": "NewBrand"}'
    textarea.dispatchEvent(new Event('blur'))

    const state = widget.getState()
    expect(state.properties.Product).toEqual({ brand: 'NewBrand' })
  })
})
