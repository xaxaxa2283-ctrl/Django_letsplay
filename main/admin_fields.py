"""Human-readable editors backed by the existing JSON columns."""
import json
from django import forms
from django.utils.html import format_html, format_html_join


class CategoryTypeSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if hasattr(value, 'instance'):
            option['attrs']['data-category-type'] = value.instance.category_type
        return option


class FeatureLinesField(forms.Field):
    widget = forms.Textarea(attrs={'rows': 5, 'cols': 60})

    def prepare_value(self, value):
        if isinstance(value, list) and all(isinstance(item, str) and '\n' not in item and '\r' not in item for item in value):
            return '\n'.join(value)
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False)
        return value or ''

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, str) and value.lstrip().startswith(('[', '{')):
            try:
                value = json.loads(value)
            except ValueError:
                raise forms.ValidationError('Не удалось прочитать прежние данные. Укажите каждую особенность отдельной строкой.')
        if isinstance(value, dict):
            raise forms.ValidationError('Нестандартные данные особенностей. Исправьте их до сохранения.')
        if isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                raise forms.ValidationError('Особенности должны быть текстовыми строками.')
            return value
        return [line.strip() for line in value.splitlines() if line.strip()]


class SpecificationWidget(forms.Widget):
    class Media:
        js = ('admin/js/product_fields.js',)
        css = {'all': ('admin/css/product_fields.css',)}

    def value_from_datadict(self, data, files, name):
        if name + '_rows' not in data:
            return data.get(name, '')  # Existing API/admin clients may still post JSON.
        labels = data.getlist(name + '_label')
        values = data.getlist(name + '_value')
        if len(labels) != len(values):
            return '__invalid_rows__'
        return [{'label': label, 'value': value} for label, value in zip(labels, values)]

    def render(self, name, value, attrs=None, renderer=None):
        if isinstance(value, str):
            try:
                value = json.loads(value) if value else []
            except ValueError:
                return forms.Textarea().render(name, value, attrs)
        if value is None:
            value = []
        if not isinstance(value, list) or any(not isinstance(row, dict) or set(row) != {'label', 'value'} or not all(isinstance(v, str) for v in row.values()) for row in value):
            return format_html('<p>Сохранённые данные имеют нестандартный формат. Проверьте их перед изменением.</p>{}', forms.Textarea().render(name, json.dumps(value, ensure_ascii=False), attrs))
        rows = value or [{'label': '', 'value': ''}]
        content = format_html_join('', '<div class="lp-spec-row"><input name="{}_label" value="{}" aria-label="Название характеристики" placeholder="Например, память"><input name="{}_value" value="{}" aria-label="Значение характеристики" placeholder="Например, 1 ТБ"><button type="button" class="lp-spec-remove" aria-label="Удалить характеристику" hidden>Удалить</button></div>', ((name, row['label'], name, row['value']) for row in rows))
        return format_html('<div class="lp-spec-editor" data-field="{}"><input type="hidden" name="{}_rows" value="1"><div class="lp-spec-head">Название — значение</div><div class="lp-spec-rows">{}</div><button type="button" class="lp-spec-add" hidden>Добавить характеристику</button><noscript>Для добавления строк включите JavaScript; существующие строки можно редактировать и без него.</noscript></div>', name, name, content)


class SpecificationField(forms.Field):
    widget = SpecificationWidget

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                raise forms.ValidationError('Проверьте название и значение каждой характеристики.')
        if not isinstance(value, list):
            raise forms.ValidationError('Характеристики должны быть списком пар «Название — значение».')
        result = []
        for row in value:
            if not isinstance(row, dict) or set(row) != {'label', 'value'} or not all(isinstance(v, str) for v in row.values()):
                raise forms.ValidationError('Нестандартная структура характеристики. Данные не сохранены, чтобы не потерять дополнительные поля.')
            if not row['label'].strip() and not row['value'].strip():
                continue
            if not row['label'].strip() or not row['value'].strip():
                raise forms.ValidationError('Заполните и название, и значение характеристики либо удалите строку.')
            result.append(row)
        return result
