"""Pytest configuration and fixtures."""

from hypothesis import settings, Verbosity

# Configure Hypothesis defaults
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("ci", max_examples=1000, verbosity=Verbosity.verbose)
settings.register_profile("dev", max_examples=10, verbosity=Verbosity.verbose)

# Load the default profile
settings.load_profile("default")
