import datetime, environ, stripe
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from ..forms import SignUpForm
from ..mixins import OnlyMyUserInformationMixin, OnlyPayingMemberMixin
from ..models import User, UserActivateTokens, Subscription

env = environ.Env()
ip_port = env('IP_PORT')
login_url = f'{ip_port}/login/'

class LoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'login.html'
    
def logout_view(request):
    logout(request)
    return redirect('top')

class SignupFormView(FormView):
    form_class = SignUpForm
    template_name = "signup_form.html"
    
    def form_valid(self, form):
        context = {
            'form': form,
            'kwargs': self.kwargs,
        }
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return render(self.request, 'signup_form.html', context)

class SignupConfirmView(FormView):
    form_class = SignUpForm
    
    def form_valid(self, form):
        passlength = len(form.cleaned_data.get("password1"))
        password = "･" * passlength
        context = {
            'form': form,
            'kwargs': self.kwargs,
            'password': password,
        }
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return render(self.request, 'signup.html', context)
    
    def form_invalid(self, form):
        context = {
            'form': form,
            'kwargs': self.kwargs,
        }
        return render(self.request, 'signup_form.html', context)

class SignupView(CreateView):
    form_class = SignUpForm
    template_name = "signup.html"
    success_url = reverse_lazy('usercreated')

class UserCreatedView(TemplateView):
    template_name = 'user_created.html'
    
    # user_created.htmlに変数を書き出し
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['register_URL'] = f'http://{ip_port}/users/{UserActivateTokens.activate_token}/activation/'
        return context

def activate_user(request, activate_token):
    activated_user = UserActivateTokens.objects.activate_user_by_token(activate_token)
    if hasattr(activated_user, 'is_active'):
        if activated_user.is_active:
            activated_user.register_time = datetime.datetime.now()
            activated_user.save()
            message = f'本登録が完了しました！<br><a href={login_url}>ログインページ</a>'
        if not activated_user.is_active:
            message = '本登録に失敗しました。'
    if not hasattr(activated_user, 'is_active'):
        message = 'エラーが発生しました'
    return HttpResponse(message)

class PasswordReset(PasswordResetView):
    # パスワード変更URL付きメールのカスタマイズ
    subject_template_name = 'mail/subject.txt'
    email_template_name = "mail/message.txt"
    template_name = "password_reset.html"
    # パスワードリセット用URLの送信ページ
    success_url = reverse_lazy("passwordresetdone")

class PasswordResetDone(PasswordResetDoneView):
    # パスワード変更用URL送信完了ページ
    template_name = "password_reset_done.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["domain"] = ip_port
        return context

class PasswordResetConfirm(PasswordResetConfirmView):
    # 新パスワード入力用ページ
    success_url = reverse_lazy("passwordresetcomplete")
    template_name = "password_reset_confirm.html"


class PasswordResetComplete(PasswordResetCompleteView):
    # 新パスワード設定完了ページ
    template_name = "password_reset_complete.html"

class PasswordChange(PasswordChangeView):
    # パスワード変更ページ
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'password_change.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.user.pk
        form = context['form']
        for v in form.fields.values():
            v.label_suffix = ""
        return context

class PasswordChangeDone(PasswordChangeDoneView):
    # パスワード変更完了ページ
    template_name = 'password_change_done.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.request.user.pk
        return context

class UpgradeGuideView(LoginRequiredMixin, TemplateView):
    template_name = "upgrade_guide.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lookup_key"] = env("STRIPE_LOOKUP_KEY")
        return context

