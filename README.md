# wagtail-seo-toolkit

[![PyPI version](https://badge.fury.io/py/wagtail-seo-toolkit.svg)](https://badge.fury.io/py/wagtail-seo-toolkit)
[![CI](https://github.com/kkm-horikawa/wagtail-seo-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/kkm-horikawa/wagtail-seo-toolkit/actions/workflows/ci.yml)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

## Philosophy

SEO optimization shouldn't require deep technical knowledge. While Wagtail provides excellent content management, setting up proper meta tags, Open Graph, Twitter Cards, and Schema.org structured data requires significant manual work.

**wagtail-seo-toolkit** provides a comprehensive SEO solution with just two template tags. Site-wide settings are managed through Wagtail's admin interface, while page-specific SEO can be configured per-page with sensible defaults.

The goal is to help content editors achieve **best-practice SEO** without touching code, while giving developers full control when needed.

## Key Features

- **Simple Integration** - Just 2 template tags: `{% seo_head %}` and `{% seo_schema %}`
- **Site-wide Settings** - Configure Organization, favicons, social profiles from admin
- **Page-level SEO** - Override title, description, OG image per page
- **13+ Schema Types** - Article, Product, FAQ, Event, LocalBusiness, and more
- **Automatic BreadcrumbList** - Generated from page hierarchy
- **Multi-language Support** - hreflang tags with wagtail-localize integration
- **Japanese UI** - Full Japanese localization for admin interface

## Comparison with Existing Libraries

| Feature | wagtail-seo | wagtail-metadata | wagtail-seo-toolkit |
|---------|-------------|------------------|---------------------|
| Meta tags | Yes | Yes | Yes |
| Open Graph | Yes | Yes | Yes |
| Twitter Card | Yes | Yes | Yes |
| Organization Schema | Yes | No | Yes |
| Article Schema | Yes | No | Yes |
| BreadcrumbList | No | No | **Auto-generated** |
| FAQPage Schema | No | No | **Yes** |
| Product Schema | No | No | **Yes** |
| Event Schema | No | No | **Yes** |
| LocalBusiness Schema | No | No | **Yes** |
| 13+ Schema types | No | No | **Yes** |
| hreflang (i18n) | No | No | **Yes** |
| Template tags | 3 includes | 1 tag | **2 tags** |
| Japanese UI | No | No | **Yes** |

## Installation

```bash
pip install wagtail-seo-toolkit
```

Add to your `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'wagtail.contrib.settings',  # Required
    'wagtail_seo_toolkit',
    # ...
]
```

## Quick Start

### 1. Add Template Tags

```html
{% load wagtail_seo_toolkit %}
<!DOCTYPE html>
<html>
<head>
    {% seo_head %}
</head>
<body>
    <!-- Your content -->

    {% seo_schema %}
</body>
</html>
```

That's it! The template tags handle everything:
- `{% seo_head %}` - All meta tags, OG, Twitter Card, favicon, hreflang
- `{% seo_schema %}` - All JSON-LD structured data

### 2. Configure Site Settings

Go to **Settings > SEO Settings** in Wagtail admin to configure:

- Organization name, logo, type
- Social media profiles (Twitter, Facebook, etc.)
- Default OG image
- Favicon and Apple Touch Icon
- Google/Bing site verification

### 3. Add SEO Mixin to Pages (Optional)

For page-level SEO control, add the mixin to your page models:

```python
from wagtail.models import Page
from wagtail_seo_toolkit.models import SEOPageMixin

class ArticlePage(SEOPageMixin, Page):
    # Your fields...

    content_panels = Page.content_panels + [
        # Your panels...
    ]

    promote_panels = Page.promote_panels + SEOPageMixin.seo_panels
```

This adds a "SEO" tab in the page editor with:
- SEO title and description
- OG image override
- Schema type selector (Article, Product, FAQ, etc.)
- noindex/nofollow options
- Canonical URL override

## Supported Schema Types

### Site-wide (Automatic)
- **WebSite** - Site search box support
- **Organization** - Company/organization info

### Page-selectable
| Type | Use Case |
|------|----------|
| WebPage | General pages (default) |
| Article | General articles |
| NewsArticle | News content |
| BlogPosting | Blog posts |
| Product | Product pages |
| LocalBusiness | Store/business info |
| Service | Service descriptions |
| FAQPage | FAQ pages |
| HowTo | How-to guides |
| Event | Events |
| Person | Profile pages |
| Recipe | Recipes |
| Course | Online courses |
| JobPosting | Job listings |

### Automatic
- **BreadcrumbList** - Generated from page hierarchy

## Output Example

### `{% seo_head %}` Output

```html
<!-- Basic Meta -->
<title>Page Title | Site Name</title>
<meta name="description" content="Page description...">
<meta name="robots" content="index, follow">

<!-- Canonical -->
<link rel="canonical" href="https://example.com/page/">

<!-- hreflang (multilingual) -->
<link rel="alternate" hreflang="ja" href="https://example.com/ja/page/">
<link rel="alternate" hreflang="en" href="https://example.com/en/page/">
<link rel="alternate" hreflang="x-default" href="https://example.com/ja/page/">

<!-- Favicon -->
<link rel="icon" type="image/png" sizes="32x32" href="/media/favicon.png">
<link rel="apple-touch-icon" sizes="180x180" href="/media/apple-touch-icon.png">

<!-- Open Graph -->
<meta property="og:type" content="article">
<meta property="og:title" content="Page Title">
<meta property="og:description" content="Page description...">
<meta property="og:image" content="https://example.com/media/og-image.jpg">
<meta property="og:url" content="https://example.com/page/">
<meta property="og:site_name" content="Site Name">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@handle">
<meta name="twitter:title" content="Page Title">
<meta name="twitter:description" content="Page description...">
<meta name="twitter:image" content="https://example.com/media/og-image.jpg">

<!-- Verification -->
<meta name="google-site-verification" content="xxxxx">
```

### `{% seo_schema %}` Output

```html
<script type="application/ld+json">
[
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Site Name",
    "url": "https://example.com/"
  },
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Company Name",
    "url": "https://example.com/",
    "logo": "https://example.com/media/logo.png",
    "sameAs": [
      "https://twitter.com/company",
      "https://www.facebook.com/company"
    ]
  },
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.com/"},
      {"@type": "ListItem", "position": 2, "name": "Blog", "item": "https://example.com/blog/"},
      {"@type": "ListItem", "position": 3, "name": "Article Title"}
    ]
  },
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Article Title",
    "image": "https://example.com/media/article-image.jpg",
    "author": {"@type": "Person", "name": "Author Name"},
    "datePublished": "2025-01-15T10:00:00+09:00",
    "dateModified": "2025-01-16T15:30:00+09:00"
  }
]
</script>
```

## Configuration

All settings are optional and configured through Wagtail admin:

### Site Settings (Admin UI)

| Setting | Description |
|---------|-------------|
| Organization name | Company/site name for Schema |
| Organization type | Corporation, LocalBusiness, etc. |
| Organization logo | Logo image for Schema |
| Twitter handle | @username (without @) |
| Facebook URL | Facebook page URL |
| Default OG image | Fallback image for social sharing |
| Favicon | Browser tab icon |
| Apple Touch Icon | iOS home screen icon |
| Google verification | google-site-verification code |

### Django Settings (Optional)

```python
# settings.py
WAGTAIL_SEO_TOOLKIT = {
    # Default robots meta (can be overridden per-page)
    'DEFAULT_ROBOTS': 'index, follow',

    # OG image rendition filter
    'OG_IMAGE_FILTER': 'fill-1200x630',

    # Favicon rendition filter
    'FAVICON_FILTER': 'fill-32x32',
}
```

## Multi-language Support

wagtail-seo-toolkit automatically generates hreflang tags when used with [wagtail-localize](https://wagtail-localize.org/):

```html
<link rel="alternate" hreflang="ja" href="https://example.com/ja/page/">
<link rel="alternate" hreflang="en" href="https://example.com/en/page/">
<link rel="alternate" hreflang="x-default" href="https://example.com/ja/page/">
```

No additional configuration needed - it detects wagtail-localize automatically.

## Requirements

| Python | Django | Wagtail |
|--------|--------|---------|
| 3.10+  | 4.2, 5.1, 5.2 | 6.4, 7.0, 7.2 |

## Documentation

- [Contributing Guide](CONTRIBUTING.md)

## Project Links

- [GitHub Repository](https://github.com/kkm-horikawa/wagtail-seo-toolkit)
- [Issue Tracker](https://github.com/kkm-horikawa/wagtail-seo-toolkit/issues)

## Related Projects

- [wagtail-seo](https://github.com/coderedcorp/wagtail-seo) - SEO optimization by CodeRed
- [wagtail-metadata](https://github.com/neon-jungle/wagtail-metadata) - Meta tags by Neon Jungle
- [wagtail-schema.org](https://github.com/neon-jungle/wagtail-schema.org) - Schema.org by Neon Jungle

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

BSD 3-Clause License. See [LICENSE](LICENSE) for details.
