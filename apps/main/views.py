from typing import Dict, Union, Tuple

from django.core.exceptions import ImproperlyConfigured
from django.views import generic
from rules.contrib.views import PermissionRequiredMixin


class PermissionRequiredMethodMixin(PermissionRequiredMixin):
    permission_required_map: Dict[str, Union[str, Tuple[str]]] = None

    def get_permission_required(self):
        if self.permission_required_map is not None:
            if not isinstance(self.permission_required_map, dict):
                raise ImproperlyConfigured(
                    f"{self.__class__.__name__} has a wrong permission_required_map attribute. "
                    "It should be a mapping from http method to permission."
                )
            perms = self.permission_required_map.get(self.request.method)
            if perms is not None:
                return (perms,) if isinstance(perms, str) else perms
        return super().get_permission_required()


class IndexView(generic.TemplateView):
    template_name = "index.html"
