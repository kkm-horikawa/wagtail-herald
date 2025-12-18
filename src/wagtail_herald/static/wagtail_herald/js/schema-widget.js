const SCHEMA_TEMPLATES = {
  // ===================
  // Site-wide schemas (default ON)
  // ===================
  WebSite: {
    type: "WebSite",
    label: "WebSite",
    labelJa: "ウェブサイト",
    category: "site-wide",
    defaultOn: true,
    helpText: "Site information. Auto-populated from Site settings.",
    helpTextJa: "サイト情報。サイト設定から自動入力されます。",
    autoFields: [
      {
        schemaProperty: "name",
        source: "site.site_name",
        description: "Site name"
      },
      {
        schemaProperty: "url",
        source: "site.root_url",
        description: "Site URL"
      }
    ],
    requiredFields: [],
    optionalFields: [
      {
        name: "potentialAction",
        type: "object",
        description: "SearchAction for sitelinks search box"
      }
    ],
    placeholder: {},
    example: {
      potentialAction: {
        "@type": "SearchAction",
        target: "https://example.com/search?q={search_term_string}"
      }
    },
    googleDocsUrl: "https://schema.org/WebSite"
  },
  Organization: {
    type: "Organization",
    label: "Organization",
    labelJa: "組織",
    category: "site-wide",
    defaultOn: true,
    helpText: "Organization info. Auto-populated from SEO Settings.",
    helpTextJa: "組織情報。SEO設定から自動入力されます。",
    autoFields: [
      {
        schemaProperty: "name",
        source: "settings.organization_name",
        description: "Org name"
      },
      {
        schemaProperty: "url",
        source: "site.root_url",
        description: "Website URL"
      },
      {
        schemaProperty: "logo",
        source: "settings.organization_logo",
        description: "Logo image"
      },
      {
        schemaProperty: "sameAs",
        source: "settings.social_profiles",
        description: "Social links"
      }
    ],
    requiredFields: [],
    optionalFields: [],
    placeholder: {},
    example: {},
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/organization"
  },
  BreadcrumbList: {
    type: "BreadcrumbList",
    label: "BreadcrumbList",
    labelJa: "パンくずリスト",
    category: "site-wide",
    defaultOn: true,
    helpText: "Breadcrumb navigation. Fully auto-generated from page hierarchy.",
    helpTextJa: "パンくずナビ。ページ階層から完全自動生成されます。",
    autoFields: [
      {
        schemaProperty: "itemListElement",
        source: "page.get_ancestors()",
        description: "Breadcrumb items"
      }
    ],
    requiredFields: [],
    optionalFields: [],
    placeholder: {},
    example: {},
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/breadcrumb"
  },
  // ===================
  // Content schemas
  // ===================
  WebPage: {
    type: "WebPage",
    label: "Web Page",
    labelJa: "ウェブページ",
    category: "content",
    helpText: "Generic web page. All properties auto-generated.",
    helpTextJa: "一般的なウェブページ。すべてのプロパティは自動生成されます。",
    autoFields: [
      {
        schemaProperty: "name",
        source: "page.title",
        description: "Page title"
      },
      {
        schemaProperty: "description",
        source: "page.search_description",
        description: "Meta description"
      },
      {
        schemaProperty: "url",
        source: "page.full_url",
        description: "Page URL"
      }
    ],
    requiredFields: [],
    optionalFields: [],
    placeholder: {},
    example: {},
    googleDocsUrl: "https://schema.org/WebPage"
  },
  Article: {
    type: "Article",
    label: "Article",
    labelJa: "記事",
    category: "content",
    helpText: "General article. Use NewsArticle for news, BlogPosting for blogs.",
    helpTextJa: "一般的な記事。ニュースにはNewsArticle、ブログにはBlogPostingを使用。",
    autoFields: [
      {
        schemaProperty: "headline",
        source: "page.seo_title || page.title",
        description: "Article headline"
      },
      {
        schemaProperty: "author",
        source: "page.owner",
        description: "Author (Person)"
      },
      {
        schemaProperty: "datePublished",
        source: "page.first_published_at",
        description: "Publish date"
      },
      {
        schemaProperty: "dateModified",
        source: "page.last_published_at",
        description: "Last modified"
      },
      {
        schemaProperty: "image",
        source: "page.og_image",
        description: "Featured image"
      },
      {
        schemaProperty: "publisher",
        source: "settings.organization",
        description: "Publisher org"
      }
    ],
    requiredFields: [],
    optionalFields: [
      {
        name: "articleSection",
        type: "string",
        description: "Article section/category"
      },
      { name: "wordCount", type: "number", description: "Word count" }
    ],
    placeholder: {},
    example: { articleSection: "Technology", wordCount: 1500 },
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/article"
  },
  NewsArticle: {
    type: "NewsArticle",
    label: "News Article",
    labelJa: "ニュース記事",
    category: "content",
    helpText: "News article. Enables Google News features.",
    helpTextJa: "ニュース記事。Googleニュース機能が有効になります。",
    autoFields: [
      {
        schemaProperty: "headline",
        source: "page.seo_title || page.title",
        description: "Article headline"
      },
      {
        schemaProperty: "author",
        source: "page.owner",
        description: "Author (Person)"
      },
      {
        schemaProperty: "datePublished",
        source: "page.first_published_at",
        description: "Publish date"
      },
      {
        schemaProperty: "dateModified",
        source: "page.last_published_at",
        description: "Last modified"
      },
      {
        schemaProperty: "image",
        source: "page.og_image",
        description: "Featured image"
      },
      {
        schemaProperty: "publisher",
        source: "settings.organization",
        description: "Publisher org"
      }
    ],
    requiredFields: [],
    optionalFields: [
      {
        name: "dateline",
        type: "string",
        description: "News dateline location"
      }
    ],
    placeholder: {},
    example: { dateline: "TOKYO" },
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/article"
  },
  BlogPosting: {
    type: "BlogPosting",
    label: "Blog Post",
    labelJa: "ブログ記事",
    category: "content",
    helpText: "Blog post. Similar to Article but for blog content.",
    helpTextJa: "ブログ投稿。Articleと同様ですがブログコンテンツ向け。",
    autoFields: [
      {
        schemaProperty: "headline",
        source: "page.seo_title || page.title",
        description: "Post headline"
      },
      {
        schemaProperty: "author",
        source: "page.owner",
        description: "Author (Person)"
      },
      {
        schemaProperty: "datePublished",
        source: "page.first_published_at",
        description: "Publish date"
      },
      {
        schemaProperty: "dateModified",
        source: "page.last_published_at",
        description: "Last modified"
      },
      {
        schemaProperty: "image",
        source: "page.og_image",
        description: "Featured image"
      },
      {
        schemaProperty: "publisher",
        source: "settings.organization",
        description: "Publisher org"
      }
    ],
    requiredFields: [],
    optionalFields: [
      { name: "articleSection", type: "string", description: "Blog category" },
      {
        name: "keywords",
        type: "string",
        description: "Comma-separated keywords"
      }
    ],
    placeholder: {},
    example: { articleSection: "Tech Blog", keywords: "wagtail, cms, python" },
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/article"
  },
  // ===================
  // Business schemas
  // ===================
  Product: {
    type: "Product",
    label: "Product",
    labelJa: "商品",
    category: "business",
    helpText: "Product with price/availability. Enables rich results.",
    helpTextJa: "価格・在庫情報付き商品ページ。リッチリザルト対応。",
    autoFields: [
      {
        schemaProperty: "name",
        source: "page.title",
        description: "Product name"
      },
      {
        schemaProperty: "description",
        source: "page.search_description",
        description: "Description"
      },
      {
        schemaProperty: "image",
        source: "page.og_image",
        description: "Product image"
      }
    ],
    requiredFields: [],
    optionalFields: [
      { name: "offers", type: "object", description: "Price and availability" },
      { name: "brand", type: "string", description: "Brand name" },
      { name: "sku", type: "string", description: "Product SKU" },
      { name: "gtin", type: "string", description: "Global Trade Item Number" }
    ],
    placeholder: {
      offers: {
        "@type": "Offer",
        price: "",
        priceCurrency: "JPY",
        availability: "https://schema.org/InStock"
      }
    },
    example: {
      offers: { "@type": "Offer", price: "1999", priceCurrency: "JPY" },
      brand: "Example Brand",
      sku: "PROD-001"
    },
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/product"
  },
  LocalBusiness: {
    type: "LocalBusiness",
    label: "Local Business",
    labelJa: "ローカルビジネス",
    category: "business",
    helpText: "Local business with address and hours. Great for local SEO.",
    helpTextJa: "住所・営業時間付きローカルビジネス。ローカルSEOに効果的。",
    autoFields: [
      {
        schemaProperty: "name",
        source: "page.title",
        description: "Business name"
      },
      {
        schemaProperty: "description",
        source: "page.search_description",
        description: "Description"
      },
      {
        schemaProperty: "image",
        source: "page.og_image",
        description: "Business image"
      }
    ],
    requiredFields: [
      { name: "address", type: "object", description: "PostalAddress object" }
    ],
    optionalFields: [
      { name: "telephone", type: "string", description: "Phone number" },
      {
        name: "openingHoursSpecification",
        type: "array",
        description: "Business hours"
      },
      {
        name: "priceRange",
        type: "string",
        description: "Price range (e.g., $$)"
      },
      { name: "geo", type: "object", description: "GeoCoordinates" }
    ],
    placeholder: {
      address: {
        "@type": "PostalAddress",
        streetAddress: "",
        addressLocality: "",
        addressRegion: "",
        postalCode: "",
        addressCountry: "JP"
      }
    },
    example: {
      address: {
        "@type": "PostalAddress",
        streetAddress: "1-1-1 Shibuya",
        addressLocality: "Shibuya-ku",
        addressRegion: "Tokyo",
        postalCode: "150-0002",
        addressCountry: "JP"
      },
      telephone: "+81-3-1234-5678",
      priceRange: "$$"
    },
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/local-business"
  },
  Service: {
    type: "Service",
    label: "Service",
    labelJa: "サービス",
    category: "business",
    helpText: "Service offering. Describe what services you provide.",
    helpTextJa: "サービス提供。提供サービスの説明に使用。",
    autoFields: [
      {
        schemaProperty: "name",
        source: "page.title",
        description: "Service name"
      },
      {
        schemaProperty: "description",
        source: "page.search_description",
        description: "Description"
      },
      {
        schemaProperty: "provider",
        source: "settings.organization",
        description: "Provider"
      }
    ],
    requiredFields: [],
    optionalFields: [
      { name: "serviceType", type: "string", description: "Type of service" },
      { name: "areaServed", type: "string", description: "Service area" },
      { name: "offers", type: "object", description: "Service pricing" }
    ],
    placeholder: {},
    example: {
      serviceType: "Web Development",
      areaServed: "Japan"
    },
    googleDocsUrl: "https://schema.org/Service"
  },
  // ===================
  // Interactive schemas
  // ===================
  FAQPage: {
    type: "FAQPage",
    label: "FAQ Page",
    labelJa: "FAQページ",
    category: "interactive",
    helpText: "FAQ with expandable Q&A. High visibility in search.",
    helpTextJa: "Q&A形式のFAQページ。検索結果で高い視認性。",
    autoFields: [],
    requiredFields: [
      {
        name: "mainEntity",
        type: "array",
        description: "Array of Question objects"
      }
    ],
    optionalFields: [],
    placeholder: {
      mainEntity: [
        {
          "@type": "Question",
          name: "",
          acceptedAnswer: { "@type": "Answer", text: "" }
        }
      ]
    },
    example: {
      mainEntity: [
        {
          "@type": "Question",
          name: "What is wagtail-herald?",
          acceptedAnswer: {
            "@type": "Answer",
            text: "A comprehensive SEO toolkit for Wagtail CMS."
          }
        }
      ]
    },
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/faqpage"
  },
  HowTo: {
    type: "HowTo",
    label: "How-To",
    labelJa: "ハウツー",
    category: "interactive",
    helpText: "Step-by-step instructions. Shows steps in search results.",
    helpTextJa: "ステップバイステップの手順。検索結果に手順が表示されます。",
    autoFields: [
      {
        schemaProperty: "name",
        source: "page.title",
        description: "How-to title"
      },
      {
        schemaProperty: "description",
        source: "page.search_description",
        description: "Description"
      },
      {
        schemaProperty: "image",
        source: "page.og_image",
        description: "Main image"
      }
    ],
    requiredFields: [
      { name: "step", type: "array", description: "Array of HowToStep" }
    ],
    optionalFields: [
      {
        name: "totalTime",
        type: "string",
        description: "ISO 8601 duration (e.g., PT30M)"
      },
      { name: "estimatedCost", type: "object", description: "MonetaryAmount" },
      { name: "supply", type: "array", description: "Required supplies" },
      { name: "tool", type: "array", description: "Required tools" }
    ],
    placeholder: {
      step: [
        {
          "@type": "HowToStep",
          name: "",
          text: ""
        }
      ]
    },
    example: {
      step: [
        {
          "@type": "HowToStep",
          name: "Install",
          text: "pip install wagtail-herald"
        },
        {
          "@type": "HowToStep",
          name: "Configure",
          text: "Add to INSTALLED_APPS"
        }
      ],
      totalTime: "PT10M"
    },
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/how-to"
  },
  // ===================
  // Events schema
  // ===================
  Event: {
    type: "Event",
    label: "Event",
    labelJa: "イベント",
    category: "events",
    helpText: "Event with date, location, and tickets. Shows in Google Events.",
    helpTextJa: "日時・場所・チケット情報付きイベント。Googleイベントに表示。",
    autoFields: [
      {
        schemaProperty: "name",
        source: "page.title",
        description: "Event name"
      },
      {
        schemaProperty: "description",
        source: "page.search_description",
        description: "Description"
      },
      {
        schemaProperty: "image",
        source: "page.og_image",
        description: "Event image"
      }
    ],
    requiredFields: [
      {
        name: "startDate",
        type: "datetime",
        description: "Event start date/time"
      },
      {
        name: "location",
        type: "object",
        description: "Place or VirtualLocation"
      }
    ],
    optionalFields: [
      { name: "endDate", type: "datetime", description: "Event end date/time" },
      {
        name: "eventStatus",
        type: "string",
        description: "EventScheduled, EventCancelled, etc."
      },
      {
        name: "eventAttendanceMode",
        type: "string",
        description: "Online, Offline, Mixed"
      },
      { name: "offers", type: "object", description: "Ticket information" },
      {
        name: "performer",
        type: "object",
        description: "Person or Organization"
      },
      {
        name: "organizer",
        type: "object",
        description: "Person or Organization"
      }
    ],
    placeholder: {
      startDate: "",
      location: {
        "@type": "Place",
        name: "",
        address: {
          "@type": "PostalAddress",
          streetAddress: "",
          addressLocality: "",
          addressCountry: "JP"
        }
      }
    },
    example: {
      startDate: "2025-03-15T19:00:00+09:00",
      endDate: "2025-03-15T21:00:00+09:00",
      location: {
        "@type": "Place",
        name: "Tokyo International Forum",
        address: {
          "@type": "PostalAddress",
          streetAddress: "3-5-1 Marunouchi",
          addressLocality: "Chiyoda-ku",
          addressCountry: "JP"
        }
      },
      eventStatus: "https://schema.org/EventScheduled",
      eventAttendanceMode: "https://schema.org/OfflineEventAttendanceMode"
    },
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/event"
  },
  // ===================
  // People schema
  // ===================
  Person: {
    type: "Person",
    label: "Person",
    labelJa: "人物",
    category: "people",
    helpText: "Person profile. Useful for author pages and team members.",
    helpTextJa: "人物プロフィール。著者ページやチームメンバーに有用。",
    autoFields: [
      {
        schemaProperty: "name",
        source: "page.title",
        description: "Person name"
      },
      {
        schemaProperty: "description",
        source: "page.search_description",
        description: "Bio"
      },
      {
        schemaProperty: "image",
        source: "page.og_image",
        description: "Photo"
      }
    ],
    requiredFields: [],
    optionalFields: [
      { name: "jobTitle", type: "string", description: "Job title" },
      { name: "worksFor", type: "object", description: "Organization" },
      { name: "email", type: "string", description: "Email address" },
      { name: "sameAs", type: "array", description: "Social profile URLs" },
      {
        name: "alumniOf",
        type: "object",
        description: "Educational organization"
      }
    ],
    placeholder: {},
    example: {
      jobTitle: "Software Engineer",
      worksFor: { "@type": "Organization", name: "Example Corp" },
      sameAs: ["https://twitter.com/example", "https://github.com/example"]
    },
    googleDocsUrl: "https://schema.org/Person"
  },
  // ===================
  // Specialized schemas
  // ===================
  Recipe: {
    type: "Recipe",
    label: "Recipe",
    labelJa: "レシピ",
    category: "specialized",
    helpText: "Recipe with ingredients and steps. Shows rich results with image.",
    helpTextJa: "材料・手順付きレシピ。画像付きリッチリザルトに表示。",
    autoFields: [
      {
        schemaProperty: "name",
        source: "page.title",
        description: "Recipe name"
      },
      {
        schemaProperty: "description",
        source: "page.search_description",
        description: "Description"
      },
      {
        schemaProperty: "image",
        source: "page.og_image",
        description: "Recipe image"
      },
      {
        schemaProperty: "author",
        source: "page.owner",
        description: "Recipe author"
      },
      {
        schemaProperty: "datePublished",
        source: "page.first_published_at",
        description: "Publish date"
      }
    ],
    requiredFields: [
      {
        name: "recipeIngredient",
        type: "array",
        description: "List of ingredients"
      },
      {
        name: "recipeInstructions",
        type: "array",
        description: "Cooking steps"
      }
    ],
    optionalFields: [
      { name: "prepTime", type: "string", description: "ISO 8601 duration" },
      { name: "cookTime", type: "string", description: "ISO 8601 duration" },
      { name: "totalTime", type: "string", description: "ISO 8601 duration" },
      {
        name: "recipeYield",
        type: "string",
        description: "Number of servings"
      },
      {
        name: "recipeCategory",
        type: "string",
        description: "Meal type (e.g., Dinner)"
      },
      {
        name: "recipeCuisine",
        type: "string",
        description: "Cuisine type (e.g., Japanese)"
      },
      {
        name: "nutrition",
        type: "object",
        description: "NutritionInformation"
      }
    ],
    placeholder: {
      recipeIngredient: [],
      recipeInstructions: [{ "@type": "HowToStep", text: "" }]
    },
    example: {
      recipeIngredient: ["2 cups flour", "1 cup sugar", "2 eggs"],
      recipeInstructions: [
        { "@type": "HowToStep", text: "Mix dry ingredients" },
        { "@type": "HowToStep", text: "Add wet ingredients" },
        { "@type": "HowToStep", text: "Bake at 350°F for 30 minutes" }
      ],
      prepTime: "PT15M",
      cookTime: "PT30M",
      recipeYield: "8 servings",
      recipeCuisine: "American"
    },
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/recipe"
  },
  Course: {
    type: "Course",
    label: "Course",
    labelJa: "コース",
    category: "specialized",
    helpText: "Educational course. Shows in Google course listings.",
    helpTextJa: "教育コース。Googleコース一覧に表示。",
    autoFields: [
      {
        schemaProperty: "name",
        source: "page.title",
        description: "Course name"
      },
      {
        schemaProperty: "description",
        source: "page.search_description",
        description: "Description"
      },
      {
        schemaProperty: "provider",
        source: "settings.organization",
        description: "Provider"
      }
    ],
    requiredFields: [],
    optionalFields: [
      { name: "courseCode", type: "string", description: "Course code/ID" },
      {
        name: "hasCourseInstance",
        type: "array",
        description: "Course instances with dates"
      },
      {
        name: "educationalLevel",
        type: "string",
        description: "Difficulty level"
      },
      { name: "offers", type: "object", description: "Pricing information" },
      {
        name: "totalHistoricalEnrollment",
        type: "number",
        description: "Total enrollments"
      }
    ],
    placeholder: {},
    example: {
      courseCode: "CS101",
      educationalLevel: "Beginner",
      hasCourseInstance: [
        {
          "@type": "CourseInstance",
          courseMode: "Online",
          startDate: "2025-04-01"
        }
      ]
    },
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/course"
  },
  JobPosting: {
    type: "JobPosting",
    label: "Job Posting",
    labelJa: "求人情報",
    category: "specialized",
    helpText: "Job listing. Shows in Google Jobs search.",
    helpTextJa: "求人情報。Google求人検索に表示。",
    autoFields: [
      {
        schemaProperty: "title",
        source: "page.title",
        description: "Job title"
      },
      {
        schemaProperty: "description",
        source: "page.search_description",
        description: "Job description"
      },
      {
        schemaProperty: "datePosted",
        source: "page.first_published_at",
        description: "Post date"
      },
      {
        schemaProperty: "hiringOrganization",
        source: "settings.organization",
        description: "Employer"
      }
    ],
    requiredFields: [
      {
        name: "jobLocation",
        type: "object",
        description: "Place with address"
      }
    ],
    optionalFields: [
      {
        name: "validThrough",
        type: "datetime",
        description: "Application deadline"
      },
      {
        name: "employmentType",
        type: "string",
        description: "FULL_TIME, PART_TIME, etc."
      },
      { name: "baseSalary", type: "object", description: "MonetaryAmount" },
      {
        name: "jobLocationType",
        type: "string",
        description: "TELECOMMUTE for remote"
      },
      {
        name: "applicantLocationRequirements",
        type: "object",
        description: "Location requirements"
      }
    ],
    placeholder: {
      jobLocation: {
        "@type": "Place",
        address: {
          "@type": "PostalAddress",
          streetAddress: "",
          addressLocality: "",
          addressRegion: "",
          postalCode: "",
          addressCountry: "JP"
        }
      }
    },
    example: {
      jobLocation: {
        "@type": "Place",
        address: {
          "@type": "PostalAddress",
          streetAddress: "1-1-1 Shibuya",
          addressLocality: "Shibuya-ku",
          addressRegion: "Tokyo",
          postalCode: "150-0002",
          addressCountry: "JP"
        }
      },
      employmentType: "FULL_TIME",
      baseSalary: {
        "@type": "MonetaryAmount",
        currency: "JPY",
        value: {
          "@type": "QuantitativeValue",
          minValue: 5e6,
          maxValue: 8e6,
          unitText: "YEAR"
        }
      },
      validThrough: "2025-06-30T23:59:59+09:00"
    },
    googleDocsUrl: "https://developers.google.com/search/docs/appearance/structured-data/job-posting"
  }
};
function getTemplatesByCategory() {
  const categories = {};
  for (const template of Object.values(SCHEMA_TEMPLATES)) {
    if (!categories[template.category]) {
      categories[template.category] = [];
    }
    categories[template.category].push(template);
  }
  return categories;
}
function getTemplate(type) {
  return SCHEMA_TEMPLATES[type];
}
function getAllTypes() {
  return Object.keys(SCHEMA_TEMPLATES);
}
function getDefaultOnTemplates() {
  return Object.values(SCHEMA_TEMPLATES).filter((t) => t.defaultOn === true);
}
const CATEGORY_LABELS = {
  "site-wide": { en: "Site-wide", ja: "サイト全体" },
  content: { en: "Content", ja: "コンテンツ" },
  business: { en: "Business", ja: "ビジネス" },
  interactive: { en: "Interactive", ja: "インタラクティブ" },
  events: { en: "Events", ja: "イベント" },
  people: { en: "People", ja: "人物" },
  specialized: { en: "Specialized", ja: "特殊" }
};
const CATEGORY_ORDER = [
  "site-wide",
  "content",
  "business",
  "interactive",
  "events",
  "people",
  "specialized"
];
function isJapaneseLocale() {
  if (typeof document === "undefined") return false;
  const htmlLang = document.documentElement.lang;
  return (htmlLang == null ? void 0 : htmlLang.startsWith("ja")) ?? false;
}
function initSchemaWidget(container, initialState) {
  const state = initialState ?? { types: [], properties: {} };
  const isJa = isJapaneseLocale();
  render(container, state, isJa);
  return {
    getState: () => ({
      types: [...state.types],
      properties: JSON.parse(JSON.stringify(state.properties))
    }),
    setState: (newState) => {
      state.types = [...newState.types];
      state.properties = JSON.parse(JSON.stringify(newState.properties));
      render(container, state, isJa);
    },
    destroy: () => {
      container.innerHTML = "";
    }
  };
}
function render(container, state, isJa) {
  container.innerHTML = `
    <div class="schema-widget">
      <div class="schema-widget__types">
        ${renderTypeCheckboxes(state.types, isJa)}
      </div>
      <div class="schema-widget__properties">
        ${renderPropertyEditors(state, isJa)}
      </div>
    </div>
  `;
  attachEventListeners(container, state, isJa);
}
function renderTypeCheckboxes(selectedTypes, isJa) {
  const categories = getTemplatesByCategory();
  return CATEGORY_ORDER.map((category) => {
    const templates = categories[category];
    if (!templates || templates.length === 0) return "";
    const categoryLabel = CATEGORY_LABELS[category];
    const displayLabel = isJa ? categoryLabel.ja : categoryLabel.en;
    return `
      <fieldset class="schema-widget__category">
        <legend>${escapeHtml(displayLabel)}</legend>
        <div class="schema-widget__category-types">
          ${templates.map((t) => {
      const label = isJa ? t.labelJa : t.label;
      const isChecked = selectedTypes.includes(t.type);
      const isDefaultOn = t.defaultOn === true;
      return `
              <label class="schema-widget__type${isDefaultOn ? " schema-widget__type--default" : ""}">
                <input type="checkbox"
                       name="schema_type"
                       value="${escapeHtml(t.type)}"
                       ${isChecked ? "checked" : ""}>
                <span class="schema-widget__type-label">${escapeHtml(label)}</span>
                ${isDefaultOn ? '<span class="schema-widget__type-badge">Auto</span>' : ""}
              </label>
            `;
    }).join("")}
        </div>
      </fieldset>
    `;
  }).join("");
}
function renderPropertyEditors(state, isJa) {
  if (state.types.length === 0) {
    const emptyMessage = isJa ? "スキーマタイプを選択してプロパティを設定してください" : "Select schema types above to configure properties";
    return `<div class="schema-widget__empty">${escapeHtml(emptyMessage)}</div>`;
  }
  return state.types.map((type) => {
    const template = SCHEMA_TEMPLATES[type];
    if (!template) return "";
    const properties = state.properties[type] ?? template.placeholder;
    const label = isJa ? template.labelJa : template.label;
    const helpText = isJa ? template.helpTextJa : template.helpText;
    const autoFieldsLabel = isJa ? "自動入力" : "Auto-filled";
    const exampleLabel = isJa ? "例" : "Example";
    const requiredLabel = isJa ? "必須項目" : "Required";
    const optionalLabel = isJa ? "オプション" : "Optional";
    const autoFieldsList = template.autoFields.length > 0 ? template.autoFields.map((f) => f.schemaProperty).join(", ") : isJa ? "なし" : "None";
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
              ${isJa ? "カスタムプロパティ (JSON)" : "Custom Properties (JSON)"}
            </label>
            <textarea
              class="schema-widget__json"
              data-schema-type="${escapeHtml(type)}"
              rows="6"
              spellcheck="false"
            >${escapeHtml(JSON.stringify(properties, null, 2))}</textarea>
          </div>

          ${Object.keys(template.example).length > 0 ? `
            <div class="schema-widget__example">
              <strong>${escapeHtml(exampleLabel)}:</strong>
              <code>${escapeHtml(JSON.stringify(template.example))}</code>
            </div>
          ` : ""}
        </div>
      </details>
    `;
  }).join("");
}
function renderFieldInfo(template, requiredLabel, optionalLabel) {
  const parts = [];
  if (template.requiredFields.length > 0) {
    const fields = template.requiredFields.map((f) => `${f.name} (${f.type})`).join(", ");
    parts.push(`
      <div class="schema-widget__fields schema-widget__fields--required">
        <strong>${escapeHtml(requiredLabel)}:</strong> ${escapeHtml(fields)}
      </div>
    `);
  }
  if (template.optionalFields.length > 0) {
    const fields = template.optionalFields.map((f) => `${f.name} (${f.type})`).join(", ");
    parts.push(`
      <div class="schema-widget__fields schema-widget__fields--optional">
        <strong>${escapeHtml(optionalLabel)}:</strong> ${escapeHtml(fields)}
      </div>
    `);
  }
  return parts.join("");
}
function attachEventListeners(container, state, isJa) {
  const checkboxes = container.querySelectorAll(
    'input[name="schema_type"]'
  );
  for (const checkbox of checkboxes) {
    checkbox.addEventListener("change", () => {
      handleCheckboxChange(container, state, checkbox, isJa);
    });
  }
  const textareas = container.querySelectorAll(
    ".schema-widget__json"
  );
  for (const textarea of textareas) {
    textarea.addEventListener("blur", () => {
      handleJsonChange(state, textarea);
    });
  }
}
function handleCheckboxChange(container, state, checkbox, isJa) {
  const type = checkbox.value;
  if (checkbox.checked) {
    if (!state.types.includes(type)) {
      state.types.push(type);
      if (!state.properties[type]) {
        const template = SCHEMA_TEMPLATES[type];
        if (template) {
          state.properties[type] = { ...template.placeholder };
        }
      }
    }
  } else {
    const index = state.types.indexOf(type);
    if (index > -1) {
      state.types.splice(index, 1);
    }
  }
  const propertiesContainer = container.querySelector(
    ".schema-widget__properties"
  );
  if (propertiesContainer) {
    propertiesContainer.innerHTML = renderPropertyEditors(state, isJa);
    const textareas = propertiesContainer.querySelectorAll(
      ".schema-widget__json"
    );
    for (const textarea of textareas) {
      textarea.addEventListener("blur", () => {
        handleJsonChange(state, textarea);
      });
    }
  }
}
function handleJsonChange(state, textarea) {
  const type = textarea.dataset.schemaType;
  if (!type) return;
  try {
    const parsed = JSON.parse(textarea.value);
    state.properties[type] = parsed;
    textarea.classList.remove("schema-widget__json--error");
  } catch {
    textarea.classList.add("schema-widget__json--error");
  }
}
function escapeHtml(str) {
  const htmlEscapes = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  };
  return str.replace(/[&<>"']/g, (char) => htmlEscapes[char]);
}
const VERSION = "0.2.0";
const WagtailHeraldSchema = {
  VERSION,
  initSchemaWidget
};
if (typeof window !== "undefined") {
  window.WagtailHeraldSchema = WagtailHeraldSchema;
}
function autoInit() {
  const elements = document.querySelectorAll(
    "[data-schema-widget]"
  );
  for (const el of elements) {
    if (el.dataset.schemaWidgetInitialized) continue;
    el.dataset.schemaWidgetInitialized = "true";
    initSchemaWidget(el);
  }
}
if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", autoInit);
  } else {
    autoInit();
  }
}
export {
  SCHEMA_TEMPLATES,
  VERSION,
  WagtailHeraldSchema,
  autoInit,
  getAllTypes,
  getDefaultOnTemplates,
  getTemplate,
  getTemplatesByCategory,
  initSchemaWidget
};
//# sourceMappingURL=schema-widget.js.map
