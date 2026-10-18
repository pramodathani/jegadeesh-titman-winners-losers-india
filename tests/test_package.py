"""Tests that the study's package can be imported."""

import jegadeesh_titman_india


class TestPackage:
    """Checks on the package itself."""

    def test_package_has_docstring(self) -> None:
        """Checks that the package imports and documents itself.

        Args:
            None.

        Returns:
            None.

        Raises:
            AssertionError: When the package has no docstring.
        """
        assert jegadeesh_titman_india.__doc__
