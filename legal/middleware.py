import json
import logging
import re

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect

from .models import ConsentRecord
from .views import DOCUMENT_VERSION

logger = logging.getLogger(__name__)

CONSENT_PURPOSES = {
    "/checkout": "order",
    "/register": "registration",
    "/api/register": "registration",
    "/submit-review": "review",
}

CONSENT_HTML = """
<div class="legal-consent" style="margin:1rem 0;padding:1rem;border:1px solid rgba(255,255,255,.2);border-radius:.75rem;color:#e2e8f0;background:rgba(255,255,255,.06)">
  <label style="display:flex;gap:.65rem;align-items:flex-start;cursor:pointer">
    <input type="checkbox" name="personal_data_consent" value="yes" required style="margin-top:.3rem;width:1.1rem;height:1.1rem">
    <span>Я даю отдельное <a href="/legal/consent/" target="_blank" style="color:#67e8f9;text-decoration:underline">согласие на обработку персональных данных</a> и ознакомлен(а) с <a href="/legal/privacy/" target="_blank" style="color:#67e8f9;text-decoration:underline">политикой обработки данных</a>.</span>
  </label>
</div>
"""

ORDER_EXTRA_HTML = """
<p style="margin:.5rem 0 1rem;color:#cbd5e1;font-size:.9rem">Нажимая кнопку оформления заказа, вы принимаете <a href="/legal/offer/" target="_blank" style="color:#67e8f9;text-decoration:underline">публичную оферту</a> и условия <a href="/legal/returns/" target="_blank" style="color:#67e8f9;text-decoration:underline">возврата</a>.</p>
"""

REGISTER_FETCH_PATCH = """
<script>
(function () {
  const originalFetch = window.fetch;
  window.fetch = function (input, init) {
    const url = typeof input === 'string' ? input : (input && input.url) || '';
    if (url.indexOf('/api/register/') !== -1 && init && init.body) {
      try {
        const payload = JSON.parse(init.body);
        const checkbox = document.querySelector('#register-form [name="personal_data_consent"]');
        payload.personal_data_consent = Boolean(checkbox && checkbox.checked);
        init.body = JSON.stringify(payload);
      } catch (error) {}
    }
    return originalFetch.call(this, input, init);
  };
})();
</script>
"""

LEGAL_FOOTER = """
<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:.8rem;padding:1rem;color:#cbd5e1;font-size:.85rem">
  <a href="/legal/privacy/">Персональные данные</a><a href="/legal/consent/">Согласие</a><a href="/legal/offer/">Оферта</a><a href="/legal/returns/">Возврат</a><a href="/legal/requisites/">Реквизиты</a><a href="/legal/cookies/">Cookies</a>
  <button type="button" onclick="document.cookie='analytics_consent=; Max-Age=0; Path=/; SameSite=Lax';location.reload()" style="border:0;background:none;color:#67e8f9;text-decoration:underline;cursor:pointer">Настройки cookies</button>
</div>
"""

COOKIE_BANNER = """
<div id="legal-cookie-banner" style="position:fixed;left:1rem;right:1rem;bottom:1rem;z-index:10000;max-width:760px;margin:auto;padding:1rem 1.2rem;border:1px solid rgba(255,255,255,.25);border-radius:1rem;background:#0f172a;color:#e2e8f0;box-shadow:0 15px 50px rgba(0,0,0,.55)">
  <div style="margin-bottom:.75rem">Сайт использует обязательные cookies. Яндекс.Метрика будет подключена только с вашего разрешения. <a href="/legal/cookies/" target="_blank" style="color:#67e8f9;text-decoration:underline">Подробнее</a></div>
  <div style="display:flex;flex-wrap:wrap;gap:.6rem">
    <button type="button" onclick="legalCookieChoice('granted')" style="padding:.55rem 1rem;border:0;border-radius:.7rem;background:#06b6d4;color:white;cursor:pointer">Разрешить аналитику</button>
    <button type="button" onclick="legalCookieChoice('denied')" style="padding:.55rem 1rem;border:1px solid #64748b;border-radius:.7rem;background:transparent;color:white;cursor:pointer">Только обязательные</button>
  </div>
</div>
<script>
function legalCookieChoice(value) {
  document.cookie = 'analytics_consent=' + value + '; Max-Age=31536000; Path=/; SameSite=Lax';
  location.reload();
}
</script>
"""


class LegalComplianceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        purpose = CONSENT_PURPOSES.get(request.path.rstrip("/"))
        accepted = False
        payload = {}

        if request.method == "POST" and purpose:
            accepted, payload = self._read_consent(request)
            if not accepted:
                if request.path.rstrip("/") == "/api/register":
                    return JsonResponse({"success": False, "error": "personal_data_consent_required"}, status=400)
                messages.error(request, "Для отправки формы необходимо отдельно подтвердить согласие на обработку персональных данных.")
                return redirect(request.path)

        response = self.get_response(request)

        if accepted and response.status_code < 400:
            self._record_consent(request, purpose, payload)

        content_type = response.get("Content-Type", "")
        if response.status_code == 200 and "text/html" in content_type and not getattr(response, "streaming", False):
            response.content = self._modify_html(request, response.content.decode(response.charset)).encode(response.charset)
            response["Content-Length"] = str(len(response.content))

        return response

    @staticmethod
    def _read_consent(request):
        if request.path.rstrip("/") == "/api/register":
            try:
                payload = json.loads(request.body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                payload = {}
            return payload.get("personal_data_consent") is True, payload
        return request.POST.get("personal_data_consent") == "yes", request.POST

    @staticmethod
    def _record_consent(request, purpose, payload):
        identifier = ""
        if request.user.is_authenticated:
            identifier = request.user.get_username()
        if not identifier:
            for key in ("email", "phone", "username", "name"):
                value = payload.get(key) if hasattr(payload, "get") else None
                if value:
                    identifier = str(value)[:254]
                    break
        try:
            ConsentRecord.objects.create(
                purpose=purpose,
                subject_identifier=identifier,
                policy_version=DOCUMENT_VERSION,
                ip_address=request.META.get("REMOTE_ADDR") or None,
                user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:1000],
            )
        except Exception:
            logger.exception("Could not record personal data consent")

    def _modify_html(self, request, html):
        path = request.path.rstrip("/")
        if path in {"/checkout", "/register", "/submit-review"}:
            addition = CONSENT_HTML + (ORDER_EXTRA_HTML if path == "/checkout" else "")
            html = self._insert_before_form_end(html, html.find("<form"), addition)
        elif path == "/auth":
            start = html.find('<form id="register-form"')
            html = self._insert_before_form_end(html, start, CONSENT_HTML)
            html = html.replace("</body>", REGISTER_FETCH_PATCH + "</body>", 1)

        if request.COOKIES.get("analytics_consent") != "granted":
            html = re.sub(r"<!-- Yandex\.Metrika counter -->.*?<!-- /Yandex\.Metrika counter -->", "", html, flags=re.DOTALL)

        if "</footer>" in html and LEGAL_FOOTER not in html:
            html = html.replace("</footer>", LEGAL_FOOTER + "</footer>", 1)

        if not request.COOKIES.get("analytics_consent"):
            html = html.replace("</body>", COOKIE_BANNER + "</body>", 1)
        return html

    @staticmethod
    def _insert_before_form_end(html, start, addition):
        if start < 0:
            return html
        end = html.find("</form>", start)
        if end < 0:
            return html
        return html[:end] + addition + html[end:]
