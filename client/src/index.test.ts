import { describe, expect, it } from 'vitest'
import { VERSION, initSchemaWidget } from './index'

describe('wagtail-herald schema widget', () => {
  it('should export VERSION', () => {
    expect(VERSION).toBe('0.2.0')
  })

  it('should export initSchemaWidget function', () => {
    expect(typeof initSchemaWidget).toBe('function')
  })
})
