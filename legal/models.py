from django.db import models


class ConsentRecord(models.Model):
    PURPOSE_CHOICES = [
        ("registration", "Регистрация"),
        ("order", "Оформление заказа"),
        ("review", "Публикация отзыва"),
    ]

    purpose = models.CharField("Цель согласия", max_length=32, choices=PURPOSE_CHOICES)
    subject_identifier = models.CharField("Идентификатор пользователя", max_length=254, blank=True)
    policy_version = models.CharField("Версия документов", max_length=32)
    ip_address = models.GenericIPAddressField("IP-адрес", null=True, blank=True)
    user_agent = models.TextField("User-Agent", blank=True)
    accepted_at = models.DateTimeField("Дата согласия", auto_now_add=True)

    class Meta:
        verbose_name = "Подтверждение согласия"
        verbose_name_plural = "Подтверждения согласий"
        ordering = ["-accepted_at"]

    def __str__(self):
        return f"{self.get_purpose_display()} — {self.accepted_at:%d.%m.%Y %H:%M}"
