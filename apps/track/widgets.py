from django.forms.widgets import TextInput


class TextListInput(TextInput):
    template_name = "django/forms/widgets/text-list.html"

    def get_context(self, name, value, attrs):
        attrs["list"] = f"datalist-{attrs['id']}"
        attrs["autocomplete"] = "off"
        context = super().get_context(name, value, attrs)
        context["widget"]["data_list"] = context["widget"]["attrs"].pop("data_list")
        return context
