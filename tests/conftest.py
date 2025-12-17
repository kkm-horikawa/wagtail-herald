"""
Pytest configuration and fixtures for wagtail-herald tests.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from wagtail.models import Page, Site

User = get_user_model()


@pytest.fixture
def rf():
    """Provide Django's RequestFactory."""
    return RequestFactory()


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="password",
    )


@pytest.fixture
def regular_user(db):
    """Create a regular user for testing."""
    return User.objects.create_user(
        username="user",
        email="user@example.com",
        password="password",
    )


@pytest.fixture
def root_page(db):
    """Get or create the root page."""
    try:
        return Page.objects.get(depth=1)
    except Page.DoesNotExist:
        return Page.add_root(title="Root", slug="root")


@pytest.fixture
def site(db, root_page):
    """Get or create the default site."""
    site, created = Site.objects.get_or_create(
        hostname="localhost",
        defaults={
            "root_page": root_page,
            "is_default_site": True,
            "site_name": "Test Site",
        },
    )
    # Ensure site_name is set even if site already existed
    if site.site_name != "Test Site":
        site.site_name = "Test Site"
        site.save()
    return site
