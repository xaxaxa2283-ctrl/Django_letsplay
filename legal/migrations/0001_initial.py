from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ConsentRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("purpose", models.CharField(choices=[("registration", "Регистрация"), ("order", "Оформление заказа"), ("review", "Публикация отзыва")], max_length=32, verbose_name="Цель согласия")),
                ("subject_identifier", models.CharField(blank=True, max_length=254, verbose_name="Идентификатор пользователя")),
                ("policy_version", models.CharField(max_length=32, verbose_name="Версия документов")),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True, verbose_name="IP-адрес")),
                ("user_agent", models.TextField(blank=True, verbose_name="User-Agent")),
                ("accepted_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата согласия")),
            ],
            options={"verbose_name": "Подтверждение согласия", "verbose_name_plural": "Подтверждения согласий", "ordering": ["-accepted_at"]},
        ),
    ]
