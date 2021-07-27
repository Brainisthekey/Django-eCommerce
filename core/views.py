from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.detail import DetailView
from core.models import Item, OrderItem, Order, Adress, Coupon, OrderDevilevered
from django.views.generic import ListView, View
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from core.forms import CheckkOutForm, CouponForm
from django.db.models import Q
from core.services.db_services import get_order_objects, filter_order_item_objects_by_slag, filter_order_objects, filter_order_item_objects, remove_item_from_orders, delete_item_from_order_items, get_all_objects_from_order_items, delete_order, check_item_order_quantity, get_coupon, add_and_save_coupon_to_the_order, check_user_for_active_coupon, filtering_items_by_caegories, filtering_items_by_icontains_filter, filter_and_check_default_adress, add_shipping_adress_to_the_order, create_a_new_address, change_status_default_address, change_pk_of_address, change_address_type_for_billing, add_billing_address_to_the_order, create_a_new_devilered_order_object, delete_all_items_from_order, check_adress_by_street_adress
from core.services.form_services import get_coupon_form_and_validate, get_code_from_from, validate_from_for_whitespaces
from core.services.business_logic import get_information_about_order, convert_order_items_into_string_view, default_shipping_adress


class HomeView(ListView):
    
    model = Item
    paginate_by = 8
    template_name = 'home-page.html'
    context_object_name = 'items'


class ItemDetailView(DetailView):

    model = Item
    template_name = 'product-page.html'


class OrderSummaryView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        try:
            order_items = get_order_objects(user=self.request.user, ordered=False)
            context = {'objects': order_items}
            return render(self.request, 'order-summary.html', context=context)
        except ObjectDoesNotExist:
            messages.info(self.request, 'Your shopping cart is empty')
            return redirect("/")

class AddCouponView(View):

    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = get_code_from_from(form)
                order = get_order_objects(user=self.request.user, ordered=False)
                if check_user_for_active_coupon(order=order):
                    messages.warning(self.request, 'You can not use one coupon two times')
                    return redirect("core:checkout")
                if get_coupon(self.request, code):
                    add_and_save_coupon_to_the_order(
                        order=order,
                        request=self.request,
                        code=code
                    )
                    messages.success(self.request, "This coupon was successfully added to your order")
                    return redirect("core:checkout")
                messages.warning(self.request, 'Coupon validation error')
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")

class RomanceView(View):

    def get(self, *args, **kwargs):

        romance_items = filtering_items_by_caegories(category='R')
        context = {'items': romance_items}
        return render(self.request, 'home-page.html', context=context)

class EducationReferenceView(View):

    def get(self, *args, **kwargs):

        education_reference_items = filtering_items_by_caegories(category='E')
        context = {'items': education_reference_items}
        return render(self.request, 'home-page.html', context=context)

class BusinessInvestingView(View):

    def get(self, *args, **kwargs):

        business_investing_items = filtering_items_by_caegories(category='B')
        context = {'items': business_investing_items}
        return render(self.request, 'home-page.html', context=context)


class SearchResult(ListView):

    model = Item
    template_name = 'home-page.html'
    context_object_name = 'items'

    def get_queryset(self):
        query = self.request.GET.get('q')
        items = filtering_items_by_icontains_filter(query=query)
        return items


