from typing import Dict, Optional, Tuple, Union

from django.core.exceptions import ImproperlyConfigured
from rules.contrib.views import PermissionRequiredMixin


class PermissionRequiredMethodMixin(PermissionRequiredMixin):
    permission_required_map: Optional[Dict[str, Union[str, Tuple[str]]]] = None

    def get_permission_required(self):
        if self.permission_required_map is not None:
            if not isinstance(self.permission_required_map, dict):
                name = self.__class__.__name__
                raise ImproperlyConfigured(
                    f"{name} has a wrong permission_required_map attribute. "
                    "It should be a mapping from http method to permission."
                )
            perms = self.permission_required_map.get(self.request.method)  # type: ignore
            if perms is not None:
                return (perms,) if isinstance(perms, str) else perms
        return super().get_permission_required()
