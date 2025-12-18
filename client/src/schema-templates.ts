export interface SchemaTemplate {
  type: string
  label: string
  labelJa: string
  category:
    | 'site-wide'
    | 'content'
    | 'business'
    | 'interactive'
    | 'events'
    | 'people'
    | 'specialized'
  defaultOn?: boolean
  helpText: string
  helpTextJa: string
  autoFields: AutoField[]
  requiredFields: FieldDef[]
  optionalFields: FieldDef[]
  placeholder: Record<string, unknown>
  example: Record<string, unknown>
  exampleJa: Record<string, unknown>
  googleDocsUrl: string
}

export interface AutoField {
  schemaProperty: string
  source: string
  description: string
}

export interface FieldDef {
  name: string
  type: 'string' | 'number' | 'array' | 'object' | 'datetime'
  description: string
}

export const SCHEMA_TEMPLATES: Record<string, SchemaTemplate> = {
  // ===================
  // Site-wide schemas (default ON)
  // ===================
  WebSite: {
    type: 'WebSite',
    label: 'WebSite',
    labelJa: 'ウェブサイト',
    category: 'site-wide',
    defaultOn: true,
    helpText: 'Site information. Auto-populated from Site settings.',
    helpTextJa: 'サイト情報。サイト設定から自動入力されます。',
    autoFields: [
      {
        schemaProperty: 'name',
        source: 'site.site_name',
        description: 'Site name',
      },
      {
        schemaProperty: 'url',
        source: 'site.root_url',
        description: 'Site URL',
      },
    ],
    requiredFields: [],
    optionalFields: [
      {
        name: 'potentialAction',
        type: 'object',
        description: 'SearchAction for sitelinks search box',
      },
    ],
    placeholder: {
      name: '(自動: サイト名)',
      url: '(自動: サイトURL)',
    },
    example: {
      potentialAction: {
        '@type': 'SearchAction',
        target: 'https://example.com/search?q={search_term_string}',
      },
    },
    exampleJa: {
      potentialAction: {
        '@type': 'SearchAction',
        target: 'https://example.co.jp/search?q={search_term_string}',
      },
    },
    googleDocsUrl: 'https://schema.org/WebSite',
  },

  Organization: {
    type: 'Organization',
    label: 'Organization',
    labelJa: '組織',
    category: 'site-wide',
    defaultOn: true,
    helpText: 'Organization info. Auto-populated from SEO Settings.',
    helpTextJa: '組織情報。SEO設定から自動入力されます。',
    autoFields: [
      {
        schemaProperty: 'name',
        source: 'settings.organization_name',
        description: 'Org name',
      },
      {
        schemaProperty: 'url',
        source: 'site.root_url',
        description: 'Website URL',
      },
      {
        schemaProperty: 'logo',
        source: 'settings.organization_logo',
        description: 'Logo image',
      },
      {
        schemaProperty: 'sameAs',
        source: 'settings.social_profiles',
        description: 'Social links',
      },
    ],
    requiredFields: [],
    optionalFields: [],
    placeholder: {
      name: '(自動: 組織名)',
      url: '(自動: サイトURL)',
      logo: '(自動: ロゴ画像)',
      sameAs: '(自動: SNSリンク)',
    },
    example: {},
    exampleJa: {},
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/organization',
  },

  BreadcrumbList: {
    type: 'BreadcrumbList',
    label: 'BreadcrumbList',
    labelJa: 'パンくずリスト',
    category: 'site-wide',
    defaultOn: true,
    helpText:
      'Breadcrumb navigation. Fully auto-generated from page hierarchy.',
    helpTextJa: 'パンくずナビ。ページ階層から完全自動生成されます。',
    autoFields: [
      {
        schemaProperty: 'itemListElement',
        source: 'page.get_ancestors()',
        description: 'Breadcrumb items',
      },
    ],
    requiredFields: [],
    optionalFields: [],
    placeholder: {
      itemListElement: '(自動: ページ階層から生成)',
    },
    example: {},
    exampleJa: {},
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/breadcrumb',
  },

  // ===================
  // Content schemas
  // ===================
  WebPage: {
    type: 'WebPage',
    label: 'Web Page',
    labelJa: 'ウェブページ',
    category: 'content',
    helpText: 'Generic web page. All properties auto-generated.',
    helpTextJa: '一般的なウェブページ。すべてのプロパティは自動生成されます。',
    autoFields: [
      {
        schemaProperty: 'name',
        source: 'page.title',
        description: 'Page title',
      },
      {
        schemaProperty: 'description',
        source: 'page.search_description',
        description: 'Meta description',
      },
      {
        schemaProperty: 'url',
        source: 'page.full_url',
        description: 'Page URL',
      },
    ],
    requiredFields: [],
    optionalFields: [],
    placeholder: {},
    example: {},
    exampleJa: {},
    googleDocsUrl: 'https://schema.org/WebPage',
  },

  Article: {
    type: 'Article',
    label: 'Article',
    labelJa: '記事',
    category: 'content',
    helpText:
      'General article. Use NewsArticle for news, BlogPosting for blogs.',
    helpTextJa:
      '一般的な記事。ニュースにはNewsArticle、ブログにはBlogPostingを使用。',
    autoFields: [
      {
        schemaProperty: 'headline',
        source: 'page.seo_title || page.title',
        description: 'Article headline',
      },
      {
        schemaProperty: 'author',
        source: 'page.owner',
        description: 'Author (Person)',
      },
      {
        schemaProperty: 'datePublished',
        source: 'page.first_published_at',
        description: 'Publish date',
      },
      {
        schemaProperty: 'dateModified',
        source: 'page.last_published_at',
        description: 'Last modified',
      },
      {
        schemaProperty: 'image',
        source: 'page.og_image',
        description: 'Featured image',
      },
      {
        schemaProperty: 'publisher',
        source: 'settings.organization',
        description: 'Publisher org',
      },
    ],
    requiredFields: [],
    optionalFields: [
      {
        name: 'articleSection',
        type: 'string',
        description: 'Article section/category',
      },
      { name: 'wordCount', type: 'number', description: 'Word count' },
    ],
    placeholder: {
      articleSection: '',
    },
    example: { articleSection: 'Technology' },
    exampleJa: { articleSection: 'テクノロジー' },
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/article',
  },

  NewsArticle: {
    type: 'NewsArticle',
    label: 'News Article',
    labelJa: 'ニュース記事',
    category: 'content',
    helpText: 'News article. Enables Google News features.',
    helpTextJa: 'ニュース記事。Googleニュース機能が有効になります。',
    autoFields: [
      {
        schemaProperty: 'headline',
        source: 'page.seo_title || page.title',
        description: 'Article headline',
      },
      {
        schemaProperty: 'author',
        source: 'page.owner',
        description: 'Author (Person)',
      },
      {
        schemaProperty: 'datePublished',
        source: 'page.first_published_at',
        description: 'Publish date',
      },
      {
        schemaProperty: 'dateModified',
        source: 'page.last_published_at',
        description: 'Last modified',
      },
      {
        schemaProperty: 'image',
        source: 'page.og_image',
        description: 'Featured image',
      },
      {
        schemaProperty: 'publisher',
        source: 'settings.organization',
        description: 'Publisher org',
      },
    ],
    requiredFields: [],
    optionalFields: [
      {
        name: 'dateline',
        type: 'string',
        description: 'News dateline location',
      },
    ],
    placeholder: {
      dateline: '',
    },
    example: { dateline: 'TOKYO' },
    exampleJa: { dateline: '東京' },
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/article',
  },

  BlogPosting: {
    type: 'BlogPosting',
    label: 'Blog Post',
    labelJa: 'ブログ記事',
    category: 'content',
    helpText: 'Blog post. Similar to Article but for blog content.',
    helpTextJa: 'ブログ投稿。Articleと同様ですがブログコンテンツ向け。',
    autoFields: [
      {
        schemaProperty: 'headline',
        source: 'page.seo_title || page.title',
        description: 'Post headline',
      },
      {
        schemaProperty: 'author',
        source: 'page.owner',
        description: 'Author (Person)',
      },
      {
        schemaProperty: 'datePublished',
        source: 'page.first_published_at',
        description: 'Publish date',
      },
      {
        schemaProperty: 'dateModified',
        source: 'page.last_published_at',
        description: 'Last modified',
      },
      {
        schemaProperty: 'image',
        source: 'page.og_image',
        description: 'Featured image',
      },
      {
        schemaProperty: 'publisher',
        source: 'settings.organization',
        description: 'Publisher org',
      },
    ],
    requiredFields: [],
    optionalFields: [
      { name: 'articleSection', type: 'string', description: 'Blog category' },
      {
        name: 'keywords',
        type: 'string',
        description: 'Comma-separated keywords',
      },
    ],
    placeholder: {
      articleSection: '',
      keywords: '',
    },
    example: { articleSection: 'Tech Blog', keywords: 'wagtail, cms, python' },
    exampleJa: {
      articleSection: '技術ブログ',
      keywords: 'Wagtail, CMS, Python, Web開発',
    },
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/article',
  },

  // ===================
  // Business schemas
  // ===================
  Product: {
    type: 'Product',
    label: 'Product',
    labelJa: '商品',
    category: 'business',
    helpText: 'Product with price/availability. Enables rich results.',
    helpTextJa: '価格・在庫情報付き商品ページ。リッチリザルト対応。',
    autoFields: [
      {
        schemaProperty: 'name',
        source: 'page.title',
        description: 'Product name',
      },
      {
        schemaProperty: 'description',
        source: 'page.search_description',
        description: 'Description',
      },
      {
        schemaProperty: 'image',
        source: 'page.og_image',
        description: 'Product image',
      },
    ],
    requiredFields: [],
    optionalFields: [
      { name: 'offers', type: 'object', description: 'Price and availability' },
      { name: 'brand', type: 'string', description: 'Brand name' },
      { name: 'sku', type: 'string', description: 'Product SKU' },
      { name: 'gtin', type: 'string', description: 'Global Trade Item Number' },
    ],
    placeholder: {
      offers: {
        '@type': 'Offer',
        price: '',
        priceCurrency: 'USD',
        availability: 'https://schema.org/InStock',
        url: '',
      },
      brand: '',
      sku: '',
      gtin: '',
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: '',
        reviewCount: '',
      },
      review: [],
    },
    example: {
      offers: {
        '@type': 'Offer',
        price: '29.99',
        priceCurrency: 'USD',
        availability: 'https://schema.org/InStock',
        url: 'https://example.com/products/wireless-earbuds',
      },
      brand: 'TechBrand',
      sku: 'WE-2024-001',
      gtin: '012345678905',
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: '4.5',
        reviewCount: '128',
      },
    },
    exampleJa: {
      offers: {
        '@type': 'Offer',
        price: '3980',
        priceCurrency: 'JPY',
        availability: 'https://schema.org/InStock',
        url: 'https://example.co.jp/products/wireless-earbuds',
      },
      brand: 'サンプルブランド',
      sku: 'WE-2024-001',
      gtin: '4901234567890',
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: '4.3',
        reviewCount: '156',
      },
    },
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/product',
  },

  LocalBusiness: {
    type: 'LocalBusiness',
    label: 'Local Business',
    labelJa: 'ローカルビジネス',
    category: 'business',
    helpText: 'Local business with address and hours. Great for local SEO.',
    helpTextJa: '住所・営業時間付きローカルビジネス。ローカルSEOに効果的。',
    autoFields: [
      {
        schemaProperty: 'name',
        source: 'page.title',
        description: 'Business name',
      },
      {
        schemaProperty: 'description',
        source: 'page.search_description',
        description: 'Description',
      },
      {
        schemaProperty: 'image',
        source: 'page.og_image',
        description: 'Business image',
      },
    ],
    requiredFields: [
      { name: 'address', type: 'object', description: 'PostalAddress object' },
    ],
    optionalFields: [
      { name: 'telephone', type: 'string', description: 'Phone number' },
      {
        name: 'openingHoursSpecification',
        type: 'array',
        description: 'Business hours',
      },
      {
        name: 'priceRange',
        type: 'string',
        description: 'Price range (e.g., $$)',
      },
      { name: 'geo', type: 'object', description: 'GeoCoordinates' },
    ],
    placeholder: {
      address: {
        '@type': 'PostalAddress',
        streetAddress: '',
        addressLocality: '',
        addressRegion: '',
        postalCode: '',
        addressCountry: 'US',
      },
      telephone: '',
      priceRange: '',
      openingHoursSpecification: [],
      geo: {
        '@type': 'GeoCoordinates',
        latitude: '',
        longitude: '',
      },
    },
    example: {
      address: {
        '@type': 'PostalAddress',
        streetAddress: '123 Main Street, Suite 100',
        addressLocality: 'San Francisco',
        addressRegion: 'CA',
        postalCode: '94102',
        addressCountry: 'US',
      },
      telephone: '+1-415-555-1234',
      priceRange: '$$',
      geo: {
        '@type': 'GeoCoordinates',
        latitude: '37.7749',
        longitude: '-122.4194',
      },
      openingHoursSpecification: [
        {
          '@type': 'OpeningHoursSpecification',
          dayOfWeek: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
          opens: '09:00',
          closes: '18:00',
        },
        {
          '@type': 'OpeningHoursSpecification',
          dayOfWeek: ['Saturday'],
          opens: '10:00',
          closes: '15:00',
        },
      ],
    },
    exampleJa: {
      address: {
        '@type': 'PostalAddress',
        streetAddress: '渋谷1-1-1 渋谷ビル3F',
        addressLocality: '渋谷区',
        addressRegion: '東京都',
        postalCode: '150-0002',
        addressCountry: 'JP',
      },
      telephone: '03-1234-5678',
      priceRange: '¥¥',
      geo: {
        '@type': 'GeoCoordinates',
        latitude: '35.6595',
        longitude: '139.7004',
      },
      openingHoursSpecification: [
        {
          '@type': 'OpeningHoursSpecification',
          dayOfWeek: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
          opens: '10:00',
          closes: '19:00',
        },
        {
          '@type': 'OpeningHoursSpecification',
          dayOfWeek: ['Saturday', 'Sunday'],
          opens: '11:00',
          closes: '18:00',
        },
      ],
    },
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/local-business',
  },

  Service: {
    type: 'Service',
    label: 'Service',
    labelJa: 'サービス',
    category: 'business',
    helpText: 'Service offering. Describe what services you provide.',
    helpTextJa: 'サービス提供。提供サービスの説明に使用。',
    autoFields: [
      {
        schemaProperty: 'name',
        source: 'page.title',
        description: 'Service name',
      },
      {
        schemaProperty: 'description',
        source: 'page.search_description',
        description: 'Description',
      },
      {
        schemaProperty: 'provider',
        source: 'settings.organization',
        description: 'Provider',
      },
    ],
    requiredFields: [],
    optionalFields: [
      { name: 'serviceType', type: 'string', description: 'Type of service' },
      { name: 'areaServed', type: 'string', description: 'Service area' },
      { name: 'offers', type: 'object', description: 'Service pricing' },
    ],
    placeholder: {
      serviceType: '',
      areaServed: '',
      offers: {
        '@type': 'Offer',
        price: '',
        priceCurrency: 'USD',
      },
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: '',
        reviewCount: '',
      },
      hoursAvailable: '',
      brand: '',
    },
    example: {
      serviceType: 'Web Development',
      areaServed: 'San Francisco Bay Area',
      offers: {
        '@type': 'Offer',
        price: '5000',
        priceCurrency: 'USD',
      },
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: '4.8',
        reviewCount: '156',
      },
    },
    exampleJa: {
      serviceType: 'Webサイト制作',
      areaServed: '東京都、神奈川県、埼玉県、千葉県',
      offers: {
        '@type': 'Offer',
        price: '300000',
        priceCurrency: 'JPY',
      },
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: '4.7',
        reviewCount: '89',
      },
    },
    googleDocsUrl: 'https://schema.org/Service',
  },

  // ===================
  // Interactive schemas
  // ===================
  FAQPage: {
    type: 'FAQPage',
    label: 'FAQ Page',
    labelJa: 'FAQページ',
    category: 'interactive',
    helpText: 'FAQ with expandable Q&A. High visibility in search.',
    helpTextJa: 'Q&A形式のFAQページ。検索結果で高い視認性。',
    autoFields: [],
    requiredFields: [
      {
        name: 'mainEntity',
        type: 'array',
        description: 'Array of Question objects',
      },
    ],
    optionalFields: [],
    placeholder: {
      mainEntity: [
        {
          '@type': 'Question',
          name: '',
          acceptedAnswer: { '@type': 'Answer', text: '' },
        },
        {
          '@type': 'Question',
          name: '',
          acceptedAnswer: { '@type': 'Answer', text: '' },
        },
      ],
    },
    example: {
      mainEntity: [
        {
          '@type': 'Question',
          name: 'What is wagtail-herald?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'A comprehensive SEO toolkit for Wagtail CMS.',
          },
        },
        {
          '@type': 'Question',
          name: 'How do I install it?',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'Run pip install wagtail-herald and add to INSTALLED_APPS.',
          },
        },
      ],
    },
    exampleJa: {
      mainEntity: [
        {
          '@type': 'Question',
          name: '送料はいくらですか？',
          acceptedAnswer: {
            '@type': 'Answer',
            text: '全国一律550円（税込）です。5,000円以上のご購入で送料無料となります。',
          },
        },
        {
          '@type': 'Question',
          name: '返品・交換はできますか？',
          acceptedAnswer: {
            '@type': 'Answer',
            text: '商品到着後7日以内であれば、未開封・未使用の商品に限り返品・交換を承ります。',
          },
        },
        {
          '@type': 'Question',
          name: '支払い方法は何がありますか？',
          acceptedAnswer: {
            '@type': 'Answer',
            text: 'クレジットカード、銀行振込、代金引換、コンビニ決済がご利用いただけます。',
          },
        },
      ],
    },
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/faqpage',
  },

  HowTo: {
    type: 'HowTo',
    label: 'How-To',
    labelJa: 'ハウツー',
    category: 'interactive',
    helpText:
      'Step-by-step instructions. (Note: Rich results deprecated Sep 2023)',
    helpTextJa: 'ステップバイステップの手順。(※2023年9月リッチリザルト廃止)',
    autoFields: [
      {
        schemaProperty: 'name',
        source: 'page.title',
        description: 'How-to title',
      },
      {
        schemaProperty: 'description',
        source: 'page.search_description',
        description: 'Description',
      },
      {
        schemaProperty: 'image',
        source: 'page.og_image',
        description: 'Main image',
      },
    ],
    requiredFields: [
      { name: 'step', type: 'array', description: 'Array of HowToStep' },
    ],
    optionalFields: [
      {
        name: 'totalTime',
        type: 'string',
        description: 'ISO 8601 duration (e.g., PT30M)',
      },
      { name: 'estimatedCost', type: 'object', description: 'MonetaryAmount' },
      { name: 'supply', type: 'array', description: 'Required supplies' },
      { name: 'tool', type: 'array', description: 'Required tools' },
    ],
    placeholder: {
      step: [
        {
          '@type': 'HowToStep',
          name: '',
          text: '',
        },
        {
          '@type': 'HowToStep',
          name: '',
          text: '',
        },
      ],
      totalTime: '',
      estimatedCost: {
        '@type': 'MonetaryAmount',
        currency: 'USD',
        value: '',
      },
      supply: [],
      tool: [],
    },
    example: {
      step: [
        {
          '@type': 'HowToStep',
          name: 'Install',
          text: 'pip install wagtail-herald',
        },
        {
          '@type': 'HowToStep',
          name: 'Configure',
          text: 'Add to INSTALLED_APPS',
        },
      ],
      totalTime: 'PT10M',
    },
    exampleJa: {
      step: [
        {
          '@type': 'HowToStep',
          name: '材料を準備する',
          text: '必要な材料をすべて計量し、室温に戻しておきます。',
        },
        {
          '@type': 'HowToStep',
          name: '生地を作る',
          text: 'ボウルに粉類を入れ、よく混ぜ合わせます。',
        },
        {
          '@type': 'HowToStep',
          name: '焼き上げる',
          text: '180度に予熱したオーブンで30分焼きます。',
        },
      ],
      totalTime: 'PT45M',
      estimatedCost: {
        '@type': 'MonetaryAmount',
        currency: 'JPY',
        value: '500',
      },
    },
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/how-to',
  },

  // ===================
  // Events schema
  // ===================
  Event: {
    type: 'Event',
    label: 'Event',
    labelJa: 'イベント',
    category: 'events',
    helpText: 'Event with date, location, and tickets. Shows in Google Events.',
    helpTextJa: '日時・場所・チケット情報付きイベント。Googleイベントに表示。',
    autoFields: [
      {
        schemaProperty: 'name',
        source: 'page.title',
        description: 'Event name',
      },
      {
        schemaProperty: 'description',
        source: 'page.search_description',
        description: 'Description',
      },
      {
        schemaProperty: 'image',
        source: 'page.og_image',
        description: 'Event image',
      },
    ],
    requiredFields: [
      {
        name: 'startDate',
        type: 'datetime',
        description: 'Event start date/time',
      },
      {
        name: 'location',
        type: 'object',
        description: 'Place or VirtualLocation',
      },
    ],
    optionalFields: [
      { name: 'endDate', type: 'datetime', description: 'Event end date/time' },
      {
        name: 'eventStatus',
        type: 'string',
        description: 'EventScheduled, EventCancelled, etc.',
      },
      {
        name: 'eventAttendanceMode',
        type: 'string',
        description: 'Online, Offline, Mixed',
      },
      { name: 'offers', type: 'object', description: 'Ticket information' },
      {
        name: 'performer',
        type: 'object',
        description: 'Person or Organization',
      },
      {
        name: 'organizer',
        type: 'object',
        description: 'Person or Organization',
      },
    ],
    placeholder: {
      startDate: '',
      endDate: '',
      location: {
        '@type': 'Place',
        name: '',
        address: {
          '@type': 'PostalAddress',
          streetAddress: '',
          addressLocality: '',
          addressCountry: 'US',
        },
      },
      eventStatus: 'https://schema.org/EventScheduled',
      eventAttendanceMode: 'https://schema.org/OfflineEventAttendanceMode',
      offers: {
        '@type': 'Offer',
        price: '',
        priceCurrency: 'USD',
        availability: 'https://schema.org/InStock',
        url: '',
      },
      performer: {
        '@type': 'Person',
        name: '',
      },
      organizer: {
        '@type': 'Organization',
        name: '',
      },
    },
    example: {
      startDate: '2025-03-15T19:00:00-08:00',
      endDate: '2025-03-15T21:00:00-08:00',
      location: {
        '@type': 'Place',
        name: 'Moscone Center',
        address: {
          '@type': 'PostalAddress',
          streetAddress: '747 Howard St',
          addressLocality: 'San Francisco',
          addressRegion: 'CA',
          postalCode: '94103',
          addressCountry: 'US',
        },
      },
      eventStatus: 'https://schema.org/EventScheduled',
      eventAttendanceMode: 'https://schema.org/OfflineEventAttendanceMode',
    },
    exampleJa: {
      startDate: '2025-04-20T14:00:00+09:00',
      endDate: '2025-04-20T17:00:00+09:00',
      location: {
        '@type': 'Place',
        name: '東京国際フォーラム ホールA',
        address: {
          '@type': 'PostalAddress',
          streetAddress: '丸の内3-5-1',
          addressLocality: '千代田区',
          addressRegion: '東京都',
          postalCode: '100-0005',
          addressCountry: 'JP',
        },
      },
      eventStatus: 'https://schema.org/EventScheduled',
      eventAttendanceMode: 'https://schema.org/OfflineEventAttendanceMode',
      offers: {
        '@type': 'Offer',
        price: '5000',
        priceCurrency: 'JPY',
        availability: 'https://schema.org/InStock',
        url: 'https://example.co.jp/events/spring-concert/tickets',
        validFrom: '2025-02-01T10:00:00+09:00',
      },
      performer: {
        '@type': 'Person',
        name: '山田太郎',
      },
      organizer: {
        '@type': 'Organization',
        name: '株式会社サンプルイベント',
        url: 'https://example.co.jp',
      },
    },
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/event',
  },

  // ===================
  // People schema
  // ===================
  Person: {
    type: 'Person',
    label: 'Person',
    labelJa: '人物',
    category: 'people',
    helpText: 'Person profile. Useful for author pages and team members.',
    helpTextJa: '人物プロフィール。著者ページやチームメンバーに有用。',
    autoFields: [
      {
        schemaProperty: 'name',
        source: 'page.title',
        description: 'Person name',
      },
      {
        schemaProperty: 'description',
        source: 'page.search_description',
        description: 'Bio',
      },
      {
        schemaProperty: 'image',
        source: 'page.og_image',
        description: 'Photo',
      },
    ],
    requiredFields: [],
    optionalFields: [
      { name: 'jobTitle', type: 'string', description: 'Job title' },
      { name: 'worksFor', type: 'object', description: 'Organization' },
      { name: 'email', type: 'string', description: 'Email address' },
      { name: 'sameAs', type: 'array', description: 'Social profile URLs' },
      {
        name: 'alumniOf',
        type: 'object',
        description: 'Educational organization',
      },
    ],
    placeholder: {
      jobTitle: '',
      worksFor: { '@type': 'Organization', name: '' },
      email: '',
      url: '',
      sameAs: [],
      alumniOf: { '@type': 'EducationalOrganization', name: '' },
      knowsAbout: [],
      award: [],
    },
    example: {
      jobTitle: 'Senior Software Engineer',
      worksFor: { '@type': 'Organization', name: 'TechCorp Inc.' },
      url: 'https://example.com/team/jane-smith',
      sameAs: [
        'https://twitter.com/janesmith_dev',
        'https://github.com/janesmith',
        'https://linkedin.com/in/janesmith',
      ],
      alumniOf: {
        '@type': 'EducationalOrganization',
        name: 'Stanford University',
      },
      knowsAbout: ['Python', 'Django', 'Wagtail CMS', 'Cloud Architecture'],
      award: ['Best Developer 2024', 'Google Developer Expert'],
    },
    exampleJa: {
      jobTitle: 'シニアエンジニア',
      worksFor: { '@type': 'Organization', name: '株式会社サンプルテック' },
      url: 'https://example.co.jp/team/tanaka-hanako',
      sameAs: [
        'https://twitter.com/tanaka_dev',
        'https://github.com/tanaka-hanako',
        'https://qiita.com/tanaka_hanako',
      ],
      alumniOf: { '@type': 'EducationalOrganization', name: '東京大学' },
      knowsAbout: ['Python', 'Django', 'Wagtail CMS', 'クラウドアーキテクチャ'],
      award: ['2024年度 社内MVP賞', 'OSS貢献賞'],
    },
    googleDocsUrl: 'https://schema.org/Person',
  },

  // ===================
  // Specialized schemas
  // ===================
  Recipe: {
    type: 'Recipe',
    label: 'Recipe',
    labelJa: 'レシピ',
    category: 'specialized',
    helpText:
      'Recipe with ingredients and steps. Shows rich results with image.',
    helpTextJa: '材料・手順付きレシピ。画像付きリッチリザルトに表示。',
    autoFields: [
      {
        schemaProperty: 'name',
        source: 'page.title',
        description: 'Recipe name',
      },
      {
        schemaProperty: 'description',
        source: 'page.search_description',
        description: 'Description',
      },
      {
        schemaProperty: 'image',
        source: 'page.og_image',
        description: 'Recipe image',
      },
      {
        schemaProperty: 'author',
        source: 'page.owner',
        description: 'Recipe author',
      },
      {
        schemaProperty: 'datePublished',
        source: 'page.first_published_at',
        description: 'Publish date',
      },
    ],
    requiredFields: [
      {
        name: 'recipeIngredient',
        type: 'array',
        description: 'List of ingredients',
      },
      {
        name: 'recipeInstructions',
        type: 'array',
        description: 'Cooking steps',
      },
    ],
    optionalFields: [
      { name: 'prepTime', type: 'string', description: 'ISO 8601 duration' },
      { name: 'cookTime', type: 'string', description: 'ISO 8601 duration' },
      { name: 'totalTime', type: 'string', description: 'ISO 8601 duration' },
      {
        name: 'recipeYield',
        type: 'string',
        description: 'Number of servings',
      },
      {
        name: 'recipeCategory',
        type: 'string',
        description: 'Meal type (e.g., Dinner)',
      },
      {
        name: 'recipeCuisine',
        type: 'string',
        description: 'Cuisine type (e.g., Japanese)',
      },
      {
        name: 'nutrition',
        type: 'object',
        description: 'NutritionInformation',
      },
    ],
    placeholder: {
      recipeIngredient: ['', '', ''],
      recipeInstructions: [
        { '@type': 'HowToStep', text: '' },
        { '@type': 'HowToStep', text: '' },
      ],
      prepTime: '',
      cookTime: '',
      totalTime: '',
      recipeYield: '',
      recipeCategory: '',
      recipeCuisine: '',
      keywords: '',
      nutrition: {
        '@type': 'NutritionInformation',
        calories: '',
      },
      video: {
        '@type': 'VideoObject',
        name: '',
        description: '',
        thumbnailUrl: '',
        contentUrl: '',
        uploadDate: '',
      },
    },
    example: {
      recipeIngredient: ['2 cups flour', '1 cup sugar', '2 eggs'],
      recipeInstructions: [
        { '@type': 'HowToStep', text: 'Mix dry ingredients' },
        { '@type': 'HowToStep', text: 'Add wet ingredients' },
        { '@type': 'HowToStep', text: 'Bake at 350°F for 30 minutes' },
      ],
      prepTime: 'PT15M',
      cookTime: 'PT30M',
      totalTime: 'PT45M',
      recipeYield: '8 servings',
      recipeCategory: 'Dessert',
      recipeCuisine: 'American',
      keywords: 'cake, easy baking, dessert',
      nutrition: {
        '@type': 'NutritionInformation',
        calories: '280 kcal',
      },
      video: {
        '@type': 'VideoObject',
        name: 'How to Make Easy Cake',
        description: 'Step by step video tutorial',
        thumbnailUrl: 'https://example.com/cake-video-thumb.jpg',
        contentUrl: 'https://example.com/cake-video.mp4',
        uploadDate: '2025-01-15T08:00:00+09:00',
      },
    },
    exampleJa: {
      recipeIngredient: [
        '豚バラ肉 300g',
        '大根 1/2本',
        'こんにゃく 1枚',
        '醤油 大さじ3',
        'みりん 大さじ2',
        '砂糖 大さじ1',
        'だし汁 400ml',
      ],
      recipeInstructions: [
        {
          '@type': 'HowToStep',
          text: '豚バラ肉は3cm幅に切り、大根は2cm厚さのいちょう切りにする。',
        },
        { '@type': 'HowToStep', text: 'こんにゃくは手でちぎり、下茹でする。' },
        {
          '@type': 'HowToStep',
          text: '鍋に豚肉を入れて炒め、色が変わったら大根とこんにゃくを加える。',
        },
        {
          '@type': 'HowToStep',
          text: 'だし汁と調味料を加え、落し蓋をして弱火で40分煮込む。',
        },
      ],
      prepTime: 'PT20M',
      cookTime: 'PT40M',
      totalTime: 'PT60M',
      recipeYield: '4人分',
      recipeCategory: '主菜',
      recipeCuisine: '和食',
      keywords: '豚の角煮, 和食, 煮物, 家庭料理',
      nutrition: {
        '@type': 'NutritionInformation',
        calories: '450 kcal',
      },
      video: {
        '@type': 'VideoObject',
        name: '豚の角煮の作り方',
        description: 'プロが教える本格豚の角煮レシピ',
        thumbnailUrl: 'https://example.co.jp/recipes/kakuni-thumb.jpg',
        contentUrl: 'https://example.co.jp/recipes/kakuni-video.mp4',
        uploadDate: '2025-01-15T08:00:00+09:00',
      },
    },
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/recipe',
  },

  Course: {
    type: 'Course',
    label: 'Course',
    labelJa: 'コース',
    category: 'specialized',
    helpText: 'Educational course. Shows in Google course listings.',
    helpTextJa: '教育コース。Googleコース一覧に表示。',
    autoFields: [
      {
        schemaProperty: 'name',
        source: 'page.title',
        description: 'Course name',
      },
      {
        schemaProperty: 'description',
        source: 'page.search_description',
        description: 'Description',
      },
      {
        schemaProperty: 'provider',
        source: 'settings.organization',
        description: 'Provider',
      },
    ],
    requiredFields: [],
    optionalFields: [
      { name: 'courseCode', type: 'string', description: 'Course code/ID' },
      {
        name: 'hasCourseInstance',
        type: 'array',
        description: 'Course instances with dates',
      },
      {
        name: 'educationalLevel',
        type: 'string',
        description: 'Difficulty level',
      },
      { name: 'offers', type: 'object', description: 'Pricing information' },
      {
        name: 'totalHistoricalEnrollment',
        type: 'number',
        description: 'Total enrollments',
      },
    ],
    placeholder: {
      hasCourseInstance: [
        {
          '@type': 'CourseInstance',
          courseMode: '',
          startDate: '',
          endDate: '',
        },
      ],
      offers: {
        '@type': 'Offer',
        price: '',
        priceCurrency: 'USD',
      },
    },
    example: {
      courseCode: 'CS101',
      educationalLevel: 'Beginner',
      hasCourseInstance: [
        {
          '@type': 'CourseInstance',
          courseMode: 'Online',
          startDate: '2025-04-01',
        },
      ],
    },
    exampleJa: {
      courseCode: 'WEB-001',
      educationalLevel: '初級',
      hasCourseInstance: [
        {
          '@type': 'CourseInstance',
          courseMode: 'オンライン',
          startDate: '2025-04-01',
          endDate: '2025-06-30',
        },
      ],
      offers: {
        '@type': 'Offer',
        price: '29800',
        priceCurrency: 'JPY',
      },
      totalHistoricalEnrollment: 1500,
    },
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/course',
  },

  JobPosting: {
    type: 'JobPosting',
    label: 'Job Posting',
    labelJa: '求人情報',
    category: 'specialized',
    helpText: 'Job listing. Shows in Google Jobs search.',
    helpTextJa: '求人情報。Google求人検索に表示。',
    autoFields: [
      {
        schemaProperty: 'title',
        source: 'page.title',
        description: 'Job title',
      },
      {
        schemaProperty: 'description',
        source: 'page.search_description',
        description: 'Job description',
      },
      {
        schemaProperty: 'datePosted',
        source: 'page.first_published_at',
        description: 'Post date',
      },
      {
        schemaProperty: 'hiringOrganization',
        source: 'settings.organization',
        description: 'Employer',
      },
    ],
    requiredFields: [
      {
        name: 'jobLocation',
        type: 'object',
        description: 'Place with address',
      },
    ],
    optionalFields: [
      {
        name: 'validThrough',
        type: 'datetime',
        description: 'Application deadline',
      },
      {
        name: 'employmentType',
        type: 'string',
        description: 'FULL_TIME, PART_TIME, etc.',
      },
      { name: 'baseSalary', type: 'object', description: 'MonetaryAmount' },
      {
        name: 'jobLocationType',
        type: 'string',
        description: 'TELECOMMUTE for remote',
      },
      {
        name: 'applicantLocationRequirements',
        type: 'object',
        description: 'Location requirements',
      },
    ],
    placeholder: {
      jobLocation: {
        '@type': 'Place',
        address: {
          '@type': 'PostalAddress',
          streetAddress: '',
          addressLocality: '',
          addressRegion: '',
          postalCode: '',
          addressCountry: 'US',
        },
      },
      employmentType: '',
      validThrough: '',
      baseSalary: {
        '@type': 'MonetaryAmount',
        currency: 'USD',
        value: {
          '@type': 'QuantitativeValue',
          minValue: '',
          maxValue: '',
          unitText: 'YEAR',
        },
      },
      jobLocationType: '',
      directApply: true,
    },
    example: {
      jobLocation: {
        '@type': 'Place',
        address: {
          '@type': 'PostalAddress',
          streetAddress: '100 Main Street',
          addressLocality: 'San Francisco',
          addressRegion: 'CA',
          postalCode: '94102',
          addressCountry: 'US',
        },
      },
      employmentType: 'FULL_TIME',
      baseSalary: {
        '@type': 'MonetaryAmount',
        currency: 'USD',
        value: {
          '@type': 'QuantitativeValue',
          minValue: 120000,
          maxValue: 180000,
          unitText: 'YEAR',
        },
      },
      validThrough: '2025-06-30T23:59:59-08:00',
    },
    exampleJa: {
      jobLocation: {
        '@type': 'Place',
        address: {
          '@type': 'PostalAddress',
          streetAddress: '渋谷2-21-1 渋谷ヒカリエ',
          addressLocality: '渋谷区',
          addressRegion: '東京都',
          postalCode: '150-8510',
          addressCountry: 'JP',
        },
      },
      employmentType: 'FULL_TIME',
      baseSalary: {
        '@type': 'MonetaryAmount',
        currency: 'JPY',
        value: {
          '@type': 'QuantitativeValue',
          minValue: 4500000,
          maxValue: 7000000,
          unitText: 'YEAR',
        },
      },
      validThrough: '2025-03-31T23:59:59+09:00',
      jobLocationType: 'TELECOMMUTE',
      applicantLocationRequirements: {
        '@type': 'Country',
        name: 'Japan',
      },
    },
    googleDocsUrl:
      'https://developers.google.com/search/docs/appearance/structured-data/job-posting',
  },
}

/**
 * Get templates grouped by category
 */
export function getTemplatesByCategory(): Record<string, SchemaTemplate[]> {
  const categories: Record<string, SchemaTemplate[]> = {}

  for (const template of Object.values(SCHEMA_TEMPLATES)) {
    if (!categories[template.category]) {
      categories[template.category] = []
    }
    categories[template.category].push(template)
  }

  return categories
}

/**
 * Get a single template by type
 */
export function getTemplate(type: string): SchemaTemplate | undefined {
  return SCHEMA_TEMPLATES[type]
}

/**
 * Get all template types
 */
export function getAllTypes(): string[] {
  return Object.keys(SCHEMA_TEMPLATES)
}

/**
 * Get templates that are default on (site-wide)
 */
export function getDefaultOnTemplates(): SchemaTemplate[] {
  return Object.values(SCHEMA_TEMPLATES).filter((t) => t.defaultOn === true)
}
