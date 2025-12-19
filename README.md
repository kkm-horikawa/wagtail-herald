# wagtail-herald

[![PyPI version](https://badge.fury.io/py/wagtail-herald.svg)](https://badge.fury.io/py/wagtail-herald)
[![CI](https://github.com/kkm-horikawa/wagtail-herald/actions/workflows/ci.yml/badge.svg)](https://github.com/kkm-horikawa/wagtail-herald/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/kkm-horikawa/wagtail-herald/graph/badge.svg)](https://codecov.io/gh/kkm-horikawa/wagtail-herald)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Published on Django Packages](https://img.shields.io/badge/Published%20on-Django%20Packages-0c3c26)](https://djangopackages.org/packages/p/wagtail-herald/)

## Philosophy

SEO optimization shouldn't require deep technical knowledge. While Wagtail provides excellent content management, setting up proper meta tags, Open Graph, Twitter Cards, and Schema.org structured data requires significant manual work.

**wagtail-herald** provides a comprehensive SEO solution with just two template tags. Site-wide settings are managed through Wagtail's admin interface, while page-specific SEO can be configured per-page with sensible defaults.

The goal is to help content editors achieve **best-practice SEO** without touching code, while giving developers full control when needed.

## Key Features

- **Simple Integration** - Just 3 template tags: `{% seo_head %}`, `{% seo_body %}`, `{% seo_schema %}`
- **Site-wide Settings** - Configure Organization, favicons, social profiles from admin
- **Page-level SEO** - Uses Wagtail's built-in SEO fields + OG image override
- **13+ Schema Types** - Article, Product, FAQ, Event, LocalBusiness, and more
- **Automatic BreadcrumbList** - Generated from page hierarchy
- **Locale Support** - Per-page language/region targeting with `{% page_lang %}` tag
- **Google Tag Manager** - GTM integration with noscript fallback
- **robots.txt Management** - Configure robots.txt from admin interface
- **Custom Code Injection** - Add custom HTML to head and body from admin
- **Japanese UI** - Full Japanese localization for admin interface

## Comparison with Existing Libraries

| Feature | wagtail-seo | wagtail-metadata | wagtail-herald |
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
| Locale (og:locale) | No | No | **Yes** |
| GTM/Analytics | No | No | **Yes** |
| robots.txt | No | No | **Yes** |
| Template tags | 3 includes | 1 tag | **2 tags** |
| Japanese UI | No | No | **Yes** |

## Installation

```bash
pip install wagtail-herald
```

Add to your `INSTALLED_APPS`:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'wagtail.contrib.settings',  # Required
    'wagtail_herald',
    # ...
]
```

## Quick Start

### 1. Add Template Tags

```html
{% load wagtail_herald %}
<!DOCTYPE html>
<html lang="{% page_lang %}">
<head>
    {% seo_head %}
</head>
<body>
    {% seo_body %}

    <!-- Your content -->

    {% seo_schema %}
</body>
</html>
```

That's it! The template tags handle everything:
- `{% seo_head %}` - Meta tags, OG, Twitter Card, favicon, GTM script, custom head HTML
- `{% seo_body %}` - GTM noscript fallback, custom body end HTML
- `{% seo_schema %}` - All JSON-LD structured data
- `{% page_lang %}` - Language code for html lang attribute

### 2. Configure Site Settings

Go to **Settings > SEO Settings** in Wagtail admin to configure:

- Organization name, logo, type
- Social media profiles (Twitter, Facebook)
- Default OG image and locale
- Favicon and Apple Touch Icon
- Google Tag Manager (GTM)
- robots.txt content
- Custom head/body HTML injection

### 3. Add SEO Mixin to Pages (Optional)

For page-level SEO control, add the mixin to your page models:

```python
from wagtail.models import Page
from wagtail_herald.models import SEOPageMixin

class ArticlePage(SEOPageMixin, Page):
    # Your fields...

    content_panels = Page.content_panels + [
        # Your panels...
    ]

    promote_panels = Page.promote_panels + SEOPageMixin.seo_panels
```

This adds an "SEO" panel in the page editor with:
- OG image override
- Schema type selector (Article, Product, FAQ, etc.)
- Locale selector (ja_JP, en_US, en_GB, etc.)
- noindex/nofollow options
- Canonical URL override

> **Note**: For SEO title and meta description, use Wagtail's built-in `seo_title` and `search_description` fields in the Promote tab. The template tags automatically use these fields.

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
<link rel="icon" type="image/svg+xml" href="/media/favicon.svg">
<link rel="icon" type="image/png" sizes="48x48" href="/media/favicon.png">
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

<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){...})(window,document,'script','dataLayer','GTM-XXXXXX');</script>

<!-- Custom Head HTML -->
<script src="https://example.com/custom.js"></script>
```

### `{% seo_body %}` Output

```html
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-XXXXXX"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

<!-- Custom Body End HTML -->
<script src="https://widget.example.com/chat.js"></script>
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
| Title separator | Character between page title and site name |
| Default locale | Default og:locale (e.g., en_US, ja_JP) |
| Default OG image | Fallback image for social sharing (1200x630) |
| Favicon (SVG) | SVG favicon for modern browsers (recommended) |
| Favicon (PNG) | PNG fallback, minimum 48x48 (Google requirement) |
| Apple Touch Icon | iOS home screen icon (180x180) |
| GTM Container ID | Google Tag Manager (GTM-XXXXXX) |
| robots.txt content | Custom robots.txt content |
| Custom head HTML | Custom HTML for `<head>` section |
| Custom body end HTML | Custom HTML before `</body>` (chat widgets, etc.) |

### Django Settings (Optional)

```python
# settings.py
WAGTAIL_HERALD = {
    # Default robots meta (can be overridden per-page)
    'DEFAULT_ROBOTS': 'index, follow',

    # OG image rendition filter (1200x630 is optimal for social sharing)
    'OG_IMAGE_FILTER': 'fill-1200x630',

    # Favicon rendition filter (48x48 minimum recommended by Google)
    'FAVICON_FILTER': 'fill-48x48',
}
```

## Locale Support

wagtail-herald provides per-page language and region targeting for mixed-language content.

### Use Case: Mixed Language Content

Write Japanese and English articles on the same site by selecting locale per page:

```html
{% load wagtail_herald %}
<!DOCTYPE html>
<html lang="{% page_lang %}">
<head>
    {% seo_head %}
    <!-- Outputs: <meta property="og:locale" content="ja_JP"> -->
</head>
```

- `{% page_lang %}` - Returns language code (e.g., `ja`, `en`)
- `{% page_locale %}` - Returns full locale (e.g., `ja_JP`, `en_US`)
- `{% seo_head %}` - Automatically includes `og:locale` meta tag

### Available Locales

| Locale | Language |
|--------|----------|
| `ja_JP` | 日本語 (日本) |
| `en_US` | English (US) |
| `en_GB` | English (UK) |
| `zh_CN` | 中文 (简体) |
| `zh_TW` | 中文 (繁體) |
| `ko_KR` | 한국어 |
| `fr_FR` | Français (France) |
| `de_DE` | Deutsch (Deutschland) |
| `es_ES` | Español (España) |
| `pt_BR` | Português (Brasil) |

Set the default locale in **Settings > SEO Settings**, then override per-page using the SEOPageMixin.

## robots.txt Management

Configure robots.txt from Wagtail admin without editing files.

### Setup

Add wagtail-herald URLs to your `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    path('', include('wagtail_herald.urls')),
    # ... other urls
]
```

### Configuration

Go to **Settings > SEO Settings** and edit the robots.txt content:

```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /search/

Sitemap: https://example.com/sitemap.xml
```

If left empty, a sensible default is generated (allow all crawlers, include sitemap URL).

## Requirements

| Python | Django | Wagtail |
|--------|--------|---------|
| 3.10+  | 4.2, 5.1, 5.2 | 6.4, 7.0, 7.2 |

## Documentation

- [Contributing Guide](CONTRIBUTING.md)

## Project Links

- [GitHub Repository](https://github.com/kkm-horikawa/wagtail-herald)
- [Issue Tracker](https://github.com/kkm-horikawa/wagtail-herald/issues)

## Related Projects

- [wagtail-seo](https://github.com/coderedcorp/wagtail-seo) - SEO optimization by CodeRed
- [wagtail-metadata](https://github.com/neon-jungle/wagtail-metadata) - Meta tags by Neon Jungle
- [wagtail-schema.org](https://github.com/neon-jungle/wagtail-schema.org) - Schema.org by Neon Jungle

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

BSD 3-Clause License. See [LICENSE](LICENSE) for details.
