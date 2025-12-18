import { describe, expect, it } from 'vitest'
import {
  SCHEMA_TEMPLATES,
  getAllTypes,
  getDefaultOnTemplates,
  getTemplate,
  getTemplatesByCategory,
} from './schema-templates'

describe('SCHEMA_TEMPLATES', () => {
  it('should contain 17 schema types', () => {
    const types = Object.keys(SCHEMA_TEMPLATES)
    expect(types).toHaveLength(17)
  })

  it('should have all required properties for each template', () => {
    for (const [type, template] of Object.entries(SCHEMA_TEMPLATES)) {
      expect(template.type).toBe(type)
      expect(template.label).toBeTruthy()
      expect(template.labelJa).toBeTruthy()
      expect(template.category).toBeTruthy()
      expect(template.helpText).toBeTruthy()
      expect(template.helpTextJa).toBeTruthy()
      expect(Array.isArray(template.autoFields)).toBe(true)
      expect(Array.isArray(template.requiredFields)).toBe(true)
      expect(Array.isArray(template.optionalFields)).toBe(true)
      expect(typeof template.placeholder).toBe('object')
      expect(typeof template.example).toBe('object')
      expect(template.googleDocsUrl).toBeTruthy()
    }
  })

  it('should have valid categories', () => {
    const validCategories = [
      'site-wide',
      'content',
      'business',
      'interactive',
      'events',
      'people',
      'specialized',
    ]

    for (const template of Object.values(SCHEMA_TEMPLATES)) {
      expect(validCategories).toContain(template.category)
    }
  })
})

describe('getTemplate', () => {
  it('should return template for valid type', () => {
    const template = getTemplate('Article')
    expect(template).toBeDefined()
    expect(template?.type).toBe('Article')
    expect(template?.category).toBe('content')
  })

  it('should return undefined for invalid type', () => {
    const template = getTemplate('InvalidType')
    expect(template).toBeUndefined()
  })
})

describe('getTemplatesByCategory', () => {
  it('should group templates by category', () => {
    const grouped = getTemplatesByCategory()

    expect(grouped['site-wide']).toBeDefined()
    expect(grouped.content).toBeDefined()
    expect(grouped.business).toBeDefined()
    expect(grouped.interactive).toBeDefined()
    expect(grouped.events).toBeDefined()
    expect(grouped.people).toBeDefined()
    expect(grouped.specialized).toBeDefined()
  })

  it('should have correct templates in each category', () => {
    const grouped = getTemplatesByCategory()

    // site-wide: WebSite, Organization, BreadcrumbList
    expect(grouped['site-wide']).toHaveLength(3)
    expect(grouped['site-wide'].map((t) => t.type)).toContain('WebSite')
    expect(grouped['site-wide'].map((t) => t.type)).toContain('Organization')
    expect(grouped['site-wide'].map((t) => t.type)).toContain('BreadcrumbList')

    // content: WebPage, Article, NewsArticle, BlogPosting
    expect(grouped.content).toHaveLength(4)

    // business: Product, LocalBusiness, Service
    expect(grouped.business).toHaveLength(3)

    // interactive: FAQPage, HowTo
    expect(grouped.interactive).toHaveLength(2)

    // events: Event
    expect(grouped.events).toHaveLength(1)

    // people: Person
    expect(grouped.people).toHaveLength(1)

    // specialized: Recipe, Course, JobPosting
    expect(grouped.specialized).toHaveLength(3)
  })
})

describe('getAllTypes', () => {
  it('should return all type names', () => {
    const types = getAllTypes()
    expect(types).toHaveLength(17)
    expect(types).toContain('Article')
    expect(types).toContain('Product')
    expect(types).toContain('FAQPage')
    expect(types).toContain('Event')
    expect(types).toContain('Person')
    expect(types).toContain('Recipe')
  })
})

describe('getDefaultOnTemplates', () => {
  it('should return only site-wide templates with defaultOn=true', () => {
    const defaultTemplates = getDefaultOnTemplates()

    expect(defaultTemplates).toHaveLength(3)
    expect(defaultTemplates.map((t) => t.type)).toContain('WebSite')
    expect(defaultTemplates.map((t) => t.type)).toContain('Organization')
    expect(defaultTemplates.map((t) => t.type)).toContain('BreadcrumbList')

    for (const template of defaultTemplates) {
      expect(template.defaultOn).toBe(true)
      expect(template.category).toBe('site-wide')
    }
  })
})

describe('AutoFields', () => {
  it('should have valid autoFields structure', () => {
    const article = getTemplate('Article')
    expect(article?.autoFields.length).toBeGreaterThan(0)

    for (const field of article?.autoFields ?? []) {
      expect(field.schemaProperty).toBeTruthy()
      expect(field.source).toBeTruthy()
      expect(field.description).toBeTruthy()
    }
  })
})

describe('FieldDefs', () => {
  it('should have valid requiredFields for FAQPage', () => {
    const faqPage = getTemplate('FAQPage')
    expect(faqPage?.requiredFields).toHaveLength(1)
    expect(faqPage?.requiredFields[0].name).toBe('mainEntity')
    expect(faqPage?.requiredFields[0].type).toBe('array')
  })

  it('should have valid optionalFields for Product', () => {
    const product = getTemplate('Product')
    expect(product?.optionalFields.length).toBeGreaterThan(0)

    const offerField = product?.optionalFields.find((f) => f.name === 'offers')
    expect(offerField).toBeDefined()
    expect(offerField?.type).toBe('object')
  })
})