class CheckoutView(LoginRequiredMixin, View):
    
    #TODO: add verification if adress exist in database, get rid of the mistake of dublication

    def get(self, *args, **kwargs):
        try:
            order_queryset = get_order_objects(user=self.request.user, ordered=False)
            context = {
                'form': CheckkOutForm(),
                'couponform': CouponForm(),
                'order': order_queryset
            }
            shipping_address_queryset = filter_and_check_default_adress(
                user=self.request.user,
                adress_type='S',
                default=True
            )
            if shipping_address_queryset:
                context.update({'default_shipping_address': shipping_address_queryset})

            billing_address_queryset = filter_and_check_default_adress(
                user=self.request.user,
                adress_type='B',
                default=True
            )
            if billing_address_queryset:
                context.update({'default_billing_address': billing_address_queryset})

            return render(self.request, "checkout-page.html", context=context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("/")

    def post(self, *args, **kwargs):
        order = get_order_objects(user=self.request.user, ordered=False)
        form = CheckkOutForm(self.request.POST or None)
        if form.is_valid():
            shipping_address1 = form.cleaned_data.get('shipping_address')
            shipping_address2 = form.cleaned_data.get('shipping_address')
            shipping_country = form.cleaned_data.get('shipping_country')
            shipping_zip = form.cleaned_data.get('shipping_zip')

            billing_address1 = form.cleaned_data.get('billing_address')
            billing_address2 = form.cleaned_data.get('billing_address2')
            billing_country = form.cleaned_data.get('billing_country')
            billing_zip = form.cleaned_data.get('billing_zip')
            
            same_billing_address = form.cleaned_data.get('same_billing_address')
            set_default_shipping = form.cleaned_data.get('set_default_shipping')
            use_default_shipping = form.cleaned_data.get('use_default_shipping')
            set_default_billing = form.cleaned_data.get('set_default_billing')
            use_default_billing = form.cleaned_data.get('use_default_billing')

            #Под вопросом остаються пока вот эти кверисеты, я бы их убрал нахер
            address_shipping_queryset = filter_and_check_default_adress(
                user=self.request.user,
                adress_type='S',
                default=True
            )
            address_billing_queryset = filter_and_check_default_adress(
                user=self.request.user,
                adress_type='B',
                default=True
            )
            shipping_adress_or_error = default_shipping_adress(
                user=self.request.user,
                order=order,
                use_default_shipping=use_default_shipping,
                address_shipping_queryset=address_shipping_queryset,
                set_default_shipping=set_default_shipping,
                shipping_address1=shipping_address1,
                shipping_address2=shipping_address2,
                shipping_country=shipping_country,
                shipping_zip=shipping_zip
            )
            if shipping_adress_or_error == 'Please fill in the required shipping address fields':
                messages.info(self.request, 'Please fill in the required shipping address fields')
                return redirect('core:checkout')
            
            if same_billing_address and use_default_billing:
                messages.info(self.request, 'You can not use 2 options at the same time <It is brake the logic>')
                return redirect('core:checkout')
            if same_billing_address:
                #Logic when shipping the same as a billing and we have default shipping
                if use_default_shipping:
                    add_billing_address_to_the_order(order=order, adress_queryset=address_shipping_queryset)
                    if set_default_billing:
                        if address_billing_queryset:
                            if address_shipping_queryset.street_adress != address_billing_queryset.street_adress:
                                change_status_default_address(address=address_billing_queryset, status=False)
                                filtered_billing_adress = check_adress_by_street_adress(user=self.request.user, street_adress=address_shipping_queryset.street_adress)
                                if not filtered_billing_adress:
                                    billing_adress = create_a_new_address(
                                        user=self.request.user,
                                        street_adress=address_shipping_queryset.street_adress,
                                        apartment_adress=address_shipping_queryset.apartment_adress,
                                        country=address_shipping_queryset.country,
                                        zip=address_shipping_queryset.zip,
                                        adress_type='B',
                                    )
                                    change_status_default_address(address=billing_adress, status=True)
                                else:
                                    change_status_default_address(address=filtered_billing_adress, status=True)
                            else:
                                #Не делаем нихуя, она равны
                                messages.info(self.request, 'Do nothing if the same')
                        else:
                            filtered_billing_adress = check_adress_by_street_adress(user=self.request.user, street_adress=address_shipping_queryset.street_adress)
                            if not filtered_billing_adress:
                                billing_adress = create_a_new_address(
                                    user=self.request.user,
                                    street_adress=address_shipping_queryset.street_adress,
                                    apartment_adress=address_shipping_queryset.apartment_adress,
                                    country=address_shipping_queryset.country,
                                    zip=address_shipping_queryset.zip,
                                    adress_type='B',
                                )
                                change_status_default_address(address=billing_adress, status=True)
                            else:
                                change_status_default_address(address=filtered_billing_adress, status=True)
                    else:
                        messages.info(self.request, 'Pizdec')
                else:        
                    messages.info(self.request, 'Govmo')
                    add_billing_address_to_the_order(order=order, adress_queryset=shipping_adress)

            if use_default_billing:
                if address_billing_queryset:
                    add_billing_address_to_the_order(order=order, adress_queryset=address_billing_queryset)
                else:
                    messages.info(self.request, "No default shipping adress available")
                    return redirect('core:checkout')

            if not same_billing_address or use_default_billing:
                if validate_from_for_whitespaces([billing_address1, billing_country, billing_zip]):
                    billing_adress = create_a_new_address(
                        user=self.request.user,
                        street_adress=billing_address1,
                        apartment_adress=billing_address2,
                        country=billing_country,
                        zip=billing_zip,
                        adress_type='B'
                    )
                    add_billing_address_to_the_order(order=order, adress_queryset=billing_adress)
                    #Check if user wants to add thia adress to default
                    if set_default_billing:
                        #Создать функцию создания, так как будет переиспользловна
                        address_queryset = filter_and_check_default_adress(
                            user=self.request.user,
                            adress_type='B',
                            default=True
                        )
                        if address_queryset:
                            change_status_default_address(address_queryset, status=False)
                        change_status_default_address(address=billing_adress, status=True)
                else:
                    messages.info(self.request, 'Please fill in the required billing address fields')
                    return redirect('core:checkout')

            orders = get_all_objects_from_order_items()
            quantity, _ = get_information_about_order(orders=orders)
            summary_items_string = convert_order_items_into_string_view(orders=orders)
            create_a_new_devilered_order_object(
                user=self.request.user,
                summary_items=summary_items_string,
                quantity=quantity
            )
            delete_all_items_from_order(orders=orders)
            delete_order(user=self.request.user, ordered=False)
            messages.info(self.request, 'The order has been send')
            return redirect('core:home')
        messages.warning(self.request, "Failed Checkout")
        return redirect('core:checkout')
        
@login_required
def add_to_cart(request, slug):
    
    item = get_object_or_404(Item, slug=slug)
    order_item, _ = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_queryset = Order.objects.filter(user=request.user, ordered=False)
    if order_queryset.exists():
        order = order_queryset[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated")
            return redirect('core:order-summary')
        else:
            order.items.add(order_item)
            messages.info(request, "This item was aded tou your cart")
            return redirect('core:order-summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was aded tou your cart")
        return redirect('core:order-summary')

@login_required
def remove_from_cart(request, slug):
    
    filtered_order_objects = filter_order_objects(user=request.user, ordered=False)

    if filtered_order_objects:
        filtered_order_items_by_slag = filter_order_item_objects_by_slag(
            user=request.user,
            slug=slug,
            order_quaryset=filtered_order_objects,
            ordered=False
        )
        if filtered_order_items_by_slag:
            remove_item_from_orders(
                user=request.user,
                slug=slug,
                ordered=False
            )
            delete_item_from_order_items(
                user=request.user,
                slug=slug,
                ordered=False
            )
            all_orders = get_all_objects_from_order_items()
            if all_orders.count() == 0:
                delete_order(user=request.user, ordered=False)
                messages.info(request, 'You successfully delete all items from your cart')
                return redirect('core:home')
            messages.info(request, "This item was removed from your cart")
            return redirect('core:order-summary')
        messages.info(request, "This item was not in your cart")
        return redirect('core:order-summary', slug=slug)
    else:
        messages.info(request, "You do not have an active order yet")
        return redirect('core:product', slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):

    filtered_order_objects = filter_order_objects(user=request.user, ordered=False)
    if filtered_order_objects:
        filtered_order_items_by_slag = filter_order_item_objects_by_slag(
            user=request.user,
            slug=slug,
            order_quaryset=filtered_order_objects,
            ordered=False
        )
        if filtered_order_items_by_slag:
            order_item = filter_order_item_objects(
                user=request.user,
                slug=slug,
                ordered=False
            )
            check_item_order_quantity(item=order_item)
            all_orders = get_all_objects_from_order_items()
            if all_orders.count() == 0:
                delete_order(user=request.user, ordered=False)
                messages.info(request, 'You successfully delete all items from your cart')
                return redirect('core:home')
            messages.info(request, "This item quantity has been changed")
            return redirect('core:order-summary')
        messages.info(request, "This item was not in your cart")
        return redirect('core:product', slug=slug)
    else:
        messages.info(request, "You do not have an active order yet")
        return redirect('core:product', slug=slug)