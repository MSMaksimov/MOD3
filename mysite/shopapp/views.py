from timeit import default_timer

from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from rest_framework.viewsets import ModelViewSet

from .models import Product, Order, ProductImage
from .forms import ProductForm
from .serializers import ProductSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]



class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),

        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 2,
        }
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/product-details.html"
    model = Product
    context_object_name = "product"


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    # fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk}
        )


class ProductDeleteView(DeleteView):
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductsListView(ListView):
    template_name = "shopapp/products-list.html"
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    def test_func(self):
        # return self.request.user.groups.filter(name="secret-group").exists()
        return self.request.user.is_superuser
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy("shopapp:products_list")


# class ProductCreateView(UserPassesTestMixin, CreateView):
#     def test_func(self):
#         # return self.request.user.groups.filter(name="secret-group").exists()
#         return self.request.user.is_superuser
#     model = Product
#     fields = "name", "price", "description", "discount"
#     success_url = reverse_lazy("shopapp:products_list")


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects.select_related("user").prefetch_related("products")
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects.select_related("user").prefetch_related("products")
    )


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by("pk").all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "description": product.description,
                "archived": product.archived,
            }
            for product in products
        ]
        return JsonResponse({"products": products_data})