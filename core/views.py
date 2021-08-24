from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.views.generic.detail import DetailView
from core.models import Item
from django.views.generic import ListView, View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from core.forms import CheckkOutForm, CouponForm
from core.services.db_services import (
    get_order_objects,
    filter_order_item_objects_by_slag,
    filter_order_objects,
    filter_order_item_objects,
    remove_item_from_orders,
    delete_item_from_order_items,
    get_all_objects_from_order_items,
    delete_order,
    check_item_order_quantity,
    get_coupon,
    add_and_save_coupon_to_the_order,
    check_user_for_active_coupon,
    filtering_items_by_caegories,
    filtering_items_by_icontains_filter,
    filter_and_check_default_adress,
    get_order_item_or_create,
    add_item_to_the_order,
    create_order_object,
    change_order_quantity,
)
from core.services.business_logic import (
    default_shipping_adress,
    the_same_billing_logic,
    disabled_billing_and_default_logic,
    create_delivered_object_item,
    delete_order_and_order_items,
)


class HomeView(ListView):
    """Home page view"""

    model = Item
    paginate_by = 8
    template_name = "home-page.html"
    context_object_name = "items"


class ItemDetailView(DetailView):
    """Items detail view"""

    model = Item
    template_name = "product-page.html"


class OrderSummaryView(LoginRequiredMixin, View):
    """Order summary view"""

    def get(self, *args, **kwargs):
        """Try to get Order Items"""
        try:
            order_items = get_order_objects(user=self.request.user, ordered=False)
            context = {"objects": order_items}
            return render(self.request, "order-summary.html", context=context)
        except ObjectDoesNotExist:
            messages.info(self.request, "Your shopping cart is empty")
            return redirect("/")


class AddCouponView(View):
    """Add coupon to user"""

    def post(self, *args, **kwargs):
        """Validate coupon code from user and add to account if valid"""
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            code = form.cleaned_data.get("code")
            order = get_order_objects(user=self.request.user, ordered=False)
            if check_user_for_active_coupon(order=order):
                messages.warning(self.request, "You can not use one coupon two times")
                return redirect("core:checkout")
            if get_coupon(code):
                add_and_save_coupon_to_the_order(order=order, code=code)
                messages.success(
                    self.request, "This coupon was successfully added to your order"
                )
                return redirect("core:checkout")
            messages.warning(self.request, "Coupon validation error")
            return redirect("core:checkout")
        messages.info(self.request, "You do not have an active order")
        return redirect("core:checkout")


class RomanceView(View):
    """Filtered Item view by category - romance"""

    def get(self, *args, **kwargs):
        """Get items in category R(Romance)"""
        romance_items = filtering_items_by_caegories(category="R")
        context = {"items": romance_items}
        return render(self.request, "home-page.html", context=context)


class EducationReferenceView(View):
    """Filtered Item view by category - education and reference"""

    def get(self, *args, **kwargs):
        """Get items in category E(Education & Reference)"""
        education_reference_items = filtering_items_by_caegories(category="E")
        context = {"items": education_reference_items}
        return render(self.request, "home-page.html", context=context)


class BusinessInvestingView(View):
    """Filtered Item view by category - inversting"""

    def get(self, *args, **kwargs):
        """Get items in category B(Business & Investing)"""
        business_investing_items = filtering_items_by_caegories(category="B")
        context = {"items": business_investing_items}
        return render(self.request, "home-page.html", context=context)


class SearchResult(ListView):
    """Search items in Item model"""

    model = Item
    template_name = "home-page.html"
    context_object_name = "items"

    def get_queryset(self):
        """Filtering items by params"""
        query = self.request.GET.get("q")
        items = filtering_items_by_icontains_filter(query=query)
        return items