def create_checkout_session(request):
    DOMAIN = ip_port
    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id = request.user.pk,
            line_items=[
                {
                    'price': env("STRIPE_PRICE_ID"),
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url = DOMAIN + '/success/',
            cancel_url = DOMAIN + '/cancel/',
        )
        return redirect(checkout_session.url)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

def cancel_subscription(request):
    user = request.user
    subscription = Subscription.objects.filter(cancel_time = None).get(user__pk = user.pk)
    stripe_subscription_id = subscription.stripe_subscription_id
    try:
        stripe.Subscription.delete(stripe_subscription_id)
        return redirect('subscriptionresigndone')
    except stripe.error.StripeError as e:
        # Stripe APIでエラーが発生した場合
        return HttpResponse(f"Error cancelling subscription: {str(e)}", status=500)

@csrf_exempt
def webhook_received(request):
    endpoint_secret = env("STRIPE_WEBHOOK_SECRET")
    payload = request.body.decode('utf-8')
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponse(status=400) # Invalid payload
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400) # Invalid signature
    event_type = event['type']
    if event_type == 'checkout.session.completed':
        # チェックアウト成功時のアクション
        session = event['data']['object']
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get('subscription')
        try:
            user = User.objects.get(pk = client_reference_id)
            user.is_subscribed = True
            user.save()
            subscription = Subscription.objects.create(
                user = user,
                stripe_customer_id = stripe_customer_id,
                stripe_subscription_id = stripe_subscription_id,
            )
            subscription.save()
        except Exception as e:
            return HttpResponse(f"Error creating profile: {str(e)}", status=500)
        print('支払いが完了しました！')
    elif event_type == 'customer.subscription.created':
        print('有料会員登録が開始されました。', event.id)
    elif event_type == 'customer.subscription.deleted':
        session = event['data']['object']
        stripe_customer_id = session.get('customer')  # stripe_customer_idを取得
        stripe_subscription_id = session.get('id')
        try:
            subscription = Subscription.objects.get(stripe_subscription_id = stripe_subscription_id)
            user = subscription.user
            # ユーザーとサブスクリプション情報を更新
            user.is_subscribed = False
            user.save()
            subscription.cancel_time = datetime.datetime.now()
            registration_date = subscription.registration_date
            i = 1
            while date.today() > (registration_date + relativedelta(months = 1) * i):
                i += 1
            cancel_date = registration_date + relativedelta(months = 1) * i
            subscription.lapse_date = cancel_date
            subscription.save()
            print('有料会員登録を解約しました。', event.id)
        except Subscription.DoesNotExist:
            return HttpResponse("Subscription not found", status=404)
    return HttpResponse(status=200)

class SuccessView(TemplateView):
    template_name = "success.html"
    
class CancelView(LoginRequiredMixin, TemplateView):
    template_name = "cancel.html"

def create_customer_portal_session(request):
    user = request.user
    try:
        # ユーザーのStripeカスタマーIDを取得
        subscription = Subscription.objects.get(user = user, cancel_time = None)
        stripe_customer_id = subscription.stripe_customer_id
        
        # カスタマーポータルセッションを作成
        session = stripe.billing_portal.Session.create(
            customer = stripe_customer_id,
            return_url = "https://nagoyameshi.omochi-mochimental.net/subscription/" # ポータルから戻る際のURL
        )
        # 作成したポータルのURLにリダイレクト
        return redirect(session.url)
    except Subscription.DoesNotExist:
        return HttpResponse("No active subscription found.", status=400)
    except stripe.error.StripeError as e:
        return HttpResponse(f"Error creating customer portal session: {str(e)}", status=500)

class SubscriptionView(OnlyPayingMemberMixin, TemplateView):
    template_name = "subscription.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_cancelled = False
        subscriptions = Subscription.objects.filter(user = user)
        for lapse_date in subscriptions.values_list("lapse_date", flat=True):
            if lapse_date == None:
                is_subscribed = True
                break
            elif lapse_date > date.today():
                context["expired_date"] = lapse_date - relativedelta(days = 1)
                is_subscribed = True
                is_cancelled = True
                break
        context["is_subscribed"] = is_subscribed
        context["is_cancelled"] = is_cancelled
        return context

class SubscriptionResignConfirmView(OnlyPayingMemberMixin, TemplateView):
    template_name = "subscription_resign_confirm.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        registration_date = Subscription.objects.get(user = self.request.user, cancel_time = None).registration_date
        i = 1
        while date.today() > (registration_date + relativedelta(months = 1) * i):
            i += 1
        cancel_date = registration_date + relativedelta(months = 1) * i - relativedelta(days = 1)
        context["cancel_date"] = cancel_date
        return context
    
class SubscriptionResignDoneView(LoginRequiredMixin, TemplateView):
    template_name = "subscription_resign_done.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        subscriptions = Subscription.objects.filter(user = user)
        for lapse_date in subscriptions.values_list("lapse_date", flat=True):
            if lapse_date and lapse_date > date.today():
                context["expired_date"] = lapse_date - relativedelta(days = 1)
                break
        return context

class ResignView(OnlyMyUserInformationMixin, UpdateView):
    model = User
    template_name = "resign.html"
    success_url = reverse_lazy("resigndone")
    fields = ("is_active",)
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.resign_time = datetime.datetime.now()
        user.save()
        return super().form_valid(form)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ResignDoneView(TemplateView):
    model = User
    template_name = "resign_done.html"
