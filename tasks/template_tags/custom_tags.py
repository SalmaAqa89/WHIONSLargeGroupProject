""" To extend the functionality of the template tags: 
    Map the field names to the custom tags
    Add the custom tags to the template"""

from django import template

FIELD_CLASS_MAPPING = {
    #'preferred_days_to_journal': 'special-style',
    # Add more field-class mappings as needed
}

register = template.Library()

@register.filter(name='custom_render_field')
def custom_render_field(field, additional_class=''):
    """Finds the field name in the FIELD_CLASS_MAPPING and adds the mapped class name to the field widget."""

    field_name = field.name
    mapped_class = FIELD_CLASS_MAPPING.get(field_name, '')
    class_name = f'{additional_class} {mapped_class}'.strip()
    return field.as_widget(attrs={'class': f' {class_name}'})

