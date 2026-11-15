from django.test import SimpleTestCase
from django.http import QueryDict
from django import forms
from .admin_fields import FeatureLinesField, SpecificationField, SpecificationWidget
from django.test import TestCase
from django.forms.models import model_to_dict
from .admin import ProductAdminForm
from .models import Category, Product

class ProductEditorTests(SimpleTestCase):
    def test_features_round_trip_and_lines(self):
        field=FeatureLinesField(required=False)
        for value in [['HDR', 'Два контроллера'], ['Несколько\nстрок'], []]:
            self.assertEqual(field.clean(field.prepare_value(value)),value)
        self.assertEqual(field.clean('HDR\n\n Второй контроллер '),['HDR','Второй контроллер'])
        with self.assertRaises(forms.ValidationError):field.clean('{"unexpected":1}')

    def test_pairs_round_trip_and_incomplete_rejected(self):
        field=SpecificationField(required=False)
        rows=[{'label':'Память','value':'1 ТБ'}, {'label':'Комплект','value':'Консоль, кабели'}]
        self.assertEqual(field.clean(rows),rows)
        self.assertEqual(field.clean([{'label':'','value':''}]),[])
        for value in [[{'label':'Память','value':''}],[{'label':'X','value':'Y','extra':1}]]:
            with self.assertRaises(forms.ValidationError):field.clean(value)

    def test_widget_reads_pairs_and_escapes_content(self):
        data=QueryDict('',mutable=True)
        data['specifications_rows']='1'
        data.setlist('specifications_label',['Память'])
        data.setlist('specifications_value',['1 ТБ'])
        widget=SpecificationWidget()
        self.assertEqual(widget.value_from_datadict(data,{},'specifications'),[{'label':'Память','value':'1 ТБ'}])
        html=widget.render('specifications',[{'label':'<script>','value':'" onfocus="bad'}])
        self.assertNotIn('<script>',html)
        self.assertIn('&lt;script&gt;',html)

class ProductFormSaveTests(TestCase):
    def test_category_context_and_inapplicable_values(self):
        for kind, platform, condition, firmware, subscription in [
            ('subscriptions','ps5','','','extra'),
            ('accessories','ps4','','',''),
            ('disks','ps4','used','',''),
            ('consoles','ps4','used','modified',''),
            ('consoles','xbox','used','',''),
        ]:
            category=Category.objects.create(name=kind,category_type=kind)
            data={'name':'Test','slug':'test','category':category.pk,'price':'10','rating':'5','variant_order':'0','platform':platform,'condition':'used','firmware_status':'modified','subscription_type':'extra'}
            form=ProductAdminForm(data=data)
            self.assertTrue(form.is_valid(),form.errors)
            self.assertEqual(form.cleaned_data['condition'],condition)
            self.assertEqual(form.cleaned_data['firmware_status'],firmware)
            self.assertEqual(form.cleaned_data['subscription_type'],subscription)
            self.assertIn('data-category-type="'+kind+'"',str(form['category']))

    def test_edit_existing_product_without_json(self):
        category=Category.objects.create(name='Приставки',category_type='consoles')
        product=Product.objects.create(name='Test',slug='test',category=category,price=100,features=['HDR'],specifications=[{'label':'Память','value':'1 ТБ'}])
        data=QueryDict('',mutable=True)
        for key,value in model_to_dict(product).items():
            if value is not None:data[key]=value
        data['features']='HDR\nВторой контроллер'
        data['specifications_rows']='1'
        data.setlist('specifications_label',['Память','Комплект'])
        data.setlist('specifications_value',['1 ТБ','Консоль, кабели'])
        form=ProductAdminForm(data=data,instance=product)
        self.assertTrue(form.is_valid(),form.errors)
        form.save();product.refresh_from_db()
        self.assertEqual(product.features,['HDR','Второй контроллер'])
        self.assertEqual(product.specifications,[{'label':'Память','value':'1 ТБ'},{'label':'Комплект','value':'Консоль, кабели'}])
