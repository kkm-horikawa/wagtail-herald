import { beforeEach, describe, expect, it, vi } from 'vitest'
import { VERSION, autoInit, initSchemaWidget } from './index'

describe('wagtail-herald schema widget', () => {
  it('should export VERSION', () => {
    expect(VERSION).toBe('0.2.0')
  })

  it('should export initSchemaWidget function', () => {
    expect(typeof initSchemaWidget).toBe('function')
  })

  it('should export autoInit function', () => {
    expect(typeof autoInit).toBe('function')
  })
})

describe('autoInit', () => {
  beforeEach(() => {
    // Clean up any existing elements
    document.body.innerHTML = ''
  })

  it('should skip already initialized elements', () => {
    // Create element with data-schema-widget attribute that is already initialized
    const el = document.createElement('div')
    el.setAttribute('data-schema-widget', '')
    el.dataset.schemaWidgetInitialized = 'true'
    document.body.appendChild(el)

    // Run autoInit
    autoInit()

    // Element should not have widget content since it was skipped
    expect(el.querySelector('.schema-widget')).toBeNull()
  })

  it('should initialize elements without initialized flag', () => {
    // Create element with data-schema-widget attribute
    const el = document.createElement('div')
    el.setAttribute('data-schema-widget', '')
    document.body.appendChild(el)

    // Run autoInit
    autoInit()

    // Element should have widget content
    expect(el.querySelector('.schema-widget')).not.toBeNull()
    expect(el.dataset.schemaWidgetInitialized).toBe('true')
  })

  it('should initialize multiple elements', () => {
    // Create multiple elements
    const el1 = document.createElement('div')
    el1.setAttribute('data-schema-widget', '')
    document.body.appendChild(el1)

    const el2 = document.createElement('div')
    el2.setAttribute('data-schema-widget', '')
    document.body.appendChild(el2)

    // Run autoInit
    autoInit()

    // Both elements should be initialized
    expect(el1.querySelector('.schema-widget')).not.toBeNull()
    expect(el2.querySelector('.schema-widget')).not.toBeNull()
  })
})

describe('DOMContentLoaded handling', () => {
  it('should register DOMContentLoaded listener when document is loading', async () => {
    // Reset modules to re-import with mocked readyState
    vi.resetModules()

    // Mock document.readyState as 'loading' before importing
    Object.defineProperty(document, 'readyState', {
      value: 'loading',
      configurable: true,
      writable: true,
    })

    const addEventListenerSpy = vi.spyOn(document, 'addEventListener')

    // Dynamically import the module to trigger the auto-init code with mocked readyState
    await import('./index')

    expect(addEventListenerSpy).toHaveBeenCalledWith(
      'DOMContentLoaded',
      expect.any(Function),
    )

    // Restore
    Object.defineProperty(document, 'readyState', {
      value: 'complete',
      configurable: true,
      writable: true,
    })
    addEventListenerSpy.mockRestore()
  })
})