class CheckoutView(LoginRequiredMixin, View):
    """Checkout view"""

    def get(self, *args, **kwargs):
        """Add default adress to checkout view if exists"""
        try:
            order_queryset = get_order_objects(user=self.request.user, ordered=False)
            context = {
                "form": CheckkOutForm(),
                "couponform": CouponForm(),
                "order": order_queryset,
            }
            shipping_address_queryset = filter_and_check_default_adress(
                user=self.request.user,
                adress_type="S",
            )
            if shipping_address_queryset:
                context.update({"default_shipping_address": shipping_address_queryset})

            billing_address_queryset = filter_and_check_default_adress(
                user=self.request.user,
                adress_type="B",
            )
            if billing_address_queryset:
                context.update({"default_billing_address": billing_address_queryset})

            return render(self.request, "checkout-page.html", context=context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("/")

    def post(self, *args, **kwargs):
        """The whole logic of validate Checkout form"""
        order = get_order_objects(user=self.request.user, ordered=False)
        form = CheckkOutForm(self.request.POST or None)
        if form.is_valid():
            shipping_address1 = form.cleaned_data.get("shipping_address")
            shipping_address2 = form.cleaned_data.get("shipping_address")
            shipping_country = form.cleaned_data.get("shipping_country")
            shipping_zip = form.cleaned_data.get("shipping_zip")

            billing_address1 = form.cleaned_data.get("billing_address")
            billing_address2 = form.cleaned_data.get("billing_address2")
            billing_country = form.cleaned_data.get("billing_country")
            billing_zip = form.cleaned_data.get("billing_zip")

            same_billing_address = form.cleaned_data.get("same_billing_address")
            set_default_shipping = form.cleaned_data.get("set_default_shipping")
            use_default_shipping = form.cleaned_data.get("use_default_shipping")
            set_default_billing = form.cleaned_data.get("set_default_billing")
            use_default_billing = form.cleaned_data.get("use_default_billing")

            if same_billing_address and use_default_billing:
                messages.info(
                    self.request,
                    "You can not use 2 options at the same time <It is brake the logic>",
                )
                return redirect("core:checkout")

            shipping_adress_or_error = default_shipping_adress(
                user=self.request.user,
                order=order,
                use_default_shipping=use_default_shipping,
                set_default_shipping=set_default_shipping,
                shipping_address1=shipping_address1,
                shipping_address2=shipping_address2,
                shipping_country=shipping_country,
                shipping_zip=shipping_zip,
                adress_type="S",
            )

            the_same_billing_logic(
                user=self.request.user,
                order=order,
                same_billing_address=same_billing_address,
                use_default_shipping=use_default_shipping,
                billing_adress1=billing_address1,
                shipping_address1=shipping_address1,
                shipping_address2=shipping_address2,
                shipping_country=shipping_country,
                shipping_zip=shipping_zip,
                set_default_billing=set_default_billing,
            )

            billing_adress_or_error = disabled_billing_and_default_logic(
                user=self.request.user,
                order=order,
                same_billing_address=same_billing_address,
                use_default_billing=use_default_billing,
                set_default_billing=set_default_billing,
                billing_address1=billing_address1,
                billing_address2=billing_address2,
                billing_country=billing_country,
                billing_zip=billing_zip,
                adress_type="B",
            )

            if (
                billing_adress_or_error == "Please fill in all required fields"
                or shipping_adress_or_error == "Please fill in all required fields"
            ):
                messages.info(self.request, "Please fill in all required fields")
                return redirect("core:checkout")

            create_delivered_object_item(user=self.request.user)
            deleting_operation = delete_order_and_order_items(user=self.request.user)
            if deleting_operation:
                messages.info(self.request, "The order has been send")
                return redirect("core:home")
        messages.warning(self.request, "Failed Checkout")
        return redirect("core:checkout")


@login_required
def add_to_cart(request, slug):
    """
    Functionality to add item to the cart
    Or change quantity if item exists
    """
    order_item = get_order_item_or_create(user=request.user, slug=slug)
    order = filter_order_objects(user=request.user, ordered=False)
    if order:
        if filter_order_item_objects_by_slag(
            user=request.user, slug=slug, order_quaryset=order, ordered=False
        ):
            change_order_quantity(order_item=order_item)
            messages.info(request, "This item quantity was updated")
            return redirect("core:order-summary")
        add_item_to_the_order(order=order, order_item=order_item)
        messages.info(request, "This item was aded tou your cart")
        return redirect("core:order-summary")
    order = create_order_object(user=request.user)
    add_item_to_the_order(order=order, order_item=order_item)
    messages.info(request, "This item was aded tou your cart")
    return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    """
    Remove items from cart if quantity more than 1
    Trash icon
    """
    filtered_order_objects = filter_order_objects(user=request.user, ordered=False)

    if filtered_order_objects:
        filtered_order_items_by_slag = filter_order_item_objects_by_slag(
            user=request.user,
            slug=slug,
            order_quaryset=filtered_order_objects,
            ordered=False,
        )
        if filtered_order_items_by_slag:
            remove_item_from_orders(user=request.user, slug=slug, ordered=False)
            delete_item_from_order_items(user=request.user, slug=slug, ordered=False)
            all_orders = get_all_objects_from_order_items()
            if all_orders.count() == 0:
                delete_order(user=request.user, ordered=False)
                messages.info(request, "You successfully delete all items from your cart")
                return redirect("core:home")
            messages.info(request, "This item was removed from your cart")
            return redirect("core:order-summary")
        messages.info(request, "This item was not in your cart")
        return redirect("core:order-summary", slug=slug)
    messages.info(request, "You do not have an active order yet")
    return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    """Remove single item from cart"""
    filtered_order_objects = filter_order_objects(user=request.user, ordered=False)
    if filtered_order_objects:
        filtered_order_items_by_slag = filter_order_item_objects_by_slag(
            user=request.user,
            slug=slug,
            order_quaryset=filtered_order_objects,
            ordered=False,
        )
        if filtered_order_items_by_slag:
            order_item = filter_order_item_objects(
                user=request.user, slug=slug, ordered=False
            )
            check_item_order_quantity(item=order_item)
            all_orders = get_all_objects_from_order_items()
            if all_orders.count() == 0:
                delete_order(user=request.user, ordered=False)
                messages.info(request, "You successfully delete all items from your cart")
                return redirect("core:home")
            messages.info(request, "This item quantity has been changed")
            return redirect("core:order-summary")
        messages.info(request, "This item was not in your cart")
        return redirect("core:product", slug=slug)
    messages.info(request, "You do not have an active order yet")
    return redirect("core:product", slug=slug)
